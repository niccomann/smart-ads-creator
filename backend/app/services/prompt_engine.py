"""
Prompt Engineering Engine.

Generates optimized prompts for AI video generation platforms.
"""

from loguru import logger

from ..models.schemas import (
    ProductAnalysis,
    MarketAnalysis,
    VideoConcept,
    VideoPrompt,
    VideoStyle,
    VideoPlatform,
    VideoProvider
)
from ..core.prompts import SYSTEM_PROMPTS
from .claude_code import claude_code


class PromptEngineService:
    """Service for generating video prompts."""

    def __init__(self):
        self.system_prompt = SYSTEM_PROMPTS["prompt_engine"]

    async def generate_concepts(
        self,
        product: ProductAnalysis,
        market: MarketAnalysis,
        styles: list[VideoStyle] = None,
        platforms: list[VideoPlatform] = None,
        num_concepts: int = 3
    ) -> list[VideoConcept]:
        """
        Generate video concepts based on product and market analysis.

        Args:
            product: Product analysis data
            market: Market analysis data
            styles: Preferred video styles (optional)
            platforms: Target platforms (optional)
            num_concepts: Number of concepts to generate

        Returns:
            List of VideoConcepts with prompts for each provider
        """
        logger.info(f"Generating {num_concepts} video concepts for {product.product_name}")

        # Set defaults
        if not styles:
            styles = [VideoStyle.CINEMATIC, VideoStyle.LIFESTYLE, VideoStyle.UGC_STYLE]
        if not platforms:
            platforms = [VideoPlatform.INSTAGRAM_REELS, VideoPlatform.TIKTOK]

        # Build context for Claude
        prompt = f"""Genera {num_concepts} concept video pubblicitari unici per questo prodotto.

## PRODOTTO
Nome: {product.product_name}
Categoria: {product.category}
Posizionamento: {product.positioning}
USP: {', '.join(product.usp)}

## BRAND
Nome: {product.brand.get('name', 'N/A')}
Tone of Voice: {product.brand.get('tone_of_voice', 'N/A')}
Colori: {product.brand.get('colors', {})}

## TARGET AUDIENCE
Eta': {product.target_audience.get('age_range', 'N/A')}
Interessi: {', '.join(product.target_audience.get('interests', []))}
Pain Points: {', '.join(product.target_audience.get('pain_points', []))}

## STILE VISIVO SUGGERITO
{product.visual_style.get('suggested_video_style', 'cinematic')}

## INSIGHT DI MERCATO
Opportunita': {', '.join(market.opportunities) if market.opportunities else 'N/A'}
Trend: {market.industry_trends}

## REQUISITI
- Stili da considerare: {', '.join([s.value for s in styles])}
- Piattaforme target: {', '.join([p.value for p in platforms])}
- Durata: 8-15 secondi
- Aspect ratio: 9:16 (vertical per Reels/TikTok)

Per ogni concept, genera:
1. Titolo e descrizione
2. Prompt dettagliato per Sora (cinematico, specifico)
3. Prompt per Runway (ottimizzato per motion)
4. Prompt per Kling (budget option)
5. Note per post-produzione (text overlay, CTA, musica)

Rispondi con un array JSON di {num_concepts} concept."""

        result = await claude_code.run_prompt(
            prompt=prompt,
            system_prompt=self.system_prompt,
            output_format="json",
            timeout=180
        )

        logger.debug(f"Prompt engine result: {result}")

        # Parse into VideoConcepts
        concepts = []

        # Handle different response structures
        concepts_data = result
        if isinstance(result, dict):
            concepts_data = result.get("concepts", result.get("video_concepts", [result]))
        if not isinstance(concepts_data, list):
            concepts_data = [concepts_data]

        for concept_data in concepts_data[:num_concepts]:
            try:
                video_concept = concept_data.get("video_concept", concept_data)

                prompts = {}
                prompts_data = concept_data.get("prompts", {})

                for provider in VideoProvider:
                    provider_key = provider.value
                    if provider_key in prompts_data:
                        p = prompts_data[provider_key]
                        prompts[provider_key] = VideoPrompt(
                            provider=provider,
                            main_prompt=p.get("main_prompt", ""),
                            style_reference=p.get("style_reference"),
                            negative_prompt=p.get("negative_prompt"),
                            duration_seconds=p.get("duration", 10),
                            resolution=p.get("resolution", "1080x1920")
                        )

                concepts.append(VideoConcept(
                    title=video_concept.get("title", f"Concept {len(concepts) + 1}"),
                    description=video_concept.get("description", ""),
                    style=VideoStyle(video_concept.get("style", "cinematic")),
                    platform=VideoPlatform(platforms[0].value),
                    duration_seconds=video_concept.get("duration_seconds", 10),
                    prompts=prompts,
                    post_production_notes=concept_data.get("post_production_notes", {})
                ))
            except Exception as e:
                logger.warning(f"Failed to parse concept: {e}")
                continue

        if not concepts:
            # Return a default concept if parsing failed
            logger.warning("No concepts parsed, returning default")
            concepts.append(VideoConcept(
                title="Default Concept",
                description="Lifestyle video showcasing the product",
                style=VideoStyle.LIFESTYLE,
                platform=platforms[0],
                duration_seconds=10,
                prompts={},
                post_production_notes={}
            ))

        return concepts


# Singleton instance
prompt_engine = PromptEngineService()
