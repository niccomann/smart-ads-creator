"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

# Calculate paths
APP_DIR = Path(__file__).parent  # backend/app
BACKEND_DIR = APP_DIR.parent      # backend
PROJECT_DIR = BACKEND_DIR.parent  # smart-ads-creator
ENV_FILE = PROJECT_DIR / ".env"


class Settings(BaseSettings):
    """Application settings."""

    # Server
    host: str = "0.0.0.0"
    port: int = 8466
    env: str = "dev"
    log_level: str = "INFO"

    # Claude Code OAuth (for Max subscription)
    claude_oauth_access_token: str

    # OpenAI (for Sora video generation)
    openai_api_key: str

    # Google Gemini (for Veo video generation)
    gemini_api_key: str

    # Runway ML (for video generation)
    runwayml_api_secret: str = ""  # Optional - from RUNWAYML_API_SECRET env var

    # GitHub API (for repository analysis)
    github_api_key: str

    # Apify (for Meta Ads Library scraping)
    # apify_api_key: str = ""  # Optional, add when needed

    # Paths
    base_dir: Path = PROJECT_DIR
    data_dir: Path = PROJECT_DIR / "data"
    videos_dir: Path = PROJECT_DIR / "data" / "videos"

    # Database
    database_url: str = f"sqlite+aiosqlite:///{PROJECT_DIR}/data/adgenius.db"

    model_config = {
        "env_file": str(ENV_FILE),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
