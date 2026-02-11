from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.core.config import get_settings

settings = get_settings()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except ValueError:
        return False


def get_password_hash(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12))
    return hashed.decode("utf-8")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def create_oauth_state_token(
    payload: dict,
    state_type: str,
    expires_minutes: int = 10,
) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    token_payload = payload.copy()
    token_payload.update({"type": state_type, "exp": expire})
    return jwt.encode(token_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_oauth_state_token(state_token: str, expected_type: str) -> dict:
    payload = jwt.decode(
        state_token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    token_type = payload.get("type")
    if token_type != expected_type:
        raise JWTError("Invalid state token type")
    return payload


def create_github_oauth_state(user_id: int) -> str:
    payload = {"sub": str(user_id)}
    return create_oauth_state_token(payload=payload, state_type="github_oauth_state")


def decode_github_oauth_state(state_token: str) -> int:
    payload = decode_oauth_state_token(state_token, expected_type="github_oauth_state")
    user_id = payload.get("sub")
    if user_id is None:
        raise JWTError("State token missing subject")
    return int(user_id)


def create_github_auth_state() -> str:
    return create_oauth_state_token(payload={}, state_type="github_auth_state")


def decode_github_auth_state(state_token: str) -> None:
    decode_oauth_state_token(state_token, expected_type="github_auth_state")
