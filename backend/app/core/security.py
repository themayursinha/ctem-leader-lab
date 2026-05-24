import hmac
import logging

from fastapi import Header, HTTPException, status

from app.config import settings

logger = logging.getLogger("ctem")


def require_admin_token(x_ctem_admin_token: str | None = Header(default=None)) -> None:
    expected = settings.admin_token
    if not expected:
        return
    if not x_ctem_admin_token or not hmac.compare_digest(x_ctem_admin_token, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid admin token.")
