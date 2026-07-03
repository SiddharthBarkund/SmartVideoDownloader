"""
Smart Video Downloader — Settings Routes
Manages user preferences (persisted in a JSON file).
"""

import json
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

from app.config import PROJECT_ROOT, DEFAULT_SETTINGS
from app.utils.logger import get_logger

logger = get_logger("settings")

router = APIRouter()

_SETTINGS_FILE = PROJECT_ROOT / "settings.json"


class SettingsUpdate(BaseModel):
    download_folder: str | None = None
    theme: str | None = None
    auto_open_folder: bool | None = None
    language: str | None = None


def _load_settings() -> dict:
    """Load settings from disk, falling back to defaults."""
    if _SETTINGS_FILE.exists():
        try:
            with open(_SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            if not isinstance(saved, dict):
                raise ValueError("Settings file must contain a JSON object.")
            # Merge with defaults so new keys are always present
            merged = {**DEFAULT_SETTINGS, **saved}
            return merged
        except (json.JSONDecodeError, OSError, ValueError):
            logger.warning("Corrupted settings file, using defaults")
    return dict(DEFAULT_SETTINGS)


def _save_settings(settings: dict) -> None:
    """Persist settings to disk."""
    with open(_SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
    logger.info("Settings saved")


@router.get("")
async def get_settings():
    """Return current application settings."""
    return {"success": True, "data": _load_settings()}


@router.put("")
async def update_settings(body: SettingsUpdate):
    """Update one or more settings fields."""
    current = _load_settings()

    # Only update fields that were explicitly provided
    updates = body.model_dump(exclude_none=True)
    current.update(updates)

    # Validate download folder
    if "download_folder" in updates:
        try:
            folder = Path(updates["download_folder"])
            folder.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass  # On cloud, custom folders may not be writable

    _save_settings(current)
    return {"success": True, "data": current}
