# 10. Diseño de Arquitecturas Cloud y Servicios de IA

Este repositorio recopila una serie de diseños arquitectónicos avanzados y planes estratégicos desarrollados durante el Máster en Inteligencia Artificial, Cloud Computing & DevOps.

## 🎯 Contexto del Negocio
Las soluciones basadas en IA no operan en el vacío; requieren ecosistemas cloud escalables, seguros y rentables. El objetivo de esta serie de entregas era diseñar arquitecturas completas que resuelvan problemas empresariales (Portales documentales, Chatbots, Voicebots, RAGs, Agentes LangChain) asegurando que el diseño cumpla con los más altos estándares empresariales.

## 🛠️ Arquitectura y Stack
*   **Proveedores Cloud:** Amazon Web Services (AWS), Microsoft Azure.
*   **Servicios AI/ML:** Amazon Bedrock, Amazon Lex, Azure OpenAI, Amazon Transcribe.
*   **Servicios de Integración:** AWS Lambda, API Gateway, Amazon Cognito, Azure Cache for Redis, AWS Secrets Manager.
*   **Diseño:** AWS Architecture Diagrams, Modelado de flujos y pipelines.

## 🧠 Retos Técnicos
*   **Seguridad y Zero-Trust:** Diseñar sistemas de autenticación robustos mediante roles IAM, Managed Identities (Entra ID) y orquestadores (API Gateway con Cognito) sin depender de credenciales estáticas o contraseñas hardcodeadas.
*   **Control de Costes (FinOps):** Implementar estrategias de mitigación de costes, como cachés semánticos (Redis) para evitar invocar al LLM en consultas redundantes y reducir el gasto en tokens hasta un 90%.
*   **Optimización de Latencia:** Reemplazar llamadas costosas a LLMs por flujos en Amazon Lex o búsquedas vectoriales rápidas (OpenSearch) para mantener la respuesta por debajo de los 100 milisegundos.

## 📈 Impacto y Resultados
*   *(Sección en edición)* Diseños validados y listos para implementarse en entornos de producción reales, demostrando no solo conocimientos técnicos de programación, sino también de FinOps, seguridad perimetral y estrategia empresarial a nivel de Arquitecto Cloud.
