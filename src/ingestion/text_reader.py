"""
Text reader and transcript parser for DOCX, TXT, and PDF files.
Extracts speakers, timestamps, and spoken segments.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class TranscriptSegment:
    start: float           # Seconds
    end: float             # Seconds
    text: str
    speaker: Optional[str] = None
    start_str: Optional[str] = None
    end_str: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if not self.start_str:
            d["start_str"] = format_timestamp(self.start)
        if not self.end_str:
            d["end_str"] = format_timestamp(self.end)
        return d


def parse_timestamp_to_seconds(ts_str: str) -> float:
    """Converts MM:SS or HH:MM:SS into seconds."""
    parts = ts_str.strip().split(":")
    if len(parts) == 2:
        return float(parts[0]) * 60 + float(parts[1])
    elif len(parts) == 3:
        return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    try:
        return float(ts_str)
    except ValueError:
        return 0.0


def format_timestamp(seconds: float) -> str:
    """Converts seconds into MM:SS or HH:MM:SS."""
    secs = int(round(seconds))
    hrs = secs // 3600
    mins = (secs % 3600) // 60
    rem_secs = secs % 60
    if hrs > 0:
        return f"{hrs:02d}:{mins:02d}:{rem_secs:02d}"
    return f"{mins:02d}:{rem_secs:02d}"


class TextReader:
    """Reads .docx, .txt, and .pdf transcriptions into structured segments."""

    TEAMS_PATTERN = re.compile(
        r"^([A-ZÁÉÍÓÚÑa-záéíóúñ\s\.\,\-]+?)\s+(\d{1,2}:\d{2}(?::\d{2})?)\s*$"
    )
    SRT_TIME_PATTERN = re.compile(
        r"(\d{2}:\d{2}:\d{2}[,\.]\d{1,3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{1,3})"
    )

    @classmethod
    def read_raw_text(cls, file_path: str | Path) -> str:
        path = Path(file_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        ext = path.suffix.lower()
        if ext == ".docx":
            return cls._read_docx(path)
        elif ext == ".pdf":
            return cls._read_pdf(path)
        elif ext in {".txt", ".srt", ".vtt"}:
            return cls._read_txt(path)
        else:
            raise ValueError(f"Unsupported document format: {ext}")

    @classmethod
    def parse_to_segments(cls, file_path: str | Path) -> List[TranscriptSegment]:
        path = Path(file_path).resolve()
        raw_text = cls.read_raw_text(path)
        return cls.parse_raw_text(raw_text)

    @classmethod
    def parse_raw_text(cls, raw_text: str) -> List[TranscriptSegment]:
        lines = [line.strip() for line in raw_text.splitlines()]
        lines = [l for l in lines if l]

        # 1. Try Teams / Moodle transcript format (e.g. "PROFESOR 1:04")
        segments = cls._parse_teams_format(lines)
        if segments:
            return segments

        # 2. Try SRT / VTT format
        segments = cls._parse_srt_format(lines)
        if segments:
            return segments

        # 3. Fallback: split into logical blocks/paragraphs and estimate timestamps
        return cls._parse_plain_text(lines)

    @classmethod
    def _read_docx(cls, path: Path) -> str:
        try:
            import docx
            doc = docx.Document(path)
            paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            return "\n".join(paragraphs)
        except Exception as e:
            raise RuntimeError(f"Error reading docx file {path}: {e}")

    @classmethod
    def _read_pdf(cls, path: Path) -> str:
        text_parts = []
        try:
            from pypdf import PdfReader
            reader = PdfReader(path)
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text_parts.append(t)
            return "\n".join(text_parts)
        except Exception:
            # Fallback to pdfplumber
            try:
                import pdfplumber
                with pdfplumber.open(path) as pdf:
                    for p in pdf.pages:
                        t = p.extract_text()
                        if t:
                            text_parts.append(t)
                return "\n".join(text_parts)
            except Exception as e2:
                raise RuntimeError(f"Error reading pdf file {path}: {e2}")

    @classmethod
    def _read_txt(cls, path: Path) -> str:
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
        for enc in encodings:
            try:
                with open(path, "r", encoding=enc) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    @classmethod
    def _parse_teams_format(cls, lines: List[str]) -> List[TranscriptSegment]:
        segments: List[TranscriptSegment] = []
        current_speaker: Optional[str] = None
        current_start: Optional[float] = None
        current_start_str: Optional[str] = None
        current_text_lines: List[str] = []

        for line in lines:
            m = cls.TEAMS_PATTERN.match(line)
            if m:
                # Flush previous
                if current_start is not None and current_text_lines:
                    text = " ".join(current_text_lines).strip()
                    if text:
                        segments.append(TranscriptSegment(
                            start=current_start,
                            end=current_start + 10.0,  # Will be adjusted by next segment start
                            text=text,
                            speaker=current_speaker,
                            start_str=current_start_str,
                            end_str=None
                        ))
                current_speaker = m.group(1).strip()
                current_start_str = m.group(2).strip()
                current_start = parse_timestamp_to_seconds(current_start_str)
                current_text_lines = []
            else:
                if current_start is not None:
                    current_text_lines.append(line)

        # Flush final
        if current_start is not None and current_text_lines:
            text = " ".join(current_text_lines).strip()
            if text:
                segments.append(TranscriptSegment(
                    start=current_start,
                    end=current_start + 15.0,
                    text=text,
                    speaker=current_speaker,
                    start_str=current_start_str,
                    end_str=format_timestamp(current_start + 15.0)
                ))

        # Adjust segment ends based on consecutive starts
        for i in range(len(segments) - 1):
            next_start = segments[i + 1].start
            if next_start > segments[i].start:
                segments[i].end = next_start
                segments[i].end_str = format_timestamp(next_start)
            else:
                segments[i].end = segments[i].start + 10.0
                segments[i].end_str = format_timestamp(segments[i].end)

        return segments

    @classmethod
    def _parse_srt_format(cls, lines: List[str]) -> List[TranscriptSegment]:
        segments: List[TranscriptSegment] = []
        i = 0
        while i < len(lines):
            line = lines[i]
            m = cls.SRT_TIME_PATTERN.search(line)
            if m:
                start_raw = m.group(1).replace(",", ".")
                end_raw = m.group(2).replace(",", ".")
                start_s = parse_timestamp_to_seconds(start_raw)
                end_s = parse_timestamp_to_seconds(end_raw)
                i += 1
                text_accum = []
                while i < len(lines) and not cls.SRT_TIME_PATTERN.search(lines[i]) and not lines[i].isdigit():
                    text_accum.append(lines[i])
                    i += 1
                text = " ".join(text_accum).strip()
                if text:
                    segments.append(TranscriptSegment(
                        start=start_s,
                        end=end_s,
                        text=text,
                        speaker=None,
                        start_str=format_timestamp(start_s),
                        end_str=format_timestamp(end_s)
                    ))
            else:
                i += 1
        return segments

    @classmethod
    def _parse_plain_text(cls, lines: List[str]) -> List[TranscriptSegment]:
        # Group every ~3-5 sentences or paragraphs into a segment
        segments: List[TranscriptSegment] = []
        current_lines: List[str] = []
        current_time = 0.0

        for line in lines:
            current_lines.append(line)
            # Roughly every 500 characters or 3 paragraphs
            if sum(len(l) for l in current_lines) >= 450:
                text = " ".join(current_lines).strip()
                duration = max(10.0, len(text.split()) * 0.4)  # ~150 words/min
                segments.append(TranscriptSegment(
                    start=current_time,
                    end=current_time + duration,
                    text=text,
                    speaker=None,
                    start_str=format_timestamp(current_time),
                    end_str=format_timestamp(current_time + duration)
                ))
                current_time += duration
                current_lines = []

        if current_lines:
            text = " ".join(current_lines).strip()
            duration = max(10.0, len(text.split()) * 0.4)
            segments.append(TranscriptSegment(
                start=current_time,
                end=current_time + duration,
                text=text,
                speaker=None,
                start_str=format_timestamp(current_time),
                end_str=format_timestamp(current_time + duration)
            ))

        return segments
