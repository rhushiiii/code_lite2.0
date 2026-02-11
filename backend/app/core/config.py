from functools import lru_cache
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")
load_dotenv()


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "AI PR Review Agent API")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    CORS_ORIGINS_RAW: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    CORS_ALLOW_ORIGIN_REGEX: str = os.getenv(
        "CORS_ALLOW_ORIGIN_REGEX",
        r"https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    )

    GITHUB_API_BASE_URL: str = os.getenv("GITHUB_API_BASE_URL", "https://api.github.com")
    GITHUB_OAUTH_AUTHORIZE_URL: str = os.getenv(
        "GITHUB_OAUTH_AUTHORIZE_URL",
        "https://github.com/login/oauth/authorize",
    )
    GITHUB_OAUTH_TOKEN_URL: str = os.getenv(
        "GITHUB_OAUTH_TOKEN_URL",
        "https://github.com/login/oauth/access_token",
    )
    GITHUB_CLIENT_ID: str = os.getenv("GITHUB_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET: str = os.getenv("GITHUB_CLIENT_SECRET", "")
    GITHUB_OAUTH_REDIRECT_URI: str = os.getenv(
        "GITHUB_OAUTH_REDIRECT_URI",
        "http://localhost:8000/github/callback",
    )
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    TOKEN_ENCRYPTION_KEY: str = os.getenv("TOKEN_ENCRYPTION_KEY", "")

    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
    LLM_MAX_RETRIES: int = int(os.getenv("LLM_MAX_RETRIES", "3"))
    LLM_TIMEOUT_SECONDS: int = int(os.getenv("LLM_TIMEOUT_SECONDS", "90"))
    MAX_DIFF_CHARS: int = int(os.getenv("MAX_DIFF_CHARS", "18000"))

    GENERAL_RATE_LIMIT_PER_MIN: int = int(os.getenv("GENERAL_RATE_LIMIT_PER_MIN", "120"))
    REVIEW_RATE_LIMIT_PER_MIN: int = int(os.getenv("REVIEW_RATE_LIMIT_PER_MIN", "20"))

    @property
    def cors_origins(self) -> list[str]:
        origins = [origin.strip() for origin in self.CORS_ORIGINS_RAW.split(",") if origin.strip()]
        return origins or ["http://localhost:5173"]

    @property
    def cors_allow_origin_regex(self) -> str | None:
        regex = self.CORS_ALLOW_ORIGIN_REGEX.strip()
        return regex or None


@lru_cache
def get_settings() -> Settings:
    return Settings()
