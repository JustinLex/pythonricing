import logging
import sys
from types import FrameType
from typing import cast

from loguru import logger


class InterceptHandler(logging.Handler):
    """
    Loguru injection code from loguru's documentation

    See documentation here
    https://github.com/Delgan/loguru#entirely-compatible-with-standard-logging

    Type hints and linter bypasses taken from
    https://github.com/nsidnev/fastapi-realworld-example-app/blob/master/app/core/logging.py
    """
    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # noqa: WPS609
            frame = cast(FrameType, frame.f_back)
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


# Loguru's log injection code extended to inject into uvicorn logging as well, taken from
# https://github.com/nsidnev/fastapi-realworld-example-app/blob/master/app/core/settings/app.py
def init_logger() -> None:
    logging.getLogger().handlers = [InterceptHandler()]
    for logger_name in ("uvicorn.asgi", "uvicorn.access"):
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler(level=logging.INFO)]
    logger.configure(handlers=[{"sink": sys.stdout, "level": logging.INFO, "enqueue": True, "serialize": True}])
