"""
Global class synthesizer.
Unifies multi-segment analyses into a coherent university study curriculum.
"""

import json
from typing import List, Dict, Any
from ..providers.base import LLMProvider
from ..analysis.prompts import GLOBAL_SYNTHESIS_PROMPT


class GlobalSynthesizer:
    """Performs the second-pass global AI synthesis across all analyzed segments."""

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def synthesize(
        self,
        class_id: str,
        segment_analyses: List[Dict[str, Any]],
        consolidated_equations: List[Dict[str, Any]],
        consolidated_problems: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        # Build synthesis context summarizing all segments
        summarized_segments = []
        for s in segment_analyses:
            summarized_segments.append({
                "chunk_id": s.get("chunk_id"),
                "interval": s.get("interval"),
                "topics": s.get("topics", []),
                "subtopics": s.get("subtopics", []),
                "theory": s.get("theory", ""),
                "key_concepts": [c.get("concept") for c in s.get("concepts", [])],
                "equations_found": [e.get("name") for e in s.get("equations", [])],
                "problems_found": [p.get("title") for p in s.get("problems", [])],
                "teacher_warnings": s.get("teacher_warnings", []),
                "common_errors": s.get("common_errors", [])
            })

        context = (
            f"CLASE ID: {class_id}\n\n"
            f"RESUMEN ESTRUCTURADO DE SEGMENTOS:\n"
            f"{json.dumps(summarized_segments, ensure_ascii=False, indent=2)}\n\n"
            f"ECUACIONES RELEVANTES EXTRAÍDAS:\n"
            f"{json.dumps(consolidated_equations, ensure_ascii=False, indent=2)}\n\n"
            f"PROBLEMAS IDENTIFICADOS:\n"
            f"{json.dumps(consolidated_problems, ensure_ascii=False, indent=2)}"
        )

        prompt = f"sintesis: Realiza la síntesis global de la clase '{class_id}'.\n{GLOBAL_SYNTHESIS_PROMPT}"
        result = self.provider.analyze_json(prompt, context)

        # Attach class identifier
        result["class_id"] = class_id
        return result
