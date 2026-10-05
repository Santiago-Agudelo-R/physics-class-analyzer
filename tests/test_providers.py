"""
Tests for LLM Providers and schema parsing.
"""

from src.providers.base import LLMProvider
from src.providers.offline_mock import OfflineMockProvider


def test_clean_and_parse_json():
    raw_markdown = """
    Aquí está el resultado:
    ```json
    {
      "topic": "Efecto Fotoeléctrico",
      "valid": true
    }
    ```
    Espero te sirva.
    """
    parsed = LLMProvider._clean_and_parse_json(raw_markdown)
    assert parsed["topic"] == "Efecto Fotoeléctrico"
    assert parsed["valid"] is True


def test_offline_mock_provider():
    provider = OfflineMockProvider()
    context = (
        "[12:15] Andrés Arias: El efecto fotoeléctrico explica que K_max = hf - W. "
        "Dos haces con longitudes de onda de 80 nm y 110 nm con energías cinéticas de 11.39 eV y 7.154 eV. "
        "Estimamos la constante de Planck."
    )
    result = provider.analyze_json("segment_analysis: analiza este segmento", context)
    assert "topics" in result
    assert "equations" in result
    assert "problems" in result
    assert len(result["equations"]) >= 1
    assert len(result["problems"]) >= 1
    assert "LaTeX" in str(result) or "latex" in str(result)
