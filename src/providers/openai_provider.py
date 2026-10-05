"""
OpenAI-compatible LLM Provider.
Supports OpenAI, OpenRouter, Groq, DeepSeek, LocalAI, vLLM.
"""

from typing import Optional, Dict, Any
from .base import LLMProvider


class OpenAIProvider(LLMProvider):
    """LLM Provider using the OpenAI API or compatible endpoints."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.1,
        timeout: int = 120
    ):
        import os
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key missing. Please set OPENAI_API_KEY in your .env file or environment."
            )
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = model
        self.temperature = temperature
        self.timeout = timeout

        from openai import OpenAI
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=self.timeout)

    def analyze(self, prompt: str, context: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "Eres un asistente académico de élite especializado en Física Moderna universitaria. "
                    "Tu misión es analizar clases universitarias, estructurar la teoría, extraer ecuaciones exactas "
                    "en LaTeX, identificar problemas y métodos de resolución, sin inventar información jamás."
                )
            },
            {
                "role": "user",
                "content": f"{prompt}\n\n=== CONTENIDO DE LA CLASE / SEGMENTO ===\n{context}"
            }
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
        )
        return response.choices[0].message.content or ""
