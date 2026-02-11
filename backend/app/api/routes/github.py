from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from jose import JWTError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import create_github_oauth_state, decode_github_oauth_state
from app.models.user import User
from app.schemas.github import ReposPendingPullsResponse
from app.services.github_service import GitHubService
from app.services.github_oauth_service import GitHubOAuthService
from app.services.token_crypto import decrypt_secret, encrypt_secret

router = APIRouter(prefix="/github", tags=["github"])
settings = get_settings()
oauth_service = GitHubOAuthService()
github_service = GitHubService()


def _get_connected_token(current_user: User) -> str:
    if not current_user.github_token_encrypted:
        raise HTTPException(status_code=400, detail="GitHub is not connected for this account")
    try:
        return decrypt_secret(current_user.github_token_encrypted)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail="Stored GitHub token is invalid. Reconnect GitHub.") from exc


@router.get("/connect-url")
def get_connect_url(current_user: User = Depends(get_current_user)):
    state = create_github_oauth_state(current_user.id)
    auth_url = oauth_service.build_authorize_url(state)
    return {"url": auth_url}


@router.get("/status")
def github_status(current_user: User = Depends(get_current_user)):
    return {
        "connected": bool(current_user.github_token_encrypted),
        "username": current_user.github_username,
    }


@router.get("/repos-pending-prs", response_model=ReposPendingPullsResponse)
async def list_repos_pending_prs(
    max_repos: int = Query(default=25, ge=1, le=100),
    pulls_per_repo: int = Query(default=5, ge=1, le=20),
    only_with_open: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
):
    token = _get_connected_token(current_user)
    total_repos_scanned, repos = await github_service.list_repos_with_pending_prs(
        token=token,
        max_repos=max_repos,
        pulls_per_repo=pulls_per_repo,
        only_with_open=only_with_open,
    )
    return ReposPendingPullsResponse(total_repos_scanned=total_repos_scanned, repos=repos)


@router.post("/disconnect")
def disconnect_github(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.github_token_encrypted = None
    current_user.github_username = None
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return {"connected": False}


@router.get("/callback")
async def github_callback(
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    dashboard_url = f"{settings.FRONTEND_URL.rstrip('/')}/dashboard"

    if error:
        return RedirectResponse(f"{dashboard_url}?github=error")

    if not code or not state:
        return RedirectResponse(f"{dashboard_url}?github=invalid_callback")

    try:
        user_id = decode_github_oauth_state(state)
    except (JWTError, ValueError):
        return RedirectResponse(f"{dashboard_url}?github=invalid_state")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return RedirectResponse(f"{dashboard_url}?github=user_not_found")

    try:
        token = await oauth_service.exchange_code_for_token(code)
        username = await oauth_service.fetch_github_username(token)
    except HTTPException:
        return RedirectResponse(f"{dashboard_url}?github=token_exchange_failed")

    user.github_token_encrypted = encrypt_secret(token)
    user.github_username = username
    db.add(user)
    db.commit()

    return RedirectResponse(f"{dashboard_url}?github=connected")
