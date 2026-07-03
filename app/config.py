"""
Smart Video Downloader — Configuration Module
Centralizes all application settings with sensible defaults.
"""

import os
from pathlib import Path


# ──────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
DB_PATH = PROJECT_ROOT / "history.db"
LOG_DIR = PROJECT_ROOT / "logs"

# Default download location (user-configurable via Settings)
DEFAULT_DOWNLOAD_DIR = Path.home() / "Downloads" / "SmartVideoDownloader"
DEFAULT_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────
# Server
# ──────────────────────────────────────────────
HOST = "0.0.0.0"
PORT = 5050
DEBUG = os.getenv("SVD_DEBUG", "true").lower() == "true"

# ──────────────────────────────────────────────
# Application Defaults
# ──────────────────────────────────────────────
DEFAULT_SETTINGS = {
    "download_folder": str(DEFAULT_DOWNLOAD_DIR),
    "theme": "dark",
    "auto_open_folder": False,
    "language": "en",
}

# ──────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────
LOG_LEVEL = os.getenv("SVD_LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
