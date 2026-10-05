"""
Analyzes individual class segments using the configured LLM Provider.
"""

from typing import List, Dict, Any
from ..segmentation.chunker import ClassChunk
from ..providers.base import LLMProvider
from .prompts import SEGMENT_ANALYSIS_PROMPT


class SegmentAnalyzer:
    """Orchestrates segment-by-segment academic extraction."""

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def analyze_chunk(self, chunk: ClassChunk) -> Dict[str, Any]:
        context = (
            f"--- INFORMACIÓN DEL SEGMENTO ---\n"
            f"Segmento #{chunk.chunk_id} | Intervalo: {chunk.start_str} - {chunk.end_str} "
            f"({chunk.duration_minutes} min)\n\n"
        )
        if chunk.context_prefix:
            context += f"Contexto previo inmediato: {chunk.context_prefix}\n\n"
        context += f"Transcripción del segmento:\n{chunk.text}"

        prompt = f"segment_analysis: Analiza el siguiente segmento #{chunk.chunk_id}.\n{SEGMENT_ANALYSIS_PROMPT}"
        result = self.provider.analyze_json(prompt, context)

        # Attach metadata
        result["chunk_id"] = chunk.chunk_id
        result["interval"] = f"{chunk.start_str} - {chunk.end_str}"
        return result

    def analyze_all(self, chunks: List[ClassChunk]) -> List[Dict[str, Any]]:
        results = []
        for c in chunks:
            res = self.analyze_chunk(c)
            results.append(res)
        return results
