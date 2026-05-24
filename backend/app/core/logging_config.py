import logging
import sys
import uuid
from contextvars import ContextVar

request_id: ContextVar[str] = ContextVar("request_id", default="")


class RequestIDFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id.get()[:8]
        return True


def setup_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    handler.addFilter(RequestIDFilter())
    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler],
        format="%(levelname)s [%(request_id)s] %(name)s: %(message)s",
        force=True,
    )


def generate_request_id() -> str:
    return uuid.uuid4().hex
