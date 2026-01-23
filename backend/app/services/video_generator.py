"""
Video Generator Service.

Uses OpenAI Sora, Google Veo, and Runway ML for AI video generation.
"""

import uuid
import time
import httpx
from datetime import datetime
from pathlib import Path
from typing import Optional, Literal
from loguru import logger
from openai import AsyncOpenAI

from ..config import settings
from ..models.schemas import (
    VideoConcept,
    VideoPrompt,
    GeneratedVideo,
    VideoProvider
)


# Size options
SoraSize = Literal["720x1280", "1280x720", "1024x1792", "1792x1024"]
VeoAspectRatio = Literal["16:9", "9:16"]
RunwayRatio = Literal["1280:720", "720:1280", "1920:1080", "1080:1920"]


class VideoGeneratorService:
    """Service for AI video generation using OpenAI Sora, Google Veo, and Runway ML."""

    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.gemini_api_key = settings.gemini_api_key
        self.runway_api_key = settings.runwayml_api_secret
        self.videos_dir = settings.videos_dir
        self.videos_dir.mkdir(parents=True, exist_ok=True)

    async def generate(
        self,
        project_id: str,
        concept: VideoConcept,
        provider: VideoProvider = VideoProvider.SORA
    ) -> GeneratedVideo:
        """Generate a video using the specified provider."""
        video_id = str(uuid.uuid4())
        logger.info(f"Starting video generation: {video_id}")

        # Get prompt
        prompt_data = concept.prompts.get("sora") or concept.prompts.get("veo")
        if not prompt_data:
            for p in concept.prompts.values():
                prompt_data = p
                break

        main_prompt = prompt_data.main_prompt if prompt_data else f"{concept.title}: {concept.description}"

        video = GeneratedVideo(
            id=video_id,
            project_id=project_id,
            concept_title=concept.title,
            provider=provider,
            status="queued",
            duration_seconds=concept.duration_seconds,
            resolution="720x1280",
            created_at=datetime.now()
        )

        try:
            if provider == VideoProvider.SORA:
                video = await self._generate_sora(video, main_prompt, concept.duration_seconds)
            else:
                video = await self._generate_veo(video, main_prompt, concept.duration_seconds)
        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            video.status = "failed"
            video.error = str(e)

        return video

    async def generate_from_prompt(
        self,
        prompt: str,
        duration: int = 8,
        size: str = "720x1280",
        provider: str = "auto"
    ) -> GeneratedVideo:
        """
        Generate video directly from a prompt string.

        Args:
            prompt: Text description of the video
            duration: 4, 6, or 8 seconds
            size: Resolution (720x1280 for vertical, 1280x720 for horizontal)
            provider: "sora", "veo", or "auto" (tries Sora first, falls back to Veo)
        """
        video_id = str(uuid.uuid4())
        logger.info(f"Direct video generation: {video_id}")
        logger.info(f"Provider: {provider}, Prompt: {prompt[:100]}...")

        video = GeneratedVideo(
            id=video_id,
            project_id="direct",
            concept_title="Direct Generation",
            provider=VideoProvider.SORA,
            status="queued",
            duration_seconds=duration,
            resolution=size,
            created_at=datetime.now()
        )

        # Auto mode: try Sora first, fallback to Veo
        if provider == "auto":
            logger.info("Auto mode: trying Sora first...")
            try:
                video = await self._generate_sora(video, prompt, duration, size)
                if video.status == "completed":
                    return video
            except Exception as e:
                logger.warning(f"Sora failed ({e}), falling back to Veo...")

            # Fallback to Veo
            video.status = "queued"
            video.error = None
            video.provider = VideoProvider.VEO
            try:
                video = await self._generate_veo(video, prompt, duration, size)
            except Exception as e:
                logger.error(f"Veo also failed: {e}")
                video.status = "failed"
                video.error = f"Both Sora and Veo failed: {e}"

        elif provider == "sora":
            try:
                video = await self._generate_sora(video, prompt, duration, size)
            except Exception as e:
                video.status = "failed"
                video.error = str(e)

        elif provider == "veo":
            video.provider = VideoProvider.VEO
            try:
                video = await self._generate_veo(video, prompt, duration, size)
            except Exception as e:
                video.status = "failed"
                video.error = str(e)

        elif provider == "runway":
            video.provider = VideoProvider.RUNWAY
            try:
                video = await self._generate_runway(video, prompt, duration, size)
            except Exception as e:
                video.status = "failed"
                video.error = str(e)

        return video

    async def _generate_sora(
        self,
        video: GeneratedVideo,
        prompt: str,
        duration: int = 8,
        size: str = "720x1280",
        model: str = "sora-2"
    ) -> GeneratedVideo:
        """Generate video using OpenAI Sora API."""
        logger.info(f"Generating with Sora ({model}): {prompt[:100]}...")
        video.status = "processing"
        video.provider = VideoProvider.SORA

        # Validate duration (must be 4, 8, or 12 for Sora)
        valid_durations = [4, 8, 12]
        if duration not in valid_durations:
            duration = min(valid_durations, key=lambda x: abs(x - duration))

        duration_str = str(duration)

        # Validate size
        valid_sizes = ["720x1280", "1280x720", "1024x1792", "1792x1024"]
        if size not in valid_sizes:
            size = "720x1280"

        try:
            logger.info("Sending request to Sora API...")

            sora_video = await self.openai_client.videos.create_and_poll(
                prompt=prompt,
                model=model,
                seconds=duration_str,
                size=size,
                timeout=600.0
            )

            logger.info(f"Sora response status: {sora_video.status}")

            if sora_video.status == "completed":
                video.status = "completed"
                video.sora_video_id = sora_video.id

                logger.info("Downloading generated video...")
                content = await self.openai_client.videos.download_content(sora_video.id)

                output_path = self.videos_dir / f"{video.id}.mp4"
                with open(output_path, "wb") as f:
                    f.write(content.content)

                video.local_path = str(output_path)
                logger.info(f"Video saved to {output_path}")

            elif sora_video.status == "failed":
                error_msg = getattr(sora_video, 'error', 'Unknown error')
                video.status = "failed"
                video.error = str(error_msg)
                raise Exception(f"Sora generation failed: {error_msg}")
            else:
                video.status = "failed"
                video.error = f"Unexpected status: {sora_video.status}"
                raise Exception(video.error)

        except Exception as e:
            logger.error(f"Sora API error: {e}")
            video.status = "failed"
            video.error = str(e)
            raise

        return video

    async def _generate_veo(
        self,
        video: GeneratedVideo,
        prompt: str,
        duration: int = 8,
        size: str = "720x1280"
    ) -> GeneratedVideo:
        """Generate video using Google Veo API."""
        logger.info(f"Generating with Veo: {prompt[:100]}...")
        video.status = "processing"

        # Import google genai
        try:
            from google import genai
            from google.genai import types
        except ImportError:
            raise Exception("google-genai package not installed. Run: pip install google-genai")

        # Determine aspect ratio from size
        if "1280x720" in size or "1792x1024" in size:
            aspect_ratio = "16:9"
        else:
            aspect_ratio = "9:16"

        # Veo 1080p requires 8 seconds duration
        # For other resolutions, supports 4, 6, 8 seconds
        duration = 8  # Force 8 seconds for 1080p compatibility

        try:
            # Initialize client
            client = genai.Client(api_key=self.gemini_api_key)

            logger.info(f"Sending request to Veo API (aspect_ratio={aspect_ratio}, duration={duration}s)...")

            # Generate video
            operation = client.models.generate_videos(
                model="veo-3.1-generate-preview",
                prompt=prompt,
                config=types.GenerateVideosConfig(
                    aspect_ratio=aspect_ratio,
                    resolution="1080p",
                    duration_seconds=str(duration),
                ),
            )

            # Poll for completion
            max_wait = 600  # 10 minutes
            wait_time = 0
            poll_interval = 10

            while not operation.done and wait_time < max_wait:
                logger.info(f"Waiting for Veo... ({wait_time}s)")
                time.sleep(poll_interval)
                wait_time += poll_interval
                operation = client.operations.get(operation)

            if not operation.done:
                raise Exception("Veo generation timed out")

            # Download video
            if operation.response and operation.response.generated_videos:
                generated_video = operation.response.generated_videos[0]

                # Download and save
                output_path = self.videos_dir / f"{video.id}.mp4"
                client.files.download(file=generated_video.video)
                generated_video.video.save(str(output_path))

                video.status = "completed"
                video.local_path = str(output_path)
                logger.info(f"Veo video saved to {output_path}")
            else:
                raise Exception("No video generated by Veo")

        except Exception as e:
            logger.error(f"Veo API error: {e}")
            video.status = "failed"
            video.error = str(e)
            raise

        return video

    async def _generate_runway(
        self,
        video: GeneratedVideo,
        prompt: str,
        duration: int = 5,
        size: str = "720x1280"
    ) -> GeneratedVideo:
        """Generate video using Runway ML API."""
        logger.info(f"Generating with Runway: {prompt[:100]}...")
        video.status = "processing"

        if not self.runway_api_key:
            raise Exception("RUNWAYML_API_SECRET not configured")

        # Import RunwayML
        try:
            from runwayml import RunwayML, TaskFailedError
        except ImportError:
            raise Exception("runwayml package not installed. Run: pip install runwayml")

        # Convert size to Runway ratio format
        if "1280x720" in size or "1280:720" in size:
            ratio = "1280:720"
        elif "1920x1080" in size or "1920:1080" in size:
            ratio = "1920:1080"
        elif "1080x1920" in size or "1080:1920" in size:
            ratio = "1080:1920"
        else:
            ratio = "720:1280"  # Default vertical

        # Runway supports 5 or 10 second videos for text-to-video
        if duration <= 5:
            runway_duration = 5
        else:
            runway_duration = 10

        try:
            # Initialize client with API key
            client = RunwayML(api_key=self.runway_api_key)

            logger.info(f"Sending request to Runway API (ratio={ratio}, duration={runway_duration}s)...")

            # Use text_to_video endpoint
            task = client.text_to_video.create(
                model="veo3.1",  # Runway's text-to-video model
                prompt_text=prompt,
                ratio=ratio,
                duration=runway_duration,
            )

            logger.info(f"Runway task created: {task.id}")

            # Wait for completion with timeout
            try:
                result = task.wait_for_task_output(timeout=600)
                logger.info(f"Runway task completed: {result}")

                # Download the video
                if hasattr(result, 'output') and result.output:
                    video_url = result.output[0] if isinstance(result.output, list) else result.output

                    # Download video file
                    output_path = self.videos_dir / f"{video.id}.mp4"

                    async with httpx.AsyncClient() as http_client:
                        response = await http_client.get(video_url, timeout=120.0)
                        response.raise_for_status()

                        with open(output_path, "wb") as f:
                            f.write(response.content)

                    video.status = "completed"
                    video.local_path = str(output_path)
                    logger.info(f"Runway video saved to {output_path}")
                else:
                    raise Exception("No video output from Runway")

            except TaskFailedError as e:
                logger.error(f"Runway task failed: {e}")
                video.status = "failed"
                video.error = str(e.task_details) if hasattr(e, 'task_details') else str(e)
                raise

        except Exception as e:
            logger.error(f"Runway API error: {e}")
            video.status = "failed"
            video.error = str(e)
            raise

        return video

    def get_local_video_path(self, video_id: str) -> Optional[Path]:
        """Get path to locally stored video."""
        path = self.videos_dir / f"{video_id}.mp4"
        return path if path.exists() else None

    async def list_videos(self, limit: int = 20):
        """List recent videos from OpenAI."""
        try:
            videos = await self.openai_client.videos.list(limit=limit)
            return videos
        except Exception as e:
            logger.error(f"Failed to list videos: {e}")
            return []


# Singleton instance
video_generator = VideoGeneratorService()
