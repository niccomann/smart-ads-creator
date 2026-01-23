"""
GitHub Intelligence Service.

Reads repositories from GitHub, analyzes code to understand projects,
and generates marketing content for video ads.
"""

import base64
from typing import Optional
from loguru import logger
import httpx

from ..config import settings
from .claude_code import claude_code


class GitHubIntelService:
    """Service for GitHub repository analysis."""

    def __init__(self):
        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {settings.github_api_key}",
            "Accept": "application/vnd.github.v3+json",
        }

    async def get_user_repos(
        self,
        visibility: str = "public",
        sort: str = "updated",
        per_page: int = 30
    ) -> list[dict]:
        """
        Get all repositories for the authenticated user.

        Args:
            visibility: public, private, or all
            sort: created, updated, pushed, full_name
            per_page: Number of repos per page

        Returns:
            List of repository data
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_base}/user/repos",
                headers=self.headers,
                params={
                    "visibility": visibility,
                    "sort": sort,
                    "per_page": per_page,
                    "affiliation": "owner",
                },
                timeout=30.0
            )

            if response.status_code != 200:
                logger.error(f"GitHub API error: {response.status_code} - {response.text}")
                raise Exception(f"GitHub API error: {response.status_code}")

            repos = response.json()

            # Filter and enrich repos
            enriched_repos = []
            for repo in repos:
                enriched_repos.append({
                    "id": repo["id"],
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "description": repo["description"],
                    "url": repo["html_url"],
                    "homepage": repo.get("homepage"),
                    "language": repo["language"],
                    "topics": repo.get("topics", []),
                    "stars": repo["stargazers_count"],
                    "forks": repo["forks_count"],
                    "is_private": repo["private"],
                    "created_at": repo["created_at"],
                    "updated_at": repo["updated_at"],
                    "default_branch": repo["default_branch"],
                })

            logger.info(f"Found {len(enriched_repos)} repositories")
            return enriched_repos

    async def get_repo_content(self, owner: str, repo: str, path: str = "") -> list[dict]:
        """Get contents of a repository path."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_base}/repos/{owner}/{repo}/contents/{path}",
                headers=self.headers,
                timeout=30.0
            )

            if response.status_code == 404:
                return []
            elif response.status_code != 200:
                logger.warning(f"Could not fetch {path}: {response.status_code}")
                return []

            return response.json()

    async def get_file_content(self, owner: str, repo: str, path: str) -> Optional[str]:
        """Get content of a specific file."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_base}/repos/{owner}/{repo}/contents/{path}",
                headers=self.headers,
                timeout=30.0
            )

            if response.status_code != 200:
                return None

            data = response.json()
            if data.get("type") != "file":
                return None

            # Decode base64 content
            content = data.get("content", "")
            try:
                return base64.b64decode(content).decode("utf-8")
            except Exception:
                return None

    async def analyze_repository(self, repo_data: dict) -> dict:
        """
        Analyze a repository to understand what it does.

        Reads key files (README, package.json, etc.) and uses AI
        to generate a marketing-focused analysis.
        """
        owner, repo_name = repo_data["full_name"].split("/")
        logger.info(f"Analyzing repository: {repo_data['full_name']}")

        # Gather context from the repository
        context_parts = []

        # Basic info
        context_parts.append(f"Repository: {repo_data['full_name']}")
        context_parts.append(f"Description: {repo_data['description'] or 'No description'}")
        context_parts.append(f"Language: {repo_data['language'] or 'Unknown'}")
        context_parts.append(f"Topics: {', '.join(repo_data['topics']) or 'None'}")
        context_parts.append(f"Homepage: {repo_data['homepage'] or 'None'}")
        context_parts.append(f"Stars: {repo_data['stars']}, Forks: {repo_data['forks']}")

        # Try to read key files
        key_files = [
            "README.md",
            "readme.md",
            "README",
            "package.json",
            "pyproject.toml",
            "Cargo.toml",
            "setup.py",
            "docker-compose.yml",
            ".env.example",
        ]

        files_content = {}
        for file_path in key_files:
            content = await self.get_file_content(owner, repo_name, file_path)
            if content:
                # Truncate large files
                if len(content) > 5000:
                    content = content[:5000] + "\n... [truncated]"
                files_content[file_path] = content
                logger.debug(f"Read {file_path} ({len(content)} chars)")

        # Add file contents to context
        if files_content:
            context_parts.append("\n--- Repository Files ---")
            for file_name, content in files_content.items():
                context_parts.append(f"\n### {file_name}\n```\n{content}\n```")

        # Try to get directory structure
        root_contents = await self.get_repo_content(owner, repo_name)
        if root_contents:
            dir_items = [f"- {item['name']} ({item['type']})" for item in root_contents[:20]]
            context_parts.append(f"\n--- Directory Structure ---\n" + "\n".join(dir_items))

        full_context = "\n".join(context_parts)

        # Use Claude to analyze the repository
        analysis_prompt = f"""Analizza questo repository GitHub per creare un video pubblicitario efficace.

{full_context}

Basandoti su queste informazioni, estrai:

1. **Nome Prodotto**: Il nome del progetto/prodotto
2. **Categoria**: Tipo di software (SaaS, CLI tool, library, mobile app, etc.)
3. **Cosa Fa**: Descrizione chiara di cosa fa il prodotto (1-2 frasi)
4. **Problema Risolto**: Quale problema risolve per gli utenti
5. **Target Audience**: Chi sono gli utenti ideali
6. **USP**: Punti di forza unici (3-5 bullet points)
7. **Tech Stack**: Tecnologie principali usate
8. **Stato**: deployed/in development/beta
9. **URL Prodotto**: Homepage o URL di deployment se disponibile
10. **Stile Visivo Suggerito**: Che tipo di video funzionerebbe meglio

Rispondi in JSON con questa struttura:
{{
  "product_name": "string",
  "category": "string",
  "what_it_does": "string",
  "problem_solved": "string",
  "target_audience": {{
    "primary": "string",
    "interests": ["string"],
    "pain_points": ["string"]
  }},
  "usp": ["string"],
  "tech_stack": ["string"],
  "status": "deployed|development|beta",
  "product_url": "string or null",
  "visual_style": {{
    "recommended_style": "string",
    "mood": "string",
    "color_palette": "string"
  }},
  "video_hook_ideas": ["string - 3 idee per hook video accattivanti"]
}}"""

        result = await claude_code.run_prompt(
            prompt=analysis_prompt,
            system_prompt="""Sei un esperto di marketing tech e developer advocacy.
Il tuo compito e' analizzare repository GitHub per creare contenuti promozionali.
Rispondi SEMPRE in JSON valido. Sii specifico e concreto nelle descrizioni.""",
            output_format="json",
            timeout=120
        )

        # Merge with repo data
        analysis = {
            "repo": repo_data,
            "analysis": result,
        }

        logger.info(f"Analysis complete for {repo_data['full_name']}")
        return analysis

    async def generate_video_prompt_for_repo(self, analysis: dict) -> dict:
        """
        Generate optimized video prompts based on repository analysis.
        """
        repo = analysis["repo"]
        project = analysis["analysis"]

        prompt = f"""Genera prompt video per pubblicizzare questo progetto software:

## PROGETTO
Nome: {project.get('product_name', repo['name'])}
Categoria: {project.get('category', 'Software')}
Cosa Fa: {project.get('what_it_does', repo['description'])}
Problema Risolto: {project.get('problem_solved', 'N/A')}

## TARGET
Audience: {project.get('target_audience', {}).get('primary', 'Developers')}
Pain Points: {project.get('target_audience', {}).get('pain_points', [])}

## USP
{chr(10).join('- ' + usp for usp in project.get('usp', []))}

## STILE SUGGERITO
Stile: {project.get('visual_style', {}).get('recommended_style', 'tech/modern')}
Mood: {project.get('visual_style', {}).get('mood', 'professional')}

## HOOK IDEAS
{chr(10).join('- ' + hook for hook in project.get('video_hook_ideas', []))}

Genera 2 concept video pubblicitari:
1. Un video "problem-solution" che mostra il problema e come il software lo risolve
2. Un video "demo showcase" che mostra il prodotto in azione

Per ogni concept includi:
- Titolo
- Descrizione scena per scena (5-8 secondi per scena)
- Prompt dettagliato per AI video generation (Sora/Runway)
- Testo overlay suggerito
- Musica/mood audio

Rispondi in JSON."""

        result = await claude_code.run_prompt(
            prompt=prompt,
            system_prompt="""Sei un esperto di video marketing per prodotti tech.
Crea prompt cinematografici e specifici per video AI.
I video devono essere moderni, dinamici e catturare l'attenzione nei primi 2 secondi.
Rispondi in JSON valido.""",
            output_format="json",
            timeout=120
        )

        return {
            "repo": repo,
            "project_analysis": project,
            "video_concepts": result,
        }


# Singleton instance
github_intel = GitHubIntelService()
