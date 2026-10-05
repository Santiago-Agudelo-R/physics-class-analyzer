"""
PDF Study Guide Builder using ReportLab.
Generates portable study guides with styled tables, mathematical formula images,
and Unicode font registration to eliminate missing-glyph boxes.
"""

from pathlib import Path
from typing import Dict, Any, List
import os

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage

from ..visualization.math_renderer import MathRenderer


class PdfStudyGuideBuilder:
    """Builds a formatted PDF study guide with true mathematical formula rendering."""

    NAVY = colors.HexColor("#1E3A8A")
    BLUE = colors.HexColor("#2563EB")
    DARK = colors.HexColor("#1E293B")
    RED = colors.HexColor("#B91C1C")
    BG_LIGHT = colors.HexColor("#F8FAFC")
    BORDER_LIGHT = colors.HexColor("#E2E8F0")
    RED_BG = colors.HexColor("#FEE2E2")
    YELLOW_BG = colors.HexColor("#FEF3C7")

    _FONTS_INITIALIZED = False
    _BASE_FONT = "Helvetica"
    _BOLD_FONT = "Helvetica-Bold"

    @classmethod
    def _init_fonts(cls):
        if cls._FONTS_INITIALIZED:
            return

        # Attempt to register Windows TrueType Unicode fonts (Segoe UI or Arial)
        candidates = [
            ("SegoeUI", "C:/Windows/Fonts/segoeui.ttf", "SegoeUI-Bold", "C:/Windows/Fonts/segoeuib.ttf"),
            ("ArialUnicode", "C:/Windows/Fonts/arial.ttf", "ArialUnicode-Bold", "C:/Windows/Fonts/arialbd.ttf")
        ]

        for regular_name, regular_path, bold_name, bold_path in candidates:
            if os.path.exists(regular_path) and os.path.exists(bold_path):
                try:
                    pdfmetrics.registerFont(TTFont(regular_name, regular_path))
                    pdfmetrics.registerFont(TTFont(bold_name, bold_path))
                    cls._BASE_FONT = regular_name
                    cls._BOLD_FONT = bold_name
                    break
                except Exception:
                    continue

        cls._FONTS_INITIALIZED = True

    @classmethod
    def build(
        cls,
        class_name: str,
        synthesis: Dict[str, Any],
        equations: List[Dict[str, Any]],
        problems: List[Dict[str, Any]],
        output_path: Path
    ) -> Path:
        cls._init_fonts()

        out_file = Path(output_path).resolve()
        out_file.parent.mkdir(parents=True, exist_ok=True)
        img_cache_dir = out_file.parent / ".math_cache"
        img_cache_dir.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(
            str(out_file),
            pagesize=letter,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontName=cls._BOLD_FONT,
            fontSize=19,
            leading=23,
            textColor=cls.NAVY,
            alignment=1,  # Center
            spaceAfter=4
        )

        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontName=cls._BASE_FONT,
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#64748B"),
            alignment=1,
            spaceAfter=12
        )

        h1_style = ParagraphStyle(
            "SectionH1",
            parent=styles["Heading1"],
            fontName=cls._BOLD_FONT,
            fontSize=13,
            leading=17,
            textColor=cls.NAVY,
            spaceBefore=10,
            spaceAfter=5
        )

        h2_style = ParagraphStyle(
            "SectionH2",
            parent=styles["Heading2"],
            fontName=cls._BOLD_FONT,
            fontSize=10.5,
            leading=14,
            textColor=cls.BLUE,
            spaceBefore=7,
            spaceAfter=3
        )

        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontName=cls._BASE_FONT,
            fontSize=9,
            leading=12.5,
            textColor=cls.DARK,
            spaceAfter=5
        )

        bullet_style = ParagraphStyle(
            "Bullet",
            parent=styles["Normal"],
            fontName=cls._BASE_FONT,
            fontSize=8.5,
            leading=12,
            textColor=cls.DARK,
            leftIndent=12,
            spaceAfter=2.5
        )

        story = []

        # Header
        title = synthesis.get("title") or f"Guía de Estudio — {class_name}"
        clean_title = MathRenderer.clean_text_for_pdf(title)
        story.append(Paragraph("GUÍA DE ESTUDIO UNIVERSITARIA", ParagraphStyle("TopSub", fontName=cls._BOLD_FONT, textColor=cls.BLUE, fontSize=10, alignment=1)))
        story.append(Paragraph(clean_title, title_style))
        story.append(Paragraph(f"Física Moderna • {class_name}", subtitle_style))
        story.append(Spacer(1, 6))

        # 1. Resumen Ejecutivo
        story.append(Paragraph("1. Resumen Ejecutivo", h1_style))
        exec_sum = MathRenderer.clean_text_for_pdf(synthesis.get("executive_summary", ""))
        story.append(Paragraph(exec_sum, body_style))
        story.append(Spacer(1, 6))

        # 2. Conceptos Fundamentales
        story.append(Paragraph("2. Conceptos Fundamentales", h1_style))
        for c in synthesis.get("core_concepts", []):
            ctitle = MathRenderer.clean_text_for_pdf(c.get("title") or c.get("concept", ""))
            imp = c.get("importance", "IMPORTANTE")
            exp = MathRenderer.clean_text_for_pdf(c.get("explanation") or c.get("description", ""))

            bg = cls.RED_BG if "IMPRESCINDIBLE" in imp else cls.YELLOW_BG
            tag = "IMPRESCINDIBLE" if "IMPRESCINDIBLE" in imp else "IMPORTANTE"
            tag_color = "#B91C1C" if "IMPRESCINDIBLE" in imp else "#1E293B"
            cell_data = [[
                Paragraph(f"<b><font color='{tag_color}'>[{tag}]</font> {ctitle}</b><br/>{exp}", body_style)
            ]]
            t = Table(cell_data, colWidths=[540])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), bg),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]))
            story.append(t)
            story.append(Spacer(1, 4))

        # 3. Ecuaciones Principales (con imágenes renderizadas de fórmulas matemáticas)
        story.append(Paragraph("3. Ecuaciones Clave (Fórmulas Matemáticas)", h1_style))
        eq_data = [
            [
                Paragraph("<b>Ecuación</b>", body_style),
                Paragraph("<b>Expresión Matemática</b>", body_style),
                Paragraph("<b>Variables y Condiciones de Uso</b>", body_style)
            ]
        ]

        for eq in equations[:8]:
            ts = f" [{eq.get('timestamp')}]" if eq.get("timestamp") else ""
            clean_name = MathRenderer.clean_text_for_pdf(eq.get("name", ""))
            name_p = Paragraph(f"<b>{clean_name}</b>{ts}", body_style)

            # Render formula to PNG
            latex = eq.get("latex", "")
            img_path = MathRenderer.render_to_png(latex, img_cache_dir)
            if img_path and img_path.exists():
                with PILImage.open(img_path) as pim:
                    pw, ph = pim.size
                # Target height between 16 and 26 points
                target_h = min(26.0, max(16.0, ph * (180.0 / pw) if pw > 0 else 20.0))
                target_w = min(190.0, pw * (target_h / ph) if ph > 0 else 100.0)
                math_element = RLImage(str(img_path), width=target_w, height=target_h)
            else:
                math_element = Paragraph(f"<code>{latex}</code>", body_style)

            clean_vars = MathRenderer.clean_text_for_pdf(eq.get("variables", ""))
            clean_when = MathRenderer.clean_text_for_pdf(eq.get("when_to_use", ""))
            clean_units = MathRenderer.clean_text_for_pdf(eq.get("units", "SI"))

            info_p = Paragraph(
                f"{clean_when}<br/>"
                f"<b>Variables:</b> {clean_vars}<br/>"
                f"<i>Unidades:</i> {clean_units}",
                body_style
            )
            eq_data.append([name_p, math_element, info_p])

        eq_table = Table(eq_data, colWidths=[120, 200, 220])
        eq_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), cls.NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, cls.BORDER_LIGHT),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(eq_table)
        story.append(Spacer(1, 8))

        # 4. Metodología para Resolución de Problemas
        story.append(Paragraph("4. Metodología para Resolución de Problemas", h1_style))
        for p in problems:
            p_title = MathRenderer.clean_text_for_pdf(p.get("title", ""))
            story.append(Paragraph(f"<b>{p_title}</b>", h2_style))

            given = MathRenderer.clean_text_for_pdf(p.get("given_data", ""))
            target = MathRenderer.clean_text_for_pdf(p.get("target", ""))
            story.append(Paragraph(f"• <b>Qué dan:</b> {given}", bullet_style))
            story.append(Paragraph(f"• <b>Qué piden:</b> {target}", bullet_style))

            # Render formula for problem if available
            p_eq = p.get("equations_used", "")
            if p_eq:
                p_img = MathRenderer.render_to_png(p_eq, img_cache_dir)
                if p_img and p_img.exists():
                    with PILImage.open(p_img) as pim:
                        pw, ph = pim.size
                    target_h = min(22.0, max(13.0, ph * (320.0 / pw) if pw > 0 else 18.0))
                    target_w = min(340.0, pw * (target_h / ph) if ph > 0 else 150.0)
                    story.append(Paragraph("• <b>Ecuación base:</b>", bullet_style))
                    story.append(RLImage(str(p_img), width=target_w, height=target_h))
                else:
                    clean_p_eq = MathRenderer.clean_text_for_pdf(p_eq)
                    story.append(Paragraph(f"• <b>Ecuación base:</b> {clean_p_eq}", bullet_style))

            procs = p.get("general_procedure", [])
            for step in procs:
                clean_step = MathRenderer.clean_text_for_pdf(step)
                story.append(Paragraph(f"  → {clean_step}", bullet_style))

            pitfalls = p.get("common_pitfalls", [])
            if pitfalls:
                err_text = ", ".join(MathRenderer.clean_text_for_pdf(pit) for pit in pitfalls)
                story.append(Paragraph(f"  [OJO - Evitar]: {err_text}", bullet_style))

            story.append(Spacer(1, 4))

        # 5. Tips de Examen y Repaso Rápido
        story.append(Paragraph("5. Tips de Examen y Repaso Rápido", h1_style))
        for tip in synthesis.get("study_tips", []):
            clean_tip = MathRenderer.clean_text_for_pdf(tip)
            story.append(Paragraph(f"<b>[TIP EXAMEN]</b> {clean_tip}", bullet_style))
        story.append(Spacer(1, 4))

        for rev in synthesis.get("quick_review_5min", []):
            clean_rev = MathRenderer.clean_text_for_pdf(rev)
            story.append(Paragraph(f"• {clean_rev}", bullet_style))

        doc.build(story)
        return out_file
