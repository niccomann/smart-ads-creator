"""
Videos API routes with database persistence.

Lists, retrieves, and serves generated videos.
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from loguru import logger
from pathlib import Path

from ...db.database import get_db
from ...db.models import Video
from ...config import settings

router = APIRouter(prefix="/videos", tags=["videos"])


@router.get("")
async def list_videos(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    repo: Optional[str] = None
):
    """
    List all generated videos.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        status: Filter by status (queued, processing, completed, failed)
        repo: Filter by repository full name (e.g., "niccomann/valore-casa")
    """
    query = db.query(Video).order_by(Video.created_at.desc())

    if status:
        query = query.filter(Video.status == status)
    if repo:
        query = query.filter(Video.repo_full_name == repo)

    total = query.count()
    videos = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "videos": [v.to_dict() for v in videos]
    }


@router.get("/stats")
async def get_video_stats(db: Session = Depends(get_db)):
    """Get video generation statistics."""
    total = db.query(Video).count()
    completed = db.query(Video).filter(Video.status == "completed").count()
    failed = db.query(Video).filter(Video.status == "failed").count()
    processing = db.query(Video).filter(Video.status == "processing").count()
    queued = db.query(Video).filter(Video.status == "queued").count()

    return {
        "total": total,
        "completed": completed,
        "failed": failed,
        "processing": processing,
        "queued": queued
    }


@router.get("/{video_id}")
async def get_video(video_id: str, db: Session = Depends(get_db)):
    """Get a specific video by ID."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video.to_dict()


@router.get("/{video_id}/stream")
async def stream_video(video_id: str, db: Session = Depends(get_db)):
    """Stream/download a video file."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    if video.status != "completed":
        raise HTTPException(status_code=400, detail=f"Video not ready (status: {video.status})")

    if not video.local_path:
        raise HTTPException(status_code=404, detail="Video file not found")

    file_path = Path(video.local_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Video file missing from disk")

    return FileResponse(
        path=str(file_path),
        media_type="video/mp4",
        filename=f"{video.title or video_id}.mp4"
    )


@router.delete("/{video_id}")
async def delete_video(video_id: str, db: Session = Depends(get_db)):
    """Delete a video and its file."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Delete file if exists
    if video.local_path:
        file_path = Path(video.local_path)
        if file_path.exists():
            try:
                file_path.unlink()
                logger.info(f"Deleted video file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete file: {e}")

    # Delete from database
    db.delete(video)
    db.commit()

    return {"message": "Video deleted", "id": video_id}


@router.get("/repo/{owner}/{repo}")
async def list_videos_for_repo(
    owner: str,
    repo: str,
    db: Session = Depends(get_db)
):
    """List all videos for a specific repository."""
    full_name = f"{owner}/{repo}"
    videos = db.query(Video).filter(
        Video.repo_full_name == full_name
    ).order_by(Video.created_at.desc()).all()

    return {
        "repo": full_name,
        "count": len(videos),
        "videos": [v.to_dict() for v in videos]
    }
