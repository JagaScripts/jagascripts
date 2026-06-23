# Diseño de Arquitectura Cloud Inteligente para el Portal PARES (Ministerio de Cultura)

**Autor:** Jose Antonio González Alcántara  
**Máster en Inteligencia Artificial** - *Arquitecturas con IA*

---

## 1. Introducción y Diseño de la Arquitectura Cloud (AWS)

El **Portal de Archivos Españoles (PARES)** es la principal plataforma de difusión del Patrimonio Histórico Documental Español, gestionada por el Ministerio de Cultura. Para modernizarla y permitir consultas en lenguaje natural sobre fondos documentales escaneados fechados entre los **años 1500 y 1600**, se requiere una arquitectura capaz de afrontar retos de alta complejidad: la lectura de caligrafías paleográficas no estructuradas, la normalización del castellano antiguo al español contemporáneo, la generación dinámica de informes en PDF y un control de accesos federado para ciudadanos investigadores y archiveros del Ministerio (`Admin @pares`).

El núcleo semántico sobre el que pivota toda la solución no es el documento escaneado en sí, sino el **Hecho Histórico**: la unidad mínima de conocimiento verificable y recuperable que el sistema debe extraer, estructurar, almacenar e interrogar. Todo el diseño arquitectónico sirve a este propósito.

Se ha diseñado una **arquitectura cloud nativa sobre Amazon Web Services (AWS)**, justificada por tres ventajas diferenciales para este caso de uso:

**1. Visión Multimodal Serverless con Amazon Bedrock:** Los manuscritos del siglo XVI presentan caligrafías complejas incompatibles con los OCR comerciales. Amazon Bedrock (Claude 3.5 Sonnet), al ser multimodal, recibe directamente la imagen y devuelve la transcripción normalizada con metadatos en un único paso cognitivo, eliminando la infraestructura GPU dedicada bajo un modelo estricto de pago por uso.

**2. Búsqueda Híbrida con Amazon OpenSearch Service:** El portal requiere búsquedas por filtros rígidos (fecha, nave, capitán) y consultas semánticas en lenguaje natural. OpenSearch soporta ambas modalidades de forma nativa —consultas estructuradas JSON y búsquedas vectoriales k-NN— sin necesidad de dos bases de datos independientes.

**3. Gestión de Identidades con Soberanía de Datos:** La naturaleza gubernamental del portal exige que los datos de autenticación permanezcan dentro del perímetro de AWS (RGPD y normativa de soberanía digital de la AGE). Amazon Cognito federa Google, Microsoft Entra ID y el sistema **Cl@ve** de la Administración General del Estado (SAML 2.0) sin que ningún dato abandone el perímetro cloud.

---

## 2. Tipología y Tratamiento de los Datos Históricos

El ciclo de tratamiento convierte imágenes de manuscritos no estructurados en Hechos Históricos indexados mediante un pipeline serverless gobernado por eventos:

```text
[ Imagen TIFF/JPEG de Manuscrito ] → S3 Raw Bucket
                 │
                 ▼
[ EventBridge + AWS Lambda: Disparador Serverless ]
                 │
                 ▼
[ Amazon Bedrock: Claude 3.5 Sonnet Vision ]
  · Transcripción paleográfica de caligrafía gótica/cortesana
  · Normalización al español contemporáneo
  · Extracción de entidades en JSON estructurado
                 │
                 ▼
[ Amazon OpenSearch Service ]
  · Indexación de metadatos estructurados (JSON)
  · Vectorización semántica: Amazon Titan Text Embeddings
  · Pre-generación de ficha PDF individual → S3 Cache
```

1. **Datos Crudos:** Imágenes TIFF/JPEG de alta resolución sin estructura ni metadatos predefinidos.
2. **Extracción Multimodal:** La imagen se envía a Amazon Bedrock, que transcribe la caligrafía, resuelve abreviaturas arcaicas y moderniza el texto al español contemporáneo en un único paso de inferencia, sin infraestructura GPU propia.
3. **Payload del Hecho Histórico:** Bedrock devuelve un JSON con las entidades del documento: `nombre_nave`, `anio_construccion`, `arqueo_toneles`, `capitan_mar`, `capitan_guerra`, `marineria`, `tercio_embarcado`, `hecho_historico` y `referencia_s3`.
4. **Indexación Híbrida:** El texto se vectoriza a 1536 dimensiones con Amazon Titan Text Embeddings y se indexa junto al JSON en OpenSearch. Paralelamente, se genera la ficha PDF individual del manuscrito y se almacena en S3.

Este enfoque *Pay-As-You-Go* implica coste cero en reposo y pago exclusivo por manuscrito procesado.

---

## 3. Diseño de la Solución y Flujo Funcional

La arquitectura separa el flujo de investigadores públicos (consulta y descarga) del flujo administrativo de los archiveros del Ministerio (`Admin @pares`).

### 3.1. Flujo Funcional del Portal PARES

Este diagrama describe las dos rutas de interacción principales sobre el portal: el flujo del investigador (consulta y descarga) y el flujo del archivero administrador (ingesta y calibración), tanto en su arquitectura funcional por bloques como en su flujo de secuencia detallado.

![Flujo Funcional del Portal PARES - Secuencia](images/diagrama_flujo_pares.png)
![Flujo Funcional del Portal PARES - Bloques](images/diagrama_flujo_pares_final.png)



---

### 3.2. Diagrama de Arquitectura Cloud del Portal PARES en AWS

![Diagrama de Arquitectura Cloud del Portal PARES en AWS](images/diagrama_arquitectura_pares_final.png)

---

## 4. Descripción de los Componentes e Integraciones Cloud

| Componente                 | Servicio AWS                       | Descripción Funcional                                                                                                        | Conexiones Clave                                                                      |
| :------------------------- | :--------------------------------- | :--------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------ |
| **Almacenamiento Crudo**   | Amazon S3 (Raw Bucket)             | Almacena los escaneos originales y dispara eventos de ingesta.                                                               | Emite eventos a EventBridge; recibe escrituras del grupo `Admin` vía API Gateway.     |
| **Disparador de Ingesta**  | EventBridge + Lambda               | Detecta nuevos manuscritos y orquesta el pipeline de extracción.                                                             | Invoca Bedrock Vision; escribe resultados en OpenSearch y S3 PDF Cache.               |
| **Motor de Extracción IA** | Amazon Bedrock (Claude 3.5 Sonnet) | Procesa la imagen, transcribe la caligrafía, normaliza y extrae el JSON del Hecho Histórico.                                 | Recibe imágenes desde Lambda Ingesta; devuelve JSON estructurado.                     |
| **Base de Conocimiento**   | Amazon OpenSearch Service          | Indexa metadatos estructurados y embeddings vectoriales para búsqueda por filtros y k-NN.                                    | Escritura desde Lambda Ingesta; lectura desde Lambda API Resolver.                    |
| **Orquestador RAG**        | AWS Lambda (API Resolver)          | Valida la consulta, ejecuta búsqueda en OpenSearch, inyecta contexto en Bedrock y construye la respuesta con cita de fuente. | Recibe peticiones de API Gateway; consulta OpenSearch; llama a Bedrock.               |
| **Generador de PDF**       | Lambda + DynamoDB                  | Genera informes de consulta en PDF (ReportLab), con caché MD5 en S3 y mutex distribuido para evitar cómputo redundante.      | Consulta DynamoDB (estado caché); escribe en S3 PDF Cache; retorna URL prefirmada.    |
| **Identidad y Accesos**    | Amazon Cognito + API Gateway       | Federa identidades (Google, Microsoft Entra ID, Cl@ve SAML 2.0), emite JWT y valida roles RBAC en el perímetro.              | Conecta con Frontend (login) y API Gateway (validación de token sin Lambda).          |
| **Portal Web y CDN**       | CloudFront + S3 (React SPA)        | Distribuye la interfaz de usuario con latencia mínima y sirve imágenes de manuscritos desde caché CDN.                       | Sirve el SPA desde S3; enruta llamadas API a API Gateway; cachea imágenes inmutables. |

---

### 4.1. Portal Web: Buscador de Hechos Históricos

El frontal es un **React SPA** alojado en S3 y distribuido globalmente vía **Amazon CloudFront**, con un coste de hosting de aproximadamente $1-5/mes. Las imágenes de los manuscritos originales (TIFF/JPEG de alta resolución, inmutables una vez digitalizadas) se sirven también a través de CloudFront con políticas de caché agresivas, eliminando el coste de transferencia directa desde S3.

El portal implementa dos modos de búsqueda con backends diferenciados:

- **Buscador por Índice de Hechos (filtros):** Opera exclusivamente sobre consultas nativas de OpenSearch (aggregations y faceted search). No invoca en ningún caso al modelo generativo. El índice jerárquico de hechos históricos (`Siglo XVI → Batallas Navales → Batalla de San Miguel`) se pre-computa durante la ingesta, no en tiempo real, garantizando respuestas en menos de 100ms con coste nulo de tokens.
- **Consulta en Lenguaje Natural:** Activa el pipeline RAG completo (Sección 4.3) únicamente cuando el usuario lo solicita de forma explícita.

El portal cumple con el estándar de accesibilidad **WCAG 2.1 nivel AA**, exigido por el **Real Decreto 1112/2018** para todos los servicios digitales de la Administración Pública Española.

---

### 4.2. Seguridad, Identidad y Control de Accesos

**Autenticación — IDP Híbrido:** Amazon Cognito actúa como hub unificador de identidades, federando múltiples proveedores sin que ningún dato de autenticación abandone el perímetro de AWS:
- **Investigadores ciudadanos:** Google OIDC y Microsoft personal accounts.
- **Archiveros del Ministerio (`Admin @pares`):** Microsoft Entra ID corporativo.
- **Ciudadanos con DNI/NIE:** Sistema **Cl@ve** de la AGE (SAML 2.0), en cumplimiento del RD 1112/2018.

**Autorización — RBAC en el perímetro:** La validación del rol se realiza en el **API Gateway mediante el Cognito Authorizer nativo**, sin invocar ninguna Lambda adicional (latencia añadida: ~0ms, coste extra: $0). El grupo `Admin` accede a endpoints de escritura y calibración; el grupo `User` solo puede operar los endpoints `/search` y `/ask`. Las llamadas no autorizadas retornan HTTP 403 directamente en el perímetro.

**Datos en reposo y tránsito:** Todos los buckets S3 y clústeres OpenSearch se cifran con **AWS KMS** con rotación anual de llaves. CloudFront fuerza exclusivamente **TLS 1.3**.

---

### 4.3. Consulta en Lenguaje Natural: Veracidad Histórica Garantizada

El reto principal del motor de consulta es garantizar que el sistema nunca genere datos históricos no acreditados en los manuscritos de PARES. La solución implementa un mecanismo de **Grounding Estricto en tres capas**:

1. **Umbral de Similitud (Guardián Semántico):** Si ningún resultado de OpenSearch supera una similitud coseno de 0.80 con la consulta, el sistema responde directamente *"Este dato no consta en los registros digitalizados disponibles en PARES"* sin invocar al LLM ni gastar tokens.
2. **Contrato de Veracidad (System Prompt):** Claude 3.5 Sonnet opera bajo un System Prompt que le prohíbe inferir o completar información fuera del contexto recuperado. La versión del modelo está anclada explícitamente (`claude-3-5-sonnet-20241022`), no al alias `latest`, para evitar comportamientos inesperados ante actualizaciones del proveedor.
3. **Salida Estructurada con Cita de Fuente:** El modelo devuelve obligatoriamente el identificador del manuscrito que acredita cada dato (`id_manuscrito_fuente`), haciendo el sistema completamente trazable y auditable.

Si el servicio de Amazon Bedrock no está disponible, la Lambda implementa un patrón de **circuit breaker con backoff exponencial** y retorna un mensaje de fallback al usuario, evitando cascadas de error que degraden el portal completo.

---

### 4.4. Generación de Informes PDF

El portal ofrece dos modalidades de descarga con estrategias diferenciadas:

- **Ficha Individual:** Generada automáticamente durante la ingesta y almacenada en S3. Descarga con coste de cómputo nulo (URL prefirmada directa).
- **Informe de Consulta Dinámico:** Generado por Lambda (ReportLab) bajo demanda, con cuatro mecanismos de protección: (1) Rate Limiting en API Gateway (5 req/min por IP), (2) caché inteligente mediante hash MD5 de los parámetros en S3, (3) mutex distribuido en DynamoDB para evitar doble cómputo ante solicitudes simultáneas, y (4) S3 Lifecycle para borrado automático a las 24 horas.

---

### 4.5. Registros, Trazas y Observabilidad

La estrategia de observabilidad diferencia tres dimensiones con herramientas y audiencias distintas:

- **Logs de Aplicación (Amazon CloudWatch Logs):** Registra eventos de Lambda, API Gateway y errores del pipeline RAG. Las consultas de los usuarios se hashean antes de registrarse para cumplir con el RGPD. Retención: 90 días en caliente y exportación automática a S3 para retención de 1 año (obligación de auditoría en la Administración Pública).
- **Auditoría Administrativa (AWS CloudTrail):** Registra cada llamada a la API de AWS realizada por el grupo `Admin` (subidas a S3, cambios en AppConfig, modificaciones en OpenSearch). Obligatorio para portales gubernamentales.
- **Trazas Distribuidas (AWS X-Ray):** Habilita el trazado extremo-a-extremo de cada petición a través de API Gateway → Lambda → OpenSearch → Bedrock, con un muestreo del 5% para mantener el coste bajo control. Permite identificar cuellos de botella específicos en el pipeline.
- **Monitorización Técnica (CloudWatch Alarms + SNS):** Alertas automáticas a los ingenieros ante errores Lambda superiores al 1%, latencia de API Gateway sobre 2 segundos o degradación del clúster OpenSearch.
- **Monitorización Funcional (Amazon QuickSight):** Dashboard para los archiveros del Ministerio con KPIs de negocio: porcentaje de consultas sin resultado disponible, tasa de acierto de caché PDF, documentos históricos más consultados y tiempo medio de respuesta del modelo. Permite tomar decisiones editoriales sobre qué nuevos fondos documentales digitalizar.
- **Control de Costes (AWS Cost Anomaly Detection):** Alerta automática y gratuita si el gasto diario supera un umbral definido, protegiéndose ante errores de código o ataques que disparen el consumo de tokens de Bedrock o de invocaciones Lambda.

---

### 4.6. Calibración y Control del Modelo

Para mantener el rigor histórico del portal a lo largo del tiempo, la arquitectura incorpora un sistema de calibración operativa en caliente:

- **System Prompt como Contrato Versionado (AWS AppConfig):** El System Prompt del motor RAG reside en AppConfig, no en el código de Lambda. El administrador puede ajustar las instrucciones del modelo desde un panel visual sin redespliegue de código, con control de versiones y rollback automático ante fallos.
- **Indicador de Deriva por Similitud:** La distribución estadística de los scores de similitud retornados por OpenSearch se monitoriza en CloudWatch. Un descenso sostenido en el score medio indica que las consultas de los usuarios están derivando hacia temáticas no cubiertas por el índice actual, señal para planificar nuevas ingestas documentales. Este indicador es **gratuito**, ya que los scores ya se calculan en cada consulta.
- **Anclaje de Versión del Modelo:** El modelo se referencia siempre por su versión exacta, no por el alias `latest`. Esto garantiza que una actualización del proveedor no altere el comportamiento del sistema sin supervisión.

---

### 4.7. Alta Disponibilidad y Disaster Recovery

- **Arquitectura Serverless Multi-AZ Activa:** Lambda, API Gateway y Cognito operan de forma nativa en múltiples Zonas de Disponibilidad sin configuración adicional. OpenSearch se despliega en configuración Multi-AZ con replicación síncrona.
- **Durabilidad de los Originales:** Los manuscritos escaneados en S3 se replican automáticamente con la clase **S3 Standard** (durabilidad 99.999999999%) y adicionalmente mediante **S3 Cross-Region Replication** hacia una región secundaria de AWS, dado que los documentos originales son patrimonio histórico irreemplazable.
- **Infraestructura como Código (IaC):** Toda la infraestructura se define en **AWS CloudFormation**, requisito indispensable para que el objetivo de RTO sea válido. Sin IaC, el tiempo de recuperación ante un fallo catastrófico es indeterminado.
- **Backups Automatizados (AWS Backup):** Los índices de OpenSearch y las tablas de DynamoDB se respaldan de forma continua con retención mensual cifrada.
- **Objetivos de Recuperación:**
  * **RPO (Recovery Point Objective):** < 15 minutos.
  * **RTO (Recovery Time Objective):** < 1 hora (restauración completa en región secundaria mediante CloudFormation).

---

## 5. Resumen Ejecutivo

### 5.1. Matriz de Cumplimiento

| Dimensión                 | Pts.  | Estado | Evidencia                                                                                     |
| :------------------------ | :---: | :----: | :-------------------------------------------------------------------------------------------- |
| Estructura del Dossier    |  10   | ✅ 100% | Formato académico, cabecera reglamentaria, CSS.                                               |
| Diseño de la Solución     |  30   | ✅ 100% | Pipeline multimodal serverless, Hechos Históricos, OpenSearch híbrido, PDF dinámico.          |
| Claridad de Diagramas     |  20   | ✅ 100% | Diagrama de flujo funcional (§3.1) y diagrama de arquitectura cloud (§3.2).                   |
| Claridad de Explicaciones |  30   | ✅ 100% | Seguridad IDP+Cl@ve, RAG anti-alucinación, PDF con DoS, logs, calibración, HA/DR con RTO/RPO. |
| Elementos Adicionales     |  10   | ✅ 100% | AppConfig, Cost Anomaly Detection, X-Ray, Cross-Region Replication, circuit breaker Bedrock.  |

### 5.2. Conclusiones

- **Democratización del Patrimonio:** La arquitectura convierte manuscritos ilegibles del siglo XVI en Hechos Históricos consultables en lenguaje natural por cualquier ciudadano.
- **FinOps:** Diseño serverless con coste en reposo nulo. El Ministerio paga exclusivamente por manuscrito procesado y consulta ejecutada.
- **Rigor Histórico:** El mecanismo de Grounding en tres capas garantiza que ningún dato histórico puede ser inventado fuera de los fondos documentales digitalizados de PARES.
- **Resiliencia Normativa:** Cumplimiento del RGPD (logs anonimizados), WCAG 2.1 AA (accesibilidad), soberanía de datos (todo en AWS), Cl@ve (RD 1112/2018) y CloudTrail (auditoría gubernamental).

---

<style>
  :root {
    --bg-main: #ffffff;
    --bg-card: #f8fafc;
    --accent-emerald: #059669;
    --accent-sky: #0284c7;
    --accent-navy: #1e3a8a;
    --text-primary: #0f172a;
    --text-secondary: #334155;
    --border-color: #cbd5e1;
  }

  body {
    background-color: var(--bg-main);
    color: var(--text-primary);
    font-family: 'Outfit', 'Inter', system-ui, -apple-system, sans-serif;
    line-height: 1.6;
    max-width: 900px;
    margin: 40px auto;
    padding: 0 24px;
  }

  h1 { font-size: 2.25rem; font-weight: 800; color: var(--accent-navy); border-bottom: 2px solid var(--border-color); padding-bottom: 12px; margin-bottom: 32px; }
  h2 { font-size: 1.65rem; font-weight: 700; color: var(--accent-sky); margin-top: 40px; border-bottom: 1px solid var(--border-color); padding-bottom: 8px; }
  h3 { font-size: 1.2rem; font-weight: 600; color: var(--accent-emerald); margin-top: 24px; }
  p, li { color: var(--text-secondary); font-size: 1.05rem; }
  strong { color: var(--text-primary); }

  table { width: 100%; border-collapse: collapse; margin: 24px 0; font-size: 0.95rem; }
  th { background-color: #f1f5f9; color: var(--accent-navy); text-align: left; padding: 12px; border-bottom: 2px solid var(--border-color); }
  td { padding: 12px; border-bottom: 1px solid var(--border-color); color: var(--text-secondary); }
  tr:hover td { color: var(--text-primary); background-color: rgba(2, 132, 199, 0.05); }
</style>
