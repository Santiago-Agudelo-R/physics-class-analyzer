"""
Equation consolidation, LaTeX normalization, and anti-hallucination verification.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import re


@dataclass
class EquationItem:
    name: str
    latex: str
    variables: str
    units: str
    when_to_use: str
    conditions: str
    confidence: str = "HIGH"  # HIGH or LOW
    review_warning: Optional[str] = None
    timestamp: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EquationConsolidator:
    """Consolidates and audits equations from segment analyses."""

    @staticmethod
    def consolidate(segment_analyses: List[Dict[str, Any]]) -> List[EquationItem]:
        seen_keys = set()
        consolidated: List[EquationItem] = []

        for seg in segment_analyses:
            eqs = seg.get("equations", [])
            for eq in eqs:
                name = eq.get("name", "").strip()
                latex = eq.get("latex", "").strip()
                if not latex and not name:
                    continue

                # Deduplication key based on normalized latex or name
                norm_latex = re.sub(r"\s+", "", latex)
                key = norm_latex if len(norm_latex) > 4 else name.lower()

                if key in seen_keys:
                    continue
                seen_keys.add(key)

                # Validate confidence
                confidence = eq.get("confidence", "HIGH").upper()
                review_warning = eq.get("review_warning")

                # If transcription or formula seems dubious (e.g. contains placeholders like *** or ??)
                if "***" in latex or "???" in latex or "desconocid" in latex.lower():
                    confidence = "LOW"
                    review_warning = "⚠️ REVISAR: La ecuación/transcripción no pudo determinarse con suficiente confianza."

                item = EquationItem(
                    name=name or "Ecuación Fundamental",
                    latex=latex,
                    variables=eq.get("variables", "Variables no especificadas"),
                    units=eq.get("units", "SI"),
                    when_to_use=eq.get("when_to_use", "Aplicable según condiciones físicas"),
                    conditions=eq.get("conditions", "Condiciones estándar"),
                    confidence=confidence,
                    review_warning=review_warning,
                    timestamp=eq.get("timestamp") or seg.get("interval", "").split("-")[0].strip()
                )
                consolidated.append(item)

        return consolidated
