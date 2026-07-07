"""
Smart Video Downloader — Entry Point
Run with:  python -m app.app
"""

import uvicorn
import 
from contextlib import asynccontextmanager

from app.config import HOST, PORT, DEBUG
from app.services.history_service import init_db


@asynccontextmanager
async def lifespan(application):
    """Initialize resources on startup, clean up on shutdown."""
    await init_db()
    yield


def create_configured_app():
    """Import and configure the app with lifespan."""
    from app import create_app
    return create_app(lifespan=lifespan)


app = create_configured_app()



if __name__ == "__main__":
    uvicorn.run(
        "app.app:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
    )
