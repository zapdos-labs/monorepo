# services/summarizer_service.py
from __future__ import annotations
import bentoml

@bentoml.service
class SummarizationService:
    """A dummy service that 'summarizes' text."""

    @bentoml.api
    def summarize(self, text: str) -> str:
        print(f"INTERNAL: Summarizing text: '{text[:20]}...'")
        return f"This is a summary of the text."

# The instance creation line has been removed.