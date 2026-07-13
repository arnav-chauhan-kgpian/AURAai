"""Observability wiring.

Initialises error tracking (Sentry), distributed tracing (OpenTelemetry → OTLP),
and Prometheus metrics. Everything is **optional and lazy**: a subsystem only
activates when its config is present and its library is installed, so the app
runs identically in dev without any of them. Correlation ids are already bound
into structured logs by ``RequestContextMiddleware``.
"""

from fastapi import FastAPI

from app.config.config import Settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def init_observability(app: FastAPI, settings: Settings) -> None:
    """Best-effort setup of Sentry, tracing and metrics."""

    _init_sentry(settings)
    _init_tracing(app, settings)
    _init_metrics(app, settings)


def _init_sentry(settings: Settings) -> None:
    if not settings.sentry_dsn:
        return
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.starlette import StarletteIntegration

        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.environment,
            traces_sample_rate=settings.sentry_traces_sample_rate,
            integrations=[StarletteIntegration(), FastApiIntegration()],
            send_default_pii=False,
        )
        logger.info("observability.sentry_enabled")
    except Exception as exc:  # noqa: BLE001 - never block startup on telemetry
        logger.warning("observability.sentry_failed", error=str(exc))


def _init_tracing(app: FastAPI, settings: Settings) -> None:
    if not settings.otel_exporter_otlp_endpoint:
        return
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        provider = TracerProvider(
            resource=Resource.create({"service.name": settings.otel_service_name})
        )
        provider.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint))
        )
        trace.set_tracer_provider(provider)
        FastAPIInstrumentor.instrument_app(app, excluded_urls="health,ready,metrics")
        logger.info("observability.tracing_enabled")
    except Exception as exc:  # noqa: BLE001
        logger.warning("observability.tracing_failed", error=str(exc))


def _init_metrics(app: FastAPI, settings: Settings) -> None:
    if not settings.metrics_enabled:
        return
    try:
        from prometheus_fastapi_instrumentator import Instrumentator

        excluded = ["/api/v1/health", "/api/v1/ready", "/health", "/ready", "/metrics"]
        instrumentator = Instrumentator(excluded_handlers=excluded).instrument(app)

        # Metrics are always collected; expose /metrics carefully. In production,
        # only serve it when a token is configured, and require it — an
        # unauthenticated public /metrics leaks operational internals.
        if not settings.is_production:
            instrumentator.expose(app, endpoint="/metrics", include_in_schema=False)
            logger.info("observability.metrics_enabled", guarded=False)
        elif settings.metrics_token:
            _expose_guarded_metrics(app, settings.metrics_token)
            logger.info("observability.metrics_enabled", guarded=True)
        else:
            logger.info("observability.metrics_endpoint_disabled_in_prod")
    except Exception as exc:  # noqa: BLE001
        logger.warning("observability.metrics_unavailable", error=str(exc))


def _expose_guarded_metrics(app: FastAPI, token: str) -> None:
    """Serve /metrics only to callers presenting the configured token."""

    from fastapi import Request, Response
    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

    @app.get("/metrics", include_in_schema=False)
    async def metrics(request: Request) -> Response:  # pragma: no cover - thin I/O
        header = request.headers.get("authorization", "")
        provided = header.removeprefix("Bearer ").strip() or request.query_params.get(
            "token", ""
        )
        if provided != token:
            # 404 (not 401) so the endpoint's existence isn't confirmed.
            return Response(status_code=404)
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
