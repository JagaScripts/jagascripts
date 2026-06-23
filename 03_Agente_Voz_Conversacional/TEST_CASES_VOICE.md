# 🧪 Plan de Pruebas QA (Nivel Experto): Cobertura Absoluta del Agente Smart Home

Este documento es la **Matriz de Certificación QA definitiva**. Contiene el 100% de los escenarios posibles, incluyendo "Happy Paths" (flujos ideales), "Edge Cases" (casos límite), recuperación de errores mediante "Slot Filling" (insistencia del bot) y flujos condicionales complejos.

Ningún agente debe pasar a producción sin completar el 100% de esta batería.

---

## 🛠️ Entorno de Pruebas (Pre-requisitos)

1. **Backend RAG Activo:** Ejecutar `uv run python backend/main.py`. Verificar conexión a ChromaDB y puerto 8000.
2. **Cliente de Voz Activo:** Ejecutar `uv run python voice_client.py`.
3. **Hardware:** Micrófono calibrado y altavoces/auriculares para verificar el TTS.

---

## 📋 MATRIZ DE CASOS DE PRUEBA (QA TEST SUITE)

### BLOQUE 1: Interacción Base (Intent 01)

| Test ID          | Objetivo           | Frase a decir (Usuario) | Resultado Esperado (Bot TTS)                                         | Estado |
| :--------------- | :----------------- | :---------------------- | :------------------------------------------------------------------- | :----: |
| **TC-1.1** | Saludo simple      | "Hola"                  | Enumera las 5 capacidades principales con el texto detallado exacto. |  [ ]  |
| **TC-1.2** | Petición de ayuda | "¿Qué puedes hacer?"  | Mismo resultado que TC-1.1. Verifica que sinónimos funcionan.       |  [ ]  |

### BLOQUE 2: Reporte de Fallos (Intent 02)

| Test ID            | Objetivo                | Frase a decir (Usuario)                     | Resultado Esperado (Bot TTS)                                                            | Estado |
| :----------------- | :---------------------- | :------------------------------------------ | :-------------------------------------------------------------------------------------- | :----: |
| **TC-2.1**   | Happy Path              | "Mi bombilla 123456 no funciona"            | "He registrado el problema para el dispositivo 123456..." (Flujo directo).              |  [ ]  |
| **TC-2.2**   | Slot Filling (Falta ID) | "Tengo un problema técnico"                | Prompt:*"Para registrar el fallo, necesito que me digas el código de 6 dígitos..."* |  [ ]  |
| **TC-2.2.1** | Recuperación Slot      | "Es el 112233" (Respuesta al prompt TC-2.2) | Captura el ID y finaliza: "He registrado el problema para el dispositivo 112233..."     |  [ ]  |

### BLOQUE 3: Consultas Técnicas RAG (Intent 03)

| Test ID          | Objetivo            | Frase a decir (Usuario)                                             | Resultado Esperado (Bot TTS)                                                                                     | Estado |
| :--------------- | :------------------ | :------------------------------------------------------------------ | :--------------------------------------------------------------------------------------------------------------- | :----: |
| **TC-3.1** | Happy Path          | "Necesito instrucciones de configuración"                          | Prompt:*"Por favor, dime el número del equipo: 1 Cámara Hikv... 2 Cerradura EZVIZ... 5 Termostato..."*       |  [ ]  |
| **TC-3.2** | Recuperación Slot  | "La 3" (Respuesta al prompt TC-3.1)                                 | El bot resuelve "la 3" como Hama (Bombilla) y devuelve la respuesta del RAG.                                     |  [ ]  |
| **TC-3.3** | Flujo Directo       | "Opción 1"                                                         | Salta directo al RAG de la Cámara Hikvision.                                                                    |  [ ]  |
| **TC-3.4** | Fallback de Webhook | (Simular apagando el backend o buscando un dispositivo inexistente) | Responde con el texto de fallback: "He consultado los manuales, pero no existe información sobre ese equipo..." |  [ ]  |

### BLOQUE 4: Vinculación Unificada (Intent 04)

| Test ID            | Objetivo              | Frase a decir (Usuario)       | Resultado Esperado (Bot TTS)                                                 | Estado |
| :----------------- | :-------------------- | :---------------------------- | :--------------------------------------------------------------------------- | :----: |
| **TC-4.1**   | Slot Filling (Inicio) | "Quiero añadir un aparato"   | Prompt:*"Perfecto. Por favor, dime el código numérico de 6 dígitos..."* |  [ ]  |
| **TC-4.1.1** | Recuperación Slot    | "112233" (Respuesta a TC-4.1) | "ID 112233 validado. La vinculación se ha completado..."                    |  [ ]  |
| **TC-4.2**   | Happy Path Inverso    | "Vincular dispositivo 999999" | Debe saltarse la pregunta e ir directo a "ID 999999 validado...".            |  [ ]  |

### BLOQUE 5: Estado de Soporte (Intent 05)

| Test ID          | Objetivo     | Frase a decir (Usuario)         | Resultado Esperado (Bot TTS)                                                         | Estado |
| :--------------- | :----------- | :------------------------------ | :----------------------------------------------------------------------------------- | :----: |
| **TC-5.1** | Happy Path   | "¿Cómo va mi ticket TK-1234?" | "Tu incidencia TK-1234 está en estado: PENDIENTE DE REVISIÓN."                     |  [ ]  |
| **TC-5.2** | Slot Filling | "Estado de mi reparación"      | Prompt:*"Para consultar el estado, necesito que me digas tu número de ticket..."* |  [ ]  |

### BLOQUE 6: Programación de Horarios (Intent 06)

| Test ID          | Objetivo                | Frase a decir (Usuario)            | Resultado Esperado (Bot TTS)                                                    | Estado |
| :--------------- | :---------------------- | :--------------------------------- | :------------------------------------------------------------------------------ | :----: |
| **TC-6.1** | Happy Path (Doble Slot) | "Programar termostato a las 10:00" | "Entendido. He programado tu termostato para las 10:00:00." (Accede al Webhook) |  [ ]  |
| **TC-6.2** | Falta Hora              | "Pon un horario para la bombilla"  | Prompt:*"¿A qué hora quieres configurar el horario?"*                       |  [ ]  |
| **TC-6.3** | Falta Dispositivo       | "Programar a las 15:00"            | Prompt:*"¿Qué dispositivo quieres programar?"*                              |  [ ]  |
| **TC-6.4** | Faltan Ambos            | "Calendario de encendido"          | Pide primero un dato, respondes, luego pide el otro, respondes, y finaliza.     |  [ ]  |

### BLOQUE 7: Compatibilidad (Intent 07)

| Test ID          | Objetivo     | Frase a decir (Usuario)      | Resultado Esperado (Bot TTS)                                               | Estado |
| :--------------- | :----------- | :--------------------------- | :------------------------------------------------------------------------- | :----: |
| **TC-7.1** | Happy Path   | "¿Es compatible con Alexa?" | "Nuestros equipos son 100% compatibles con Alexa."                         |  [ ]  |
| **TC-7.2** | Slot Filling | "Comprobar compatibilidad"   | Prompt:*"¿Con qué ecosistema quieres comprobar la compatibilidad...?"* |  [ ]  |

### BLOQUE 8: Reseteo Crítico (Intent 08 - Follow-up)

| Test ID          | Objetivo               | Frase a decir (Usuario)                 | Resultado Esperado (Bot TTS)                                                            | Estado |
| :--------------- | :--------------------- | :-------------------------------------- | :-------------------------------------------------------------------------------------- | :----: |
| **TC-8.1** | Slot + Follow-up YES   | 1. "Borrar todo"                        | Prompt:*"¿Qué dispositivo quieres resetear?"*                                       |  [ ]  |
|                  |                        | 2. "La cámara"                         | Pregunta crítica:*"¿Estás seguro de que quieres realizar el reseteo completo...?"* |  [ ]  |
|                  |                        | 3. "Sí"                                | "Procediendo al reseteo... Mantén el botón físico pulsado..."                        |  [ ]  |
| **TC-8.2** | Follow-up NO (Abortar) | 1. "Resetear de fábrica el termostato" | Va directo a la pregunta crítica:*"¿Estás seguro...?"*                             |  [ ]  |
|                  |                        | 2. "No"                                 | "Entendido. No se ha realizado ningún cambio."                                         |  [ ]  |

### BLOQUE 9: Citas Técnicas (Intent 09)

| Test ID          | Objetivo   | Frase a decir (Usuario)        | Resultado Esperado (Bot TTS)                                                                                       | Estado |
| :--------------- | :--------- | :----------------------------- | :----------------------------------------------------------------------------------------------------------------- | :----: |
| **TC-9.1** | Doble Slot | "Necesito un técnico en casa" | Prompt 1:*"¿Qué día te vendría bien...?"* -> Respondes -> Prompt 2: *"¿En qué horario...?"* -> Finaliza. |  [ ]  |

### BLOQUE 10: Garantías (Intent 10)

| Test ID           | Objetivo     | Frase a decir (Usuario)         | Resultado Esperado (Bot TTS)                                       | Estado |
| :---------------- | :----------- | :------------------------------ | :----------------------------------------------------------------- | :----: |
| **TC-10.1** | Happy Path   | "¿Mi enchufe tiene garantía?" | "Tu enchufe cuenta con una garantía de 2 años..."                |  [ ]  |
| **TC-10.2** | Slot Filling | "Quiero saber la garantía"     | Prompt:*"¿De qué dispositivo quieres consultar la garantía?"* |  [ ]  |

### BLOQUE 11: Casos Negativos y Recuperación (Robustez)

| Test ID           | Objetivo        | Frase a decir (Usuario)                           | Resultado Esperado (Bot TTS)                                           | Estado |
| :---------------- | :-------------- | :------------------------------------------------ | :--------------------------------------------------------------------- | :----: |
| **TC-11.1** | Fallback Nativo | "Me gustaría pedir una pizza de queso"           | Default Fallback Intent (ej. "No he entendido a qué te refieres..."). |  [ ]  |
| **TC-11.2** | Out of Context  | Decir "Sí" de la nada (sin estar en un reseteo). | Debería saltar el Fallback porque no hay contexto activo.             |  [ ]  |

---

## 📝 Certificación Final

Para considerar la Tarea 06 finalizada, marca todos los siguientes checkboxes tras realizar las pruebas de voz en tiempo real:

### Bloque 1: Interacción Base

- [X] TC-1.1 Saludo simple
- [X] TC-1.2 Petición de ayuda

### Bloque 2: Reporte de Fallos

- [X] TC-2.1 Happy Path
- [X] TC-2.2 Slot Filling (Falta ID)
- [X] TC-2.2.1 Recuperación Slot

### Bloque 3: Consultas Técnicas RAG

- [X] TC-3.1 Happy Path
- [X] TC-3.2 Slot Filling
- [X] TC-3.2.1 Recuperación Slot
- [X] TC-3.3 Fallback de Webhook

### Bloque 4: Vinculación Unificada

- [X] TC-4.1 Slot Filling (Inicio)
- [X] TC-4.1.1 Recuperación Slot
- [X] TC-4.2 Happy Path Inverso

### Bloque 5: Estado de Soporte

- [X] TC-5.1 Happy Path
- [X] TC-5.2 Slot Filling

### Bloque 6: Programación de Horarios

- [X] TC-6.1 Happy Path (Doble Slot)
- [X] TC-6.2 Falta Hora
- [X] TC-6.3 Falta Dispositivo
- [X] TC-6.4 Faltan Ambos

### Bloque 7: Compatibilidad

- [X] TC-7.1 Happy Path
- [X] TC-7.2 Slot Filling

### Bloque 8: Reseteo Crítico

- [X] TC-8.1 Slot + Follow-up YES
- [X] TC-8.2 Follow-up NO (Abortar)

### Bloque 9: Citas Técnicas

- [X] TC-9.1 Doble Slot

### Bloque 10: Garantías

- [X] TC-10.1 Happy Path
- [X] TC-10.2 Slot Filling

### Bloque 11: Robustez

- [X] TC-11.1 Fallback Nativo
- [X] TC-11.2 Out of Context
