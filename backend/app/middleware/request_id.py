from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging_config import generate_request_id, request_id


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("X-Request-ID", generate_request_id())
        request_id.set(rid)
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = rid[:16]
        return response
