"""
Tests for ingestion, matching, and transcript parsing.
"""

from pathlib import Path
from src.ingestion.matcher import ClassFileMatcher, normalize_stem
from src.ingestion.text_reader import (
    TextReader, TranscriptSegment, parse_timestamp_to_seconds, format_timestamp
)


def test_timestamp_conversions():
    assert parse_timestamp_to_seconds("0:03") == 3.0
    assert parse_timestamp_to_seconds("2:42") == 162.0
    assert parse_timestamp_to_seconds("1:09:18") == 4158.0

    assert format_timestamp(3.0) == "00:03"
    assert format_timestamp(162.0) == "02:42"
    assert format_timestamp(4158.0) == "01:09:18"


def test_normalize_stem():
    assert normalize_stem("Clase 01 - Transcripcion.docx") == "clase_01"
    assert normalize_stem("clase01_video.mp4") == "clase01"


def test_parse_teams_format():
    sample_text = """
DOCENTE 0:03
con respecto a la grabación como las grabaciones pesan tanto
Y.
ESTUDIANTE A 2:42
Profe, en mi caso no me ha llegado.
DOCENTE 2:45
Al correo institucional.
"""
    segments = TextReader.parse_raw_text(sample_text)
    assert len(segments) == 3
    assert segments[0].speaker == "DOCENTE"
    assert segments[0].start == 3.0
    assert segments[0].end == 162.0
    assert "con respecto a la grabación" in segments[0].text
    assert segments[1].speaker == "ESTUDIANTE A"
    assert segments[1].start == 162.0
    assert segments[2].speaker == "DOCENTE"
    assert segments[2].start == 165.0


def test_docx_reading_from_sample():
    sample_docx = Path(__file__).resolve().parent.parent / "data" / "sample" / "sample_lecture.docx"
    if sample_docx.exists():
        raw_text = TextReader.read_raw_text(sample_docx)
        assert "DOCENTE" in raw_text
        assert "fotoel" in raw_text.lower()

        segments = TextReader.parse_to_segments(sample_docx)
        assert len(segments) > 10
        assert segments[0].start >= 0.0


def test_pdf_reading_from_sample():
    sample_pdf = Path(__file__).resolve().parent.parent / "data" / "sample" / "sample_slides.pdf"
    if sample_pdf.exists():
        raw_text = TextReader.read_raw_text(sample_pdf)
        assert "cuántica" in raw_text.lower() or "cuantica" in raw_text.lower()
        assert "fotoeléctrico" in raw_text.lower() or "fotoelectrico" in raw_text.lower()

        segments = TextReader.parse_to_segments(sample_pdf)
        assert len(segments) >= 1
