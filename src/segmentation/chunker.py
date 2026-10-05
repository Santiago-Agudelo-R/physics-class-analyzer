"""
Intelligent class segmenter.
Splits long transcripts into manageable 5-15 minute contextual chunks.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from ..ingestion.text_reader import TranscriptSegment, format_timestamp


@dataclass
class ClassChunk:
    chunk_id: int
    start: float
    end: float
    start_str: str
    end_str: str
    duration_minutes: float
    text: str
    raw_segments_count: int
    context_prefix: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ClassChunker:
    """Chunks transcript segments into coherent 5-15 minute blocks with context overlap."""

    def __init__(
        self,
        target_minutes: float = 10.0,
        min_minutes: float = 5.0,
        max_minutes: float = 15.0,
        overlap_seconds: float = 30.0
    ):
        self.target_seconds = target_minutes * 60.0
        self.min_seconds = min_minutes * 60.0
        self.max_seconds = max_minutes * 60.0
        self.overlap_seconds = overlap_seconds

    def chunk_segments(self, segments: List[TranscriptSegment | Dict[str, Any]]) -> List[ClassChunk]:
        if not segments:
            return []

        # Normalize to list of dicts
        norm_segs = []
        for s in segments:
            if isinstance(s, dict):
                norm_segs.append(s)
            else:
                norm_segs.append(s.to_dict())

        chunks: List[ClassChunk] = []
        current_chunk_segs: List[Dict[str, Any]] = []
        chunk_id = 1
        previous_trailing_text = ""

        for seg in norm_segs:
            current_chunk_segs.append(seg)
            chunk_start = current_chunk_segs[0]["start"]
            chunk_end = seg["end"]
            duration = chunk_end - chunk_start

            # Check if we should close this chunk
            if duration >= self.target_seconds:
                chunk = self._build_chunk(chunk_id, current_chunk_segs, previous_trailing_text)
                chunks.append(chunk)
                chunk_id += 1

                # Gather overlap text for next chunk
                previous_trailing_text = self._extract_trailing_context(current_chunk_segs, self.overlap_seconds)
                current_chunk_segs = []

        # Remaining tail segment
        if current_chunk_segs:
            # If the last chunk is very small and we already have a previous chunk, we can merge or keep it
            chunk_start = current_chunk_segs[0]["start"]
            chunk_end = current_chunk_segs[-1]["end"]
            duration = chunk_end - chunk_start

            if chunks and duration < self.min_seconds:
                # Merge into the last chunk
                last_chunk = chunks[-1]
                merged_text = last_chunk.text + "\n" + self._format_segments_text(current_chunk_segs)
                chunks[-1] = ClassChunk(
                    chunk_id=last_chunk.chunk_id,
                    start=last_chunk.start,
                    end=chunk_end,
                    start_str=last_chunk.start_str,
                    end_str=format_timestamp(chunk_end),
                    duration_minutes=round((chunk_end - last_chunk.start) / 60.0, 2),
                    text=merged_text,
                    raw_segments_count=last_chunk.raw_segments_count + len(current_chunk_segs),
                    context_prefix=last_chunk.context_prefix
                )
            else:
                chunk = self._build_chunk(chunk_id, current_chunk_segs, previous_trailing_text)
                chunks.append(chunk)

        return chunks

    def _build_chunk(self, chunk_id: int, segs: List[Dict[str, Any]], context_prefix: str) -> ClassChunk:
        start = segs[0]["start"]
        end = segs[-1]["end"]
        duration_minutes = round((end - start) / 60.0, 2)
        text = self._format_segments_text(segs)

        return ClassChunk(
            chunk_id=chunk_id,
            start=start,
            end=end,
            start_str=format_timestamp(start),
            end_str=format_timestamp(end),
            duration_minutes=duration_minutes,
            text=text,
            raw_segments_count=len(segs),
            context_prefix=context_prefix
        )

    def _format_segments_text(self, segs: List[Dict[str, Any]]) -> str:
        lines = []
        for s in segs:
            speaker = s.get("speaker")
            time_str = s.get("start_str") or format_timestamp(s["start"])
            text = s.get("text", "").strip()
            if speaker:
                lines.append(f"[{time_str}] {speaker}: {text}")
            else:
                lines.append(f"[{time_str}] {text}")
        return "\n".join(lines)

    def _extract_trailing_context(self, segs: List[Dict[str, Any]], seconds: float) -> str:
        if not segs:
            return ""
        last_time = segs[-1]["end"]
        threshold = last_time - seconds
        tail = [s.get("text", "") for s in segs if s.get("end", 0) >= threshold]
        return " ... ".join(tail).strip()
