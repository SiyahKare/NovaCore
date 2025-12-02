"""
NovaCore Structured Logging
"""
import logging
import sys
from typing import Any

import structlog

from app.core.config import settings


def setup_logging() -> None:
    """Configure structured logging for NovaCore."""
    # Set log level
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Configure structlog
    # Note: We use PrintLoggerFactory which doesn't have .name attribute
    # So we manually add logger name in get_logger() instead of using add_logger_name processor
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.UnicodeDecoder(),
            # JSON for prod, pretty console for dev
            structlog.dev.ConsoleRenderer()
            if settings.is_dev
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure stdlib logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # Reduce noise from libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.is_dev else logging.WARNING
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    logger_name = name or "novacore"
    # Manually bind logger name since PrintLogger doesn't have .name attribute
    return structlog.get_logger(logger_name).bind(logger=logger_name)


def log_event(
    logger: structlog.stdlib.BoundLogger,
    event: str,
    level: str = "info",
    **kwargs: Any,
) -> None:
    """Log a structured event."""
    log_method = getattr(logger, level, logger.info)
    log_method(event, **kwargs)


# Request context helpers
def bind_request_context(
    request_id: str,
    user_id: int | None = None,
    path: str | None = None,
) -> None:
    """Bind request context to all subsequent logs."""
    ctx: dict[str, Any] = {"request_id": request_id}
    if user_id:
        ctx["user_id"] = user_id
    if path:
        ctx["path"] = path
    structlog.contextvars.bind_contextvars(**ctx)


def clear_request_context() -> None:
    """Clear request context after request completes."""
    structlog.contextvars.clear_contextvars()

