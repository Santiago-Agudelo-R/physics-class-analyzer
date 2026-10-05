"""
Physics Class Analyzer - CLI Entrypoint.
Converts Modern Physics university classes into high-quality study guides.
Supports single-file analysis and automatic multi-class batch processing from folders.
"""

import sys
import os
import argparse
from pathlib import Path

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config
from src.ingestion.matcher import ClassFileMatcher, ClassInputs
from src.providers.base import LLMProvider
from src.providers.openai_provider import OpenAIProvider
from src.providers.ollama_provider import OllamaProvider
from src.providers.offline_mock import OfflineMockProvider
from src.pipeline import Pipeline


def get_llm_provider(provider_name: str, config) -> LLMProvider:
    name = provider_name.lower().strip()
    if name == "openai":
        return OpenAIProvider(
            api_key=config.openai_api_key,
            base_url=config.openai_base_url,
            model=config.llm_model,
            temperature=config.llm_temperature,
            timeout=config.llm_timeout
        )
    elif name == "ollama":
        return OllamaProvider(
            host=config.ollama_host,
            model=config.llm_model,
            temperature=config.llm_temperature,
            timeout=config.llm_timeout
        )
    elif name == "mock":
        return OfflineMockProvider()
    else:
        raise ValueError(
            f"Proveedor desconocido: '{provider_name}'. Opciones disponibles: 'mock', 'ollama', 'openai'."
        )


def main():
    parser = argparse.ArgumentParser(
        description="Physics Class Analyzer — Transforma clases de Física Moderna en guías de estudio de élite."
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Ruta al archivo (.mp4, .docx, .txt, .pdf) o carpeta que contiene las clases."
    )
    parser.add_argument(
        "--resume", "-r",
        type=str,
        help="Reanudar el procesamiento de una clase existente desde su carpeta o ID."
    )
    parser.add_argument(
        "--export", "-e",
        type=str,
        help="Re-exportar documentos finales (DOCX, PDF, HTML) a partir de los datos en cache."
    )
    parser.add_argument(
        "--provider", "-p",
        type=str,
        choices=["mock", "ollama", "openai"],
        help="Proveedor LLM a utilizar (por defecto: mock o configurado en config.yaml/.env)."
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        help="Nombre del modelo LLM (ej: 'llama3.2', 'gpt-4o-mini', 'mistral')."
    )
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Ruta a un archivo config.yaml personalizado."
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Ignorar cache previo y procesar desde cero."
    )

    args = parser.parse_args()

    target_path_str = args.input or args.resume or args.export
    if not target_path_str:
        parser.print_help()
        print("\n❌ Error: Debes especificar al menos --input, --resume o --export.")
        sys.exit(1)

    target_path = Path(target_path_str).resolve()
    if not target_path.exists():
        print(f"❌ Error: La ruta especificada no existe: {target_path}")
        sys.exit(1)

    # Load configuration
    overrides = {}
    if args.provider:
        overrides.setdefault("llm", {})["provider"] = args.provider
    if args.model:
        overrides.setdefault("llm", {})["model"] = args.model

    config = load_config(args.config, overrides=overrides)

    # Match single or multiple classes
    if args.resume or args.export:
        if (target_path / "cache").exists() or target_path.parent.name == "output":
            class_id = target_path.name
            classes_to_process = [ClassInputs(class_id=class_id)]
        else:
            classes_to_process = ClassFileMatcher.match_all(target_path)
    else:
        classes_to_process = ClassFileMatcher.match_all(target_path)

    if not classes_to_process:
        print(f"❌ Error: No se encontraron clases para procesar en: {target_path}")
        sys.exit(1)

    print(f"\n=======================================================")
    print(f"📦 SESIONES DETECTADAS EN '{target_path.name}': {len(classes_to_process)}")
    for idx, c in enumerate(classes_to_process, 1):
        txt_info = c.text_path.name if c.text_path else "Sin transcripción"
        vid_info = c.video_path.name if c.video_path else "Sin video"
        print(f"   [{idx}] {c.class_id}  -->  Texto: {txt_info} | Video: {vid_info}")
    print(f"=======================================================")

    provider = get_llm_provider(config.llm_provider, config)
    pipeline = Pipeline(config, provider)

    for idx, class_inputs in enumerate(classes_to_process, 1):
        if len(classes_to_process) > 1:
            print(f"\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            print(f"▶️  PROCESANDO LOTE [{idx}/{len(classes_to_process)}]: {class_inputs.class_id}")
            print(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        pipeline.run(
            class_inputs=class_inputs,
            resume=not args.no_cache,
            export_only=bool(args.export)
        )

    print("\n🎉 ¡TODAS LAS CLASES FUERON PROCESADAS CON ÉXITO! 🎉")


if __name__ == "__main__":
    main()
