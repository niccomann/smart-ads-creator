"""
AdGenius AI - Video Ad Generator

FastAPI backend for the AI-powered video advertising platform.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger
import sys

from .config import settings
from .api.routes import projects, analysis, video, github, videos_db
from .db.database import init_db


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
    # Startup
    logger.info("Starting AdGenius AI Backend...")

    # Ensure data directories exist
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.videos_dir.mkdir(parents=True, exist_ok=True)

    # Initialize database
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized")

    logger.info(f"Data directory: {settings.data_dir}")
    logger.info(f"Videos directory: {settings.videos_dir}")

    yield

    # Shutdown
    logger.info("Shutting down AdGenius AI Backend...")


# Create FastAPI app
app = FastAPI(
    title="AdGenius AI",
    description="AI-powered video advertising platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(video.router, prefix="/api")
app.include_router(github.router, prefix="/api")
app.include_router(videos_db.router, prefix="/api")

# Serve static files (videos)
app.mount("/videos", StaticFiles(directory=str(settings.videos_dir)), name="videos")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "AdGenius AI",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.env == "dev"
    )
