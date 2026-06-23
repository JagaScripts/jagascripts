import os
import httpx
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = "http://localhost:8000/api/v1/ingest"
DATA_DIR = "data"

async def ingest_all_pdfs():
    """Busca todos los PDFs en la carpeta data/ y los envía al endpoint /ingest."""
    if not os.path.exists(DATA_DIR):
        logger.error(f"No se encontró la carpeta {DATA_DIR}")
        return

    pdf_files = [f for f in os.listdir(DATA_DIR) if f.lower().endswith(".pdf")]
    
async def ingest_file(file_path: str):
    logger.info(f"Iniciando ingesta de archivo: {os.path.basename(file_path)}")
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            logger.debug(f"Abriendo archivo para lectura: {file_path}")
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f, "application/pdf")}
                logger.info(f"Enviando petición POST a {API_URL}...")
                response = await client.post(API_URL, files=files)
            
            if response.status_code == 200:
                logger.info(f"ÉXITO: {os.path.basename(file_path)} procesado e indexado.")
                logger.debug(f"Respuesta API: {response.json()}")
            else:
                logger.error(f"FALLO en API para {os.path.basename(file_path)}: Status {response.status_code}")
                logger.error(f"Detalle del error: {response.text}")
                if response.status_code >= 500:
                    logger.critical("Error interno del servidor. Deteniendo o revisando logs del servicio API.")
        except Exception as e:
            logger.critical(f"Error de red o conexión al intentar procesar {file_path}: {e}")

async def main():
    logger.info("--- Iniciando proceso de ingesta masiva ---")
    
    if not os.path.exists(DATA_DIR):
        logger.critical(f"Directorio de datos '{DATA_DIR}' no encontrado. Abortando.")
        return

    # Buscar todos los PDFs en la raíz de data/
    files = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR) if f.endswith(".pdf")]
    
    if not files:
        logger.warning(f"No se encontraron archivos PDF en {DATA_DIR}.")
        return

    logger.info(f"Se han encontrado {len(files)} archivos para procesar.")
    
    for file_path in files:
        await ingest_file(file_path)
    
    logger.info("--- Proceso de ingesta masiva completado ---")

if __name__ == "__main__":
    asyncio.run(main())
