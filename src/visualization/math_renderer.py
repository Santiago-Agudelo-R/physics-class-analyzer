"""
High-resolution Mathematical Typography and Equation Renderer.
Converts LaTeX formulas into crisp, transparent PNG images for DOCX and PDF documents,
and sanitizes mathematical strings for universal Unicode font compatibility.
"""

import re
import hashlib
from pathlib import Path
from typing import Optional
import matplotlib.mathtext as mathtext
from PIL import Image


class MathRenderer:
    """Renders LaTeX formulas to transparent high-DPI images and sanitizes math text."""

    @classmethod
    def sanitize_latex(cls, latex: str) -> str:
        """Sanitizes LaTeX expressions for matplotlib mathtext engine."""
        s = latex.strip()

        # Remove surrounding $ or $$
        s = re.sub(r"^\$+", "", s)
        s = re.sub(r"\$+$", "", s)
        s = s.strip()

        # Replace macros with word boundary checks
        s = s.replace(r"\text{", r"\mathrm{")
        s = s.replace(r"\max", r"\mathrm{max}")
        s = s.replace(r"\min", r"\mathrm{min}")
        s = s.replace(r"\quad", " ")
        s = s.replace(r"\qquad", "  ")
        s = s.replace(r"\implies", r"\rightarrow")
        s = re.sub(r"\\le(?![a-zA-Z])", r"\\leq", s)
        s = re.sub(r"\\ge(?![a-zA-Z])", r"\\geq", s)

        # Replace unicode subscripts/superscripts with LaTeX syntax
        subs = {'₀': '_0', '₁': '_1', '₂': '_2', '₃': '_3', '₄': '_4', '₅': '_5', '₆': '_6', '₇': '_7', '₈': '_8', '₉': '_9'}
        sups = {'⁰': '^0', '¹': '^1', '²': '^2', '³': '^3', '⁴': '^4', '⁵': '^5', '⁶': '^6', '⁷': '^7', '⁸': '^8', '⁹': '^9', '⁻': '^-'}
        for u, l in subs.items():
            s = s.replace(u, l)
        for u, l in sups.items():
            s = s.replace(u, l)

        # Mathtext requires exactly one set of surrounding dollar signs
        return f"${s}$"

    @classmethod
    def render_to_png(
        cls,
        latex: str,
        output_dir: Path,
        color: str = "#1E3A8A",
        dpi: int = 250
    ) -> Optional[Path]:
        """Renders a LaTeX expression into a cropped transparent PNG file."""
        if not latex or not latex.strip():
            return None

        clean_expr = cls.sanitize_latex(latex)
        # Create unique filename based on formula hash
        hash_id = hashlib.md5(clean_expr.encode("utf-8")).hexdigest()[:10]
        out_path = Path(output_dir) / f"math_{hash_id}.png"
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if out_path.exists() and out_path.stat().st_size > 0:
            return out_path

        try:
            mathtext.math_to_image(clean_expr, str(out_path), dpi=dpi, color=color)
            if out_path.exists() and out_path.stat().st_size > 0:
                return out_path
        except Exception:
            # Fallback: try removing complex brackets or terms
            try:
                simplified = clean_expr.replace(r"\left", "").replace(r"\right", "")
                mathtext.math_to_image(simplified, str(out_path), dpi=dpi, color=color)
                if out_path.exists() and out_path.stat().st_size > 0:
                    return out_path
            except Exception:
                pass

        return None

    @classmethod
    def clean_text_for_pdf(cls, text: str) -> str:
        """
        Converts unicode subscripts/superscripts, emojis, and LaTeX symbols into ReportLab-safe
        tags (<sub>, <sup>, Greek symbols) so that NO missing-glyph black boxes (■) appear.
        """
        if not text:
            return ""

        s = str(text)

        # Remove emojis that standard TrueType fonts don't have (prevents empty square tofu)
        emoji_replacements = {
            '🔴': '',
            '🟡': '',
            '🟢': '',
            '⚠️': 'OJO: ',
            '💡': 'TIP: ',
            '⚡': '• ',
            '🗺️': '',
            '🚀': '',
            '📘': '',
            '📕': '',
            '✅': '✓',
            '❌': '✗',
            '📐': '',
            '🛠️': '',
            '🧠': '',
            '📄': '',
            '♻️': ''
        }
        for emo, rep in emoji_replacements.items():
            s = s.replace(emo, rep)

        # Replace Unicode subscripts with ReportLab <sub> tags
        sub_map = {
            '₀': '<sub>0</sub>', '₁': '<sub>1</sub>', '₂': '<sub>2</sub>',
            '₃': '<sub>3</sub>', '₄': '<sub>4</sub>', '₅': '<sub>5</sub>',
            '₆': '<sub>6</sub>', '₇': '<sub>7</sub>', '₈': '<sub>8</sub>', '₉': '<sub>9</sub>'
        }
        for u, tag in sub_map.items():
            s = s.replace(u, tag)

        # Replace Unicode superscripts with ReportLab <sup> tags
        sup_map = {
            '⁰': '<sup>0</sup>', '¹': '<sup>1</sup>', '²': '<sup>2</sup>',
            '³': '<sup>3</sup>', '⁴': '<sup>4</sup>', '⁵': '<sup>5</sup>',
            '⁶': '<sup>6</sup>', '⁷': '<sup>7</sup>', '⁸': '<sup>8</sup>', '⁹': '<sup>9</sup>',
            '⁻¹⁹': '<sup>-19</sup>', '⁻³⁴': '<sup>-34</sup>', '⁻¹⁵': '<sup>-15</sup>',
            '⁻⁹': '<sup>-9</sup>', '⁻': '<sup>-</sup>'
        }
        for u, tag in sup_map.items():
            s = s.replace(u, tag)

        # Replace LaTeX text macros in narrative prose
        s = re.sub(r"\\text\{([^}]+)\}", r"\1", s)
        s = re.sub(r"\\mathrm\{([^}]+)\}", r"\1", s)

        # Clean LaTeX superscript / subscript brackets
        s = re.sub(r"\^\{(-?\d+)\}", r"<sup>\1</sup>", s)
        s = re.sub(r"_\{([a-zA-Z0-9]+)\}", r"<sub>\1</sub>", s)
        s = re.sub(r"_([0-9])", r"<sub>\1</sub>", s)

        # Replace common raw LaTeX commands in narrative prose
        s = s.replace(r"\Phi", "Φ")
        s = s.replace(r"\lambda", "λ")
        s = s.replace(r"\varepsilon_0", "ε<sub>0</sub>")
        s = s.replace(r"\varepsilon", "ε")
        s = s.replace(r"\nu", "ν")
        s = s.replace(r"\Delta", "Δ")
        s = s.replace(r"\pi", "π")
        s = s.replace(r"\approx", "≈")
        s = s.replace(r"\times", "×")
        s = s.replace(r"\quad", " ")
        s = s.replace(r"\implies", " ➔ ")
        s = s.replace(r"K_{max}", "K<sub>max</sub>")
        s = s.replace(r"f_0", "f<sub>0</sub>")
        s = s.replace(r"V_0", "V<sub>0</sub>")
        s = s.replace(r"R_H", "R<sub>H</sub>")
        s = s.replace(r"E_n", "E<sub>n</sub>")
        s = s.replace(r"E_{fotón}", "E<sub>fotón</sub>")
        s = s.replace(r"E_fotón", "E<sub>fotón</sub>")

        # Clean double spaces
        s = re.sub(r"\s+", " ", s).strip()
        return s
