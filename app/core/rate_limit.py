import time
from collections import defaultdict

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter. Use Redis in production for multi-instance."""

    def __init__(self, app):
        super().__init__(app)
        self.minute_buckets: dict[str, list[float]] = defaultdict(list)
        self.day_buckets: dict[str, list[float]] = defaultdict(list)

    def _client_key(self, request: Request) -> str:
        # Use client_id from token if available, otherwise IP
        return request.headers.get("X-Client-ID", request.client.host if request.client else "unknown")

    def _clean_bucket(self, bucket: list[float], window_seconds: float) -> list[float]:
        cutoff = time.time() - window_seconds
        return [t for t in bucket if t > cutoff]

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for docs and health check
        if request.url.path in ("/docs", "/openapi.json", "/health", "/"):
            return await call_next(request)

        key = self._client_key(request)
        now = time.time()

        # Per-minute check
        self.minute_buckets[key] = self._clean_bucket(self.minute_buckets[key], 60)
        if len(self.minute_buckets[key]) >= settings.rate_limit_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded (per minute)",
                headers={"Retry-After": "60"},
            )

        # Per-day check
        self.day_buckets[key] = self._clean_bucket(self.day_buckets[key], 86400)
        if len(self.day_buckets[key]) >= settings.rate_limit_per_day:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded (daily)",
                headers={"Retry-After": "3600"},
            )

        self.minute_buckets[key].append(now)
        self.day_buckets[key].append(now)

        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit-Minute"] = str(settings.rate_limit_per_minute)
        response.headers["X-RateLimit-Remaining-Minute"] = str(
            settings.rate_limit_per_minute - len(self.minute_buckets[key])
        )
        response.headers["X-RateLimit-Limit-Day"] = str(settings.rate_limit_per_day)

        return response
