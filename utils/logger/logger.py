import sys
import logging
import os.path
from logging.handlers import RotatingFileHandler
from pythonjsonlogger.jsonlogger import JsonFormatter

from functools import lru_cache

def setup_logger(
    name: str, log_file: str, level: int = logging.DEBUG
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    if not logger.handlers:
        # log_dir = os.path.dirname(log_file)
        # if log_dir and not os.path.exists(log_file):
        #     os.makedirs(log_dir, exist_ok=True)
        file_formatter = JsonFormatter(
            fmt="%(name)s %(lineno)d  %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_formatter = logging.Formatter(
            fmt="%(name)s %(lineno)d  %(levelname)s %(message)s",
            datefmt="%H:%M:%S",
        )

        # file_handler = RotatingFileHandler(
        #     log_file, maxBytes=10 * 1024 * 1024, backupCount=3
        # )
        # file_handler.setLevel(level)
        # file_handler.setFormatter(file_formatter)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(console_formatter)

        logger.addHandler(console_handler)
        # logger.addHandler(file_handler)

    return logger
