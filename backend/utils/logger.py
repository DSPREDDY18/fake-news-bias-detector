"""Structured logging setup using structlog."""
from __future__ import annotations

import logging
import sys
from typing import Any

import structlog
from flask import Flask, g, request


def setup_logging(app: Flask) -> None:
    """Configure structured logging for the Flask application.

    Sets up structlog with both console and file handlers, and installs
    before/after-request hooks for request/response logging.

    Args:
        app: The Flask application instance.
    """

    # ------------------------------------------------------------------ #
    # Standard-library logging configuration
    # ------------------------------------------------------------------ #
    log_level = logging.DEBUG if app.debug else logging.INFO

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(name)s: %(message)s'
    ))

    # File handler
    file_handler = logging.FileHandler('app.log', encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(name)s: %(message)s'
    ))

    # Apply to the root logger so all libraries route through here
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    # Avoid duplicate handlers on repeated calls (e.g. tests)
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)

    # Also configure the Flask app logger
    app.logger.setLevel(log_level)
    if not app.logger.handlers:
        app.logger.addHandler(console_handler)
        app.logger.addHandler(file_handler)

    # ------------------------------------------------------------------ #
    # structlog configuration
    # ------------------------------------------------------------------ #
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt='iso'),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logger = structlog.get_logger('request')

    # ------------------------------------------------------------------ #
    # Request / response logging hooks
    # ------------------------------------------------------------------ #
    @app.before_request
    def log_request_start() -> None:
        """Log incoming request details."""
        import time
        g.request_start_time = time.time()
        logger.info(
            'request_started',
            method=request.method,
            path=request.path,
            remote_addr=request.remote_addr,
            content_length=request.content_length,
        )

    @app.after_request
    def log_request_end(response: Any) -> Any:
        """Log outgoing response details."""
        import time
        duration_ms = round(
            (time.time() - getattr(g, 'request_start_time', time.time())) * 1000, 2
        )
        logger.info(
            'request_completed',
            method=request.method,
            path=request.path,
            status=response.status_code,
            duration_ms=duration_ms,
        )
        return response
