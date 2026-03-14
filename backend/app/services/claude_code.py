"""
Claude Code CLI wrapper service.

Uses shared-llm-gateway CLIProvider for the subprocess logic.
Leverages Max subscription instead of per-token API costs.
"""

from typing import Optional
from loguru import logger

from shared_llm_gateway import CLIProvider, extract_json


class ClaudeCodeService:
    """Service to interact with Claude Code CLI."""

    def __init__(self):
        self._provider = CLIProvider("claude")

    async def run_prompt(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        output_format: str = "json",
        max_turns: int = 5,
        timeout: int = 180
    ) -> dict:
        """
        Run a prompt through Claude Code CLI.

        Args:
            prompt: The user prompt to send
            system_prompt: Optional system prompt for context
            output_format: Expected output format (json, text)
            max_turns: Maximum conversation turns
            timeout: Timeout in seconds

        Returns:
            Parsed response from Claude Code
        """
        logger.info(f"Running Claude Code with prompt ({len(prompt)} chars)...")

        response = await self._provider.agenerate(
            messages=[{"role": "user", "content": prompt}],
            system=system_prompt,
        )

        if not response.success:
            logger.error(f"Claude Code error: {response.error}")
            raise RuntimeError(f"Claude Code failed: {response.error}")

        logger.info(f"Claude Code completed, output length: {len(response.content)}")

        if output_format == "json":
            parsed = extract_json(response.content)
            if parsed and isinstance(parsed, dict):
                return parsed
            logger.warning("Could not extract JSON from Claude Code output")
            return {"raw_text": response.content}
        else:
            return {"text": response.content}

    async def analyze_with_vision(
        self,
        prompt: str,
        image_paths: list[str],
        system_prompt: Optional[str] = None,
        timeout: int = 180
    ) -> dict:
        """
        Run a prompt with image analysis using Claude Code.
        """
        images_text = "\n".join([f"Image: {path}" for path in image_paths])
        full_prompt = f"{prompt}\n\n{images_text}"

        return await self.run_prompt(
            prompt=full_prompt,
            system_prompt=system_prompt,
            timeout=timeout
        )


# Singleton instance
claude_code = ClaudeCodeService()
