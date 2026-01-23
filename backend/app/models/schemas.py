"""Pydantic models for the AdGenius API."""

from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from enum import Enum
from datetime import datetime


# ============================================================
# Enums
# ============================================================

class ProjectStatus(str, Enum):
    DRAFT = "draft"
    ANALYZING = "analyzing"
    READY_FOR_VIDEO = "ready_for_video"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoStyle(str, Enum):
    CINEMATIC = "cinematic"
    LIFESTYLE = "lifestyle"
    UGC_STYLE = "ugc_style"
    PRODUCT_DEMO = "product_demo"
    TESTIMONIAL = "testimonial"


class VideoPlatform(str, Enum):
    INSTAGRAM_REELS = "instagram_reels"
    TIKTOK = "tiktok"
    YOUTUBE_SHORTS = "youtube_shorts"
    FACEBOOK_FEED = "facebook_feed"


class VideoProvider(str, Enum):
    SORA = "sora"
    VEO = "veo"
    RUNWAY = "runway"
    KLING = "kling"


# ============================================================
# Product Intelligence
# ============================================================

class ProductInput(BaseModel):
    """Input for product analysis."""
    url: Optional[HttpUrl] = None
    images: list[str] = Field(default_factory=list, description="List of image URLs or base64")
    description: Optional[str] = None
    category: Optional[str] = None


class BrandInfo(BaseModel):
    """Extracted brand information."""
    name: str
    tone_of_voice: str
    colors: dict[str, str]  # primary, secondary, accent


class TargetAudience(BaseModel):
    """Target audience profile."""
    age_range: str
    gender: str
    interests: list[str]
    pain_points: list[str]


class VisualStyle(BaseModel):
    """Visual style recommendations."""
    aesthetic: str
    photography_style: str
    suggested_video_style: str


class ProductAnalysis(BaseModel):
    """Complete product analysis result."""
    product_name: str
    category: str
    price: Optional[float] = None
    currency: str = "EUR"
    positioning: str  # budget, premium, luxury
    brand: BrandInfo
    usp: list[str]  # Unique selling propositions
    target_audience: TargetAudience
    visual_style: VisualStyle
    cta_current: Optional[str] = None
    competitors_inferred: list[str] = Field(default_factory=list)


# ============================================================
# Market Intelligence
# ============================================================

class CompetitorAd(BaseModel):
    """Single competitor ad."""
    ad_id: str
    page_name: str
    ad_text: Optional[str] = None
    media_url: Optional[str] = None
    cta: Optional[str] = None
    start_date: Optional[str] = None
    is_active: bool = True
    format: str  # video, image, carousel


class CompetitorAnalysis(BaseModel):
    """Analysis of a single competitor."""
    name: str
    total_active_ads: int
    dominant_formats: dict[str, int]
    top_ads: list[CompetitorAd]
    messaging_themes: list[str]
    gaps_identified: list[str]


class MarketAnalysis(BaseModel):
    """Complete market analysis."""
    competitors: list[CompetitorAnalysis]
    industry_trends: dict
    opportunities: list[str]


# ============================================================
# Prompt Engine
# ============================================================

class VideoPrompt(BaseModel):
    """Generated video prompt."""
    provider: VideoProvider
    main_prompt: str
    style_reference: Optional[str] = None
    negative_prompt: Optional[str] = None
    duration_seconds: int = 10
    resolution: str = "1080x1920"


class VideoConcept(BaseModel):
    """Video concept with prompts."""
    title: str
    description: str
    style: VideoStyle
    platform: VideoPlatform
    duration_seconds: int
    prompts: dict[str, VideoPrompt]  # provider -> prompt
    post_production_notes: dict


# ============================================================
# Video Generation
# ============================================================

class VideoGenerationRequest(BaseModel):
    """Request to generate a video."""
    project_id: str
    concept: VideoConcept
    provider: VideoProvider = VideoProvider.SORA
    quality: str = "1080p"


class GeneratedVideo(BaseModel):
    """Generated video result."""
    id: str
    project_id: str
    concept_title: str
    provider: VideoProvider
    status: str
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    local_path: Optional[str] = None
    sora_video_id: Optional[str] = None
    duration_seconds: int
    resolution: str
    created_at: datetime
    error: Optional[str] = None


# ============================================================
# Project
# ============================================================

class ProjectCreate(BaseModel):
    """Create a new project."""
    name: str
    product_input: ProductInput


class Project(BaseModel):
    """Full project model."""
    id: str
    name: str
    status: ProjectStatus
    product_input: ProductInput
    product_analysis: Optional[ProductAnalysis] = None
    market_analysis: Optional[MarketAnalysis] = None
    concepts: list[VideoConcept] = Field(default_factory=list)
    videos: list[GeneratedVideo] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
