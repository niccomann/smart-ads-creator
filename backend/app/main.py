"""
AdGenius AI - Video Ad Generator

FastAPI backend for the AI-powered video advertising platform.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger
import sys

from .config import settings
from .api.routes import projects, analysis, video, github, videos_db
from .db.database import init_db

from shared_fastapi_bootstrap import create_app, run


# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.log_level
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting AdGenius AI Backend...")
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.videos_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized")
    logger.info(f"Data directory: {settings.data_dir}")
    logger.info(f"Videos directory: {settings.videos_dir}")
    yield
    logger.info("Shutting down AdGenius AI Backend...")


app = create_app(
    title="AdGenius AI",
    description="AI-powered video advertising platform",
    lifespan=lifespan,
    static_dirs={"/videos": str(settings.videos_dir)},
)

app.include_router(projects.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(video.router, prefix="/api")
app.include_router(github.router, prefix="/api")
app.include_router(videos_db.router, prefix="/api")


if __name__ == "__main__":
    run("app.main:app", port=settings.port)
