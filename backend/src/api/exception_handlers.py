import structlog
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.domain.exceptions import DomainException

logger = structlog.get_logger(__name__)


ERROR_CODE_TO_HTTP = {
    # Validation
    "VALIDATION_ERROR": status.HTTP_400_BAD_REQUEST,
    # Business
    "BUSINESS_RULE_VIOLATION": status.HTTP_422_UNPROCESSABLE_ENTITY,
    # Entity
    "ENTITY_NOT_FOUND": status.HTTP_404_NOT_FOUND,
    "ENTITY_ALREADY_EXISTS": status.HTTP_409_CONFLICT,
    # Auth
    "INVALID_CREDENTIALS": status.HTTP_401_UNAUTHORIZED,
    "ACCOUNT_INACTIVE": status.HTTP_403_FORBIDDEN,
    "EMAIL_ALREADY_EXISTS": status.HTTP_409_CONFLICT,
    "FORBIDDEN": status.HTTP_403_FORBIDDEN,
    # Token
    "TOKEN_MISSING": status.HTTP_401_UNAUTHORIZED,
    "TOKEN_INVALID": status.HTTP_401_UNAUTHORIZED,
    "TOKEN_EXPIRED": status.HTTP_401_UNAUTHORIZED,
    "TOKEN_REVOKED": status.HTTP_401_UNAUTHORIZED,
    # Security
    "SECURITY_BREACH": status.HTTP_403_FORBIDDEN,
}


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(DomainException)
    async def handle_domain_exception(request: Request, exc: DomainException) -> JSONResponse:
        status_code = ERROR_CODE_TO_HTTP.get(exc.code, status.HTTP_400_BAD_REQUEST)

        logger.warning(
            "Domain exception occurred",
            error_code=exc.code,
            error_message=exc.message,
            path=request.url.path,
            method=request.method,
        )

        return JSONResponse(
            status_code=status_code,
            content={
                "status": status_code,
                "error": exc.code,
                "message": exc.message,
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:

        logger.debug(
            "HTTP exception occurred",
            status_code=exc.status_code,
            error_detail=exc.detail,
            path=request.url.path,
            method=request.method,
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": exc.status_code,
                "error": "HTTP_ERROR",
                "message": exc.detail,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_exception(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.debug(
            "Request validation failed",
            path=request.url.path,
            method=request.method,
            validation_errors=exc.errors(),
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status": 422,
                "error": "REQUEST_VALIDATION_ERROR",
                "message": "Invalid request",
                "meta": jsonable_encoder(exc.errors()),
            },
        )

    @app.exception_handler(IntegrityError)
    async def handle_integrity_error(request: Request, exc: IntegrityError) -> JSONResponse:
        logger.warning(
            "Database integrity violation",
            path=request.url.path,
            method=request.method,
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "status": status.HTTP_409_CONFLICT,
                "error": "ENTITY_ALREADY_EXISTS",
                "message": "A record with this value already exists.",
            },
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_exception(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(
            "Unhandled exception occurred",
            path=request.url.path,
            method=request.method,
        )
        return JSONResponse(
            status_code=500,
            content={
                "status": 500,
                "error": "INTERNAL_SERVER_ERROR",
                "message": "Something went wrong",
            },
        )
