"""
GitHub API routes.

Handles repository listing, analysis, and video generation for GitHub projects.
"""

import uuid
from datetime import datetime
from typing import Literal
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from loguru import logger

from ...services.github_intel import github_intel
from ...services.prompt_engine import prompt_engine
from ...services.video_generator import video_generator
from ...models.schemas import Project, ProjectStatus, ProductInput, ProductAnalysis, GeneratedVideo
from ...db.database import get_db
from ...db.models import Video as VideoModel

# Import projects_db from projects module to store analyzed repos
from .projects import projects_db

router = APIRouter(prefix="/github", tags=["github"])


class VideoGenerateRequest(BaseModel):
    """Request for video generation."""
    prompt: str
    duration: Literal[4, 8, 12] = 8
    size: Literal["720x1280", "1280x720"] = "720x1280"
    model: str = "sora-2"


@router.get("/repos")
async def list_repositories(
    visibility: str = "all",
    sort: str = "updated"
) -> list[dict]:
    """
    List all GitHub repositories for the authenticated user.

    Args:
        visibility: public, private, or all
        sort: created, updated, pushed, full_name
    """
    try:
        repos = await github_intel.get_user_repos(visibility=visibility, sort=sort)
        return repos
    except Exception as e:
        logger.error(f"Failed to fetch repos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/repos/{owner}/{repo}")
async def get_repository_details(owner: str, repo: str) -> dict:
    """Get details of a specific repository."""
    try:
        # Get basic repo info first
        repos = await github_intel.get_user_repos(visibility="all", per_page=100)
        repo_data = next(
            (r for r in repos if r["full_name"] == f"{owner}/{repo}"),
            None
        )

        if not repo_data:
            raise HTTPException(status_code=404, detail="Repository not found")

        return repo_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch repo details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/repos/{owner}/{repo}/analyze")
async def analyze_repository(owner: str, repo: str) -> dict:
    """
    Analyze a repository to understand what it does.

    Uses AI to read the code and generate marketing insights.
    """
    logger.info(f"Starting analysis for {owner}/{repo}")

    try:
        # Get repo data
        repos = await github_intel.get_user_repos(visibility="all", per_page=100)
        repo_data = next(
            (r for r in repos if r["full_name"] == f"{owner}/{repo}"),
            None
        )

        if not repo_data:
            raise HTTPException(status_code=404, detail="Repository not found")

        # Analyze the repository
        analysis = await github_intel.analyze_repository(repo_data)

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/repos/{owner}/{repo}/create-project")
async def create_project_from_repo(owner: str, repo: str) -> Project:
    """
    Create a full project from a GitHub repository.

    This analyzes the repo, creates a project, and generates video concepts.
    """
    logger.info(f"Creating project from repo {owner}/{repo}")

    try:
        # Get repo data
        repos = await github_intel.get_user_repos(visibility="all", per_page=100)
        repo_data = next(
            (r for r in repos if r["full_name"] == f"{owner}/{repo}"),
            None
        )

        if not repo_data:
            raise HTTPException(status_code=404, detail="Repository not found")

        # Analyze the repository
        analysis = await github_intel.analyze_repository(repo_data)
        project_analysis = analysis.get("analysis", {})

        # Create a project
        project_id = str(uuid.uuid4())
        now = datetime.now()

        # Convert analysis to ProductAnalysis format
        target = project_analysis.get("target_audience", {})
        visual = project_analysis.get("visual_style", {})

        product_analysis = ProductAnalysis(
            product_name=project_analysis.get("product_name", repo_data["name"]),
            category=project_analysis.get("category", "Software"),
            price=None,
            currency="EUR",
            positioning="premium",
            brand={
                "name": repo_data["name"],
                "tone_of_voice": "tech, professional, innovative",
                "colors": {
                    "primary": "#0066FF",
                    "secondary": "#00D4FF",
                    "accent": "#FF6B00"
                }
            },
            usp=project_analysis.get("usp", []),
            target_audience={
                "age_range": "25-45",
                "gender": "unisex",
                "interests": target.get("interests", ["technology", "software"]),
                "pain_points": target.get("pain_points", [])
            },
            visual_style={
                "aesthetic": visual.get("recommended_style", "modern tech"),
                "photography_style": "digital, screen recordings, UI showcase",
                "suggested_video_style": visual.get("mood", "dynamic and professional")
            },
            cta_current="Try it now",
            competitors_inferred=[]
        )

        project = Project(
            id=project_id,
            name=f"{repo_data['name']} - Video Ad",
            status=ProjectStatus.READY_FOR_VIDEO,
            product_input=ProductInput(
                url=repo_data.get("homepage") or repo_data["url"],
                images=[],
                description=project_analysis.get("what_it_does", repo_data["description"]),
                category=project_analysis.get("category", "Software")
            ),
            product_analysis=product_analysis,
            market_analysis=None,
            concepts=[],
            videos=[],
            created_at=now,
            updated_at=now
        )

        # Store extra data for video generation
        project_extra = {
            "github_repo": repo_data,
            "full_analysis": project_analysis,
            "video_hooks": project_analysis.get("video_hook_ideas", [])
        }

        projects_db[project_id] = project

        logger.info(f"Created project {project_id} from repo {owner}/{repo}")

        return project

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Project creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/repos/{owner}/{repo}/generate-video-prompt")
async def generate_video_prompt(owner: str, repo: str) -> dict:
    """
    Generate video prompts directly from a repository.

    This is a quick way to get video prompts without creating a full project.
    """
    logger.info(f"Generating video prompt for {owner}/{repo}")

    try:
        # Get repo data
        repos = await github_intel.get_user_repos(visibility="all", per_page=100)
        repo_data = next(
            (r for r in repos if r["full_name"] == f"{owner}/{repo}"),
            None
        )

        if not repo_data:
            raise HTTPException(status_code=404, detail="Repository not found")

        # Analyze and generate video prompts
        analysis = await github_intel.analyze_repository(repo_data)
        video_prompts = await github_intel.generate_video_prompt_for_repo(analysis)

        return video_prompts

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video prompt generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/repos/{owner}/{repo}/generate-video")
async def generate_video_for_repo(
    owner: str,
    repo: str,
    duration: int = 8,
    size: str = "720x1280",
    provider: str = "veo",  # Default to Veo since Sora requires org verification
    db: Session = Depends(get_db)
) -> dict:
    """
    Generate a video ad for a GitHub repository using Sora.

    This:
    1. Analyzes the repository
    2. Generates an optimized video prompt
    3. Creates the video with Sora
    4. Returns the video details

    Args:
        owner: GitHub username
        repo: Repository name
        duration: Video duration (4, 8, or 12 seconds)
        size: Video size (720x1280 for vertical, 1280x720 for horizontal)
    """
    logger.info(f"Generating video for {owner}/{repo}")

    try:
        # Get repo data
        repos = await github_intel.get_user_repos(visibility="all", per_page=100)
        repo_data = next(
            (r for r in repos if r["full_name"] == f"{owner}/{repo}"),
            None
        )

        if not repo_data:
            raise HTTPException(status_code=404, detail="Repository not found")

        # Analyze and generate video prompt
        logger.info("Analyzing repository...")
        analysis = await github_intel.analyze_repository(repo_data)
        project_analysis = analysis.get("analysis", {})

        # Build a cinematic prompt from the analysis
        product_name = project_analysis.get("product_name", repo_data["name"])
        what_it_does = project_analysis.get("what_it_does", repo_data.get("description", ""))
        visual_style = project_analysis.get("visual_style", {})
        hooks = project_analysis.get("video_hook_ideas", [])

        # Create an optimized Sora prompt
        sora_prompt = f"""Cinematic tech product advertisement video.

Product: {product_name}
Description: {what_it_does}

Visual Style: {visual_style.get('recommended_style', 'Modern tech startup aesthetic')}
Mood: {visual_style.get('mood', 'Professional, innovative, dynamic')}
Colors: {visual_style.get('color_palette', 'Blue and white tech colors')}

Scene: Sleek modern workspace with large monitors displaying the application interface.
Smooth camera movements, professional lighting, shallow depth of field.
Show hands typing on keyboard, screens lighting up with data visualizations.
Dynamic transitions, subtle lens flares, premium tech aesthetic.

Hook: {hooks[0] if hooks else 'Innovative software that transforms how you work.'}

Style: Apple-style product video meets tech startup launch. Cinematic 4K quality."""

        logger.info(f"Generated Sora prompt: {sora_prompt[:200]}...")

        # Generate video with selected provider
        logger.info(f"Starting video generation with {provider}...")
        video = await video_generator.generate_from_prompt(
            prompt=sora_prompt,
            duration=duration,
            size=size,
            provider=provider
        )

        logger.info(f"Video generation complete: {video.status}")

        # Save to database
        db_video = VideoModel(
            id=video.id,
            repo_owner=owner,
            repo_name=repo,
            repo_full_name=f"{owner}/{repo}",
            title=f"{product_name} - Video Ad",
            description=what_it_does,
            prompt=sora_prompt,
            provider=video.provider.value if hasattr(video.provider, 'value') else str(video.provider),
            status=video.status,
            duration_seconds=video.duration_seconds,
            resolution=video.resolution,
            local_path=video.local_path,
            sora_video_id=video.sora_video_id,
            error=video.error,
            created_at=video.created_at,
            completed_at=datetime.now() if video.status == "completed" else None
        )
        db.add(db_video)
        db.commit()
        db.refresh(db_video)

        logger.info(f"Video saved to database: {video.id}")

        return db_video.to_dict()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-video-direct")
async def generate_video_direct(request: VideoGenerateRequest) -> GeneratedVideo:
    """
    Generate a video directly from a custom prompt using Sora.

    Useful for testing or custom video generation.
    """
    logger.info(f"Direct video generation with prompt: {request.prompt[:100]}...")

    try:
        video = await video_generator.generate_from_prompt(
            prompt=request.prompt,
            duration=request.duration,
            size=request.size,
            model=request.model
        )
        return video

    except Exception as e:
        logger.error(f"Direct video generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
