"""Rate limiting module name aligned to required structure."""

from app.middleware.rate_limit_middleware import RateLimitMiddleware

__all__ = ["RateLimitMiddleware"]

