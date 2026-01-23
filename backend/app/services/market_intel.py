"""
Market Intelligence Service.

Analyzes competitor ads and market trends.
"""

from typing import Optional
from loguru import logger

from ..models.schemas import MarketAnalysis, CompetitorAnalysis, CompetitorAd
from ..core.prompts import SYSTEM_PROMPTS
from .claude_code import claude_code


class MarketIntelService:
    """Service for market and competitor analysis."""

    def __init__(self):
        self.system_prompt = SYSTEM_PROMPTS["market_intel"]

    async def analyze_competitors(
        self,
        competitor_names: list[str],
        category: str,
        country: str = "IT",
        limit_per_competitor: int = 20
    ) -> MarketAnalysis:
        """
        Analyze competitor ads from Meta Ads Library.

        Args:
            competitor_names: List of competitor brand names
            category: Product category for context
            country: Country code for ads
            limit_per_competitor: Max ads to analyze per competitor

        Returns:
            MarketAnalysis with competitor insights
        """
        logger.info(f"Analyzing competitors: {competitor_names}")

        # For now, we'll use Claude Code to analyze based on public knowledge
        # In production, this would integrate with Apify for Meta Ads Library scraping

        prompt = f"""Analizza i seguenti competitor nel settore "{category}" per il mercato {country}:

Competitor da analizzare:
{chr(10).join(f'- {name}' for name in competitor_names)}

Basandoti sulla tua conoscenza di questi brand e delle loro strategie pubblicitarie:
1. Identifica i formati pubblicitari dominanti (video, immagine, carousel)
2. Analizza i temi di messaging principali
3. Identifica gap e opportunita' nel mercato
4. Suggerisci trend emergenti nel settore

Rispondi in formato JSON strutturato."""

        result = await claude_code.run_prompt(
            prompt=prompt,
            system_prompt=self.system_prompt,
            output_format="json",
            timeout=120
        )

        logger.debug(f"Market analysis result: {result}")

        # Parse result into MarketAnalysis
        try:
            competitors = []
            for comp_data in result.get("competitors", []):
                competitors.append(CompetitorAnalysis(
                    name=comp_data.get("name", "Unknown"),
                    total_active_ads=comp_data.get("total_active_ads", 0),
                    dominant_formats=comp_data.get("dominant_formats", {}),
                    top_ads=[
                        CompetitorAd(**ad) for ad in comp_data.get("top_ads", [])
                    ],
                    messaging_themes=comp_data.get("messaging_themes", []),
                    gaps_identified=comp_data.get("gaps_identified", [])
                ))

            return MarketAnalysis(
                competitors=competitors,
                industry_trends=result.get("industry_trends", {}),
                opportunities=result.get("opportunities", [])
            )
        except Exception as e:
            logger.error(f"Failed to parse market analysis: {e}")
            # Return minimal analysis on error
            return MarketAnalysis(
                competitors=[],
                industry_trends={},
                opportunities=[]
            )

    async def scrape_meta_ads(
        self,
        search_query: str,
        country: str = "IT",
        limit: int = 50
    ) -> list[dict]:
        """
        Scrape ads from Meta Ads Library using Apify.

        This is a placeholder - implement with Apify integration.
        """
        # TODO: Implement Apify integration
        # from apify_client import ApifyClient
        # client = ApifyClient(settings.apify_api_key)
        # ...
        logger.warning("Meta Ads Library scraping not yet implemented")
        return []


# Singleton instance
market_intel = MarketIntelService()
