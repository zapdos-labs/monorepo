# service.py (your main gateway file)
from __future__ import annotations
import bentoml

# Step 1: Import the service CLASSES from the other files.
from services.summarizer_service import SummarizationService
from services.translator_service import TranslationService

@bentoml.service
class ApiGateway:
    """
    This is the only service exposed to the internet.
    """
    # Step 2: Use bentoml.depends() with the CLASSES.
    # BentoML will create the instances for you.
    summarization_svc = bentoml.depends(SummarizationService)
    translation_svc = bentoml.depends(TranslationService)

    @bentoml.api
    async def process_text(self, text: str) -> dict:
        summary = await self.summarization_svc.to_async.summarize(text)
        translation = await self.translation_svc.to_async.translate(summary)

        return {
            "original_text": text,
            "summary": summary,
            "translation": translation,
        }

# Create an instance of the gateway itself. This is still necessary
# for `bentoml serve` to know what to run.
gateway = ApiGateway()