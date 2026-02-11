from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, github, review
from app.core.config import get_settings
from app.core.database import init_db
from app.core.rate_limit import RateLimitMiddleware

settings = get_settings()

init_db()

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)

app.include_router(auth.router)
app.include_router(github.router)
app.include_router(review.router)


@app.get("/")
def health_check():
    return {"status": "ok", "service": settings.APP_NAME}
