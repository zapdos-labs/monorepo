# service.py (The Unified API Gateway)
from __future__ import annotations
import bentoml
from typing import List, Dict

# Import all the internal service CLASSES
from services.summarizer_service import SummarizationService
from services.translator_service import TranslationService
from services.image_description_service import InferenceService

@bentoml.service
class ApiGateway:
    """A unified gateway for all application services."""

    # Define dependencies on all internal services
    summarization_svc = bentoml.depends(SummarizationService)
    translation_svc = bentoml.depends(TranslationService)
    image_inference_svc = bentoml.depends(InferenceService)

    # --- Endpoint 1: Text Processing ---
    @bentoml.api
    async def process_text(self, text: str) -> dict:
        """Takes a string, summarizes it, and translates the summary."""
        summary = await self.summarization_svc.to_async.summarize(text)
        translation = await self.translation_svc.to_async.translate(summary)
        return {
            "original_text": text,
            "summary": summary,
            "translation": translation,
        }

    # --- Endpoint 2: Image Description (Batchable) ---
    @bentoml.api(batchable=True)
    async def describe_images(self, filenames: List[str]) -> List[Dict[str, str]]:
        """Takes a list of filenames and returns their descriptions."""
        descriptions = await self.image_inference_svc.to_async.predict(filenames)
        return [
            {"filename": name, "description": desc}
            for name, desc in zip(filenames, descriptions)
        ]
