"""
Cache and resumption manager for Physics Class Analyzer.
Manages stage-by-stage caching (01 to 08) so interrupted executions can resume.
"""

import json
from pathlib import Path
from typing import Any, Optional, Dict


class CacheStages:
    STAGE_01_TRANSCRIPTION = "01_transcription"
    STAGE_02_CLEANED = "02_cleaned"
    STAGE_03_SEGMENTS = "03_segments"
    STAGE_04_SEGMENT_ANALYSIS = "04_segment_analysis"
    STAGE_05_EQUATIONS = "05_equations"
    STAGE_06_PROBLEMS = "06_problems"
    STAGE_07_GLOBAL_SYNTHESIS = "07_global_synthesis"
    STAGE_08_FINAL_DOCUMENT = "08_final_document"

    ALL = [
        STAGE_01_TRANSCRIPTION,
        STAGE_02_CLEANED,
        STAGE_03_SEGMENTS,
        STAGE_04_SEGMENT_ANALYSIS,
        STAGE_05_EQUATIONS,
        STAGE_06_PROBLEMS,
        STAGE_07_GLOBAL_SYNTHESIS,
        STAGE_08_FINAL_DOCUMENT,
    ]


class CacheManager:
    """Handles saving and loading intermediate data across pipeline stages."""

    def __init__(self, cache_dir: Path):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_stage_path(self, stage: str) -> Path:
        return self.cache_dir / f"{stage}.json"

    def has(self, stage: str) -> bool:
        path = self.get_stage_path(stage)
        return path.exists() and path.stat().st_size > 0

    def load(self, stage: str) -> Optional[Any]:
        path = self.get_stage_path(stage)
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def save(self, stage: str, data: Any) -> Path:
        path = self.get_stage_path(stage)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return path

    def clear(self, stage: Optional[str] = None):
        """Clears all or a specific cache stage."""
        if stage:
            path = self.get_stage_path(stage)
            if path.exists():
                path.unlink()
        else:
            for s in CacheStages.ALL:
                p = self.get_stage_path(s)
                if p.exists():
                    p.unlink()

    def get_status(self) -> Dict[str, bool]:
        """Returns the status of each stage in the cache."""
        return {s: self.has(s) for s in CacheStages.ALL}
