# Physics Class Analyzer

Multimodal Python processing pipeline for transcribing, segmenting, extracting mathematical formulations, and generating structured study guides from university-level modern physics lectures.

[![Tests](https://github.com/Titaaron/physics-class-analyzer/actions/workflows/tests.yml/badge.svg)](https://github.com/Titaaron/physics-class-analyzer/actions)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

University physics lectures contain complex mathematical derivations, spoken explanations, and board exercises that are difficult to consolidate manually. `Physics Class Analyzer` is an automated processing engine that ingests lecture recordings (video/audio) or transcripts (DOCX/PDF/TXT) and produces publication-quality study guides with:

- Chronological lecture segmentation and topic boundary detection.
- Mathematical equation parsing and extraction formatted in LaTeX.
- Exercise and problem-solving step isolation (givens, formula, resolution, units).
- Multi-provider LLM abstraction layer: local inference (Ollama), OpenAI-compatible cloud APIs, and an offline mock provider for zero-cost testing.
- Study guides exported as DOCX and PDF (ReportLab), plus an interactive Mermaid concept map (HTML).

---

## Architecture

The system implements a decoupled pipeline pattern:

```text
[Input Ingestion] ------> [Transcription (Whisper)]
                               |
                               v
[Synthesis Engine] <--- [Segmenter & Equation Parser]
       |
       +---> DOCX / PDF Study Guide
       +---> HTML Concept Map (Mermaid)
```

- `src/ingestion/`: Handles multimodal input normalization (DOCX, PDF, audio/video extraction).
- `src/segmentation/`: Splits content into coherent pedagogical blocks.
- `src/equations/`: Parses and validates mathematical expressions into standard LaTeX.
- `src/problems/`: Identifies solved exercises, problem statements, and quantitative results.
- `src/providers/`: LLM provider interface (`MockProvider`, `OllamaProvider`, `OpenAIProvider`).
- `src/documents/`: Document generation engine producing formatted DOCX and PDF deliverables.
- `src/visualization/`: LaTeX formula rendering and Mermaid concept map generation.

---

## Requirements

- Python 3.10+
- FFmpeg (for video and audio extraction; provided by `imageio-ffmpeg`)
- Optional, for local speech-to-text: `faster-whisper` (recommended) or `openai-whisper`

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## Configuration

Copy `.env.example` to `.env` and configure your preferred provider:

```ini
# Provider options: mock | ollama | openai
LLM_PROVIDER=mock

# OpenAI configuration (optional)
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Ollama configuration (optional local execution)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

---

## Usage

### Run with Mock Provider (Zero API Costs / Offline Testing)
```bash
python main.py --input "data/sample/sample_lecture.docx" --provider mock
```

### Run with a Real Provider
```bash
python main.py --input "path/to/lecture.mp4" --provider ollama --model llama3.2
python main.py --input "path/to/lectures_folder/" --provider openai
```

### Other Options
| Flag | Description |
| :--- | :--- |
| `--resume`, `-r` | Resume processing an existing class from its folder or ID |
| `--export`, `-e` | Re-export DOCX / PDF / HTML from cached results |
| `--config`, `-c` | Use a custom `config.yaml` |
| `--no-cache` | Ignore previous cache and process from scratch |

Results are written to `output/<class_id>/`:

```text
guia_estudio.docx      guia_estudio.pdf      mapa_conceptual.html
transcripcion.json     analisis.json         ecuaciones.json
problemas.json         sintesis.json
```

### Sample Data

`data/sample/` contains a **synthetic** lecture transcript and slide deck created for this repository. They do not come from a real class and contain no personal data.

---

## Testing

Execute unit test suite with pytest:
```bash
pytest tests/ -v
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
