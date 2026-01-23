"""Database models for AdGenius."""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class VideoStatus(str, enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoProvider(str, enum.Enum):
    SORA = "sora"
    VEO = "veo"
    RUNWAY = "runway"


class Video(Base):
    """Video model for storing generated videos."""

    __tablename__ = "videos"

    id = Column(String(36), primary_key=True)

    # Repository info
    repo_owner = Column(String(255), nullable=True)
    repo_name = Column(String(255), nullable=True)
    repo_full_name = Column(String(511), nullable=True)

    # Video metadata
    title = Column(String(500), nullable=False, default="Untitled")
    description = Column(Text, nullable=True)
    prompt = Column(Text, nullable=True)

    # Generation info
    provider = Column(String(50), default="sora")
    status = Column(String(50), default="queued")
    duration_seconds = Column(Integer, default=8)
    resolution = Column(String(50), default="720x1280")

    # File paths
    local_path = Column(String(1000), nullable=True)
    video_url = Column(String(2000), nullable=True)
    thumbnail_path = Column(String(1000), nullable=True)

    # External IDs
    sora_video_id = Column(String(255), nullable=True)
    veo_video_id = Column(String(255), nullable=True)

    # Error tracking
    error = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "repo_owner": self.repo_owner,
            "repo_name": self.repo_name,
            "repo_full_name": self.repo_full_name,
            "title": self.title,
            "description": self.description,
            "prompt": self.prompt,
            "provider": self.provider,
            "status": self.status,
            "duration_seconds": self.duration_seconds,
            "resolution": self.resolution,
            "local_path": self.local_path,
            "video_url": self.video_url,
            "thumbnail_path": self.thumbnail_path,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class RepoAnalysis(Base):
    """Cached repository analysis."""

    __tablename__ = "repo_analyses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    repo_full_name = Column(String(511), unique=True, nullable=False)
    repo_owner = Column(String(255), nullable=False)
    repo_name = Column(String(255), nullable=False)

    # Analysis results (JSON stored as text)
    analysis_json = Column(Text, nullable=True)
    video_prompts_json = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
