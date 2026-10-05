"""
Master Pipeline orchestrator for Physics Class Analyzer.
Executes the 8-step pipeline with stage caching, progress reporting, and resume capabilities.
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
import json
import shutil

from .config import AppConfig
from .cache import CacheManager, CacheStages
from .ingestion.matcher import ClassInputs, ClassFileMatcher
from .ingestion.text_reader import TextReader, TranscriptSegment
from .ingestion.audio_extractor import AudioExtractor
from .transcription.whisper_stt import LocalTranscriber
from .segmentation.chunker import ClassChunker, ClassChunk
from .providers.base import LLMProvider
from .analysis.segment_analyzer import SegmentAnalyzer
from .equations.extractor import EquationConsolidator, EquationItem
from .problems.recognizer import ProblemRecognizer, ProblemItem
from .synthesis.synthesizer import GlobalSynthesizer
from .visualization.mindmap import MindmapGenerator
from .documents.docx_builder import DocxStudyGuideBuilder
from .documents.pdf_builder import PdfStudyGuideBuilder


class Pipeline:
    """Orchestrates the 8-stage Physics Class Analyzer workflow."""

    def __init__(self, config: AppConfig, provider: LLMProvider):
        self.config = config
        self.provider = provider

    def run(
        self,
        class_inputs: ClassInputs,
        resume: bool = True,
        export_only: bool = False
    ) -> Dict[str, Path]:
        class_id = class_inputs.class_id
        class_out_dir = self.config.output_dir / class_id
        cache_dir = class_out_dir / self.config.cache_dir_name
        cache = CacheManager(cache_dir)

        print(f"\n=======================================================")
        print(f"🚀 INICIANDO: {self.config.app_name}")
        print(f"📁 Clase ID: {class_id}")
        print(f"🤖 Proveedor LLM: {self.config.llm_provider} ({self.config.llm_model})")
        print(f"📂 Carpeta de Salida: {class_out_dir}")
        print(f"=======================================================\n")

        # ------------------------------------------------------------------
        # [1/8] & [2/8] EXTRACCIÓN DE AUDIO / PROCESANDO TRANSCRIPCIÓN
        # ------------------------------------------------------------------
        transcription_data: List[Dict[str, Any]] = []

        if resume and cache.has(CacheStages.STAGE_01_TRANSCRIPTION):
            print("[1/8 & 2/8] ♻️ Reutilizando transcripción desde cache...")
            transcription_data = cache.load(CacheStages.STAGE_01_TRANSCRIPTION)
        else:
            if class_inputs.has_text:
                print(f"[1/8] 📄 Documento de transcripción detectado: {class_inputs.text_path.name}")
                print(f"[2/8] ⏳ Procesando y parseando transcripción textual...")
                segments = TextReader.parse_to_segments(class_inputs.text_path)
                transcription_data = [s.to_dict() for s in segments]
            elif class_inputs.has_media:
                media_path = class_inputs.video_path or class_inputs.audio_path
                audio_file = media_path
                if class_inputs.video_path:
                    print(f"[1/8] 🎙️ Extrayendo audio de video {media_path.name}...")
                    audio_file = AudioExtractor.extract_audio(
                        media_path,
                        class_out_dir / f"{class_id}_audio.wav"
                    )
                else:
                    print(f"[1/8] 🎙️ Archivo de audio detectado: {media_path.name}")

                print(f"[2/8] 🗣️ Ejecutando speech-to-text local con Whisper...")
                transcriber = LocalTranscriber(
                    model_size=self.config.transcription.get("whisper_model", "base"),
                    device=self.config.transcription.get("device", "cpu"),
                    language=self.config.transcription.get("language", "es")
                )
                segments = transcriber.transcribe_audio(audio_file)
                transcription_data = [s.to_dict() for s in segments]
            else:
                raise ValueError(f"No se encontró archivo de video, audio ni transcripción para '{class_id}'.")

            cache.save(CacheStages.STAGE_01_TRANSCRIPTION, transcription_data)
            cache.save(CacheStages.STAGE_02_CLEANED, transcription_data)
            print(f"      ✅ Transcripción procesada: {len(transcription_data)} segmentos.")

        # ------------------------------------------------------------------
        # [3/8] SEGMENTANDO CLASE
        # ------------------------------------------------------------------
        chunks_data: List[Dict[str, Any]] = []
        if resume and cache.has(CacheStages.STAGE_03_SEGMENTS):
            print("[3/8] ♻️ Reutilizando segmentación desde cache...")
            chunks_data = cache.load(CacheStages.STAGE_03_SEGMENTS)
        else:
            print("[3/8] ✂️ Segmentando clase en bloques de 5–15 minutos...")
            chunker = ClassChunker(
                target_minutes=self.config.segmentation.get("target_duration_minutes", 10.0),
                min_minutes=self.config.segmentation.get("min_duration_minutes", 5.0),
                max_minutes=self.config.segmentation.get("max_duration_minutes", 15.0),
                overlap_seconds=self.config.segmentation.get("overlap_seconds", 30.0)
            )
            chunks = chunker.chunk_segments(transcription_data)
            chunks_data = [c.to_dict() for c in chunks]
            cache.save(CacheStages.STAGE_03_SEGMENTS, chunks_data)
            print(f"      ✅ Clase dividida en {len(chunks_data)} bloques contextuales.")

        # ------------------------------------------------------------------
        # [4/8] ANALIZANDO SEGMENTOS
        # ------------------------------------------------------------------
        segment_analyses: List[Dict[str, Any]] = []
        if resume and cache.has(CacheStages.STAGE_04_SEGMENT_ANALYSIS):
            print("[4/8] ♻️ Reutilizando análisis de segmentos desde cache...")
            segment_analyses = cache.load(CacheStages.STAGE_04_SEGMENT_ANALYSIS)
        else:
            print(f"[4/8] 🧠 Analizando {len(chunks_data)} segmentos con {self.config.llm_provider}...")
            analyzer = SegmentAnalyzer(self.provider)
            chunks_objects = [
                ClassChunk(
                    chunk_id=c["chunk_id"],
                    start=c["start"],
                    end=c["end"],
                    start_str=c["start_str"],
                    end_str=c["end_str"],
                    duration_minutes=c["duration_minutes"],
                    text=c["text"],
                    raw_segments_count=c["raw_segments_count"],
                    context_prefix=c.get("context_prefix", "")
                )
                for c in chunks_data
            ]
            for c in chunks_objects:
                print(f"      → Analizando bloque #{c.chunk_id} [{c.start_str} - {c.end_str}]...")
                res = analyzer.analyze_chunk(c)
                segment_analyses.append(res)

            cache.save(CacheStages.STAGE_04_SEGMENT_ANALYSIS, segment_analyses)
            print("      ✅ Análisis de segmentos completado.")

        # ------------------------------------------------------------------
        # [5/8] EXTRACCIÓN Y AUDITORÍA DE ECUACIONES
        # ------------------------------------------------------------------
        consolidated_equations: List[Dict[str, Any]] = []
        if resume and cache.has(CacheStages.STAGE_05_EQUATIONS):
            print("[5/8] ♻️ Reutilizando ecuaciones desde cache...")
            consolidated_equations = cache.load(CacheStages.STAGE_05_EQUATIONS)
        else:
            print("[5/8] 📐 Consolidando y auditando ecuaciones en LaTeX...")
            eq_items = EquationConsolidator.consolidate(segment_analyses)
            consolidated_equations = [e.to_dict() for e in eq_items]
            cache.save(CacheStages.STAGE_05_EQUATIONS, consolidated_equations)
            print(f"      ✅ {len(consolidated_equations)} ecuaciones consolidadas.")

        # ------------------------------------------------------------------
        # [6/8] RECONOCIMIENTO DE PROBLEMAS Y METODOLOGÍA
        # ------------------------------------------------------------------
        consolidated_problems: List[Dict[str, Any]] = []
        if resume and cache.has(CacheStages.STAGE_06_PROBLEMS):
            print("[6/8] ♻️ Reutilizando problemas desde cache...")
            consolidated_problems = cache.load(CacheStages.STAGE_06_PROBLEMS)
        else:
            print("[6/8] 🛠️ Estructurando metodología de resolución de problemas...")
            prob_items = ProblemRecognizer.consolidate(segment_analyses)
            consolidated_problems = [p.to_dict() for p in prob_items]
            cache.save(CacheStages.STAGE_06_PROBLEMS, consolidated_problems)
            print(f"      ✅ {len(consolidated_problems)} tipos de problemas estructurados.")

        # ------------------------------------------------------------------
        # [7/8] SÍNTESIS GLOBAL
        # ------------------------------------------------------------------
        synthesis: Dict[str, Any] = {}
        if resume and cache.has(CacheStages.STAGE_07_GLOBAL_SYNTHESIS):
            print("[7/8] ♻️ Reutilizando síntesis global desde cache...")
            synthesis = cache.load(CacheStages.STAGE_07_GLOBAL_SYNTHESIS)
        else:
            print("[7/8] 🌐 Ejecutando síntesis global curricular...")
            synthesizer = GlobalSynthesizer(self.provider)
            synthesis = synthesizer.synthesize(
                class_id=class_id,
                segment_analyses=segment_analyses,
                consolidated_equations=consolidated_equations,
                consolidated_problems=consolidated_problems
            )
            cache.save(CacheStages.STAGE_07_GLOBAL_SYNTHESIS, synthesis)
            print("      ✅ Síntesis global generada exitosamente.")

        # ------------------------------------------------------------------
        # [8/8] GENERANDO DOCUMENTOS FINALES
        # ------------------------------------------------------------------
        print("[8/8] 📄 Generando Guía de Estudio (DOCX, PDF, Mapa Mental y JSON)...")
        generated_files: Dict[str, Path] = {}

        # 1. Export JSON files
        trans_file = class_out_dir / "transcripcion.json"
        analisis_file = class_out_dir / "analisis.json"
        eq_file = class_out_dir / "ecuaciones.json"
        prob_file = class_out_dir / "problemas.json"
        synth_file = class_out_dir / "sintesis.json"

        with open(trans_file, "w", encoding="utf-8") as f:
            json.dump(transcription_data, f, ensure_ascii=False, indent=2)
        with open(analisis_file, "w", encoding="utf-8") as f:
            json.dump(segment_analyses, f, ensure_ascii=False, indent=2)
        with open(eq_file, "w", encoding="utf-8") as f:
            json.dump(consolidated_equations, f, ensure_ascii=False, indent=2)
        with open(prob_file, "w", encoding="utf-8") as f:
            json.dump(consolidated_problems, f, ensure_ascii=False, indent=2)
        with open(synth_file, "w", encoding="utf-8") as f:
            json.dump(synthesis, f, ensure_ascii=False, indent=2)

        generated_files["transcripcion_json"] = trans_file
        generated_files["analisis_json"] = analisis_file
        generated_files["ecuaciones_json"] = eq_file
        generated_files["problemas_json"] = prob_file
        generated_files["sintesis_json"] = synth_file

        # 2. DOCX Guide
        docx_path = class_out_dir / "guia_estudio.docx"
        DocxStudyGuideBuilder.build(
            class_name=class_id,
            synthesis=synthesis,
            equations=consolidated_equations,
            problems=consolidated_problems,
            segment_analyses=segment_analyses,
            output_path=docx_path
        )
        generated_files["docx"] = docx_path
        print(f"      📘 DOCX generado: {docx_path.name}")

        # 3. PDF Guide
        pdf_path = class_out_dir / "guia_estudio.pdf"
        try:
            PdfStudyGuideBuilder.build(
                class_name=class_id,
                synthesis=synthesis,
                equations=consolidated_equations,
                problems=consolidated_problems,
                output_path=pdf_path
            )
            generated_files["pdf"] = pdf_path
            print(f"      📕 PDF generado: {pdf_path.name}")
        except Exception as e:
            print(f"      ⚠️ Advertencia al generar PDF: {e}")

        # 4. Mindmap HTML
        mindmap_path = class_out_dir / "mapa_conceptual.html"
        topics_all = []
        for s in segment_analyses:
            topics_all.extend(s.get("topics", []))
        topics_unique = list(dict.fromkeys(topics_all))

        mermaid_code = MindmapGenerator.generate_mermaid(
            class_title=synthesis.get("title", class_id),
            topics=topics_unique,
            concepts=synthesis.get("core_concepts", []),
            equations=consolidated_equations,
            problems=consolidated_problems
        )
        MindmapGenerator.generate_html(
            class_title=synthesis.get("title", class_id),
            mermaid_code=mermaid_code,
            synthesis=synthesis,
            equations=consolidated_equations,
            problems=consolidated_problems,
            output_file=mindmap_path
        )
        generated_files["mindmap_html"] = mindmap_path
        print(f"      🗺️ Mapa conceptual interactivo: {mindmap_path.name}")

        # Mark final cache stage
        cache.save(CacheStages.STAGE_08_FINAL_DOCUMENT, {
            "completed": True,
            "generated_files": {k: str(v) for k, v in generated_files.items()}
        })

        print("\n✨ ¡PROCESO COMPLETADO EXITOSAMENTE! ✨")
        print(f"Resultados disponibles en: {class_out_dir}")
        return generated_files
