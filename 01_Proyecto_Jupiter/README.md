# 01. Proyecto Júpiter (TFM - Phishing Detect)

Este proyecto forma parte de mi portafolio profesional, desarrollado como Trabajo de Fin de Máster (TFM) para el Máster en IA, Cloud Computing & DevOps (PontIA).

## 🎯 Contexto del Negocio
El phishing sigue siendo uno de los principales vectores de ataque en ciberseguridad. Las soluciones tradicionales basadas en reglas a menudo fallan ante ataques de nueva generación (Zero-day). El objetivo de Júpiter era crear un sistema automatizado de detección de amenazas capaz de interpretar el contexto de los correos electrónicos para clasificar su nivel de riesgo.

## 🛠️ Arquitectura y Stack
*   **Inteligencia Artificial:** Modelos de Lenguaje Grandes (LLMs) para análisis semántico.
*   **Bases de Datos Vectoriales:** Qdrant para almacenar y comparar embeddings de amenazas conocidas.
*   **Backend:** Python y orquestación de microservicios.
*   **Despliegue:** Arquitectura Cloud orientada a la escalabilidad.

## 🧠 Retos Técnicos
*   **Precisión vs. Falsos Positivos:** Ajustar el modelo LLM y la búsqueda vectorial para minimizar los falsos positivos que interrumpen la operativa del usuario, sin sacrificar la detección.
*   **Latencia:** Garantizar que la inferencia de los modelos y la búsqueda en Qdrant ocurriera en milisegundos.
*   **Integración:** Orquestar el flujo de datos desde la ingesta del mensaje hasta la base de datos vectorial y el modelo generativo.

## 📈 Impacto y Resultados
*   *(Sección en edición para reflejar las métricas del TFM)* Se logró un sistema altamente preciso capaz de detectar variaciones sutiles de phishing que evaden los filtros tradicionales.
*   Automatización del triage de seguridad, reduciendo el tiempo de análisis manual.
