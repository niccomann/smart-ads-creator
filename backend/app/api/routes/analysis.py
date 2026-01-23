"""
Analysis API routes.

Handles product and market analysis endpoints.
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from loguru import logger

from ...models.schemas import (
    Project,
    ProjectStatus,
    ProductAnalysis,
    MarketAnalysis,
    VideoConcept
)
from ...services.product_intel import product_intel
from ...services.market_intel import market_intel
from ...services.prompt_engine import prompt_engine
from .projects import projects_db

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/{project_id}/product", response_model=ProductAnalysis)
async def analyze_product(project_id: str) -> ProductAnalysis:
    """
    Analyze the product for a project.

    This extracts USP, target audience, visual style, etc.
    """
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_db[project_id]
    project.status = ProjectStatus.ANALYZING
    project.updated_at = datetime.now()

    logger.info(f"Starting product analysis for project {project_id}")

    try:
        analysis = await product_intel.analyze(project.product_input)

        project.product_analysis = analysis
        project.updated_at = datetime.now()

        logger.info(f"Product analysis completed for {project_id}")
        return analysis

    except Exception as e:
        logger.error(f"Product analysis failed: {e}")
        project.status = ProjectStatus.FAILED
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/market", response_model=MarketAnalysis)
async def analyze_market(
    project_id: str,
    competitor_names: list[str] = None,
    country: str = "IT"
) -> MarketAnalysis:
    """
    Analyze competitors and market for a project.

    Uses inferred competitors from product analysis if none provided.
    """
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_db[project_id]

    # Get competitors from product analysis if not provided
    if not competitor_names:
        if project.product_analysis:
            competitor_names = project.product_analysis.competitors_inferred
        else:
            raise HTTPException(
                status_code=400,
                detail="No competitors provided and no product analysis available"
            )

    if not competitor_names:
        raise HTTPException(status_code=400, detail="No competitors to analyze")

    logger.info(f"Starting market analysis for project {project_id}")

    try:
        category = project.product_analysis.category if project.product_analysis else "general"

        analysis = await market_intel.analyze_competitors(
            competitor_names=competitor_names,
            category=category,
            country=country
        )

        project.market_analysis = analysis
        project.updated_at = datetime.now()

        logger.info(f"Market analysis completed for {project_id}")
        return analysis

    except Exception as e:
        logger.error(f"Market analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/concepts", response_model=list[VideoConcept])
async def generate_concepts(
    project_id: str,
    num_concepts: int = 3
) -> list[VideoConcept]:
    """
    Generate video concepts for a project.

    Requires product analysis to be completed first.
    """
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_db[project_id]

    if not project.product_analysis:
        raise HTTPException(
            status_code=400,
            detail="Product analysis required before generating concepts"
        )

    logger.info(f"Generating {num_concepts} concepts for project {project_id}")

    try:
        # Use empty market analysis if not available
        market = project.market_analysis or MarketAnalysis(
            competitors=[],
            industry_trends={},
            opportunities=[]
        )

        concepts = await prompt_engine.generate_concepts(
            product=project.product_analysis,
            market=market,
            num_concepts=num_concepts
        )

        project.concepts = concepts
        project.status = ProjectStatus.READY_FOR_VIDEO
        project.updated_at = datetime.now()

        logger.info(f"Generated {len(concepts)} concepts for {project_id}")
        return concepts

    except Exception as e:
        logger.error(f"Concept generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/full-analysis")
async def run_full_analysis(
    project_id: str,
    background_tasks: BackgroundTasks
) -> dict:
    """
    Run the complete analysis pipeline in the background.

    This runs: Product Analysis -> Market Analysis -> Concept Generation
    """
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    async def run_pipeline():
        try:
            await analyze_product(project_id)
            await analyze_market(project_id)
            await generate_concepts(project_id)
        except Exception as e:
            logger.error(f"Full analysis pipeline failed: {e}")
            projects_db[project_id].status = ProjectStatus.FAILED

    background_tasks.add_task(run_pipeline)

    return {
        "status": "started",
        "message": "Full analysis pipeline started in background",
        "project_id": project_id
    }
