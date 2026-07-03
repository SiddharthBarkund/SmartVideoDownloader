"""
Smart Video Downloader — Configuration Module
Centralizes all application settings with sensible defaults.
"""

import os
from pathlib import Path


# ──────────────────────────────────────────────
# Environment Detection
# ──────────────────────────────────────────────
IS_CLOUD = os.getenv("IS_CLOUD", "false").lower() == "true"

# ──────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

if IS_CLOUD:
    # Cloud: use /tmp for ephemeral storage (Render free tier)
    _CLOUD_DATA = Path("/tmp/svd_data")
    _CLOUD_DATA.mkdir(parents=True, exist_ok=True)
    DB_PATH = _CLOUD_DATA / "history.db"
    LOG_DIR = _CLOUD_DATA / "logs"
    DEFAULT_DOWNLOAD_DIR = _CLOUD_DATA / "downloads"
else:
    DB_PATH = PROJECT_ROOT / "history.db"
    LOG_DIR = PROJECT_ROOT / "logs"
    DEFAULT_DOWNLOAD_DIR = Path.home() / "Downloads" / "SmartVideoDownloader"

DEFAULT_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────
# Server
# ──────────────────────────────────────────────
HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", "5050"))
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
