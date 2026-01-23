"""
Projects API routes.

Handles CRUD operations for ad projects.
"""

import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from loguru import logger

from ...models.schemas import (
    Project,
    ProjectCreate,
    ProjectStatus,
    ProductInput
)

router = APIRouter(prefix="/projects", tags=["projects"])

# In-memory storage (replace with database in production)
projects_db: dict[str, Project] = {}


@router.post("/", response_model=Project)
async def create_project(project_in: ProjectCreate) -> Project:
    """Create a new ad project."""
    project_id = str(uuid.uuid4())
    now = datetime.now()

    project = Project(
        id=project_id,
        name=project_in.name,
        status=ProjectStatus.DRAFT,
        product_input=project_in.product_input,
        created_at=now,
        updated_at=now
    )

    projects_db[project_id] = project
    logger.info(f"Created project: {project_id} - {project_in.name}")

    return project


@router.get("/", response_model=list[Project])
async def list_projects() -> list[Project]:
    """List all projects."""
    return list(projects_db.values())


@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: str) -> Project:
    """Get a project by ID."""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    return projects_db[project_id]


@router.delete("/{project_id}")
async def delete_project(project_id: str) -> dict:
    """Delete a project."""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    del projects_db[project_id]
    logger.info(f"Deleted project: {project_id}")

    return {"status": "deleted", "id": project_id}


@router.patch("/{project_id}/status")
async def update_project_status(project_id: str, status: ProjectStatus) -> Project:
    """Update project status."""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_db[project_id]
    project.status = status
    project.updated_at = datetime.now()

    return project
