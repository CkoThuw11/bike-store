# src/core/middleware.py
import time
import uuid
import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger(__name__)

_SKIP_PATHS = {"/health", "/metrics", "/favicon.ico"}


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Runs around every HTTP request. Responsibilities:
      1. Attach a short request_id to request.state (handlers can read it) and
         bind it into structlog's contextvars, so every log line emitted while
         this request is in flight - including the ones in exception_handlers.py
         and any service/repository code - carries it automatically without
         having to thread it through every call.
      2. Log method + path + status + duration as structured fields
      3. Safely handle the case where call_next raises an exception that
         escapes FastAPI's own exception handlers (without this, duration
         and status would be lost on that failure path)
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in _SKIP_PATHS:
            return await call_next(request)

        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start_time = time.perf_counter()

        try:
            logger.debug(
                "Request started",
                method=request.method,
                path=request.url.path,
                client_ip=_get_client_ip(request),
            )

            try:
                response = await call_next(request)
            except Exception:
                duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
                logger.error(
                    "Request failed with unhandled exception",
                    method=request.method,
                    path=request.url.path,
                    status_code=500,
                    duration_ms=duration_ms,
                )
                raise

            status_code = response.status_code
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

            log_fn = logger.debug
            if status_code >= 500:
                log_fn = logger.error
            elif status_code >= 400:
                log_fn = logger.warning

            log_fn(
                "Request completed",
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                duration_ms=duration_ms,
            )

            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            structlog.contextvars.clear_contextvars()


def _get_client_ip(request: Request) -> str:
    """
    Real IP when behind a reverse proxy (nginx, AWS ALB).
    X-Forwarded-For contains the chain: "client, proxy1, proxy2"
    The leftmost value is the original client.
    Falls back to the direct connection IP if the header is absent.
    """
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
