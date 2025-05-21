"""Logging module"""

import sys
import logging
import logging.handlers


LOG_LEVEL = logging.INFO
LOG_FORMAT = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def setup_logging() -> None:
    """Configure basic logging with console output."""
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(LOG_FORMAT)
    console_handler.setLevel(LOG_LEVEL)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Add handler
    root_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(name)
