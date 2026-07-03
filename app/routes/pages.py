"""
Smart Video Downloader — Page Routes
Serves the SPA shell HTML template.
"""

from fastapi import APIRouter, Request
from app import templates

router = APIRouter()


@router.get("/")
async def index(request: Request):
    """Serve the single-page application."""
    return templates.TemplateResponse(request=request, name="index.html")
