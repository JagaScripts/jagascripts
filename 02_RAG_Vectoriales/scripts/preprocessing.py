import os
import json
import logging
import sys
from typing import List, Dict, Any

sys.path.append(os.getcwd())

from pypdf import PdfReader, PdfWriter
from src.config import settings
from llama_index.llms.google_genai import GoogleGenAI
import asyncio

# Configuración del logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Preprocessing")

async def generate_summary(text: str) -> str:
    """Genera un resumen del texto usando el modelo configurado."""
    logger.debug(f"Iniciando generación de resumen para texto de longitud: {len(text)}")
    
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "dummy_key_for_testing":
        logger.warning("No se detectó una GEMINI_API_KEY válida. Usando modo MOCK.")
        return "Resumen de prueba (Mock)."
    
    model = settings.MODEL_NAME
    prompt = f"Resume este texto de forma técnica y profesional:\n\n{text[:15000]}"
    
    try:
        logger.info(f"Llamando a Gemini ({model}) para generar resumen...")
        llm = GoogleGenAI(model=model, api_key=settings.GEMINI_API_KEY)
        response = await llm.acomplete(prompt)
        summary = str(response)
        logger.info("Resumen generado con éxito.")
        logger.debug(f"Resumen (cabecera): {summary[:100]}...")
        return summary
    except Exception as e:
        logger.error(f"Error crítico durante la generación con modelo {model}: {e}")
        logger.critical("El proceso de resumen ha fallado. Revisa la cuota o conectividad de la API.")
        return f"Error en generación: {str(e)}"

async def process_pdf(pdf_path: str, output_dir: str = "data/optimized_chunks") -> Dict[str, Any]:
    logger.info(f"Iniciando procesamiento del PDF: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        logger.error(f"El archivo fuente no existe: {pdf_path}")
        raise FileNotFoundError(f"No existe {pdf_path}")

    if not os.path.exists(output_dir):
        logger.debug(f"Creando directorio de salida: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
    
    try:
        reader = PdfReader(pdf_path)
        num_pages = len(reader.pages)
        logger.info(f"PDF cargado correctamente. Páginas totales: {num_pages}")
    except Exception as e:
        logger.critical(f"No se pudo leer el PDF {pdf_path}: {e}")
        raise

    # Estrategia de fragmentación: Bloques de 10 páginas para mantener coherencia semántica
    logger.info("Dividiendo PDF en bloques de 10 páginas (estrategia sin marcadores).")
    sections = []
    pages_per_chunk = 10
    for i in range(0, num_pages, pages_per_chunk):
        end_p = min(i + pages_per_chunk, num_pages)
        sections.append({
            "title": f"Seccion_Pag_{i+1}_{end_p}",
            "start_page": i,
            "end_page": end_p
        })
    logger.debug(f"Total secciones planificadas: {len(sections)}")

    summaries = {}
    for i, section in enumerate(sections):
        logger.info(f"Procesando sección [{i+1}/{len(sections)}]: {section['title']}")
        writer = PdfWriter()
        section_text = ""
        
        for p in range(section["start_page"], section["end_page"]):
            logger.debug(f"Extrayendo página {p+1}")
            writer.add_page(reader.pages[p])
            page_text = reader.pages[p].extract_text()
            if page_text:
                section_text += page_text + "\n"
        
        if not section_text.strip():
            logger.warning(f"La sección {section['title']} parece estar vacía de texto.")

        filename = f"{section['title']}.pdf"
        filepath = os.path.join(output_dir, filename)
        
        try:
            with open(filepath, "wb") as f:
                writer.write(f)
            logger.debug(f"Mini-PDF guardado en: {filepath}")
        except Exception as e:
            logger.error(f"Error al guardar el mini-PDF {filename}: {e}")
            continue
            
        summary = await generate_summary(section_text)
        
        # Consolidación de metadatos y resúmenes para la posterior indexación vectorial
        summaries[filename] = {
            "title": section["title"],
            "summary": summary,
            "path": filepath
        }

    summaries_file = "data/summaries.json"
    try:
        with open(summaries_file, "w", encoding="utf-8") as f:
            json.dump(summaries, f, indent=4, ensure_ascii=False)
        logger.info(f"Archivo de resúmenes guardado con éxito: {summaries_file}")
    except Exception as e:
        logger.critical(f"Error al guardar el archivo de resúmenes: {e}")

    logger.info("Procesamiento de PDF finalizado.")
    return {"count": len(sections)}

if __name__ == "__main__":
    asyncio.run(process_pdf("data/Estrategia_IA_2024.pdf"))
