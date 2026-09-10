# src/core/logging_config.py
import logging
import sys
import time

import structlog


def setup_logging(log_level: str = "INFO", log_format: str = "text") -> None:
    """
    Configure structlog and standard logging.
    - Application logs (via structlog) bypass standard logging and print directly to stdout/stderr.
    - Third-party logs (via standard logging) are captured and formatted cleanly.
    - Both paths emit UTC timestamps so log lines from different hosts/timezones stay comparable.
    """
    level = getattr(logging, log_level.upper(), logging.INFO)
    log_format = log_format.lower()

    # 1. Configure standard library logging for third-party libs
    logging.Formatter.converter = time.gmtime  

    handler = logging.StreamHandler(sys.stdout)
    if log_format == "json":
        from pythonjsonlogger import jsonlogger
        formatter = jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%SZ",
            rename_fields={
                "asctime": "timestamp",
                "levelname": "level",
                "name": "logger",
            },
        )
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%SZ",
        )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Silence noisy third-party loggers
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    # 2. Configure structlog natively to bypass standard logging for application logs
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(sys.stdout),
        wrapper_class=structlog.make_filtering_bound_logger(level),
        cache_logger_on_first_use=True,
    )
