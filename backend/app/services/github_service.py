import re
import asyncio

import httpx
from fastapi import HTTPException

from app.core.config import get_settings

settings = get_settings()


class GitHubService:
    @staticmethod
    def _json_headers(token: str) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    @staticmethod
    def _handle_error(response: httpx.Response, fallback_detail: str) -> None:
        if response.status_code == 401:
            raise HTTPException(status_code=401, detail="Invalid GitHub token")
        if response.status_code == 403:
            raise HTTPException(status_code=403, detail="GitHub API rate limit or access denied")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="GitHub resource not found")
        if response.status_code >= 500:
            raise HTTPException(status_code=502, detail="GitHub is currently unavailable")
        if response.status_code >= 400:
            raise HTTPException(status_code=400, detail=fallback_detail)

    async def validate_token(self, token: str) -> bool:
        headers = self._json_headers(token)
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(f"{settings.GITHUB_API_BASE_URL}/user", headers=headers)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail="Unable to validate GitHub token right now") from exc

        return response.status_code == 200

    async def fetch_pr_diff(
        self,
        repo_owner: str,
        repo_name: str,
        pr_number: int,
        token: str,
    ) -> tuple[str, list[str]]:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3.diff",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        pr_url = f"{settings.GITHUB_API_BASE_URL}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}"

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(pr_url, headers=headers)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail="Unable to reach GitHub API") from exc

        self._handle_error(response, "Unable to fetch pull request diff")

        diff = response.text
        if not diff.strip():
            raise HTTPException(status_code=400, detail="Empty pull request diff")

        return diff, self.extract_changed_files(diff)

    async def fetch_user_repos(
        self,
        token: str,
        per_page: int = 100,
        max_pages: int = 3,
    ) -> list[dict]:
        headers = self._json_headers(token)
        repos: list[dict] = []

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                for page in range(1, max_pages + 1):
                    response = await client.get(
                        f"{settings.GITHUB_API_BASE_URL}/user/repos",
                        headers=headers,
                        params={
                            "sort": "updated",
                            "per_page": per_page,
                            "page": page,
                            "affiliation": "owner,collaborator,organization_member",
                        },
                    )
                    self._handle_error(response, "Unable to fetch repositories")
                    batch = response.json()
                    if not isinstance(batch, list) or not batch:
                        break
                    repos.extend(batch)
                    if len(batch) < per_page:
                        break
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail="Unable to reach GitHub API") from exc

        return repos

    async def fetch_open_pulls(
        self,
        token: str,
        repo_owner: str,
        repo_name: str,
        per_page: int = 5,
    ) -> list[dict]:
        headers = self._json_headers(token)
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(
                    f"{settings.GITHUB_API_BASE_URL}/repos/{repo_owner}/{repo_name}/pulls",
                    headers=headers,
                    params={"state": "open", "per_page": per_page, "sort": "updated", "direction": "desc"},
                )
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail="Unable to reach GitHub API") from exc

        self._handle_error(response, "Unable to fetch pull requests")
        data = response.json()
        if not isinstance(data, list):
            return []
        return data

    async def list_repos_with_pending_prs(
        self,
        token: str,
        max_repos: int = 25,
        pulls_per_repo: int = 5,
        only_with_open: bool = False,
    ) -> tuple[int, list[dict]]:
        repos = await self.fetch_user_repos(token=token)
        repos = repos[:max_repos]

        semaphore = asyncio.Semaphore(5)

        async def fetch_repo_entry(repo: dict) -> dict | None:
            owner = ((repo.get("owner") or {}).get("login")) or ""
            name = repo.get("name") or ""
            full_name = repo.get("full_name") or f"{owner}/{name}"
            if not owner or not name:
                return None

            async with semaphore:
                pulls = await self.fetch_open_pulls(
                    token=token,
                    repo_owner=owner,
                    repo_name=name,
                    per_page=pulls_per_repo,
                )

            entry = {
                "owner": owner,
                "repo": name,
                "full_name": full_name,
                "private": bool(repo.get("private", False)),
                "html_url": repo.get("html_url") or "",
                "pending_pr_count": len(pulls),
                "pending_pull_requests": [
                    {
                        "number": pr.get("number"),
                        "title": pr.get("title") or "",
                        "html_url": pr.get("html_url") or "",
                        "state": pr.get("state") or "open",
                        "draft": bool(pr.get("draft", False)),
                        "created_at": pr.get("created_at") or "",
                        "updated_at": pr.get("updated_at") or "",
                        "author": ((pr.get("user") or {}).get("login")),
                    }
                    for pr in pulls
                ],
            }

            if only_with_open and entry["pending_pr_count"] == 0:
                return None
            return entry

        tasks = [fetch_repo_entry(repo) for repo in repos]
        raw_entries = await asyncio.gather(*tasks)
        entries = [entry for entry in raw_entries if entry]
        return len(repos), entries

    @staticmethod
    def extract_changed_files(diff_text: str) -> list[str]:
        files: list[str] = []
        seen = set()

        for line in diff_text.splitlines():
            if line.startswith("diff --git "):
                match = re.search(r" b/(.+)$", line)
                if match:
                    filename = match.group(1).strip()
                    if filename not in seen:
                        seen.add(filename)
                        files.append(filename)

        return files
