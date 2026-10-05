"""
Audio extractor for video files using local imageio-ffmpeg or system ffmpeg.
Extracts 16kHz mono PCM WAV for high-accuracy local Whisper speech-to-text.
"""

import subprocess
import os
from pathlib import Path
from typing import Optional


class AudioExtractor:
    """Extracts audio track from video files."""

    @staticmethod
    def get_ffmpeg_binary() -> Optional[str]:
        # 1. Try imageio_ffmpeg
        try:
            import imageio_ffmpeg
            return imageio_ffmpeg.get_ffmpeg_exe()
        except ImportError:
            pass

        # 2. Try system PATH
        import shutil
        sys_ffmpeg = shutil.which("ffmpeg")
        if sys_ffmpeg:
            return sys_ffmpeg

        return None

    @classmethod
    def extract_audio(cls, video_path: str | Path, output_wav_path: Optional[str | Path] = None) -> Path:
        vpath = Path(video_path).resolve()
        if not vpath.exists():
            raise FileNotFoundError(f"Video file not found: {vpath}")

        if output_wav_path:
            out_path = Path(output_wav_path).resolve()
        else:
            out_path = vpath.with_suffix(".wav")

        out_path.parent.mkdir(parents=True, exist_ok=True)

        ffmpeg_bin = cls.get_ffmpeg_binary()
        if not ffmpeg_bin:
            raise RuntimeError(
                "No FFmpeg binary available. Please install imageio-ffmpeg (`pip install imageio-ffmpeg`) "
                "or install ffmpeg in system PATH."
            )

        cmd = [
            ffmpeg_bin,
            "-y",  # Overwrite output
            "-i", str(vpath),
            "-vn",  # Disable video
            "-acodec", "pcm_s16le",
            "-ar", "16000",  # 16kHz required by Whisper
            "-ac", "1",      # Mono channel
            str(out_path)
        ]

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg audio extraction failed:\n{result.stderr}")

        if not out_path.exists() or out_path.stat().st_size == 0:
            raise RuntimeError(f"Extracted audio file is empty or missing: {out_path}")

        return out_path
