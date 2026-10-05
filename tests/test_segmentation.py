"""
Tests for chunking and window segmentation.
"""

from src.ingestion.text_reader import TranscriptSegment
from src.segmentation.chunker import ClassChunker


def test_chunker_basic():
    # Create 30 segments each lasting 60 seconds (total 30 minutes)
    segments = []
    for i in range(30):
        start = i * 60.0
        end = (i + 1) * 60.0
        segments.append(TranscriptSegment(
            start=start,
            end=end,
            text=f"Explicación del minuto {i} al {i+1} sobre física cuántica.",
            speaker="Profesor"
        ))

    # Target 10 minutes per chunk
    chunker = ClassChunker(target_minutes=10.0, min_minutes=5.0, max_minutes=15.0, overlap_seconds=30.0)
    chunks = chunker.chunk_segments(segments)

    # 30 minutes / 10 = ~3 chunks
    assert len(chunks) == 3
    assert chunks[0].chunk_id == 1
    assert chunks[0].start == 0.0
    assert chunks[0].end >= 600.0
    assert chunks[1].chunk_id == 2
    assert chunks[1].context_prefix != ""  # Has context overlap


def test_chunker_merges_short_tail():
    # 12 minutes total with 10 min target (tail of 2 minutes should be merged if min is 5 min)
    segments = [
        TranscriptSegment(start=0.0, end=600.0, text="Parte 1", speaker="Profesor"),
        TranscriptSegment(start=600.0, end=720.0, text="Parte 2 corta", speaker="Profesor"),
    ]
    chunker = ClassChunker(target_minutes=10.0, min_minutes=5.0)
    chunks = chunker.chunk_segments(segments)

    assert len(chunks) == 1
    assert chunks[0].end == 720.0
    assert "Parte 2 corta" in chunks[0].text
