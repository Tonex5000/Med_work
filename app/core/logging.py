import json
import logging
import time
from datetime import datetime, timezone
from typing import Any

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class JsonFormatter(logging.Formatter):
    """Format log records as JSON for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        for key in ("request_id", "method", "path", "status_code", "duration_ms"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)

        return json.dumps(payload)


def configure_logging() -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    if root_logger.handlers:
        root_logger.handlers.clear()

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root_logger.addHandler(handler)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Logs incoming requests and outgoing responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        logger = logging.getLogger("app.request")
        start_time = time.perf_counter()

        response: Response
        try:
            response = await call_next(request)
        finally:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.info(
                "request_completed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": getattr(locals().get("response"), "status_code", 500),
                    "duration_ms": duration_ms,
                },
            )

        return response
