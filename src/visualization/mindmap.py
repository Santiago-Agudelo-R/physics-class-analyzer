"""
Mindmap and conceptual map generator.
Produces both standalone Mermaid definitions and interactive self-contained HTML/SVG diagrams
with MathJax 3 support for beautiful mathematical typography.
"""

from pathlib import Path
from typing import Dict, Any, List


class MindmapGenerator:
    """Generates interactive and graphical concept maps with MathJax mathematical rendering."""

    @classmethod
    def generate_mermaid(
        cls,
        class_title: str,
        topics: List[str],
        concepts: List[Dict[str, Any]],
        equations: List[Dict[str, Any]],
        problems: List[Dict[str, Any]]
    ) -> str:
        safe_title = class_title.replace('"', '').replace("'", "")
        lines = ["mindmap", f'  root(("{safe_title}"))']

        # Concepts branch
        lines.append('    Conceptos Clave')
        for c in concepts[:6]:
            c_name = c.get("title") or c.get("concept", "")
            c_name = c_name.replace('"', '').replace("'", "").strip()
            imp = c.get("importance", "")
            icon = "🔴 " if "IMPRESCINDIBLE" in imp else "🟡 " if "IMPORTANTE" in imp else "🟢 "
            if c_name:
                lines.append(f'      ["{icon}{c_name}"]')

        # Theory & Topics branch
        lines.append('    Teoria y Fundamentos')
        for t in topics[:5]:
            t_clean = t.replace('"', '').replace("'", "").strip()
            if t_clean:
                lines.append(f'      ["{t_clean}"]')

        # Equations branch
        lines.append('    Ecuaciones')
        for eq in equations[:6]:
            name = eq.get("name", "").replace('"', '').replace("'", "").strip()
            ltx = eq.get("latex", "").replace('"', '').replace("'", "").strip()
            if name:
                lines.append(f'      ["{name}"]')

        # Problems & Methods branch
        lines.append('    Problemas y Metodos')
        for p in problems[:5]:
            p_title = p.get("title", "").replace('"', '').replace("'", "").strip()
            if p_title:
                lines.append(f'      ["{p_title}"]')

        return "\n".join(lines)

    @classmethod
    def generate_html(
        cls,
        class_title: str,
        mermaid_code: str,
        synthesis: Dict[str, Any],
        equations: List[Dict[str, Any]],
        problems: List[Dict[str, Any]],
        output_file: Path
    ) -> Path:
        output_path = Path(output_file).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mapa Conceptual — {class_title}</title>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <script>
    mermaid.initialize({{ startOnLoad: true, theme: 'neutral' }});
  </script>
  <!-- MathJax 3 for textbook-quality mathematical rendering -->
  <script>
    window.MathJax = {{
      tex: {{
        inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
        displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
        processEscapes: true
      }},
      options: {{
        skipHtmlTags: ['script', 'noscript', 'style', 'textarea']
      }}
    }};
  </script>
  <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
  <style>
    :root {{
      --primary: #1e3a8a;
      --secondary: #2563eb;
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --text: #0f172a;
      --border: #e2e8f0;
      --red: #ef4444;
      --yellow: #f59e0b;
      --green: #10b981;
    }}
    body {{
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      margin: 0;
      padding: 2rem;
      line-height: 1.6;
    }}
    .header {{
      text-align: center;
      margin-bottom: 2rem;
      border-bottom: 2px solid var(--border);
      padding-bottom: 1.5rem;
    }}
    .header h1 {{
      color: var(--primary);
      margin-bottom: 0.5rem;
    }}
    .header p {{
      color: #64748b;
      font-size: 1.1rem;
      max-width: 800px;
      margin: 0 auto;
    }}
    .container {{
      max-width: 1200px;
      margin: 0 auto;
    }}
    .card {{
      background: var(--card-bg);
      border-radius: 12px;
      box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
      padding: 1.5rem;
      margin-bottom: 2rem;
      border: 1px solid var(--border);
    }}
    .card h2 {{
      color: var(--primary);
      margin-top: 0;
      border-bottom: 1px solid var(--border);
      padding-bottom: 0.5rem;
    }}
    .mermaid-container {{
      display: flex;
      justify-content: center;
      overflow-x: auto;
      padding: 1rem;
      background: #ffffff;
      border-radius: 8px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 1.5rem;
    }}
    .badge {{
      display: inline-block;
      padding: 0.25rem 0.5rem;
      border-radius: 4px;
      font-size: 0.8rem;
      font-weight: 600;
    }}
    .badge-red {{ background: #fee2e2; color: #991b1b; }}
    .badge-yellow {{ background: #fef3c7; color: #92400e; }}
    .badge-green {{ background: #d1fae5; color: #065f46; }}
    .eq-box {{
      background: #f1f5f9;
      padding: 1rem;
      border-radius: 8px;
      margin: 0.75rem 0;
      border-left: 4px solid var(--secondary);
      text-align: center;
      font-size: 1.15rem;
      overflow-x: auto;
    }}
    .procedure-list {{
      padding-left: 1.2rem;
    }}
    .procedure-list li {{
      margin-bottom: 0.35rem;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🗺️ Mapa Conceptual y Estructura Cognitiva</h1>
      <h2>{class_title}</h2>
      <p>{synthesis.get('executive_summary', '')[:250]}...</p>
    </div>

    <div class="card">
      <h2>Diagrama de Relaciones y Dependencias</h2>
      <div class="mermaid-container">
        <pre class="mermaid">
{mermaid_code}
        </pre>
      </div>
    </div>

    <div class="grid">
      <div class="card">
        <h2>🔴 Conceptos Fundamentales</h2>
        {cls._render_concepts_html(synthesis.get('core_concepts', []))}
      </div>

      <div class="card">
        <h2>📐 Ecuaciones Clave (LaTeX Tipográfico)</h2>
        {cls._render_equations_html(equations)}
      </div>
    </div>

    <div class="card">
      <h2>🛠️ Metodología de Resolución de Problemas</h2>
      {cls._render_problems_html(problems)}
    </div>
  </div>
</body>
</html>
"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return output_path

    @classmethod
    def _render_concepts_html(cls, concepts: List[Dict[str, Any]]) -> str:
        html = []
        for c in concepts:
            title = c.get("title") or c.get("concept", "")
            imp = c.get("importance", "IMPORTANTE")
            badge_cls = "badge-red" if "IMPRESCINDIBLE" in imp else "badge-yellow" if "IMPORTANTE" in imp else "badge-green"
            desc = c.get('explanation') or c.get('description', '')
            html.append(f"""
            <div style="margin-bottom: 1rem;">
              <strong>{title}</strong> <span class="badge {badge_cls}">{imp}</span>
              <p style="margin: 0.25rem 0; font-size: 0.95rem; color: #475569;">{desc}</p>
            </div>
            """)
        return "".join(html)

    @classmethod
    def _render_equations_html(cls, equations: List[Dict[str, Any]]) -> str:
        html = []
        for eq in equations[:6]:
            latex = eq.get('latex', '').strip()
            # Wrap in $$ if not already
            if not latex.startswith("$$") and not latex.startswith("$"):
                math_display = f"$${latex}$$"
            else:
                math_display = latex

            html.append(f"""
            <div style="margin-bottom: 1.25rem; border-bottom: 1px solid #f1f5f9; padding-bottom: 0.75rem;">
              <strong style="color: #1e3a8a;">{eq.get('name', 'Ecuación')}</strong>
              <div class="eq-box">{math_display}</div>
              <small style="color: #64748b; display: block;"><strong>Variables:</strong> {eq.get('variables', '')}</small>
              <small style="color: #64748b; display: block;"><strong>Uso:</strong> {eq.get('when_to_use', '')}</small>
            </div>
            """)
        return "".join(html)

    @classmethod
    def _render_problems_html(cls, problems: List[Dict[str, Any]]) -> str:
        html = []
        for p in problems:
            procs = p.get("general_procedure") or p.get("step_by_step_method") or []
            if isinstance(procs, str):
                procs = [procs]
            proc_items = "".join(f"<li>{step}</li>" for step in procs)
            p_eq = p.get('equations_used', '')
            math_display = f"$${p_eq}$$" if p_eq and not p_eq.startswith("$") else p_eq

            html.append(f"""
            <div style="margin-bottom: 1.5rem; border-bottom: 1px dashed #e2e8f0; padding-bottom: 1rem;">
              <h3 style="color: #1e3a8a; margin-bottom: 0.25rem;">{p.get('title', '')}</h3>
              <p style="margin: 0.2rem 0;"><strong>Tipo:</strong> {p.get('type', '')}</p>
              <p style="margin: 0.2rem 0;"><strong>Fenómeno Físico:</strong> {p.get('concepts_to_remember') or p.get('physical_phenomenon', '')}</p>
              <div class="eq-box">{math_display}</div>
              <strong>Procedimiento General:</strong>
              <ol class="procedure-list">
                {proc_items}
              </ol>
            </div>
            """)
        return "".join(html)
