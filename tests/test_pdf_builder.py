"""
Regression tests for the PDF study guide builder.

ReportLab parses Paragraph text as markup, so physics notation such as "0<x<L" used to raise
ValueError and abort the PDF. All LLM-provided text is now escaped before rendering.
"""

from pathlib import Path

from pypdf import PdfReader

from src.documents.pdf_builder import PdfStudyGuideBuilder
from src.visualization.math_renderer import MathRenderer


def test_clean_text_escapes_markup_but_keeps_generated_subscripts():
    cleaned = MathRenderer.clean_text_for_pdf("Si 0<x<L & E_0 > 0")
    assert "&lt;" in cleaned and "&gt;" in cleaned and "&amp;" in cleaned
    assert "<sub>0</sub>" in cleaned


def test_pdf_builds_with_inequalities_and_broken_markup(tmp_path: Path):
    hostile = "Confinada en 0<x<L, A<B y C>D, <b>sin cerrar & más"
    synthesis = {
        "title": "Pozo infinito: 0<x<L",
        "executive_summary": hostile,
        "core_concepts": [{"title": "x<y", "importance": "IMPRESCINDIBLE", "explanation": hostile}],
        "study_tips": [hostile],
        "quick_review_5min": [hostile],
    }
    equations = [{
        "name": "Energía <n>",
        "latex": "",  # forces the text fallback path
        "variables": hostile,
        "when_to_use": "cuando 0<x<L",
        "units": "J <SI>",
        "timestamp": "12:00<",
    }]
    problems = [{
        "title": "Problema <1>",
        "given_data": hostile,
        "target": "E<sub>n</sub> roto <",
        "general_procedure": [hostile],
        "equations_used": "E < V",
        "common_pitfalls": [hostile],
    }]

    out = PdfStudyGuideBuilder.build(
        class_name="Clase <04>",
        synthesis=synthesis,
        equations=equations,
        problems=problems,
        output_path=tmp_path / "guia.pdf",
    )

    text = "".join(page.extract_text() or "" for page in PdfReader(str(out)).pages)
    assert "0<x<L" in text
