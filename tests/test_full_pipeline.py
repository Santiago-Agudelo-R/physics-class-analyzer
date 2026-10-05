"""
Full pipeline integration test on sample Modern Physics lecture.
"""

from pathlib import Path
from src.config import load_config
from src.ingestion.matcher import ClassInputs
from src.providers.offline_mock import OfflineMockProvider
from src.pipeline import Pipeline


def test_full_pipeline_run():
    sample_docx = Path(__file__).resolve().parent.parent / "data" / "sample" / "sample_lecture.docx"
    assert sample_docx.exists(), "Sample sample_lecture.docx must be in data/sample/"

    config = load_config()
    provider = OfflineMockProvider()
    pipeline = Pipeline(config, provider)

    class_inputs = ClassInputs(
        class_id="Sesion_02_Test",
        text_path=sample_docx
    )

    # Run pipeline with clean cache
    generated = pipeline.run(class_inputs, resume=False)

    # Assert outputs
    assert "docx" in generated
    assert generated["docx"].exists()
    assert generated["docx"].stat().st_size > 5000  # Non-empty docx

    assert "pdf" in generated
    assert generated["pdf"].exists()
    assert generated["pdf"].stat().st_size > 1000

    assert "mindmap_html" in generated
    assert generated["mindmap_html"].exists()
    html_content = generated["mindmap_html"].read_text(encoding="utf-8")
    assert "mermaid" in html_content.lower()
    assert "Efecto Fotoeléctrico" in html_content

    assert "transcripcion_json" in generated
    assert "analisis_json" in generated
    assert "ecuaciones_json" in generated
    assert "problemas_json" in generated
    assert "sintesis_json" in generated

    # Second run with resume=True should be fast and succeed
    generated_resume = pipeline.run(class_inputs, resume=True)
    assert generated_resume["docx"].exists()
