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

        excluded = ["/api/v1/health", "/api/v1/ready", "/metrics"]
        Instrumentator(excluded_handlers=excluded).instrument(app).expose(
            app, endpoint="/metrics", include_in_schema=False
        )
        logger.info("observability.metrics_enabled")
    except Exception as exc:  # noqa: BLE001
        logger.warning("observability.metrics_unavailable", error=str(exc))
