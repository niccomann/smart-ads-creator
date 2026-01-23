"""
Claude Code CLI wrapper service.

This service invokes Claude Code as a subprocess to leverage the Max subscription
instead of paying per-token API costs.

NOTE: Claude Code uses the user's logged-in Max subscription authentication.
Do NOT set ANTHROPIC_AUTH_TOKEN - it will override the Max auth and fail.
"""

import asyncio
import json
import os
import tempfile
from typing import Optional
from loguru import logger


class ClaudeCodeService:
    """Service to interact with Claude Code CLI."""

    def __init__(self):
        # Claude Code uses the local Max subscription auth automatically
        pass

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
        # Write prompt to a temp file to avoid shell escaping issues
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(prompt)
            prompt_file = f.name

        # Write system prompt to a separate file if provided
        system_prompt_file = None
        if system_prompt:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(system_prompt)
                system_prompt_file = f.name

        try:
            # Build the command - use --system-prompt flag if provided
            shell_cmd = f'cat "{prompt_file}" | claude --print --max-turns {max_turns}'
            if system_prompt_file:
                shell_cmd = f'cat "{prompt_file}" | claude --print --max-turns {max_turns} --system-prompt "$(cat {system_prompt_file})"'

            logger.info(f"Running Claude Code with prompt ({len(prompt)} chars)...")

            # Run the subprocess - inherit user's environment for Claude auth
            process = await asyncio.create_subprocess_shell(
                shell_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )

            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                stdout_msg = stdout.decode() if stdout else ""
                logger.error(f"Claude Code error: {error_msg}")
                logger.error(f"Claude Code stdout: {stdout_msg}")
                raise RuntimeError(f"Claude Code failed: {error_msg or stdout_msg or 'Unknown error'}")

            # Parse output
            output = stdout.decode()
            logger.info(f"Claude Code completed, output length: {len(output)}")
            logger.debug(f"Claude Code raw output: {output[:1000]}")

            if output_format == "json":
                return self._extract_json(output)
            else:
                return {"text": output}

        except asyncio.TimeoutError:
            logger.error(f"Claude Code timed out after {timeout}s")
            raise TimeoutError(f"Claude Code request timed out after {timeout} seconds")
        finally:
            # Clean up temp files
            for filepath in [prompt_file, system_prompt_file]:
                if filepath:
                    try:
                        os.unlink(filepath)
                    except:
                        pass

    def _extract_json(self, text: str) -> dict:
        """Extract JSON from Claude Code output."""
        import re

        # Try to parse the entire output as JSON first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Look for JSON blocks in the output
        json_patterns = [
            r'```json\s*([\s\S]*?)\s*```',  # ```json ... ```
            r'```\s*(\{[\s\S]*?\})\s*```',   # ``` { ... } ```
        ]

        for pattern in json_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    cleaned = match.strip()
                    parsed = json.loads(cleaned)
                    if isinstance(parsed, dict):
                        return parsed
                except json.JSONDecodeError:
                    continue

        # Try to find a raw JSON object (greedy match for the largest valid JSON)
        # Find all { and try to parse from each one
        for i, char in enumerate(text):
            if char == '{':
                # Try to find matching closing brace
                depth = 0
                for j in range(i, len(text)):
                    if text[j] == '{':
                        depth += 1
                    elif text[j] == '}':
                        depth -= 1
                        if depth == 0:
                            try:
                                candidate = text[i:j+1]
                                parsed = json.loads(candidate)
                                if isinstance(parsed, dict):
                                    return parsed
                            except json.JSONDecodeError:
                                pass
                            break

        # If no JSON found, return the text in a wrapper
        logger.warning("Could not extract JSON from Claude Code output")
        return {"raw_text": text}

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
