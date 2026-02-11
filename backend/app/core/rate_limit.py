from collections import defaultdict, deque
from threading import Lock
from time import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.config import get_settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        settings = get_settings()
        self.default_limit = settings.GENERAL_RATE_LIMIT_PER_MIN
        self.review_limit = settings.REVIEW_RATE_LIMIT_PER_MIN
        self.window_seconds = 60
        self.bucket: dict[str, deque[float]] = defaultdict(deque)
        self.lock = Lock()

    def _resolve_limit(self, path: str) -> int:
        if path.startswith("/review"):
            return self.review_limit
        return self.default_limit

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path.startswith("/docs") or path.startswith("/openapi"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        key = f"{client_ip}:{path}"
        now = time()
        limit = self._resolve_limit(path)

        with self.lock:
            timestamps = self.bucket[key]
            while timestamps and now - timestamps[0] > self.window_seconds:
                timestamps.popleft()

            if len(timestamps) >= limit:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded. Please retry in a minute."},
                )

            timestamps.append(now)

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        return response
