import os
import json
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import uvicorn
import ngrok

# --- LIBRERIAS DE INTELIGENCIA ARTIFICIAL ---
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

# 1. Configuracion Inicial y Logs
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WebhookSmartHome")

app = FastAPI()

# 2. Inicializacion de Componentes IA (Solo una vez al arrancar)
gemini_key = os.getenv("GEMINI_API_KEY")

# Embeddings (HuggingFace Local - Ultra Rápido)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# --- CACHÉ PERSISTENTE EN DISCO ---
CACHE_FILE = "data/rag_cache.json"

def cargar_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def guardar_cache(cache):
    os.makedirs("data", exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=4)

consulta_cache = cargar_cache()

# Cargar la base de datos vectorial que creamos en la Tarea 04
vector_db = Chroma(
    persist_directory="./data/chroma_db", 
    embedding_function=embeddings
)

# Configurar el LLM (Google Gemini 1.5 Flash)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite", 
    google_api_key=gemini_key,
    temperature=0.7
)

# Definir un prompt conciso para evitar timeouts en Dialogflow
# Definir un prompt optimizado para soporte tecnico por voz
template = """Eres el experto de soporte técnico de Smart Home. Tu misión es dar instrucciones claras y breves basadas en los manuales.

CONTEXTO DE MANUALES:
{context}

PREGUNTA DEL USUARIO: {question}

REGLAS DE ORO:
1. Usa el contexto para dar una solución técnica directa.
2. Responde en máximo 2 o 3 frases cortas.
3. Si la información NO está en el contexto, di exactamente: "Lo siento, no he encontrado instrucciones específicas para ese equipo en los manuales."
4. NO menciones "según el manual" ni repitas la marca. Ve directo al grano.

RESPUESTA:"""

PROMPT = PromptTemplate(template=template, input_variables=["context", "question"])

# Crear la cadena de RAG (Consulta + Generación) con prompt optimizado
rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_db.as_retriever(search_kwargs={"k": 2}), # K=2 para máxima velocidad y evitar timeouts
    chain_type_kwargs={"prompt": PROMPT}
)

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    
    # Extraemos el intent y la pregunta del usuario
    intent = data.get('queryResult', {}).get('intent', {}).get('displayName', '')
    query_text = data.get('queryResult', {}).get('queryText', '')
    

    # Si es una consulta tecnica, usamos el motor RAG
    if intent == "Consultar_Manual":
        # Extraemos parametros para enriquecer la busqueda
        parameters = data.get('queryResult', {}).get('parameters', {})
        marca = parameters.get('marca', '')
        dispositivo = parameters.get('dispositivo', '')
        
        # Construimos una query enriquecida para el RAG
        rag_query = f"{query_text} {marca} {dispositivo}".strip()

        # CLAVE DE CACHÉ ROBUSTA: Usamos la marca normalizada como identificador principal
        # Esto evita fallos si Dialogflow a veces manda el dispositivo y otras no
        m_norm = str(marca).strip().lower()
        is_menu_selection = len(query_text.split()) < 4
        
        if is_menu_selection and m_norm:
            cache_key = f"menu_{m_norm}".replace(" ", "_")
        else:
            cache_key = rag_query.lower().replace(".", "").strip()

        if cache_key in consulta_cache:
            final_text = consulta_cache[cache_key]
            return JSONResponse(content={"fulfillmentText": final_text})

        try:
            import time
            start_time = time.time()
            
            # Ejecutamos la consulta RAG con la query enriquecida
            respuesta_ai = rag_chain.invoke(rag_query)
            
            # El resultado viene en el campo 'result'
            final_text = respuesta_ai.get('result', "No lo he encontrado")
            
            # Filtro de calidad para la caché: Solo guardamos si la respuesta es útil
            bad_responses = ["no lo sé", "no lo he encontrado", "especifica el modelo", "problemas técnicos"]
            is_bad = any(phrase in final_text.lower() for phrase in bad_responses)

            if not is_bad:
                consulta_cache[cache_key] = final_text
                guardar_cache(consulta_cache)
            else:
                logger.warning("Respuesta negativa detectada. NO se guardará en caché.")
            
            duration = time.time() - start_time
            
            return JSONResponse(content={"fulfillmentText": final_text})
        except Exception as e:
            logger.error(f"Error en el motor RAG: {e}")
            return JSONResponse(content={"fulfillmentText": "Lo siento, tengo problemas técnicos para consultar los manuales ahora mismo."})

    # Lógica para otros intents heredados
    elif intent == "Configurar_Horario":
        hora = data.get('queryResult', {}).get('parameters', {}).get('time', 'la hora')
        return JSONResponse(content={"fulfillmentText": f"Entendido. He programado el encendido para las {hora}."})

    # Respuesta por defecto
    return JSONResponse(content={"fulfillmentText": "Webhook conectado: He recibido tu mensaje pero no tengo una respuesta específica para esta intención."})

if __name__ == "__main__":
    # Integración de ngrok vía SDK (Como en la Tarea 03)
    authtoken = os.getenv("NGROK_AUTHTOKEN")
    if authtoken:
        ngrok.set_auth_token(authtoken)
        listener = ngrok.forward(8000)
        print(f"\n🚀 WEBHOOK RAG ACTIVO: {listener.url()}/webhook")
        print(f"Copia esta URL en el Fulfillment de Dialogflow\n")
    else:
        print("⚠️ NGROK_AUTHTOKEN no encontrada. El servidor solo será local.")

    uvicorn.run(app, host="0.0.0.0", port=8000)