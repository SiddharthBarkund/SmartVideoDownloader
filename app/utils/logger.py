"""
Smart Video Downloader — Centralized Logging
Provides a consistent logger for all modules.
"""

import logging
import sys
from pathlib import Path

from app.config import LOG_DIR, LOG_LEVEL, LOG_FORMAT


def setup_logging() -> None:
    """Configure root logger with console and file handlers."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger("svd")
    root_logger.setLevel(LOG_LEVEL)

    # Prevent duplicate handlers on reload
    if root_logger.handlers:
        return

    formatter = logging.Formatter(LOG_FORMAT)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8")
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the 'svd' namespace."""
    return logging.getLogger(f"svd.{name}")
