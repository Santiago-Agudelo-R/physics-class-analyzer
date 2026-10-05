"""Ingestion module for Physics Class Analyzer."""
from .matcher import ClassFileMatcher, ClassInputs
from .text_reader import TextReader, TranscriptSegment
from .audio_extractor import AudioExtractor

__all__ = ["ClassFileMatcher", "ClassInputs", "TextReader", "TranscriptSegment", "AudioExtractor"]
