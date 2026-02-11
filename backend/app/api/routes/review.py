from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewRequest, ReviewResponse
from app.services.review_service import ReviewService, summarize_severity

router = APIRouter(tags=["reviews"])
review_service = ReviewService()


@router.post("/review", response_model=ReviewResponse)
async def create_review(
    payload: ReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review, result_json = await review_service.run_review(payload, current_user, db)
    issues = result_json.get("issues", [])
    changed_files = result_json.get("changed_files", [])

    return ReviewResponse(
        id=review.id,
        repo_name=review.repo_name,
        pr_number=review.pr_number,
        result_json=review.result_json,
        severity_summary=summarize_severity(issues),
        changed_files=changed_files,
        created_at=review.created_at,
    )


@router.get("/reviews", response_model=list[ReviewResponse])
def list_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reviews = (
        db.query(Review)
        .filter(Review.user_id == current_user.id)
        .order_by(Review.created_at.desc())
        .all()
    )

    response: list[ReviewResponse] = []
    for review in reviews:
        result_json = review.result_json or {}
        issues = result_json.get("issues", [])
        response.append(
            ReviewResponse(
                id=review.id,
                repo_name=review.repo_name,
                pr_number=review.pr_number,
                result_json=result_json,
                severity_summary=summarize_severity(issues),
                changed_files=result_json.get("changed_files", []),
                created_at=review.created_at,
            )
        )

    return response
