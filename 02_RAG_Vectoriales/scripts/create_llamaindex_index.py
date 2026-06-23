import os
import json
import logging
import sys
import qdrant_client

# Añadimos el directorio raíz al path para que encuentre 'src'
sys.path.append(os.getcwd())

from qdrant_client.models import VectorParams, Distance
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI
from src.config import settings

# Configuración del logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Indexer")

async def create_index_from_processed_chunks(data_path: str = "data/optimized_chunks", summaries_path: str = "data/summaries.json"):
    logger.info("Iniciando proceso de indexación masiva.")
    
    if not os.path.exists(data_path):
        logger.critical(f"Directorio de datos no encontrado: {data_path}")
        return
    
    # Cargar resúmenes
    summaries = {}
    if os.path.exists(summaries_path):
        logger.debug(f"Cargando resúmenes desde: {summaries_path}")
        with open(summaries_path, "r", encoding="utf-8") as f:
            summaries = json.load(f)
        logger.info(f"Se cargaron {len(summaries)} resúmenes de secciones.")
    else:
        logger.warning(f"No se encontró el archivo de resúmenes en {summaries_path}. Los metadatos estarán incompletos.")

    # Configuración de LLM y Embeddings
    logger.info(f"Configurando LLM ({settings.MODEL_NAME}) y Embeddings ({settings.EMBEDDING_MODEL})")
    try:
        embed_model = GoogleGenAIEmbedding(model_name=settings.EMBEDDING_MODEL, api_key=settings.GEMINI_API_KEY)
        llm = GoogleGenAI(model=settings.MODEL_NAME, api_key=settings.GEMINI_API_KEY)
        
        Settings.llm = llm
        Settings.embed_model = embed_model
        Settings.chunk_size = settings.CHUNK_SIZE
        Settings.chunk_overlap = settings.CHUNK_OVERLAP
        logger.debug("Componentes de LlamaIndex configurados correctamente.")
    except Exception as e:
        logger.critical(f"Error al configurar componentes de IA: {e}")
        raise

    # Cargar documentos (mini-pdfs)
    logger.info(f"Leyendo mini-PDFs desde: {data_path}")
    try:
        reader = SimpleDirectoryReader(input_dir=data_path, recursive=False)
        documents = reader.load_data()
        logger.info(f"Se cargaron {len(documents)} páginas de mini-PDFs.")
    except Exception as e:
        logger.error(f"Error al leer documentos: {e}")
        raise

    # Enriquecer documentos con metadatos del resumen original
    logger.info("Enriqueciendo documentos con metadatos de secciones...")
    for doc in documents:
        file_name = doc.metadata.get("file_name", "")
        if file_name in summaries:
            doc.metadata["section_title"] = summaries[file_name]["title"]
            # Truncamos el resumen para evitar errores de tamaño de metadatos en Qdrant
            summary_text = summaries[file_name]["summary"]
            doc_id = file_name.split('.')[0] # Usamos el nombre del archivo como ID único base
            doc.metadata["doc_id"] = doc_id
            doc.metadata["section_summary"] = (summary_text[:1000] + "...") if len(summary_text) > 1000 else summary_text
            logger.debug(f"Metadatos añadidos para: {file_name}")
        # Marcamos como 'active' por defecto en la fase de indexación inicial
        doc.metadata["status"] = "active" 

    # Configuración de Qdrant
    logger.info(f"Conectando a Qdrant en {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
    try:
        client = qdrant_client.QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT, timeout=60)
        aclient = qdrant_client.AsyncQdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT, timeout=60)
        
        # Verificar o crear colección
        collections = client.get_collections().collections
        exists = any(c.name == settings.COLLECTION_NAME for c in collections)
        
        if not exists:
            logger.info(f"Creando nueva colección: {settings.COLLECTION_NAME} con dim=3072")
            client.create_collection(
                collection_name=settings.COLLECTION_NAME,
                vectors_config=VectorParams(size=3072, distance=Distance.COSINE) # Configuración para Gemini Embedding
            )

        else:
            logger.info(f"Usando colección existente: {settings.COLLECTION_NAME}")
            
        vector_store = QdrantVectorStore(
            collection_name=settings.COLLECTION_NAME, 
            client=client, 
            aclient=aclient
        )
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        logger.debug("Storage Context de Qdrant listo.")
    except Exception as e:
        logger.critical(f"Error fatal de conexión con Qdrant: {e}")
        raise

    # Crear el índice e insertar documentos
    logger.info("Iniciando proceso de embedding e inserción en Qdrant (esto puede tardar)...")
    try:
        index = VectorStoreIndex.from_documents(
            documents, 
            storage_context=storage_context,
            show_progress=True
        )
        logger.info(f"Indexación completada con éxito en la colección '{settings.COLLECTION_NAME}'.")
    except Exception as e:
        logger.error(f"Error durante la creación del índice: {e}")
        logger.critical("La base de datos vectorial podría estar en un estado inconsistente.")
        raise

if __name__ == "__main__":
    asyncio.run(create_index_from_processed_chunks())
