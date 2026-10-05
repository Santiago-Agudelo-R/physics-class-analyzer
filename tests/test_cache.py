"""
Tests for CacheManager and stage resumption.
"""

import tempfile
from pathlib import Path
from src.cache import CacheManager, CacheStages


def test_cache_lifecycle():
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = CacheManager(Path(tmpdir))

        # Initially empty
        assert not cache.has(CacheStages.STAGE_01_TRANSCRIPTION)
        assert cache.load(CacheStages.STAGE_01_TRANSCRIPTION) is None

        # Save stage 1
        data1 = [{"start": 0.0, "end": 10.0, "text": "Hola física"}]
        saved_path = cache.save(CacheStages.STAGE_01_TRANSCRIPTION, data1)
        assert saved_path.exists()
        assert cache.has(CacheStages.STAGE_01_TRANSCRIPTION)

        loaded = cache.load(CacheStages.STAGE_01_TRANSCRIPTION)
        assert loaded == data1

        # Clear stage 1
        cache.clear(CacheStages.STAGE_01_TRANSCRIPTION)
        assert not cache.has(CacheStages.STAGE_01_TRANSCRIPTION)
