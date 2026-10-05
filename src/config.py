"""
Configuration manager for Physics Class Analyzer.
Loads YAML configuration, handles .env overrides and CLI arguments.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"


class AppConfig:
    def __init__(self, config_dict: Dict[str, Any]):
        self._raw = config_dict

    @property
    def app_name(self) -> str:
        return self._raw.get("app", {}).get("name", "Physics Class Analyzer")

    @property
    def language(self) -> str:
        return self._raw.get("app", {}).get("language", "es")

    @property
    def output_dir(self) -> Path:
        return Path(self._raw.get("paths", {}).get("output_dir", "./output")).resolve()

    @property
    def cache_dir_name(self) -> str:
        return self._raw.get("paths", {}).get("cache_dir_name", "cache")

    @property
    def segmentation(self) -> Dict[str, Any]:
        return self._raw.get("segmentation", {
            "target_duration_minutes": 10,
            "min_duration_minutes": 5,
            "max_duration_minutes": 15,
            "overlap_seconds": 30
        })

    @property
    def llm_provider(self) -> str:
        # Check env first
        env_prov = os.getenv("LLM_PROVIDER")
        if env_prov:
            return env_prov.lower()
        return self._raw.get("llm", {}).get("provider", "mock").lower()

    @property
    def llm_model(self) -> str:
        provider = self.llm_provider
        if provider == "openai":
            return os.getenv("OPENAI_MODEL", self._raw.get("llm", {}).get("openai", {}).get("model", "gpt-4o-mini"))
        elif provider == "ollama":
            return os.getenv("OLLAMA_MODEL", self._raw.get("llm", {}).get("model", "llama3.2"))
        return self._raw.get("llm", {}).get("model", "mock")

    @property
    def llm_temperature(self) -> float:
        return float(self._raw.get("llm", {}).get("temperature", 0.1))

    @property
    def llm_timeout(self) -> int:
        return int(self._raw.get("llm", {}).get("timeout", 120))

    @property
    def ollama_host(self) -> str:
        return os.getenv("OLLAMA_HOST", self._raw.get("llm", {}).get("ollama", {}).get("host", "http://localhost:11434"))

    @property
    def openai_base_url(self) -> str:
        return os.getenv("OPENAI_BASE_URL", self._raw.get("llm", {}).get("openai", {}).get("base_url", "https://api.openai.com/v1"))

    @property
    def openai_api_key(self) -> Optional[str]:
        return os.getenv("OPENAI_API_KEY")

    @property
    def transcription(self) -> Dict[str, Any]:
        return self._raw.get("transcription", {
            "whisper_model": "base",
            "device": "cpu",
            "language": "es"
        })

    @property
    def documents(self) -> Dict[str, bool]:
        return self._raw.get("documents", {
            "generate_docx": True,
            "generate_pdf": True,
            "generate_mindmap": True,
            "export_json": True
        })


def load_config(config_file: Optional[Path] = None, overrides: Optional[Dict[str, Any]] = None) -> AppConfig:
    """Load configuration from YAML file and apply optional overrides."""
    path = Path(config_file) if config_file else DEFAULT_CONFIG_PATH
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {}

    if overrides:
        # Merge shallow/deep overrides
        for k, v in overrides.items():
            if isinstance(v, dict) and k in data and isinstance(data[k], dict):
                data[k].update(v)
            else:
                data[k] = v

    return AppConfig(data)
