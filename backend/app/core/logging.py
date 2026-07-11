"""Structured logging configuration.

Configures ``structlog`` to emit JSON in production and human-readable console
output in development. Call :func:`configure_logging` once at application start.
"""

import logging
import sys

import structlog

from app.config.config import get_settings


def configure_logging() -> None:
    """Configure standard library and structlog processors for the process."""

    settings = get_settings()
    level = logging.DEBUG if settings.debug else logging.INFO

    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=level)

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    renderer: structlog.types.Processor = (
        structlog.dev.ConsoleRenderer()
        if settings.environment == "development"
        else structlog.processors.JSONRenderer()
    )

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a bound structlog logger."""

    return structlog.get_logger(name)
