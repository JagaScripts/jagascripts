"""Servicio RAG centralizado para indexación y consultas de documentos de phishing.

Utiliza LangChain + Qdrant + Google Gemini para:
- Cargar y procesar documentos PDF del directorio data/rag
- Generar embeddings y almacenarlos en una base de datos vectorial Qdrant
- Recuperar documentos similares a consultas
- Generar respuestas contextuales con atribución de fuentes
"""
from __future__ import annotations

import re
import unicodedata
import urllib.request
import hashlib
import json
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import ResponseHandlingException

from app.core.logging import get_logger, log_event
from app.core.settings import settings

logger = get_logger("services.rag")

_DOCS_DIR = Path(__file__).resolve().parent.parent / "data" / "rag"
_CHUNKS_DIR = _DOCS_DIR / "optimized_chunks"
_URLS_FILE = _DOCS_DIR / "URLs base conocimiento.txt"
_MANIFEST_FILE = _DOCS_DIR / ".manifest.json"
_URL_PATTERN = re.compile(r"^\s*-\s*(.+?)\s*:\s*(https?://\S+)\s*$", flags=re.IGNORECASE)
_RELEVANCE_THRESHOLD = 0.6


def _normalize(value: str) -> str:
    lowered = value.casefold().replace("phising", "phishing")
    normalized = unicodedata.normalize("NFKD", lowered)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    compact = re.sub(r"[^a-z0-9]+", "_", ascii_text)
    return re.sub(r"_+", "_", compact).strip()


def _file_checksum(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()


class RAGService:
    """Servicio RAG para indexación y consulta de documentos sobre phishing"""

    def __init__(self) -> None:
        self.qdrant_client = QdrantClient(url=settings.qdrant_url)
        self.embeddings: GoogleGenerativeAIEmbeddings | None = None
        self.llm: ChatGoogleGenerativeAI | None = None
        self.vector_store: QdrantVectorStore | None = None
        self._url_mapping_cache: dict[str, str] | None = None

    def _ensure_qdrant_connection(self) -> None:
        """Valida que Qdrant sea accesible.

        Raises:
            ValueError: Si Qdrant no responde o no está disponible.
        """
        try:
            self.qdrant_client.get_collections()
        except ResponseHandlingException as exc:
            log_event(
                logger,
                level=40,
                event="qdrant_connection_error",
                message="No se puede conectar a Qdrant",
                extra={"qdrant_url": settings.qdrant_url, "error": str(exc)},
            )
            raise ValueError(
                f"No se puede conectar a Qdrant ({settings.qdrant_url}). "
                "Verifica que el servicio esté corriendo. Ejecuta el siguiente comando: "
                "docker compose -f docker_compose.yml up -d qdrant"
            ) from exc

    def _ensure_models(self) -> None:
        """Inicializa modelos de embeddings y LLM (inicialización perezosa)

        Crea instancias de GoogleGenerativeAIEmbeddings y ChatGoogleGenerativeAI
        la primera vez que se llamam y las cachea.

        Raises:
            ValueError: Si GOOGLE_API_KEY no está configurada.
        """
        if not settings.google_api_key:
            log_event(
                logger,
                level=40,
                event="rag_config_error",
                message="GOOGLE_API_KEY no configurada",
            )
            raise ValueError("GOOGLE_API_KEY no está configurada en el entorno")

        if self.embeddings is None:
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/gemini-embedding-001",
                google_api_key=settings.google_api_key,
            )
            logger.info("Modelo de embeddings inicializado: models/gemini-embedding-001")

        if self.llm is None:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash-lite",
                google_api_key=settings.google_api_key,
                temperature=0.1,
            )
            logger.info("LLM inicializado: gemini-2.5-flash-lite")

    def _read_url_entries(self) -> list[tuple[str, str]]:
        """Parsea URLs base conocimiento.txt y devuelve lista de (título, url)."""
        if not _URLS_FILE.exists():
            return []
        entries = []
        for raw_line in _URLS_FILE.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line:
                continue
            match = _URL_PATTERN.match(line)
            if not match:
                continue
            entries.append((match.group(1).strip(), match.group(2).strip()))
        return entries

    def _ensure_pdfs_downloaded(self) -> None:
        """Descarga los PDFs que no existen localmente usando las URLs del archivo de conocimiento"""
        if not _URLS_FILE.exists():
            return

        _DOCS_DIR.mkdir(parents=True, exist_ok=True)

        for title, url in self._read_url_entries():
            pdf_path = _DOCS_DIR / f"{_normalize(title)}.pdf"

            if pdf_path.exists():
                logger.info("PDF ya existe: %s", pdf_path.name)
                continue

            try:
                logger.info("Descargando %s...", pdf_path.name)
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}  # noqa: E501
                req = urllib.request.Request(
                    url,
                    headers=headers,
                )
                with urllib.request.urlopen(req) as response:
                    content_type = response.headers.get("Content-Type", "")
                    if "pdf" not in content_type.lower():
                        log_event(
                            logger,
                            level=30,
                            event="rag_pdf_url_not_pdf",
                            message="La URL no devuelve un PDF",
                            extra={"title": title, "url": url, "content_type": content_type},
                        )
                        continue
                    pdf_path.write_bytes(response.read())
                logger.info("PDF descargado: %s", pdf_path.name)
            except Exception as exc:
                log_event(
                    logger,
                    level=30,
                    event="rag_pdf_download_failed",
                    message="No se pudo descargar el PDF",
                    extra={"file": pdf_path.name, "url": url, "error": str(exc)},
                )

    def _load_urls_mapping(self) -> dict[str, str]:
        """Carga el mapeo de nombres de PDF a URLs desde archivo.

        Parsea 'URLs base conocimiento.txt' buscando líneas con formato:
        '- Nombre PDF: https://url'

        Cachea el resultado para posteriores llamadas.

        Returns:
            Diccionario mapeando PDF normalizado a URL.
        """
        if self._url_mapping_cache is not None:
            return self._url_mapping_cache

        self._url_mapping_cache = {
            _normalize(title): url for title, url in self._read_url_entries()
        }
        return self._url_mapping_cache

    def _match_source_url(self, pdf_path: Path) -> str | None:
        """Busca la URL de fuente para un archivo PDF.

        Primero intenta coincidencia exacta. Si falla, usa coincidencia difusa
        (SequenceMatcher) con umbral del 55%.

        Args:
            pdf_path: Ruta al archivo PDF.

        Returns:
            URL de la fuente, o None si no se encuentra.
        """
        urls_mapping = self._load_urls_mapping()
        if not urls_mapping:
            return None

        return urls_mapping.get(_normalize(pdf_path.stem))

    def _load_pdf_documents(self) -> list[Document]:
        """Carga todos los archivos PDF del directorio de datos.

        Busca recursivamente archivos *.pdf, extrae páginas,
        y enriquece metadatos con nombre de archivo y URL de fuente.

        Returns:
            Lista de documentos LangChain extraidos de los PDFs.

        Raises:
            ValueError: Si directorio no existe o no hay PDFs.
        """
        if not _DOCS_DIR.exists():
            log_event(
                logger,
                level=40,
                event="rag_docs_dir_not_found",
                message="Directorio de documentos no existe",
                extra={"docs_dir": str(_DOCS_DIR)},
            )
            raise ValueError(
                f"Directorio de documentos no existe: {_DOCS_DIR}. "
                "Asegúrate de que URLs base conocimiento.txt está en data/rag/."
            )

        pdf_paths = sorted(p for p in _DOCS_DIR.rglob("*.pdf"))
        if not pdf_paths:
            log_event(
                logger,
                level=40,
                event="rag_no_pdfs_found",
                message="No se encontraron PDFs en el directorio de documentos",
                extra={"docs_dir": str(_DOCS_DIR)},
            )
            raise ValueError(f"No se encontraron PDFs en {_DOCS_DIR}")

        all_docs: list[Document] = []
        for pdf_path in pdf_paths:
            loader = PyPDFLoader(str(pdf_path))
            pages = loader.load()
            source_url = self._match_source_url(pdf_path)

            for page in pages:
                page.metadata = {
                    **(page.metadata or {}),
                    "file_name": pdf_path.name,
                    "file_stem": pdf_path.stem,
                    "source_url": source_url or "",
                }

            all_docs.extend(pages)
            logger.info("PDF cargado: %s (%d páginas)", pdf_path.name, len(pages))

        return all_docs

    def _load_manifest(self) -> dict[str, str]:
        """Carga el manifiesto de checksums de archivos ingestados."""
        if _MANIFEST_FILE.exists():
            try:
                return json.loads(_MANIFEST_FILE.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def _save_manifest(self, manifest: dict[str, str]) -> None:
        """Guarda el manifiesto de checksums."""
        _MANIFEST_FILE.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _compute_source_checksums(self, *, use_chunks: bool) -> dict[str, str]:
        """Calcula checksums agrupados por fuente.

        Para chunks: clave = base_stem (sin __chunk_*), hash combinado de todos sus chunks.
        Para PDFs: clave = filename, hash del PDF.
        """
        if use_chunks:
            if not _CHUNKS_DIR.exists():
                return {}
            by_base: dict[str, list[Path]] = {}
            for p in sorted(_CHUNKS_DIR.glob("*.txt")):
                base = p.stem.split("__chunk_")[0]
                by_base.setdefault(base, []).append(p)
            result: dict[str, str] = {}
            for base, paths in sorted(by_base.items()):
                h = hashlib.sha256()
                for p in sorted(paths):
                    h.update(p.name.encode())
                    h.update(_file_checksum(p).encode())
                result[base] = h.hexdigest()
            return result
        return {p.name: _file_checksum(p) for p in sorted(_DOCS_DIR.glob("*.pdf"))}

    def _delete_source_vectors(self, source_key: str) -> None:
        """Elimina de Qdrant todos los vectores cuyo metadata.file_name == source_key."""
        from qdrant_client.models import Filter, FieldCondition, MatchValue, FilterSelector

        self.qdrant_client.delete(
            collection_name=settings.qdrant_collection,
            points_selector=FilterSelector(
                filter=Filter(
                    must=[FieldCondition(
                        key="metadata.file_name",
                        match=MatchValue(value=source_key),
                    )]
                )
            ),
        )
        logger.info("Vectores eliminados de Qdrant para: %s", source_key)

    def ingest(self, recreate: bool = False) -> dict[str, str | int | list[str]]:
        """Indexa documentos en Qdrant.

        Estrategia:
        1. Compara checksums actuales con el manifiesto guardado y sólo reembedda
           fuentes nuevas o modificadas. Si no hay cambios y la colección existe,
           retorna inmediatamente sin llamar a la API de Gemini
        1. Prefer chunks pre-procesados si existen (más rápido)
        2. Sino, carga y divide PDFs
        3. Genera embeddings con Google Gemini
        4. Almacena en Qdrant con metadatos

        Args:
            recreate: Si True, recrea la colección (destruye datos existentes).

        Returns:
            Diccionario con estadísticas: nombre colección, páginas/chunks indexados,
            archivos indexados, URLs de fuentes y estados.

        Raises:
            ValueError: Si no hay documentos o falla conexión a Qdrant.
        """
        self._ensure_models()
        self._ensure_qdrant_connection()
        self._ensure_pdfs_downloaded()

        use_chunks = _CHUNKS_DIR.exists() and any(_CHUNKS_DIR.glob("*.txt"))
        collection_exists = self.qdrant_client.collection_exists(settings.qdrant_collection)

        manifest = self._load_manifest()
        current_checksums = self._compute_source_checksums(use_chunks=use_chunks)
        changed = {k for k, v in current_checksums.items() if manifest.get(k) != v}
        removed = {k for k in manifest if k not in current_checksums}

        if collection_exists and not recreate and not changed and not removed:
            logger.info(
                "RAG: sin cambios desde última ingesta, omitiendo",
                extra={"event": "rag_ingest_no_changes"},
            )
            return {
                "collection_name": settings.qdrant_collection,
                "indexed_pages": 0,
                "indexed_chunks": 0,
                "indexed_files": [],
                "indexed_urls": [],
                "status": "no_changes",
            }

        documents: list[Document] = []
        chunks: list[Document] = []
        ingestion_mode = "full" if (recreate or not collection_exists) else "incremental"

        if ingestion_mode == "full":
            if use_chunks:
                chunks = self._load_chunk_documents()
            else:
                documents = self._load_pdf_documents()
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=settings.cu04_chunk_size,
                    chunk_overlap=settings.cu04_chunk_overlap,
                )
                chunks = splitter.split_documents(documents)

            if not chunks:
                log_event(
                    logger,
                    level=40,
                    event="rag_ingest_no_chunks",
                    message="No se generaron chunks a partir de los documentos",
                )
                raise ValueError("No se generaron chunks a partir de los documentos")

            logger.info("Ingesta completa: %d chunks en Qdrant...", len(chunks))
            self.vector_store = QdrantVectorStore.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                url=settings.qdrant_url,
                collection_name=settings.qdrant_collection,
                force_recreate=True,
            )

        else:
            # Incremental: borrar vectores de fuentes cambiadas/eliminadas
            for source_key in changed | removed:
                self._delete_source_vectors(source_key)

            if changed:
                if use_chunks:
                    all_docs = self._load_chunk_documents()
                    new_docs = [
                        d for d in all_docs
                        if Path(str((d.metadata or {}).get("source", ""))).stem.split("__chunk_")[0] in changed
                    ]
                    chunks = new_docs
                else:
                    all_docs = self._load_pdf_documents()
                    new_docs = [d for d in all_docs if (d.metadata or {}).get("file_name", "") in changed]
                    documents = new_docs
                    splitter = RecursiveCharacterTextSplitter(
                        chunk_size=settings.cu04_chunk_size,
                        chunk_overlap=settings.cu04_chunk_overlap,
                    )
                    chunks = splitter.split_documents(new_docs)

                if chunks:
                    logger.info("Ingesta incremental: %d chunks nuevos/actualizados...", len(chunks))
                    QdrantVectorStore.from_documents(
                        documents=chunks,
                        embedding=self.embeddings,
                        url=settings.qdrant_url,
                        collection_name=settings.qdrant_collection,
                        force_recreate=False,
                    )
                    self.vector_store = None  # reset caché para que _get_vector_store() reconecte
            else:
                logger.info("RAG: solo eliminaciones, sin chunks nuevos")

        self._save_manifest(current_checksums)

        indexed_files = sorted({doc.metadata.get("file_name", "") for doc in chunks if doc.metadata})
        indexed_urls = sorted(
            {
                str(doc.metadata.get("source_url"))
                for doc in chunks
                if doc.metadata and doc.metadata.get("source_url")
            }
        )
        logger.info("Ingesta completada: %d chunks, %d archivos", len(chunks), len(indexed_files))

        return {
            "collection_name": settings.qdrant_collection,
            "indexed_pages": len(documents),
            "indexed_chunks": len(chunks),
            "indexed_files": indexed_files,
            "indexed_urls": indexed_urls,
            "status": ingestion_mode,
        }

    def _get_vector_store(self) -> QdrantVectorStore:
        """Obtiene o inicializa QdrantVectorStore para búsquedas de similitud.

        Carga perezosamente embeddings y conecta a colección Qdrant existente.
        Cachea después de primera recuperación.

        Returns:
            Instancia QdrantVectorStore conectada a colección configurada.

        Raises:
            ValueError: Si colección no existe o falla conexión.
        """
        self._ensure_models()
        self._ensure_qdrant_connection()

        if self.vector_store is not None:
            return self.vector_store

        if not self.qdrant_client.collection_exists(settings.qdrant_collection):
            log_event(
                logger,
                level=30,
                event="rag_collection_not_found",
                message="Colección no encontrada en Qdrant",
                extra={"collection": settings.qdrant_collection},
            )
            raise ValueError("Collection not found. Run POST /ingest before asking questions.")

        logger.info("Conectando a colección existente: %s", settings.qdrant_collection)
        self.vector_store = QdrantVectorStore.from_existing_collection(
            embedding=self.embeddings,
            url=settings.qdrant_url,
            collection_name=settings.qdrant_collection,
        )
        return self.vector_store

    def ask(self, question: str) -> dict[str, str | list[str]]:
        """Responde una pregunta usando RAG (Generación Aumentada con Recuperación).

        Proceso:
        1. Recupera documentos más similares del índice vectorial
        2. Construye contexto con esos documentos
        3. Genera respuesta con Google Gemini usando el contexto
        4. Extrae y retorna URLs de fuentes para atribución
        5. Si no hay URL retorna el nombre del archivo

        Args:
            question: Pregunta del usuario sobre phishing.

        Returns:
            Diccionario con:
            - 'answer': Respuesta generada con fuentes adjuntas
            - 'sources': Lista de URLs de fuentes usadas

        Raises:
            ValueError: Si pregunta está vacía o colección no existe.
        """
        clean_question = question.strip()
        if not clean_question:
            log_event(
                logger,
                level=30,
                event="rag_empty_question",
                message="Pregunta vacía recibida en el servicio RAG",
            )
            raise ValueError("La pregunta no puede estar vacía")

        logger.info("Pregunta RAG recibida: %.80s", clean_question)

        store = self._get_vector_store()
        docs_with_scores = store.similarity_search_with_score(
            clean_question, k=settings.cu04_similarity_top_k
        )

        docs = [doc for doc, score in docs_with_scores if score >= _RELEVANCE_THRESHOLD]
        logger.info(
            "Documentos recuperados: %d relevantes de %d totales (umbral %.2f)",
            len(docs), len(docs_with_scores), _RELEVANCE_THRESHOLD,
        )

        if not docs:
            return {
                "answer": "No he encontrado información relevante en la base de conocimiento para responder esa pregunta.",  # noqa: E501
                "sources": [],
            }

        context = "\n\n".join(doc.page_content for doc in docs)
        prompt = (
            "Eres un asistente experto en phishing. Responde en espanol usando SOLO el contexto. "
            "Si el contexto no contiene suficiente informacion, dilo explicitamente. "
            "Devuelve una unica respuesta clara y directa, sin inventar datos.\n\n"
            f"Contexto:\n{context}\n\n"
            f"Pregunta: {clean_question}"
        )

        llm_response = self.llm.invoke(prompt)
        answer_text = (llm_response.content or "").strip()

        # URL si existe, nombre del PDF como fallback
        seen: set[str] = set()
        sources_display: list[str] = []
        sources_urls: list[str] = []
        for doc in docs:
            if not doc.metadata:
                continue
            url = doc.metadata.get("source_url", "")
            name = doc.metadata.get("file_name", "")
            source = url if url else name
            if source and source not in seen:
                seen.add(source)
                sources_display.append(source)
                if url:
                    sources_urls.append(url)

        sources_display.sort()
        sources_urls.sort()

        sources_block = "\n".join(f"- {s}" for s in sources_display) if sources_display else "- No disponibles"

        return {
            "answer": f"{answer_text}\n\nFuentes:\n{sources_block}",
            "sources": sources_urls,
        }


# Instancia singleton global de RAGService para que FastAPI la importe y use en endpoints
rag_service = RAGService()
