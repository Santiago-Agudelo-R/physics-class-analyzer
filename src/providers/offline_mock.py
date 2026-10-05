"""
Offline Mock & Rule-Based LLM Provider for Modern Physics.
Supports Sesión 02 (Fotoeléctrico/Espectros), Sesión 03 (Bohr/Compton/De Broglie),
and Sesión 04 (Schrödinger/Pozos/Incertidumbre).
"""

import json
import re
from typing import Dict, Any, List
from .base import LLMProvider


class OfflineMockProvider(LLMProvider):
    """Provides high-quality academic analysis using domain parsing rules for Modern Physics."""

    def __init__(self, **kwargs):
        pass

    def analyze(self, prompt: str, context: str) -> str:
        ctx_lower = context.lower()

        if "segment_analysis" in prompt.lower() or "analiza este segmento" in prompt.lower():
            return json.dumps(self._analyze_segment(ctx_lower, context), ensure_ascii=False, indent=2)
        elif "sintesis" in prompt.lower() or "synthesis" in prompt.lower():
            return json.dumps(self._synthesize_class(ctx_lower, context), ensure_ascii=False, indent=2)
        elif "mindmap" in prompt.lower() or "mapa" in prompt.lower():
            return json.dumps(self._build_mindmap(ctx_lower), ensure_ascii=False, indent=2)

        return json.dumps({
            "status": "success",
            "summary": "Análisis académico completado.",
            "topics": ["Física Moderna"],
        }, ensure_ascii=False)

    def _analyze_segment(self, ctx_lower: str, raw_text: str) -> Dict[str, Any]:
        topics = []
        subtopics = []
        concepts = []
        equations = []
        problems = []
        warnings = []
        errors = []

        ts_match = re.search(r"\[(\d{1,2}:\d{2}(?::\d{2})?)\]", raw_text)
        current_ts = ts_match.group(1) if ts_match else "00:00"

        # -------------------------------------------------------------
        # SESIÓN 04: SCHRÖDINGER, POZO DE POTENCIAL, INCERTIDUMBRE
        # -------------------------------------------------------------
        if "schrodinger" in ctx_lower or "pozo" in ctx_lower or "caja" in ctx_lower or "sesión 04" in ctx_lower or "sesion 04" in ctx_lower:
            topics.append("Mecánica Cuántica Ondulatoria y Ecuación de Schrödinger")
            subtopics.extend([
                "Función de onda y postulado probabilístico de Born",
                "Ecuación de Schrödinger independiente del tiempo en 1D",
                "Partícula en una caja unidimensional (Pozo infinito de potencial)",
                "Energías cuantizadas y energía de punto cero",
                "Principio de Incertidumbre de Heisenberg"
            ])
            concepts.append({
                "concept": "Interpretación Probabilística de Born",
                "importance": "IMPRESCINDIBLE",
                "description": "La función de onda ψ(x) en sí no es directamente medible, pero su módulo al cuadrado |ψ(x)|² representa la densidad de probabilidad de hallar la partícula en la posición x.",
                "timestamp": current_ts
            })
            concepts.append({
                "concept": "Energía de Punto Cero en el Pozo Infinito",
                "importance": "IMPRESCINDIBLE",
                "description": "El estado fundamental n=1 tiene una energía estrictamente positiva E₁ > 0. La partícula cuántica confinada no puede estar en reposo total debido al principio de incertidumbre.",
                "timestamp": current_ts
            })
            concepts.append({
                "concept": "Principio de Incertidumbre de Heisenberg",
                "importance": "IMPRESCINDIBLE",
                "description": "Es intrínsecamente imposible medir simultáneamente y con precisión arbitraria la posición y el momento lineal de una partícula cuántica: Δx · Δp ≥ ħ/2.",
                "timestamp": current_ts
            })
            equations.append({
                "name": "Ecuación de Schrödinger 1D Independiente del Tiempo",
                "latex": "-\\frac{\\hbar^2}{2m} \\frac{d^2\\psi(x)}{dx^2} + V(x)\\psi(x) = E\\psi(x)",
                "variables": "\\hbar = h/(2\\pi): constante reducida de Planck, m: masa de la partícula, V(x): energía potencial, E: energía total, \\psi(x): función de onda espacial.",
                "units": "Joules o eV",
                "when_to_use": "Para determinar los estados estacionarios y energías permitidas de cualquier partícula confinada en un potencial V(x).",
                "conditions": "Sistemas unidimensionales no relativistas independientes del tiempo.",
                "confidence": "HIGH",
                "timestamp": current_ts
            })
            equations.append({
                "name": "Energías Cuantizadas en el Pozo Infinito (Caja 1D)",
                "latex": "E_n = \\frac{n^2 \\pi^2 \\hbar^2}{2m L^2} = \\frac{n^2 h^2}{8m L^2}",
                "variables": "E_n: energía del nivel n, n = 1, 2, 3...: número cuántico principal, L: longitud del pozo, m: masa de la partícula.",
                "units": "Joules (J) o eV",
                "when_to_use": "Para calcular niveles de energía o fotones emitidos por partículas confinadas en una caja unidimensional.",
                "conditions": "Pozo infinito rígido (paredes impenetrables en x=0 y x=L).",
                "confidence": "HIGH",
                "timestamp": current_ts
            })
            equations.append({
                "name": "Funciones de Onda Normalizadas del Pozo Infinito",
                "latex": "\\psi_n(x) = \\sqrt{\\frac{2}{L}} \\sin\\left(\\frac{n\\pi x}{L}\\right)",
                "variables": "\\psi_n(x): eigenfunción espacial del nivel n, L: ancho de la caja, x: posición (0 <= x <= L).",
                "units": "m^(-1/2)",
                "when_to_use": "Para calcular densidades de probabilidad y valores esperados en pozos de potencial.",
                "conditions": "0 <= x <= L; fuera de la caja ψ(x) = 0.",
                "confidence": "HIGH",
                "timestamp": current_ts
            })
            equations.append({
                "name": "Principio de Incertidumbre Posición-Momento",
                "latex": "\\Delta x \\cdot \\Delta p \\ge \\frac{\\hbar}{2}",
                "variables": "\\Delta x: incertidumbre en la posición, \\Delta p: incertidumbre en el momento lineal.",
                "units": "J*s (SI)",
                "when_to_use": "Para estimar límites de precisión en mediciones o estimar energías de confinamiento.",
                "conditions": "Válido para cualquier par de variables canónicamente conjugadas.",
                "confidence": "HIGH",
                "timestamp": current_ts
            })
            problems.append({
                "title": "Transiciones energéticas y emisión de fotones en un pozo de potencial infinito",
                "type": "Cálculo de niveles cuánticos en una caja unidimensional",
                "given_data": "Partícula de masa m (electrón) confinada en una caja de ancho L. Transición del nivel n₂ al nivel n₁.",
                "target": "Calcular la longitud de onda λ del fotón emitido en la transición.",
                "physical_phenomenon": "Confinamiento cuántico de onda estacionaria. La diferencia de energía entre eigenestados discretos se emite como un fotón con energía ΔE = hc / λ.",
                "equations_used": "E_n = \\frac{n^2 h^2}{8m L^2},\\quad \\Delta E = E_{n2} - E_{n1} = \\frac{hc}{\\lambda} \\implies \\lambda = \\frac{hc}{\\Delta E}",
                "step_by_step_method": [
                    "1. Identificar el número cuántico inicial n₂ y el final n₁.",
                    "2. Calcular la energía del nivel inicial E_n2 y del final E_n1 usando E_n = (n² h²) / (8 m L²).",
                    "3. Obtener la diferencia energética liberada: ΔE = E_n2 - E_n1.",
                    "4. Igualar a la energía del fotón emitido: ΔE = hc / λ.",
                    "5. Despejar λ y calcular numéricamente asegurando unidades SI consistentes."
                ],
                "common_pitfalls": [
                    "Olvidar elevar n al cuadrado en la fórmula de energía.",
                    "Usar L en nanómetros directamente en lugar de convertir a metros (m)."
                ],
                "timestamp": current_ts
            })

        # -------------------------------------------------------------
        # SESIÓN 03: MODELO DE BOHR, DE BROGLIE, EFECTO COMPTON
        # -------------------------------------------------------------
        elif "bohr" in ctx_lower or "compton" in ctx_lower or "broglie" in ctx_lower or "sesión 03" in ctx_lower or "sesion 03" in ctx_lower:
            topics.append("Modelo Atómico de Bohr y Dualidad Onda-Partícula")
            subtopics.extend([
                "Postulados de Bohr y cuantización del momento angular",
                "Radios orbitales y niveles de energía del Hidrógeno",
                "Hipótesis de De Broglie sobre la longitud de onda de la materia",
                "Efecto Compton y dispersión inelástica de fotones",
                "Longitud de onda de Compton del electrón"
            ])
            concepts.append({
                "concept": "Cuantización del Momento Angular de Bohr",
                "importance": "IMPRESCINDIBLE",
                "description": "Bohr postuló que el electrón solo puede orbitar en órbitas circulares estacionarias donde su momento angular orbital es un múltiplo entero de ħ: L = mvr = nħ.",
                "timestamp": current_ts
            })
            concepts.append({
                "concept": "Longitud de Onda de De Broglie",
                "importance": "IMPRESCINDIBLE",
                "description": "Toda partícula material con momento p posee una longitud de onda asociada λ = h/p. Los electrones manifiestan comportamientos ondulatorios como difracción e interferencia.",
                "timestamp": current_ts
            })
            concepts.append({
                "concept": "Efecto Compton",
                "importance": "IMPRESCINDIBLE",
                "description": "Demuestra la naturaleza corpuscular de la radiación X/gamma al colisionar elásticamente fotones con electrones cuasi-libres, transfiriendo energía y momento y aumentando la longitud de onda del fotón dispersado.",
                "timestamp": current_ts
            })
            equations.append({
                "name": "Cuantización del Momento Angular Orbital",
                "latex": "L = m v r = \\frac{n h}{2\\pi} = n\\hbar",
                "variables": "L: momento angular, m: masa del electrón, v: velocidad orbital, r: radio de la órbita, n = 1, 2, 3..., \\hbar: constante reducida de Planck.",
                "units": "J*s (kg*m^2/s)",
                "when_to_use": "Para deducir radios cuantizados y niveles permitidos en átomos hidrogenoides.",
                "conditions": "Órbitas circulares del átomo de Bohr.",
                "confidence": "HIGH",
                "timestamp": current_ts
            })
            equations.append({
                "name": "Radios Orbitales de Bohr",
                "latex": "r_n = n^2 a_0 = n^2 \\left( \\frac{4\\pi \\varepsilon_0 \\hbar^2}{m e^2} \\right)",
                "variables": "r_n: radio del nivel n, a_0: radio de Bohr del estado fundamental (\\approx 0.0529 \\text{ nm} = 0.529 \\text{ Å}).",
                "units": "metros (m) o Ångströms (Å)",
                "when_to_use": "Para calcular el tamaño orbital del átomo según el nivel cuántico principal n.",
                "conditions": "Átomo de hidrógeno o iones monoelectrónicos.",
                "confidence": "HIGH",
                "timestamp": current_ts
            })
            equations.append({
                "name": "Longitud de Onda de De Broglie",
                "latex": "\\lambda = \\frac{h}{p} = \\frac{h}{m v} = \\frac{h}{\\sqrt{2m K}}",
                "variables": "\\lambda: longitud de onda de la materia, p: momento lineal, m: masa, v: velocidad, K: energía cinética no relativista.",
                "units": "metros (m)",
                "when_to_use": "Para relacionar la longitud de onda cuántica con la velocidad o potencial acelerador de cualquier partícula con masa.",
                "conditions": "Régimen no relativista (v << c).",
                "confidence": "HIGH",
                "timestamp": current_ts
            })
            equations.append({
                "name": "Ecuación del Desplazamiento Compton",
                "latex": "\\Delta \\lambda = \\lambda' - \\lambda = \\frac{h}{m_e c} (1 - \\cos\\theta) = \\lambda_C (1 - \\cos\\theta)",
                "variables": "\\lambda: longitud de onda incidente, \\lambda': longitud de onda dispersada, \\theta: ángulo de dispersión del fotón, \\lambda_C: longitud de onda de Compton (\\approx 2.426 \\times 10^{-12} \\text{ m} = 0.00243 \\text{ nm}).",
                "units": "metros (m)",
                "when_to_use": "Para calcular el incremento de longitud de onda tras la colisión inelástica de fotones de rayos X o gamma con electrones.",
                "conditions": "Electrón inicialmente en reposo.",
                "confidence": "HIGH",
                "timestamp": current_ts
            })
            problems.append({
                "title": "Cálculo del corrimiento Compton y energía del fotón dispersado",
                "type": "Dispersión de fotones de alta energía (Rayos X)",
                "given_data": "Fotón incidente con longitud de onda λ incide sobre un electrón en reposo y se dispersa a un ángulo θ (ej. 90° o 180°).",
                "target": "Calcular la nueva longitud de onda λ' y la energía cinética transferida al electrón de retroceso.",
                "physical_phenomenon": "Conservación del momento lineal relativista y de la energía total en la colisión elástica fotón-electrón.",
                "equations_used": "\\Delta \\lambda = \\frac{h}{m_e c}(1 - \\cos\\theta),\\quad \\lambda' = \\lambda + \\Delta\\lambda,\\quad K_e = hc \\left( \\frac{1}{\\lambda} - \\frac{1}{\\lambda'} \\right)",
                "step_by_step_method": [
                    "1. Calcular el desplazamiento de longitud de onda Δλ = λ_C (1 - cos θ) usando λ_C = 0.00243 nm.",
                    "2. Sumar el desplazamiento para hallar la longitud de onda final: λ' = λ + Δλ.",
                    "3. Calcular la energía del fotón incidente (E = hc/λ) y la del fotón dispersado (E' = hc/λ').",
                    "4. Por conservación de energía, la energía cinética del electrón es: K_e = E - E' = hc (1/λ - 1/λ')."
                ],
                "common_pitfalls": [
                    "Olvidar que el corrimiento Δλ depende únicamente del ángulo de dispersión θ, NO de la longitud de onda incidente.",
                    "A 180° (retrodispersión), 1 - cos(180°) = 1 - (-1) = 2, por lo que el corrimiento es máximo: 2 λ_C."
                ],
                "timestamp": current_ts
            })

        # -------------------------------------------------------------
        # SESIÓN 02: EFECTO FOTOELÉCTRICO Y ESPECTROS
        # -------------------------------------------------------------
        else:
            topics.append("Efecto Fotoeléctrico")
            subtopics.extend([
                "Contraste clásico vs cuántico",
                "Frecuencia de corte y umbral",
                "Función de trabajo del material",
                "Energía cinética máxima de los fotoelectrones",
                "Potencial de frenado"
            ])
            concepts.append({
                "concept": "Cuantización de la luz en fotones",
                "importance": "IMPRESCINDIBLE",
                "description": "La luz no transfiere energía de forma continua como una onda clásica, sino en paquetes discretos o cuantos llamados fotones, con energía E = hf.",
                "timestamp": current_ts
            })
            concepts.append({
                "concept": "Proceso de Todo o Nada en absorción fotoeléctrica",
                "importance": "IMPRESCINDIBLE",
                "description": "Un fotón es absorbido completamente por un solo electrón. Si la energía del fotón es menor que la función de trabajo, no se liberan electrones sin importar la intensidad.",
                "timestamp": current_ts
            })
            equations.append({
                "name": "Ecuación de Einstein del Efecto Fotoeléctrico",
                "latex": "K_{max} = hf - \\Phi = h(f - f_0)",
                "variables": "K_{max}: energía cinética máxima (J o eV), h: constante de Planck, f: frecuencia incidente (Hz), \\Phi: función de trabajo (J o eV), f_0: frecuencia umbral.",
                "units": "Joules (J) o electrón-voltios (eV)",
                "when_to_use": "Para calcular la energía cinética de electrones expulsados o la frecuencia umbral de un metal iluminado.",
                "conditions": "Interacción de un solo fotón con un solo electrón en superficie metálica.",
                "confidence": "HIGH",
                "timestamp": current_ts
            })
            equations.append({
                "name": "Energía del fotón y relación de dispersión",
                "latex": "E = hf = \\frac{hc}{\\lambda}",
                "variables": "E: energía del fotón, h: constante de Planck, c: velocidad de la luz, \\lambda: longitud de onda.",
                "units": "J o eV",
                "when_to_use": "Siempre que se relacione la longitud de onda con su cuanto de energía.",
                "conditions": "Fotones en el vacío / medio homogéneo.",
                "confidence": "HIGH",
                "timestamp": current_ts
            })
            equations.append({
                "name": "Conversión de Unidades de Energía",
                "latex": "1\\text{ eV} = 1.602 \\times 10^{-19}\\text{ J}",
                "variables": "eV: electrón-voltio, J: Joule.",
                "units": "Energía",
                "when_to_use": "Conversión obligatoria en cálculos con constante de Planck y potencial eléctrico.",
                "conditions": "Definición fundamental.",
                "confidence": "HIGH",
                "timestamp": current_ts
            })
            equations.append({
                "name": "Fórmula de Rydberg para las series del Hidrógeno",
                "latex": "\\frac{1}{\\lambda} = R_H \\left( \\frac{1}{n_1^2} - \\frac{1}{n_2^2} \\right)",
                "variables": "\\lambda: longitud de onda, R_H: constante de Rydberg (1.097 x 10^7 m^-1), n_1, n_2: números cuánticos.",
                "units": "m^-1",
                "when_to_use": "Para predecir longitudes de onda de transiciones electrónicas en átomos hidrogenoides.",
                "conditions": "Transiciones en el átomo de hidrógeno.",
                "confidence": "HIGH",
                "timestamp": current_ts
            })
            equations.append({
                "name": "Energía de niveles discretos en el Hidrógeno",
                "latex": "E_n = -\\frac{hc R_H}{n^2} = -\\frac{13.6\\text{ eV}}{n^2}",
                "variables": "E_n: energía del nivel n, n = 1, 2, 3...",
                "units": "eV o Joules",
                "when_to_use": "Para determinar la energía de estados excitados en hidrógeno.",
                "conditions": "Estado ligado electrón-protón.",
                "confidence": "HIGH",
                "timestamp": current_ts
            })
            problems.append({
                "title": "Estimación de la constante de Planck a partir de dos longitudes de onda",
                "type": "Cálculo de constantes fundamentales mediante efecto fotoeléctrico",
                "given_data": "λ₁ = 80 nm (K_max,1 = 11.39 eV), λ₂ = 110 nm (K_max,2 = 7.154 eV), sobre la misma superficie metálica.",
                "target": "Estimar experimentalmente la constante de Planck h.",
                "physical_phenomenon": "Efecto fotoeléctrico sobre un mismo cátodo donde la función de trabajo Φ es constante.",
                "equations_used": "K_{max,1} = \\frac{hc}{\\lambda_1} - \\Phi,\\quad K_{max,2} = \\frac{hc}{\\lambda_2} - \\Phi \\implies h = \\frac{K_{max,1} - K_{max,2}}{c(1/\\lambda_1 - 1/\\lambda_2)}",
                "step_by_step_method": [
                    "1. Restar ambas ecuaciones para eliminar la función de trabajo Φ: K_{max,1} - K_{max,2} = h (f_1 - f_2).",
                    "2. Convertir frecuencias: f = c / λ.",
                    "3. Despejar h: h = (K_{max,1} - K_{max,2}) / (f_1 - f_2).",
                    "4. Obtener h en eV·s y contrastar con el valor teórico (4.136 x 10⁻¹⁵ eV·s)."
                ],
                "common_pitfalls": [
                    "Olvidar convertir nanómetros a metros (x 10⁻⁹).",
                    "Mezclar unidades de Joules y eV en la resta."
                ],
                "timestamp": current_ts
            })
            problems.append({
                "title": "Carga eléctrica neta producida sobre una esfera de cobre aislada",
                "type": "Fotoelectricidad combinada con potencial electrostático",
                "given_data": "Esfera aislada de radio r = 0.05 m, λ = 200 nm, función de trabajo Φ = 4.7 eV.",
                "target": "Calcular la carga total Q acumulada sobre la esfera.",
                "physical_phenomenon": "La emisión cesa cuando el potencial electrostático acumulado alcanza el potencial de frenado.",
                "equations_used": "K_{max} = \\frac{hc}{\\lambda} - \\Phi,\\quad V = \\frac{Q}{4\\pi\\varepsilon_0 r} = \\frac{K_{max}}{e} \\implies Q = 4\\pi\\varepsilon_0 r \\left(\\frac{K_{max}}{e}\\right)",
                "step_by_step_method": [
                    "1. Calcular la energía del fotón incidente E = hc/λ.",
                    "2. Calcular la energía cinética máxima K_max = E - Φ.",
                    "3. Igualar al potencial de frenado: V = K_max / e.",
                    "4. Despejar la carga total: Q = 4πε₀ r V."
                ],
                "common_pitfalls": ["No igualar el potencial superficial al potencial de frenado."],
                "timestamp": current_ts
            })
            problems.append({
                "title": "Cálculo del número de fotones por segundo emitidos por un haz de luz",
                "type": "Flujo de fotones y potencia radiante",
                "given_data": "Potencia P = 100 W, longitud de onda λ = 200 nm.",
                "target": "Número de fotones por segundo (N/t).",
                "physical_phenomenon": "La potencia radiante equivale a la tasa de fotones multiplicada por la energía individual.",
                "equations_used": "P = \\left(\\frac{N}{t}\\right) E_{fotón} \\implies \\frac{N}{t} = \\frac{P \\lambda}{h c}",
                "step_by_step_method": [
                    "1. Calcular la energía de un fotón: E = hc / λ.",
                    "2. Despejar el flujo de partículas: N/t = P / E.",
                    "3. Verificar unidades en s⁻¹."
                ],
                "common_pitfalls": ["Confundir potencia (W) con intensidad (W/m²)."],
                "timestamp": current_ts
            })

        theory = (
            "En esta sesión se estructuran los principios fundamentales de la física moderna universitaria. "
            "Se contrasta la formulación clásica continua frente a la cuantización de variables físicas cardinales "
            "(energía, momento angular, longitud de onda y probabilidad), estableciendo las bases experimentales "
            "y analíticas necesarias para resolver problemas de examen."
        )

        return {
            "topics": topics or ["Física Moderna"],
            "subtopics": subtopics or ["Fundamentos Cuánticos"],
            "theory": theory,
            "concepts": concepts,
            "equations": equations,
            "problems": problems,
            "teacher_warnings": warnings,
            "common_errors": errors
        }

    def _synthesize_class(self, ctx_lower: str, context: str) -> Dict[str, Any]:
        if "clase id: sesión 04" in ctx_lower or "clase id: sesion 04" in ctx_lower or "clase id: sesion_04" in ctx_lower:
            is_sesion_04, is_sesion_03 = True, False
        elif "clase id: sesión 03" in ctx_lower or "clase id: sesion 03" in ctx_lower or "clase id: sesion_03" in ctx_lower:
            is_sesion_04, is_sesion_03 = False, True
        elif "clase id: sesión 02" in ctx_lower or "clase id: sesion 02" in ctx_lower or "clase id: sesion_02" in ctx_lower:
            is_sesion_04, is_sesion_03 = False, False
        else:
            is_sesion_04 = "schrodinger" in ctx_lower or "pozo" in ctx_lower
            is_sesion_03 = "compton" in ctx_lower or "bohr" in ctx_lower

        if is_sesion_04:
            title = "Sesión 04 — Mecánica Cuántica Ondulatoria: Ecuación de Schrödinger y Pozos de Potencial"
            exec_summary = (
                "Esta clase introduce el formalismo matricial y ondulatorio de la mecánica cuántica moderna. "
                "Se parte de la interpretación estadística de Born, donde la función de onda ψ(x) define la probabilidad espacial. "
                "Se formula la Ecuación de Schrödinger independiente del tiempo y se resuelve rigurosamente para el pozo "
                "de potencial infinito unidimensional (partícula en una caja), deduciendo las autofunciones sinusoidales y la "
                "cuantización cuadrática de las energías permitidas E_n = n²h²/(8mL²). Finalmente, se consolida el Principio de "
                "Incertidumbre de Heisenberg como una propiedad intrínseca de la naturaleza ondulatoria de la materia."
            )
            core_concepts = [
                {"title": "Función de Onda y Probabilidad de Born", "importance": "IMPRESCINDIBLE", "explanation": "La probabilidad de encontrar una partícula entre x y x+dx es dP = |ψ(x)|² dx, sujeta a normalización unitaria integral."},
                {"title": "Estados Estacionarios en el Pozo Infinito", "importance": "IMPRESCINDIBLE", "explanation": "Las condiciones de frontera ψ(0)=ψ(L)=0 fuerzan que solo existan ondas estacionarias discretas con número cuántico n=1, 2, 3..."},
                {"title": "Energía del Estado Fundamental", "importance": "IMPRESCINDIBLE", "explanation": "En n=1, E₁ > 0, lo que significa que el confinamiento espacial impone una energía cinética mínima ineludible."},
                {"title": "Principio de Incertidumbre de Heisenberg", "importance": "IMPRESCINDIBLE", "explanation": "La indeterminación simultánea en posición y momento satisface Δx·Δp ≥ ħ/2 de manera estricta."}
            ]
            study_tips = [
                "Para exámenes: Recuerda que en el pozo infinito las energías crecen como n², a diferencia del átomo de hidrógeno donde van como -1/n².",
                "Al calcular la probabilidad en un intervalo [a, b], siempre debes integrar |ψ(x)|² dx entre esos límites usando la identidad sin²(θ) = (1 - cos(2θ))/2.",
                "La energía del estado fundamental de una caja NUNCA puede ser cero."
            ]
            exam_qs = {
                "conceptual": [
                    "¿Por qué la función de onda de una partícula cuántica confinada debe ser nula en las paredes de un pozo infinito?",
                    "Explique por qué el principio de incertidumbre prohíbe que una partícula atrapada en una caja esté en reposo (E=0)."
                ],
                "mathematical": [
                    "Demuestre que la constante de normalización de la función de onda ψ(x) = A sin(nπx/L) en [0, L] es A = √(2/L).",
                    "Calcule la longitud de onda del fotón emitido cuando un electrón en un pozo de ancho L decae del estado n=3 al estado n=1."
                ],
                "problem_solving": [
                    "Un protón está confinado en un pozo de potencial infinito de ancho L = 10 fm (escala nuclear). Calcule la energía del estado fundamental en MeV."
                ]
            }
            quick_review = [
                "1. Schrödinger 1D: -(ħ²/2m) d²ψ/dx² + Vψ = Eψ.",
                "2. Pozo infinito: E_n = n² h² / (8 m L²).",
                "3. Funciones de onda: ψ_n(x) = √(2/L) sin(nπx/L).",
                "4. Densidad de probabilidad: P(x) = |ψ(x)|².",
                "5. Heisenberg: Δx · Δp ≥ ħ/2."
            ]
        elif "bohr" in ctx_lower or "compton" in ctx_lower or "broglie" in ctx_lower or "sesión 03" in ctx_lower:
            title = "Sesión 03 — Modelo Atómico de Bohr, Dualidad Onda-Partícula y Efecto Compton"
            exec_summary = (
                "Esta sesión profundiza en la estructura atómica y en la confirmación definitiva de la dualidad onda-partícula. "
                "Se analizan los postulados de Bohr que cuantizan el momento angular orbital (L = nħ), deduciendo los radios orbitales "
                "de Bohr y los niveles de energía del átomo de hidrógeno. A continuación, se introduce la revolucionaria hipótesis de "
                "De Broglie, que asigna a toda masa en movimiento una longitud de onda λ = h/p. Por último, se examina el Efecto Compton, "
                "demostrando la cinemática relativista de la dispersión elástica fotón-electrón."
            )
            core_concepts = [
                {"title": "Postulado de Cuantización de Bohr", "importance": "IMPRESCINDIBLE", "explanation": "El momento angular orbital del electrón solo toma valores discretos múltiplos enteros de la constante reducida de Planck: L = nħ."},
                {"title": "Longitud de Onda de De Broglie", "importance": "IMPRESCINDIBLE", "explanation": "La materia exhibe propiedades ondulatorias asociadas con longitud de onda λ = h/p, verificables mediante difracción electrónica."},
                {"title": "Efecto Compton y Dispersión de Fotones", "importance": "IMPRESCINDIBLE", "explanation": "Colisión elástica donde un fotón de rayos X cede energía y momento a un electrón, provocando un aumento en su longitud de onda Δλ = λ_C(1 - cos θ)."}
            ]
            study_tips = [
                "Para exámenes: El desplazamiento Compton Δλ solo depende del ángulo de dispersión θ, nunca de la longitud de onda inicial ni del material dispersor.",
                "Para calcular la longitud de onda de De Broglie a partir del voltaje acelerador V: recuerda que K = eV, luego p = √(2m eV) y λ = h / √(2m eV).",
                "En el átomo de Bohr, el radio r_n aumenta con n², mientras que la energía E_n varía inversamente con n²."
            ]
            exam_qs = {
                "conceptual": [
                    "¿Por qué el efecto Compton solo es apreciable con fotones de alta energía (rayos X o gamma) y no con luz visible?",
                    "Explique cómo la hipótesis de De Broglie fundamenta físicamente el postulado de cuantización de órbitas de Bohr."
                ],
                "mathematical": [
                    "Deduzca que la longitud de onda de De Broglie de un electrón acelerado por un potencial V (no relativista) es aproximadamente λ = 1.226 / √V (en nm).",
                    "Demuestre que el máximo corrimiento Compton ocurre para retrodispersión a 180° y equivale al doble de la longitud de onda Compton."
                ],
                "problem_solving": [
                    "Un fotón de rayos X con λ = 0.020 nm choca con un electrón libre y se dispersa a 90°. Calcule: a) La longitud de onda del fotón dispersado, b) La energía cinética del electrón de retroceso."
                ]
            }
            quick_review = [
                "1. Momento angular de Bohr: L = nħ = nh / (2π).",
                "2. Radios de Bohr: r_n = n² a₀ (a₀ ≈ 0.0529 nm).",
                "3. De Broglie: λ = h / p = h / (m v).",
                "4. Desplazamiento Compton: Δλ = λ' - λ = λ_C (1 - cos θ).",
                "5. Longitud de onda Compton: λ_C = h / (m_e c) ≈ 0.00243 nm."
            ]
        else:
            title = "Sesión 02 — Antecedentes de la Mecánica Cuántica: Efecto Fotoeléctrico y Espectros Atómicos"
            exec_summary = (
                "Esta sesión aborda la ruptura histórica con la física clásica a través de dos fenómenos cardinales: "
                "el Efecto Fotoeléctrico y la estructura de los Espectros Atómicos. "
                "Se demuestra cómo el modelo ondulatorio clásico fallaba al no predecir la frecuencia de corte ni la ausencia de retardo temporal. "
                "Einstein introduce el concepto de fotón cuantizado (E = hf), formulando la relación fundamental de balance energético "
                "K_max = hf - Φ. A través de ejercicios resueltos, se aprende a estimar la constante de Planck experimentalmente, "
                "a calcular el potencial de frenado y la carga acumulada en conductores aislados, y a determinar el flujo de fotones a partir de la potencia. "
                "Finalmente, se analizan los espectros de líneas mediante la fórmula de Balmer-Rydberg, introduciendo la cuantización "
                "de niveles de energía discretos y negativos en el átomo de hidrógeno como antesala del modelo atómico de Bohr."
            )
            core_concepts = [
                {"title": "Fotón y Cuantización de la Energía", "importance": "IMPRESCINDIBLE", "explanation": "La luz se propaga e interactúa en paquetes discretos de energía E = hf = hc/λ. La constante de Planck actúa como la escala fundamental del régimen cuántico."},
                {"title": "Función de Trabajo (Φ) y Frecuencia Umbral (f₀)", "importance": "IMPRESCINDIBLE", "explanation": "Es la energía mínima indispensable para liberar al electrón más débilmente ligado del metal: Φ = h f₀. Si f < f₀, ningún electrón es emitido sin importar la intensidad de la radiación."},
                {"title": "Potencial de Frenado (V₀)", "importance": "IMPORTANTE", "explanation": "Diferencia de potencial inversa aplicada para detener incluso a los fotoelectrones más rápidos, cumpliendo e V₀ = K_max."},
                {"title": "Espectros Discretos y Niveles Negativos", "importance": "IMPRESCINDIBLE", "explanation": "Los átomos solo emiten o absorben fotones cuyas energías correspondan a la diferencia entre estados discretos: ΔE = E_final - E_inicial. Los estados ligados poseen energía negativa."}
            ]
            study_tips = [
                "Para exámenes: Asegúrate de tener claras las dos unidades de la constante de Planck (Joules·s y eV·s). Si te dan longitudes de onda en nanómetros y energías en eV, trabajar en eV ahorra tiempo y evita errores exponenciales.",
                "Identifica si el problema habla de la misma superficie metálica: en ese caso, la función de trabajo Φ se cancela restando las dos ecuaciones de Einstein.",
                "En problemas de esferas o conductores aislados que se iluminan, recuerda que la pérdida de electrones genera un potencial de frenado electrostático que detiene el efecto automáticamente."
            ]
            exam_qs = {
                "conceptual": [
                    "¿Por qué la física clásica predecía erróneamente un retraso temporal en la expulsión de electrones bajo luz débil, y cómo lo resolvió la hipótesis de fotones?",
                    "Explique por qué los niveles energéticos de los estados ligados en el átomo de hidrógeno se definen con signo negativo."
                ],
                "mathematical": [
                    "Demuestre que al iluminar un mismo cátodo con dos longitudes de onda λ₁ y λ₂, la constante de Planck se puede obtener como h = (K₁,max - K₂,max) / [c (1/λ₁ - 1/λ₂)]."
                ],
                "problem_solving": [
                    "Una superficie metálica con función de trabajo de 2.3 eV es iluminada con luz de 450 nm. Determine: a) La energía del fotón en eV, b) Si hay efecto fotoeléctrico, c) La velocidad máxima de los electrones expulsados."
                ]
            }
            quick_review = [
                "1. Ecuación de Einstein: K_max = hf - Φ.",
                "2. Si f < f₀: No hay emisión fotoeléctrica.",
                "3. Rydberg: 1/λ = R_H (1/n₁² - 1/n₂²).",
                "4. Intensidad aumenta la corriente de electrones, NO la energía cinética máxima."
            ]

        return {
            "title": title,
            "executive_summary": exec_summary,
            "core_concepts": core_concepts,
            "prerequisites_and_dependencies": [
                {"concept": "Frecuencia y longitud de onda (c = λf)", "needed_for": "Energía del fotón (E = hf)"},
                {"concept": "Hipótesis de De Broglie", "needed_for": "Ecuación de ondas de Schrödinger"}
            ],
            "study_tips": study_tips,
            "potential_exam_questions": exam_qs,
            "quick_review_5min": quick_review
        }

    def _build_mindmap(self, ctx_lower: str) -> Dict[str, Any]:
        return {
            "root": "Física Moderna",
            "branches": [
                {"title": "Conceptos", "children": ["Cuantización", "Dualidad Onda-Partícula"]},
                {"title": "Ecuaciones", "children": ["E=hf", "K_max = hf - Φ", "λ = h/p"]}
            ]
        }
