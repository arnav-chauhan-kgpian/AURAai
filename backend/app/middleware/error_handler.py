"""Global exception handlers.

Translates the application's exception hierarchy and unhandled errors into
consistent JSON responses so clients receive a stable error contract.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AuraError, RateLimitedError, UnauthenticatedError
from app.core.logging import get_logger

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Attach exception handlers to the FastAPI application."""

    @app.exception_handler(AuraError)
    async def handle_aura_error(request: Request, exc: AuraError) -> JSONResponse:
        logger.warning(
            "request.handled_error",
            error_code=exc.error_code,
            path=request.url.path,
        )
        headers: dict[str, str] = {}
        if isinstance(exc, RateLimitedError) and exc.retry_after:
            headers["Retry-After"] = str(exc.retry_after)
        if isinstance(exc, UnauthenticatedError):
            headers["WWW-Authenticate"] = "Bearer"
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.error_code, "message": exc.message}},
            headers=headers or None,
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.error("request.unhandled_error", path=request.url.path, exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "internal_error", "message": "Internal server error"}},
        )
