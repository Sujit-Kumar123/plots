import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

import structlog

# backend/app/common/logging.py → parents[2] = backend/
_LOG_DIR = Path(__file__).parents[2] / "logs"


def setup_logging(debug: bool = False) -> None:
    _LOG_DIR.mkdir(parents=True, exist_ok=True)

    log_level = logging.DEBUG if debug else logging.INFO
    fmt = "%(message)s"

    handlers: list[logging.Handler] = [
        # Stdout — always present (Docker captures this)
        logging.StreamHandler(sys.stdout),
        # app.log — all INFO+ messages, rotates at 10 MB, keeps 5 files
        RotatingFileHandler(
            _LOG_DIR / "app.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        ),
        # error.log — WARNING+ only, rotates at 5 MB, keeps 3 files
        _make_error_handler(_LOG_DIR / "error.log"),
    ]

    logging.basicConfig(format=fmt, level=log_level, handlers=handlers)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def _make_error_handler(path: Path) -> RotatingFileHandler:
    handler = RotatingFileHandler(
        path,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    handler.setLevel(logging.WARNING)
    return handler
