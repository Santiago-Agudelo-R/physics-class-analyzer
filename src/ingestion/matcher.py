"""
File matcher for associating video, audio and transcript companion files.
Supports single-file matching and multi-class batch discovery in folders.
"""

import os
import re
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".webm"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}
TEXT_EXTENSIONS = {".docx", ".txt", ".pdf"}


def normalize_stem(name: str) -> str:
    """Normalize file stem for robust fuzzy matching."""
    s = Path(name).stem.lower()
    s = re.sub(r"[\s\-_.]+", "_", s)
    s = re.sub(r"_(transcripcion|transcription|grabacion|grabaci_n|audio|video|meeting)", "", s)
    return s.strip("_")


def extract_session_key(filename: str) -> str:
    """Extracts session tag like 'Sesión 02', 'Sesión 03', 'Clase 01'."""
    m = re.search(r"(sesi[oó]n\s*\d+|clase\s*\d+|lecture\s*\d+)", filename, re.IGNORECASE)
    if m:
        # Standardize formatting, e.g. 'Sesión 02'
        val = m.group(1).strip()
        num_m = re.search(r"\d+", val)
        if num_m:
            num = int(num_m.group(0))
            if "sesi" in val.lower():
                return f"Sesión {num:02d}"
            elif "clase" in val.lower():
                return f"Clase {num:02d}"
        return val
    return normalize_stem(filename)


@dataclass
class ClassInputs:
    class_id: str
    video_path: Optional[Path] = None
    audio_path: Optional[Path] = None
    text_path: Optional[Path] = None

    @property
    def has_text(self) -> bool:
        return self.text_path is not None and self.text_path.exists()

    @property
    def has_media(self) -> bool:
        return (self.video_path is not None and self.video_path.exists()) or \
               (self.audio_path is not None and self.audio_path.exists())


class ClassFileMatcher:
    """Matches class companion files based on naming patterns."""

    @classmethod
    def match(cls, input_path: str | Path) -> ClassInputs:
        """Returns the primary or first matching ClassInputs for the given path."""
        all_matches = cls.match_all(input_path)
        if not all_matches:
            raise FileNotFoundError(f"No valid media or text files found in: {input_path}")
        return all_matches[0]

    @classmethod
    def match_all(cls, input_path: str | Path) -> List[ClassInputs]:
        """Discovers and pairs all distinct classes found at the target path."""
        path = Path(input_path).resolve()

        if not path.exists():
            raise FileNotFoundError(f"Input path does not exist: {path}")

        if path.is_file():
            ext = path.suffix.lower()
            stem = normalize_stem(path.name)
            folder = path.parent
            siblings = list(folder.iterdir())

            video = None
            audio = None
            text = None

            if ext in VIDEO_EXTENSIONS:
                video = path
            elif ext in AUDIO_EXTENSIONS:
                audio = path
            elif ext in TEXT_EXTENSIONS:
                text = path

            # Find matching companion in same folder
            session_key = extract_session_key(path.name)
            for s in siblings:
                if s == path or not s.is_file():
                    continue
                s_ext = s.suffix.lower()
                s_key = extract_session_key(s.name)

                if s_key == session_key or normalize_stem(s.name) == stem:
                    if not video and s_ext in VIDEO_EXTENSIONS:
                        video = s
                    elif not audio and s_ext in AUDIO_EXTENSIONS:
                        audio = s
                    elif not text and s_ext in TEXT_EXTENSIONS:
                        text = s

            return [ClassInputs(
                class_id=session_key if session_key else path.stem,
                video_path=video,
                audio_path=audio,
                text_path=text
            )]

        elif path.is_dir():
            files = [f for f in path.iterdir() if f.is_file()]
            groups: Dict[str, Dict[str, Optional[Path]]] = {}

            for f in files:
                ext = f.suffix.lower()
                if ext not in VIDEO_EXTENSIONS and ext not in AUDIO_EXTENSIONS and ext not in TEXT_EXTENSIONS:
                    continue

                key = extract_session_key(f.name)
                if key not in groups:
                    groups[key] = {"video": None, "audio": None, "text": None}

                if ext in VIDEO_EXTENSIONS:
                    groups[key]["video"] = f
                elif ext in AUDIO_EXTENSIONS:
                    groups[key]["audio"] = f
                elif ext in TEXT_EXTENSIONS:
                    # Prefer docx or pdf
                    if not groups[key]["text"] or ext == ".docx":
                        groups[key]["text"] = f

            results = []
            for key in sorted(groups.keys()):
                info = groups[key]
                if info["video"] or info["audio"] or info["text"]:
                    results.append(ClassInputs(
                        class_id=key,
                        video_path=info["video"],
                        audio_path=info["audio"],
                        text_path=info["text"]
                    ))

            return results

        raise ValueError(f"Invalid path type: {path}")
