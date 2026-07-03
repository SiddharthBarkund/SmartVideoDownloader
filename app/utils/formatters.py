"""
Smart Video Downloader — Formatters
Human-readable formatting for file sizes, durations, and dates.
"""

from datetime import datetime


def format_size(bytes_count: int | float | None) -> str:
    """Convert bytes to a human-readable string (e.g. '14.3 MB')."""
    if bytes_count is None:
        return "Unknown"
    if bytes_count == 0:
        return "0 B"

    bytes_count = float(bytes_count)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(bytes_count) < 1024:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024
    return f"{bytes_count:.1f} PB"


def format_duration(seconds: int | float | None) -> str:
    """Convert seconds to HH:MM:SS or MM:SS format."""
    if seconds is None or seconds < 0:
        return "Unknown"
    if seconds == 0:
        return "0:00"

    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def format_date(date_str: str | None) -> str:
    """Convert YYYYMMDD to a readable date string."""
    if not date_str:
        return "Unknown"

    try:
        dt = datetime.strptime(str(date_str)[:8], "%Y%m%d")
        return dt.strftime("%B %d, %Y")
    except (ValueError, TypeError):
        return str(date_str)


def format_views(count: int | float | None) -> str:
    """Format view count with suffixes (e.g. '1.2M views')."""
    if count is None:
        return "Unknown"

    count = int(count)
    if count >= 1_000_000_000:
        return f"{count / 1_000_000_000:.1f}B views"
    if count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M views"
    if count >= 1_000:
        return f"{count / 1_000:.1f}K views"
    return f"{count:,} views"


def format_speed(bytes_per_sec: float | None) -> str:
    """Format download speed (e.g. '2.4 MB/s')."""
    if bytes_per_sec is None or bytes_per_sec <= 0:
        return "—"
    return f"{format_size(bytes_per_sec)}/s"


def format_eta(seconds: float | None) -> str:
    """Format ETA in a friendly way."""
    if seconds is None or seconds <= 0:
        return "—"

    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        m, s = divmod(seconds, 60)
        return f"{m}m {s}s"

    h, remainder = divmod(seconds, 3600)
    m, _ = divmod(remainder, 60)
    return f"{h}h {m}m"
