from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewRequest
from app.services.github_service import GitHubService
from app.services.llm_service import LLMService
from app.services.token_crypto import decrypt_secret


def summarize_severity(issues: list[dict]) -> dict[str, int]:
    summary = {"low": 0, "medium": 0, "high": 0}
    for issue in issues:
        severity = str(issue.get("severity", "low")).lower()
        if severity in summary:
            summary[severity] += 1
    return summary


class ReviewService:
    def __init__(self) -> None:
        self.github_service = GitHubService()
        self.llm_service = LLMService()

    async def run_review(
        self,
        payload: ReviewRequest,
        user: User,
        db: Session,
    ) -> tuple[Review, dict]:
        token = payload.github_token
        if not token and user.github_token_encrypted:
            try:
                token = decrypt_secret(user.github_token_encrypted)
            except Exception as exc:  # noqa: BLE001
                raise HTTPException(
                    status_code=400,
                    detail="Stored GitHub token could not be decrypted. Reconnect GitHub.",
                ) from exc

        if not token:
            raise HTTPException(
                status_code=400,
                detail="GitHub access is required. Connect your GitHub account or provide a token.",
            )

        token_ok = await self.github_service.validate_token(token)
        if not token_ok:
            raise HTTPException(status_code=401, detail="Invalid GitHub token")

        diff, changed_files = await self.github_service.fetch_pr_diff(
            repo_owner=payload.repo_owner,
            repo_name=payload.repo_name,
            pr_number=payload.pr_number,
            token=token,
        )

        result_json = await self.llm_service.analyze_diff(diff, changed_files)

        review = Review(
            user_id=user.id,
            repo_name=f"{payload.repo_owner}/{payload.repo_name}",
            pr_number=payload.pr_number,
            result_json=result_json,
        )

        db.add(review)
        db.commit()
        db.refresh(review)

        return review, result_json
