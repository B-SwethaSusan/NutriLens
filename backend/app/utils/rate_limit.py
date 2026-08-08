import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class InMemoryRateLimitMiddleware(BaseHTTPMiddleware):
    """A safe single-process limiter; use an API gateway/Redis for multi-replica deployments."""

    def __init__(self, app, limit: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        if request.url.path in {"/health", "/api/health", "/docs", "/openapi.json"}:
            return await call_next(request)
        key = request.client.host if request.client else "unknown"
        now = time.monotonic()
        bucket = self.requests[key]
        while bucket and now - bucket[0] > self.window_seconds:
            bucket.popleft()
        if len(bucket) >= self.limit:
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded. Please retry shortly."}, headers={"Retry-After": str(self.window_seconds)})
        bucket.append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, self.limit - len(bucket)))
        return response
