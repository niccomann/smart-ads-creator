"""
Video API routes.

Handles video generation and retrieval.
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from loguru import logger

from ...models.schemas import (
    ProjectStatus,
    GeneratedVideo,
    VideoProvider
)
from ...services.video_generator import video_generator
from .projects import projects_db

router = APIRouter(prefix="/video", tags=["video"])


@router.post("/{project_id}/generate/{concept_index}", response_model=GeneratedVideo)
async def generate_video(
    project_id: str,
    concept_index: int = 0,
    provider: VideoProvider = VideoProvider.SORA,
    background_tasks: BackgroundTasks = None
) -> GeneratedVideo:
    """
    Generate a video for a project concept.

    Args:
        project_id: Project ID
        concept_index: Index of the concept to use (0-based)
        provider: Video generation provider (sora, runway, kling)
    """
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_db[project_id]

    if not project.concepts:
        raise HTTPException(
            status_code=400,
            detail="No concepts available. Run analysis first."
        )

    if concept_index >= len(project.concepts):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid concept index. Available: 0-{len(project.concepts)-1}"
        )

    concept = project.concepts[concept_index]
    logger.info(f"Generating video for project {project_id}, concept: {concept.title}")

    project.status = ProjectStatus.GENERATING
    project.updated_at = datetime.now()

    try:
        video = await video_generator.generate(
            project_id=project_id,
            concept=concept,
            provider=provider
        )

        project.videos.append(video)

        if video.status == "completed":
            project.status = ProjectStatus.COMPLETED
        elif video.status == "failed":
            project.status = ProjectStatus.READY_FOR_VIDEO  # Allow retry

        project.updated_at = datetime.now()

        return video

    except Exception as e:
        logger.error(f"Video generation failed: {e}")
        project.status = ProjectStatus.READY_FOR_VIDEO
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}/videos", response_model=list[GeneratedVideo])
async def list_videos(project_id: str) -> list[GeneratedVideo]:
    """List all videos for a project."""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    return projects_db[project_id].videos


@router.get("/{project_id}/videos/{video_id}/download")
async def download_video(project_id: str, video_id: str):
    """Download a generated video file."""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_db[project_id]

    # Find the video
    video = next((v for v in project.videos if v.id == video_id), None)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    if video.status != "completed":
        raise HTTPException(status_code=400, detail="Video not ready for download")

    # Get local file path
    local_path = video_generator.get_local_video_path(video_id)
    if not local_path:
        raise HTTPException(status_code=404, detail="Video file not found")

    return FileResponse(
        path=local_path,
        media_type="video/mp4",
        filename=f"{video.concept_title.replace(' ', '_')}.mp4"
    )
