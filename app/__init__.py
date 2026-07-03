"""
Smart Video Downloader — Application Factory
Creates and configures the FastAPI application instance.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import STATIC_DIR, TEMPLATES_DIR
from app.utils.logger import setup_logging


def create_app(lifespan=None) -> FastAPI:
    """Build and return a fully configured FastAPI application."""

    # Initialize logging first
    setup_logging()

    kwargs = {
        "title": "Smart Video Downloader",
        "description": "A modern video downloader with premium UI",
        "version": "1.0.0",
    }
    if lifespan:
        kwargs["lifespan"] = lifespan

    application = FastAPI(**kwargs)

    # ── Mount static files ───────────────────────
    application.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    # ── Register route modules ───────────────────
    from app.routes.api import router as api_router
    from app.routes.history import router as history_router
    from app.routes.settings import router as settings_router
    from app.routes.pages import router as pages_router

    application.include_router(api_router, prefix="/api", tags=["Video"])
    application.include_router(history_router, prefix="/api/history", tags=["History"])
    application.include_router(settings_router, prefix="/api/settings", tags=["Settings"])
    application.include_router(pages_router, tags=["Pages"])

    return application


# Jinja2 template renderer (shared across page routes)
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
