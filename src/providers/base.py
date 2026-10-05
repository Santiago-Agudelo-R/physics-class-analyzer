"""
Base abstract interface for LLM Providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json
import re


class LLMProvider(ABC):
    """Abstract interface for pluggable LLM backends (Ollama, OpenAI, Mock, etc.)."""

    @abstractmethod
    def analyze(self, prompt: str, context: str) -> str:
        """Executes prompt on context and returns string completion."""
        pass

    def analyze_json(self, prompt: str, context: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Executes prompt and returns validated JSON object."""
        system_instruction = (
            "\n\nIMPORTANTE: Responde ÚNICAMENTE con un objeto JSON válido. "
            "No agregues texto explicativo antes ni después del bloque JSON."
        )
        full_prompt = prompt + system_instruction
        raw_response = self.analyze(full_prompt, context)
        return self._clean_and_parse_json(raw_response)

    @staticmethod
    def _clean_and_parse_json(text: str) -> Dict[str, Any]:
        """Strips markdown code blocks (```json ... ```) and parses JSON."""
        clean = text.strip()
        # Remove ```json and ```
        clean = re.sub(r"^```json\s*", "", clean, flags=re.IGNORECASE)
        clean = re.sub(r"^```\s*", "", clean)
        clean = re.sub(r"\s*```$", "", clean)
        clean = clean.strip()

        # Find first { and last } if surrounded by extra commentary
        first_brace = clean.find("{")
        last_brace = clean.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            clean = clean[first_brace:last_brace + 1]

        try:
            return json.loads(clean)
        except json.JSONDecodeError as e:
            # Return fallback structure
            return {
                "error": f"JSONDecodeError: {str(e)}",
                "raw_text": text
            }
