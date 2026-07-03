"""
Smart Video Downloader — URL Validators
Validates and sanitizes user-supplied URLs before processing.
"""

import re
from urllib.parse import urlparse


# Patterns commonly supported by yt-dlp
_SUPPORTED_DOMAINS = {
    "youtube.com", "www.youtube.com", "m.youtube.com",
    "youtu.be",
    "vimeo.com", "www.vimeo.com",
    "dailymotion.com", "www.dailymotion.com",
    "twitter.com", "www.twitter.com", "x.com", "www.x.com",
    "facebook.com", "www.facebook.com", "fb.watch",
    "instagram.com", "www.instagram.com",
    "tiktok.com", "www.tiktok.com",
    "reddit.com", "www.reddit.com",
    "twitch.tv", "www.twitch.tv",
}

_URL_REGEX = re.compile(
    r"^https?://"                           # scheme
    r"(?:[a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,}"   # domain
    r"(?:/[^\s]*)?$"                        # path
)


def validate_url(url: str) -> dict:
    """
    Validate that a URL is well-formed and from a known platform.

    Returns:
        dict with keys: valid (bool), error (str|None), domain (str|None)
    """
    if not url or not isinstance(url, str):
        return {"valid": False, "error": "URL is required.", "domain": None}

    url = url.strip()

    # Basic format check
    if not _URL_REGEX.match(url):
        return {"valid": False, "error": "Invalid URL format.", "domain": None}

    # Parse domain
    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    # Remove port if present
    if ":" in domain:
        domain = domain.split(":")[0]

    # yt-dlp supports thousands of sites; we just warn on unknown ones
    is_known = domain in _SUPPORTED_DOMAINS
    warning = None if is_known else "This domain may not be supported."

    return {
        "valid": True,
        "error": None,
        "domain": domain,
        "warning": warning,
    }
