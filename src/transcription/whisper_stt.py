"""
Local speech-to-text transcriber using faster-whisper or openai-whisper.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from ..ingestion.text_reader import TranscriptSegment, format_timestamp


class LocalTranscriber:
    """Performs local speech-to-text transcription with timestamp preservation."""

    def __init__(self, model_size: str = "base", device: str = "cpu", language: str = "es"):
        self.model_size = model_size
        self.device = device
        self.language = language

    def transcribe_audio(self, audio_path: str | Path) -> List[TranscriptSegment]:
        path = Path(audio_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {path}")

        # 1. Try faster-whisper (fastest local CTranslate2 engine)
        try:
            from faster_whisper import WhisperModel
            model = WhisperModel(self.model_size, device=self.device, compute_type="int8")
            segments_gen, _ = model.transcribe(str(path), language=self.language, beam_size=5)
            results = []
            for seg in segments_gen:
                results.append(TranscriptSegment(
                    start=float(seg.start),
                    end=float(seg.end),
                    text=seg.text.strip(),
                    speaker="Profesor",
                    start_str=format_timestamp(seg.start),
                    end_str=format_timestamp(seg.end)
                ))
            return results
        except ImportError:
            pass

        # 2. Try openai-whisper
        try:
            import whisper
            model = whisper.load_model(self.model_size, device=self.device)
            res = model.transcribe(str(path), language=self.language)
            results = []
            for seg in res.get("segments", []):
                results.append(TranscriptSegment(
                    start=float(seg["start"]),
                    end=float(seg["end"]),
                    text=seg["text"].strip(),
                    speaker="Profesor",
                    start_str=format_timestamp(seg["start"]),
                    end_str=format_timestamp(seg["end"])
                ))
            return results
        except ImportError:
            raise RuntimeError(
                "No local speech-to-text engine is installed.\n"
                "To transcribe audio/video directly, please install faster-whisper:\n"
                "  pip install faster-whisper\n"
                "or openai-whisper:\n"
                "  pip install openai-whisper\n"
                "Alternatively, provide an existing .docx, .txt or .pdf transcript file."
            )
