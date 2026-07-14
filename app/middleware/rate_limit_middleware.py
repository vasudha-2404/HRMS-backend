"""Rate limiting middleware (Redis-ready)."""

import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.config import settings

# In-memory fallback when Redis is unavailable
_request_counts: dict[str, list[float]] = defaultdict(list)


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        if request.method == "OPTIONS" or request.url.path in ("/health", "/docs", "/openapi.json", "/redoc"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = 60.0

        timestamps = _request_counts[client_ip]
        _request_counts[client_ip] = [t for t in timestamps if now - t < window]

        if len(_request_counts[client_ip]) >= settings.RATE_LIMIT_PER_MINUTE:
            return JSONResponse(
                status_code=429,
                content={"success": False, "error": "Rate limit exceeded. Try again later."},
            )

        _request_counts[client_ip].append(now)
        return await call_next(request)
