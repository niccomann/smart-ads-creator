"""
Product Intelligence Service.

Analyzes products to extract marketing-relevant information.
"""

from loguru import logger

from ..models.schemas import ProductInput, ProductAnalysis
from ..core.prompts import SYSTEM_PROMPTS
from .claude_code import claude_code


class ProductIntelService:
    """Service for product analysis."""

    def __init__(self):
        self.system_prompt = SYSTEM_PROMPTS["product_intel"]

    async def analyze(self, product_input: ProductInput) -> ProductAnalysis:
        """
        Analyze a product and extract marketing information.

        Args:
            product_input: Product input with URL, images, description

        Returns:
            ProductAnalysis with extracted information
        """
        logger.info(f"Analyzing product: {product_input.url or 'from images'}")

        # Build the analysis prompt
        prompt_parts = ["Analizza questo prodotto per creare una video ad efficace.\n"]

        if product_input.url:
            prompt_parts.append(f"URL: {product_input.url}\n")

        if product_input.description:
            prompt_parts.append(f"Descrizione: {product_input.description}\n")

        if product_input.category:
            prompt_parts.append(f"Categoria: {product_input.category}\n")

        if product_input.images:
            prompt_parts.append(f"\nImmagini prodotto:")
            for i, img in enumerate(product_input.images, 1):
                prompt_parts.append(f"  {i}. {img}")

        prompt_parts.append("\nEstrai tutte le informazioni rilevanti in formato JSON.")

        prompt = "\n".join(prompt_parts)

        # Call Claude Code
        result = await claude_code.run_prompt(
            prompt=prompt,
            system_prompt=self.system_prompt,
            output_format="json",
            timeout=120
        )

        logger.debug(f"Product analysis result: {result}")

        # Parse into ProductAnalysis
        try:
            # Handle nested structure if present
            if "raw_text" in result:
                raise ValueError("Could not parse product analysis")

            return ProductAnalysis(
                product_name=result.get("product_name", "Unknown"),
                category=result.get("category", "Unknown"),
                price=result.get("price"),
                currency=result.get("currency", "EUR"),
                positioning=result.get("positioning", "premium"),
                brand=result.get("brand", {
                    "name": "Unknown",
                    "tone_of_voice": "professional",
                    "colors": {"primary": "#000000", "secondary": "#ffffff", "accent": "#ff0000"}
                }),
                usp=result.get("usp", []),
                target_audience=result.get("target_audience", {
                    "age_range": "25-45",
                    "gender": "unisex",
                    "interests": [],
                    "pain_points": []
                }),
                visual_style=result.get("visual_style", {
                    "aesthetic": "modern",
                    "photography_style": "professional",
                    "suggested_video_style": "cinematic"
                }),
                cta_current=result.get("cta_current"),
                competitors_inferred=result.get("competitors_inferred", [])
            )
        except Exception as e:
            logger.error(f"Failed to parse product analysis: {e}")
            raise ValueError(f"Failed to parse product analysis: {e}")


# Singleton instance
product_intel = ProductIntelService()
