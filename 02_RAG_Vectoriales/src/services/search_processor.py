import logging

import qdrant_client
from llama_index.core import VectorStoreIndex, PromptTemplate
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.vector_stores.types import MetadataFilters, ExactMatchFilter
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.core import Settings
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
from src.config import settings

# Configuración del registro de eventos para trazabilidad de errores y reintentos
logger = logging.getLogger(__name__)


def _is_rate_limit_error(exception: BaseException) -> bool:
    """Detecta errores de límite de cuota (HTTP 429) o agotamiento de recursos del proveedor de LLM."""
    error_msg = str(exception).lower()
    return (
        "429" in error_msg
        or "resource exhausted" in error_msg
        or "rate limit" in error_msg
        or "resourceexhausted" in error_msg
    )


@retry(
    stop=stop_after_attempt(3), # Máximo 3 intentos para evitar bloqueos prolongados
    wait=wait_exponential(multiplier=2, min=2, max=60), # Reintento exponencial progresivo
    retry=retry_if_exception(_is_rate_limit_error),
    reraise=True,
    before_sleep=lambda retry_state: logger.warning(
        "Límite de tasa detectado. Reintentando en %.1fs (intento %d/%d)",
        retry_state.next_action.sleep,
        retry_state.attempt_number,
        3,
    ),
)
async def _query_with_retry(query_engine, query: str):
    """Ejecuta la consulta al LLM con lógica de reintento automático ante errores de cuota."""
    return await query_engine.aquery(query)

_index = None

def _get_index():
    global _index
    if _index is not None:
        return _index

    if settings.GEMINI_API_KEY == "dummy_key_for_testing" or not settings.GEMINI_API_KEY:
        from llama_index.core.llms import MockLLM
        from llama_index.core.embeddings import MockEmbedding
        Settings.llm = MockLLM(max_tokens=64)
        Settings.embed_model = MockEmbedding(embed_dim=3072)
    else:
        Settings.llm = GoogleGenAI(model=settings.MODEL_NAME, api_key=settings.GEMINI_API_KEY)
        Settings.embed_model = GoogleGenAIEmbedding(model_name=settings.EMBEDDING_MODEL, api_key=settings.GEMINI_API_KEY)

    client = qdrant_client.QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT, timeout=60)
    aclient = qdrant_client.AsyncQdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT, timeout=60)
    
    vector_store = QdrantVectorStore(
        client=client,
        aclient=aclient,
        collection_name=settings.COLLECTION_NAME
    )
    # Orquestador del índice vectorial usando el almacenamiento en Qdrant
    _index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    return _index


async def perform_search(query: str):
    index = _get_index()

    # Filtro estricto de metadatos para resolver el problema de la información actualizada
    # Solo recuperamos fragmentos que tengan el estado 'active'
    filters = MetadataFilters(
        filters=[ExactMatchFilter(key="status", value="active")]
    )

    qa_template_str = (
        "Context information is below.\n"
        "---------------------\n"
        "{context_str}\n"
        "---------------------\n"
        "Given the context information and not prior knowledge, answer the query.\n"
        "If you don't know the answer or the context does not contain relevant information, "
        "explicitly state 'I do not possess the information.' Do not hallucinate.\n"
        "Query: {query_str}\n"
        "Answer: "
    )
    qa_template = PromptTemplate(qa_template_str)

    # Configuración del motor de búsqueda con el filtro de obsolescencia y plantilla personalizada
    query_engine = index.as_query_engine(
        filters=filters,
        similarity_top_k=5,
        text_qa_template=qa_template
    )

    response = await _query_with_retry(query_engine, query)

    source_nodes = []
    for node in response.source_nodes:
        source_nodes.append({
            "text": node.node.get_content(),
            "metadata": node.node.metadata,
            "score": node.score or 0.0
        })

    return str(response), source_nodes