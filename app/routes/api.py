"""
Smart Video Downloader — API Routes
Handles video analysis, download initiation, progress streaming, and cancellation.
"""

import asyncio
import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services import video_service
from app.services.history_service import add_record
from app.utils.validators import validate_url
from app.utils.formatters import format_speed, format_eta, format_size
from app.utils.logger import get_logger
from app.config import DEFAULT_SETTINGS

logger = get_logger("api")

router = APIRouter()


# ──────────────────────────────────────────────
# Request schemas
# ──────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    url: str


class DownloadRequest(BaseModel):
    url: str
    format_id: str | None = None
    quality_label: str = "720p HD"
    output_format: str = "mp4"        # mp4 | webm | mp3
    download_dir: str | None = None   # Override the default


# ──────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────

@router.post("/analyze")
async def analyze(body: AnalyzeRequest):
    """Analyze a video URL and return metadata + available formats."""
    # Validate URL
    check = validate_url(body.url)
    if not check["valid"]:
        raise HTTPException(status_code=400, detail=check["error"])

    try:
        # yt-dlp is synchronous — run in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        metadata = await loop.run_in_executor(None, video_service.analyze_url, body.url)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error during analysis")
        raise HTTPException(status_code=500, detail="Analysis failed. Please try again.")

    return {"success": True, "data": metadata, "warning": check.get("warning")}


@router.post("/download")
async def download(body: DownloadRequest):
    """Start a video download and return a download_id for progress tracking."""
    check = validate_url(body.url)
    if not check["valid"]:
        raise HTTPException(status_code=400, detail=check["error"])

    download_dir = body.download_dir or DEFAULT_SETTINGS["download_folder"]

    download_id = video_service.start_download(
        url=body.url,
        format_id=body.format_id,
        output_format=body.output_format,
        download_dir=download_dir,
        quality_label=body.quality_label,
    )

    return {"success": True, "download_id": download_id}


@router.get("/progress/{download_id}")
async def progress(download_id: str):
    """
    Server-Sent Events (SSE) endpoint that streams real-time download progress.
    The client connects with EventSource and receives JSON progress updates.
    """

    async def event_generator():
        while True:
            state = video_service.get_download_state(download_id)
            if state is None:
                yield f"data: {json.dumps({'error': 'Download not found'})}\n\n"
                break

            payload = {
                "status": state["status"],
                "percent": state["percent"],
                "speed": format_speed(state.get("speed")),
                "eta": format_eta(state.get("eta")),
                "filename": state.get("filename"),
                "filesize": format_size(state.get("filesize")),
                "downloaded_bytes": state.get("downloaded_bytes", 0),
                "error": state.get("error"),
                "title": state.get("title"),
                "thumbnail": state.get("thumbnail"),
            }
            yield f"data: {json.dumps(payload)}\n\n"

            # Terminal states — send one final update and close
            if state["status"] in ("complete", "error", "cancelled"):
                # If completed, save to history
                if state["status"] == "complete":
                    try:
                        await add_record(
                            title=state.get("title") or "Untitled",
                            url=state.get("url", ""),
                            thumbnail=state.get("thumbnail"),
                            file_path=state.get("filename"),
                            file_size=state.get("filesize"),
                            fmt=state.get("output_format") or state.get("format_id"),
                            quality=state.get("quality_label"),
                        )
                    except Exception:
                        logger.exception("Failed to save history record")
                break

            await asyncio.sleep(0.5)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/cancel/{download_id}")
async def cancel(download_id: str):
    """Cancel an active download."""
    success = video_service.cancel_download(download_id)
    if not success:
        raise HTTPException(status_code=404, detail="Download not found or already finished.")
    return {"success": True, "message": "Download cancelled."}
