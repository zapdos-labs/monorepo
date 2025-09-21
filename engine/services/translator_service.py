# services/translator_service.py
from __future__ import annotations
import bentoml

@bentoml.service(
    workers=1
)
class TranslationService:
    """A dummy service that 'translates' text."""

    @bentoml.api
    def translate(self, text: str, lang: str = "French") -> str:
        print(f"INTERNAL: Translating text to {lang}: '{text[:20]}...'")
        return f"This is the text translated to {lang}."

# The instance creation line has been removed.