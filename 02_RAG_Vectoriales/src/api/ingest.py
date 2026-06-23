from fastapi import APIRouter, HTTPException, UploadFile, File
import os
import shutil
import logging
from scripts.preprocessing import process_pdf
from scripts.create_llamaindex_index import create_index_from_processed_chunks

# Configuración del logger
logger = logging.getLogger("IngestAPI")

router = APIRouter()

@router.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    logger.info(f"Recibida petición de ingesta: {file.filename}")
    
    if not file.filename.endswith(".pdf"):
        logger.warning(f"Intento de subida de archivo no PDF: {file.filename}")
        raise HTTPException(status_code=400, detail="Solo se admiten archivos PDF.")

    temp_path = os.path.join("data", "raw", file.filename)
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    
    try:
        logger.debug(f"Guardando archivo temporal en: {temp_path}")
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"Archivo guardado correctamente: {temp_path}")
    except Exception as e:
        logger.critical(f"Error al escribir el archivo en disco: {e}")
        raise HTTPException(status_code=500, detail=f"Error al guardar el archivo: {str(e)}")

    # Paso 1: Preprocesamiento (Mini-PDFs y resúmenes)
    logger.info(f"--- FASE 1: Preprocesamiento de {file.filename} ---")
    try:
        preprocessing_result = await process_pdf(temp_path)
        logger.info(f"Preprocesamiento completado. Secciones generadas: {preprocessing_result.get('count')}")
    except Exception as e:
        logger.error(f"Fallo en la fase de preprocesamiento: {e}")
        raise HTTPException(status_code=500, detail=f"Error en preprocesamiento: {str(e)}")

    # Paso 2: Indexación en Qdrant (LlamaIndex)
    logger.info(f"--- FASE 2: Indexación en Qdrant ---")
    try:
        await create_index_from_processed_chunks()
        logger.info("Indexación masiva completada con éxito.")
    except Exception as e:
        logger.error(f"Fallo en la fase de indexación: {e}")
        raise HTTPException(status_code=500, detail=f"Error en indexación: {str(e)}")

    logger.info(f"Proceso de ingesta finalizado con éxito para {file.filename}")
    return {
        "status": "success",
        "filename": file.filename,
        "sections_count": preprocessing_result.get("count"),
        "message": "Archivo procesado, resumido e indexado correctamente."
    }
