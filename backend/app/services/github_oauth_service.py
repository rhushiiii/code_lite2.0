from urllib.parse import urlencode

import httpx
from fastapi import HTTPException

from app.core.config import get_settings

settings = get_settings()


class GitHubOAuthService:
    def ensure_configured(self) -> None:
        if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
            raise HTTPException(
                status_code=500,
                detail="GitHub OAuth is not configured. Set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET.",
            )

    def build_authorize_url(self, state: str) -> str:
        self.ensure_configured()

        query = urlencode(
            {
                "client_id": settings.GITHUB_CLIENT_ID,
                "redirect_uri": settings.GITHUB_OAUTH_REDIRECT_URI,
                "scope": "repo read:user",
                "state": state,
            }
        )
        return f"{settings.GITHUB_OAUTH_AUTHORIZE_URL}?{query}"

    async def exchange_code_for_token(self, code: str) -> str:
        self.ensure_configured()
        payload = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "client_secret": settings.GITHUB_CLIENT_SECRET,
            "code": code,
            "redirect_uri": settings.GITHUB_OAUTH_REDIRECT_URI,
        }
        headers = {"Accept": "application/json"}

        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.post(settings.GITHUB_OAUTH_TOKEN_URL, data=payload, headers=headers)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail="Unable to connect to GitHub OAuth") from exc

        if response.status_code >= 400:
            raise HTTPException(status_code=400, detail="GitHub OAuth token exchange failed")

        body = response.json()
        access_token = body.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="GitHub OAuth token missing in response")

        return access_token

    async def fetch_github_username(self, access_token: str) -> str | None:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.get(f"{settings.GITHUB_API_BASE_URL}/user", headers=headers)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail="Unable to fetch GitHub user profile") from exc

        if response.status_code >= 400:
            raise HTTPException(status_code=400, detail="GitHub user profile fetch failed")

        body = response.json()
        return body.get("login")
