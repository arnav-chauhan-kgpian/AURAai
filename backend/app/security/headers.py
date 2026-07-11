"""Security headers middleware (the FastAPI equivalent of Helmet).

Adds a conservative set of response headers appropriate for a JSON API. HSTS is
opt-in (only correct behind HTTPS) and CSP locks the API down to no active
content, since it never serves HTML.
"""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.config.config import Settings

_BASE_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'; base-uri 'none'",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-origin",
    "X-XSS-Protection": "0",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Attach hardened security headers to every response."""

    def __init__(self, app, settings: Settings) -> None:
        super().__init__(app)
        self._headers = dict(_BASE_HEADERS)
        if settings.hsts_enabled:
            self._headers["Strict-Transport-Security"] = (
                "max-age=63072000; includeSubDomains; preload"
            )

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        for key, value in self._headers.items():
            response.headers.setdefault(key, value)
        return response
