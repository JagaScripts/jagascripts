# 02. RAG & Bases de Datos Vectoriales

Este proyecto explora la implementación de sistemas de **Recuperación Aumentada por Generación (RAG)**, una de las arquitecturas más demandadas en Inteligencia Artificial Generativa.

## 🎯 Contexto del Negocio
Las empresas poseen vastas cantidades de información interna (documentos, políticas) que los LLMs genéricos desconocen. La necesidad era construir un sistema que permitiera consultar información corporativa obteniendo respuestas precisas, sin alucinaciones y con referencias directas a las fuentes originales.

## 🛠️ Arquitectura y Stack
*   **Inteligencia Artificial:** Modelos de lenguaje Open Source y APIs integradas mediante LangChain.
*   **Bases de Datos Vectoriales:** Qdrant para indexación y búsqueda por similitud semántica.
*   **Procesamiento de Datos:** Python (Pandas) para la limpieza, chunking y generación de embeddings.

## 🧠 Retos Técnicos
*   **Estrategias de Chunking:** Dividir los documentos de forma inteligente para no perder el contexto semántico entre párrafos, crítico para una buena recuperación (retrieval).
*   **Optimización Vectorial:** Configurar Qdrant para realizar búsquedas rápidas limitando los resultados a los "Top K" más relevantes.
*   **Mitigación de Alucinaciones:** Restringir el prompt del LLM para que únicamente generase respuestas basadas en el contexto recuperado de la base de datos.

## 📈 Impacto y Resultados
*   *(Sección en edición)* Demostración empírica de cómo la combinación de bases de datos vectoriales y LLMs soluciona el problema de la memoria corporativa.
