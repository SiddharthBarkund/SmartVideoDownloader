"""
Smart Video Downloader — History Routes
CRUD endpoints for download history.
"""

import os
import subprocess
import sys

from fastapi import APIRouter, HTTPException, Query

from app.services.history_service import get_all, delete_record, clear_all
from app.utils.logger import get_logger

logger = get_logger("history")

router = APIRouter()


@router.get("")
async def list_history(search: str = Query(default=None, description="Search by title")):
    """Get all download history records, optionally filtered."""
    records = await get_all(search=search)
    return {"success": True, "data": records}


@router.delete("/{record_id}")
async def delete_one(record_id: int):
    """Delete a single history record."""
    deleted = await delete_record(record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Record not found.")
    return {"success": True, "message": "Record deleted."}


@router.delete("")
async def clear_history():
    """Delete all history records."""
    count = await clear_all()
    return {"success": True, "message": f"{count} records cleared."}


@router.post("/{record_id}/open")
async def open_file_location(record_id: int):
    """Open the folder containing the downloaded file in the OS file explorer."""
    records = await get_all()
    record = next((r for r in records if r["id"] == record_id), None)

    if not record:
        raise HTTPException(status_code=404, detail="Record not found.")

    file_path = record.get("file_path")
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk.")

    folder = os.path.dirname(file_path)

    try:
        if sys.platform == "win32":
            subprocess.Popen(["explorer", f"/select,{file_path}"])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-R", file_path])
        else:
            subprocess.Popen(["xdg-open", folder])
    except Exception as exc:
        logger.error("Failed to open file location: %s", exc)
        raise HTTPException(status_code=500, detail="Could not open file location.")

    return {"success": True, "message": "Opened file location."}
