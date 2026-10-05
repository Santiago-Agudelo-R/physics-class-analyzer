"""
Ollama local LLM Provider.
Runs local models (e.g. llama3.2, mistral, qwen2.5, deepseek-r1) via Ollama HTTP API.
"""

from typing import Optional, Dict, Any
import requests
from .base import LLMProvider


class OllamaProvider(LLMProvider):
    """LLM Provider using local Ollama instance."""

    def __init__(
        self,
        host: str = "http://localhost:11434",
        model: str = "llama3.2",
        temperature: float = 0.1,
        timeout: int = 180
    ):
        self.host = host.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.timeout = timeout

    def analyze(self, prompt: str, context: str) -> str:
        url = f"{self.host}/api/generate"
        system_instruction = (
            "Eres un asistente académico universitario de élite especializado en Física Moderna. "
            "Analiza las clases con rigor científico, extrayendo ecuaciones en LaTeX, metodología de resolución "
            "de problemas, y sin inventar jamás información inexistente en el texto provisto."
        )

        full_prompt = (
            f"<system>{system_instruction}</system>\n\n"
            f"<prompt>{prompt}</prompt>\n\n"
            f"=== CONTENIDO DE LA CLASE ===\n{context}"
        )

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature
            }
        }

        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"No se pudo conectar con Ollama en '{self.host}'. "
                "Asegúrate de que Ollama esté ejecutándose (`ollama serve`)."
            )
        except Exception as e:
            raise RuntimeError(f"Error calling Ollama model '{self.model}': {e}")
