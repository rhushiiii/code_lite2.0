import secrets

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from jose import JWTError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_github_oauth_state,
    decode_oauth_state_token,
    get_password_hash,
)
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
    auth_url = oauth_service.build_authorize_url(
        state=state,
        redirect_uri=settings.GITHUB_OAUTH_REDIRECT_URI,
        scope="repo read:user user:email",
    )
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
    login_url = f"{settings.FRONTEND_URL.rstrip('/')}/login"
    auth_success_url = f"{settings.FRONTEND_URL.rstrip('/')}/auth/github/success"

    if error:
        return RedirectResponse(f"{login_url}?github_auth=error")

    if not code or not state:
        return RedirectResponse(f"{login_url}?github_auth=invalid_callback")

    try:
        state_payload = decode_oauth_state_token(state, expected_type="github_oauth_state")
        state_type = "github_oauth_state"
    except (JWTError, ValueError):
        try:
            state_payload = decode_oauth_state_token(state, expected_type="github_auth_state")
            state_type = "github_auth_state"
        except JWTError:
            return RedirectResponse(f"{login_url}?github_auth=invalid_state")

    try:
        token = await oauth_service.exchange_code_for_token(
            code=code,
            redirect_uri=settings.GITHUB_OAUTH_REDIRECT_URI,
        )
        github_user = await oauth_service.fetch_github_user(token)
        username = github_user.get("login")
    except HTTPException:
        return RedirectResponse(f"{login_url}?github_auth=token_exchange_failed")

    if state_type == "github_oauth_state":
        user_id = state_payload.get("sub")
        if user_id is None:
            return RedirectResponse(f"{dashboard_url}?github=invalid_state")
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            return RedirectResponse(f"{dashboard_url}?github=user_not_found")

        user.github_token_encrypted = encrypt_secret(token)
        user.github_username = username
        db.add(user)
        db.commit()
        return RedirectResponse(f"{dashboard_url}?github=connected")

    github_id_raw = github_user.get("id")
    github_id = str(github_id_raw) if github_id_raw is not None else None
    if not github_id:
        return RedirectResponse(f"{login_url}?github_auth=missing_profile")

    github_email = await oauth_service.fetch_primary_email(token)
    candidate_email = str(github_email).lower() if github_email else f"github-{github_id}@users.local"

    user = db.query(User).filter(User.github_id == github_id).first()
    if not user:
        user = db.query(User).filter(User.email == candidate_email).first()

    if user:
        user.github_id = github_id
        user.github_username = username
        user.github_token_encrypted = encrypt_secret(token)
    else:
        random_password = secrets.token_urlsafe(32)
        user = User(
            email=candidate_email,
            hashed_password=get_password_hash(random_password),
            github_id=github_id,
            github_username=username,
            github_token_encrypted=encrypt_secret(token),
        )
        db.add(user)

    db.commit()
    db.refresh(user)
    app_token = create_access_token({"sub": str(user.id)})
    return RedirectResponse(f"{auth_success_url}?token={app_token}")
