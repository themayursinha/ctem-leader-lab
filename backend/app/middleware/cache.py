from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class CacheControlMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if request.method == "GET" and response.status_code == 200:
            path = request.url.path
            if path.startswith("/api/") and path != "/healthz":
                if "export" in path:
                    response.headers["Cache-Control"] = "no-cache"
                else:
                    response.headers["Cache-Control"] = "private, max-age=30"
        else:
            response.headers["Cache-Control"] = "no-store"
        return response
