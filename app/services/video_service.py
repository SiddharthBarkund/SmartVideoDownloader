"""
Smart Video Downloader — Video Service
Wraps yt-dlp to analyze URLs, extract metadata, and manage downloads.
"""

import threading
import uuid
import os
import shutil
from pathlib import Path
from typing import Any

import yt_dlp

from app.utils.logger import get_logger
from app.utils.formatters import format_size, format_duration, format_date, format_views

logger = get_logger("video_service")


def _base_ydl_opts(use_cookies: bool = False) -> dict:
    """Return base yt-dlp options shared across all operations.

    Includes headers to avoid HTTP 403 errors from YouTube's bot-detection.
    Cookie extraction is opt-in because Chrome locks its DB while running.
    """
    opts: dict = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        # Use browser-like HTTP headers to avoid 403 Forbidden
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        },
    }
    if use_cookies:
        opts["cookiesfrombrowser"] = ("chrome",)
    return opts


def _has_ffmpeg() -> bool:
    """Return True if ffmpeg is available on the system PATH."""
    return shutil.which("ffmpeg") is not None

# ──────────────────────────────────────────────
# In-memory download state (keyed by download_id)
# ──────────────────────────────────────────────
_active_downloads: dict[str, dict] = {}


# ──────────────────────────────────────────────
# Quality label mapping
# ──────────────────────────────────────────────
QUALITY_LABELS = {
    144: "144p",
    240: "240p",
    360: "360p",
    480: "480p",
    720: "720p HD",
    1080: "1080p Full HD",
    1440: "1440p",
    2160: "2160p (4K)",
}


def _map_formats(formats: list[dict]) -> list[dict]:
    """
    Parse yt-dlp's raw format list into a clean, deduplicated list
    grouped by quality label.
    """
    seen = set()
    result = []

    # Audio-only option (yt-dlp formats are usually worst-to-best, so we reverse to get the best audio)
    for fmt in reversed(formats):
        if fmt.get("vcodec") == "none" and fmt.get("acodec") != "none":
            key = "audio"
            if key not in seen:
                seen.add(key)
                result.append({
                    "format_id": fmt.get("format_id"),
                    "label": "Audio Only",
                    "ext": fmt.get("ext", "m4a"),
                    "filesize": fmt.get("filesize") or fmt.get("filesize_approx"),
                    "type": "audio",
                    "height": 0,
                })
            break  # Only need one audio entry

    # Video formats
    for fmt in formats:
        height = fmt.get("height")
        ext = fmt.get("ext", "")

        if not height or fmt.get("vcodec") == "none":
            continue
        if ext not in ("mp4", "webm"):
            continue

        # Snap to nearest known quality
        snapped = min(QUALITY_LABELS.keys(), key=lambda q: abs(q - height))
        if abs(snapped - height) > 50:
            continue  # Skip oddball resolutions

        key = f"{snapped}_{ext}"
        if key in seen:
            continue
        seen.add(key)

        result.append({
            "format_id": fmt.get("format_id"),
            "label": QUALITY_LABELS[snapped],
            "ext": ext,
            "filesize": fmt.get("filesize") or fmt.get("filesize_approx"),
            "type": "video",
            "height": snapped,
        })

    # Sort: audio first, then ascending quality
    result.sort(key=lambda f: (0 if f["type"] == "audio" else 1, f["height"]))
    return result


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

def analyze_url(url: str) -> dict[str, Any]:
    """
    Extract video metadata without downloading.
    Returns a dict with title, thumbnail, duration, formats, etc.

    Tries with browser cookies first (for age-restricted / auth content),
    and falls back to no cookies if the browser DB is locked.
    """
    logger.info("Analyzing URL: %s", url)

    def _extract(use_cookies: bool) -> dict:
        ydl_opts = _base_ydl_opts(use_cookies=use_cookies)
        ydl_opts["skip_download"] = True
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)

    # Try with cookies first, fall back to without
    try:
        info = _extract(use_cookies=True)
    except yt_dlp.utils.DownloadError as exc:
        if "cookie" in str(exc).lower():
            logger.warning("Cookie extraction failed, retrying without cookies: %s", exc)
            try:
                info = _extract(use_cookies=False)
            except yt_dlp.utils.DownloadError as exc2:
                logger.error("yt-dlp error (no cookies): %s", exc2)
                raise ValueError(f"Could not analyze URL: {exc2}") from exc2
        else:
            logger.error("yt-dlp error: %s", exc)
            raise ValueError(f"Could not analyze URL: {exc}") from exc

    raw_formats = info.get("formats") or []
    mapped = _map_formats(raw_formats)

    # Compute approximate total filesize from best format
    best_filesize = None
    for fmt in reversed(raw_formats):
        fs = fmt.get("filesize") or fmt.get("filesize_approx")
        if fs:
            best_filesize = fs
            break

    metadata = {
        "title": info.get("title", "Untitled"),
        "thumbnail": info.get("thumbnail"),
        "channel": info.get("uploader") or info.get("channel") or "Unknown",
        "duration": info.get("duration"),
        "duration_formatted": format_duration(info.get("duration")),
        "views": info.get("view_count"),
        "views_formatted": format_views(info.get("view_count")),
        "upload_date": info.get("upload_date"),
        "upload_date_formatted": format_date(info.get("upload_date")),
        "filesize_approx": best_filesize,
        "filesize_formatted": format_size(best_filesize),
        "webpage_url": info.get("webpage_url", url),
        "formats": mapped,
    }

    logger.info("Analysis complete: %s (%d formats)", metadata["title"], len(mapped))
    return metadata


def start_download(
    url: str,
    format_id: str,
    output_format: str,
    download_dir: str,
    quality_label: str,
) -> str:
    """
    Begin downloading a video in a background thread.
    Returns a download_id for progress tracking.
    """
    download_id = str(uuid.uuid4())[:8]

    state = {
        "id": download_id,
        "url": url,
        "status": "starting",      # starting | downloading | complete | error | cancelled
        "percent": 0.0,
        "speed": None,
        "eta": None,
        "filename": None,
        "filesize": None,
        "downloaded_bytes": 0,
        "error": None,
        "title": None,
        "thumbnail": None,
        "format_id": format_id,
        "quality_label": quality_label,
        "output_format": output_format,
        "cancel_event": threading.Event(),
    }
    _active_downloads[download_id] = state

    thread = threading.Thread(
        target=_download_worker,
        args=(download_id, url, format_id, output_format, download_dir, quality_label),
        daemon=True,
    )
    thread.start()

    logger.info("Download %s started for %s", download_id, url)
    return download_id


def get_download_state(download_id: str) -> dict | None:
    """Return the current state of a download (without the threading event)."""
    state = _active_downloads.get(download_id)
    if state is None:
        return None
    # Return a copy without the cancel_event (not serializable)
    return {k: v for k, v in state.items() if k != "cancel_event"}


def cancel_download(download_id: str) -> bool:
    """Signal a download to cancel."""
    state = _active_downloads.get(download_id)
    if state and state["status"] == "downloading":
        state["cancel_event"].set()
        state["status"] = "cancelled"
        logger.info("Download %s cancelled", download_id)
        return True
    return False


# ──────────────────────────────────────────────
# Worker thread
# ──────────────────────────────────────────────

def _download_worker(
    download_id: str,
    url: str,
    format_id: str,
    output_format: str,
    download_dir: str,
    quality_label: str,
) -> None:
    """Background worker that performs the actual download via yt-dlp."""
    state = _active_downloads[download_id]

    # Build output template
    output_dir = Path(download_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    outtmpl = str(output_dir / "%(title)s.%(ext)s")

    def progress_hook(d: dict) -> None:
        """Called by yt-dlp with download progress updates."""
        # Check for cancellation
        if state["cancel_event"].is_set():
            raise yt_dlp.utils.DownloadError("Download cancelled by user")

        if d.get("status") == "downloading":
            state["status"] = "downloading"
            state["filename"] = d.get("filename")
            state["filesize"] = d.get("total_bytes") or d.get("total_bytes_estimate")
            state["downloaded_bytes"] = d.get("downloaded_bytes", 0)
            state["speed"] = d.get("speed")
            state["eta"] = d.get("eta")

            total = state["filesize"]
            if total and total > 0:
                state["percent"] = round(
                    (state["downloaded_bytes"] / total) * 100, 1
                )
            else:
                # Fallback: parse yt-dlp's _percent_str
                pct_str = d.get("_percent_str", "0%").strip().replace("%", "")
                try:
                    state["percent"] = float(pct_str)
                except ValueError:
                    pass

        elif d.get("status") == "finished":
            state["filename"] = d.get("filename")

    # Configure yt-dlp options
    ffmpeg_available = _has_ffmpeg()
    logger.info("ffmpeg available: %s", ffmpeg_available)

    ydl_opts = _base_ydl_opts()
    ydl_opts["outtmpl"] = outtmpl
    ydl_opts["progress_hooks"] = [progress_hook]

    # Format selection
    if output_format == "mp3":
        if ffmpeg_available:
            # Audio extraction — requires ffmpeg
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
        else:
            # Fallback: download best audio as-is
            ydl_opts["format"] = "bestaudio/best"
            logger.warning(
                "ffmpeg not found for MP3 conversion — downloading best raw audio format instead for %s",
                download_id,
            )
    elif format_id:
        if quality_label == "Audio Only":
            ydl_opts["format"] = format_id
        elif ffmpeg_available:
            # Merge selected video with best audio
            ydl_opts["format"] = f"{format_id}+bestaudio/{format_id}/best"
        else:
            # No ffmpeg — try the selected format alone, then fall back to
            # best pre-muxed stream (single file with video+audio already combined)
            limit = "1080"
            if quality_label and "p" in quality_label:
                limit = quality_label.split("p")[0]
            ydl_opts["format"] = f"{format_id}/best[height<={limit}]/best"
            logger.info(
                "ffmpeg not found — using pre-muxed format fallback for %s",
                download_id,
            )
    else:
        ydl_opts["format"] = "best"

    if ffmpeg_available and output_format in ("mp4", "webm") and output_format != "mp3":
        ydl_opts["merge_output_format"] = output_format

    try:
        state["status"] = "downloading"
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            state["title"] = info.get("title", "Untitled")
            state["thumbnail"] = info.get("thumbnail")

        if state["status"] != "cancelled":
            state["status"] = "complete"
            state["percent"] = 100.0
            logger.info("Download %s complete: %s", download_id, state.get("filename"))

    except Exception as exc:
        if state["status"] != "cancelled":
            state["status"] = "error"
            state["error"] = str(exc)
            logger.error("Download %s failed: %s", download_id, exc)
