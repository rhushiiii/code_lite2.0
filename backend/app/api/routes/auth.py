from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_github_auth_state,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import TokenResponse, UserCreate, UserLogin, UserOut
from app.services.github_oauth_service import GitHubOAuthService

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()
oauth_service = GitHubOAuthService()


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email.lower(),
        hashed_password=get_password_hash(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token, user=user)


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token, user=user)


@router.get("/github/login-url")
def github_login_url():
    state = create_github_auth_state()
    auth_url = oauth_service.build_authorize_url(
        state=state,
        redirect_uri=settings.GITHUB_OAUTH_REDIRECT_URI,
        scope="repo read:user user:email",
    )
    return {"url": auth_url}


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
