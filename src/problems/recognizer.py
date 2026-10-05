"""
Problem recognizer and generalization framework for Modern Physics exercises.
Extracts reusable methods, identifying patterns, step-by-step algorithms, and common pitfalls.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class ProblemItem:
    title: str
    type: str
    how_to_recognize: str
    given_data: str
    target: str
    concepts_to_remember: str
    equations_used: str
    general_procedure: List[str]
    common_pitfalls: List[str]
    timestamp: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ProblemRecognizer:
    """Consolidates and enriches problems identified across segment analyses into universal problem-solving templates."""

    @staticmethod
    def consolidate(segment_analyses: List[Dict[str, Any]]) -> List[ProblemItem]:
        seen_titles = set()
        items: List[ProblemItem] = []

        for seg in segment_analyses:
            problems = seg.get("problems", [])
            for p in problems:
                title = p.get("title", "").strip()
                if not title or title.lower() in seen_titles:
                    continue
                seen_titles.add(title.lower())

                ptype = p.get("type", "Problema de Física Moderna")
                given = p.get("given_data", "Datos del enunciado")
                target = p.get("target", "Incógnita física")
                phenomenon = p.get("physical_phenomenon", "Fenómeno cuántico o relativista")
                eqs = p.get("equations_used", "")
                procedure = p.get("step_by_step_method", [])
                if isinstance(procedure, str):
                    procedure = [procedure]
                pitfalls = p.get("common_pitfalls", [])
                if isinstance(pitfalls, str):
                    pitfalls = [pitfalls]

                how_to_recognize = (
                    f"Identifica palabras clave sobre {ptype.lower()} donde se involucre {phenomenon.lower()}."
                )

                item = ProblemItem(
                    title=title,
                    type=ptype,
                    how_to_recognize=how_to_recognize,
                    given_data=given,
                    target=target,
                    concepts_to_remember=phenomenon,
                    equations_used=eqs,
                    general_procedure=procedure,
                    common_pitfalls=pitfalls,
                    timestamp=p.get("timestamp") or seg.get("interval", "").split("-")[0].strip()
                )
                items.append(item)

        return items
