import os
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

# Cargamos las variables de entorno
load_dotenv()

# 1. Configuracion de Azure OCR (Desde tu .env)
endpoint = os.getenv("AZURE_DOC_INTEL_ENDPOINT")
key = os.getenv("AZURE_DOC_INTEL_KEY")

if not endpoint or not key:
    print("--- ERROR: No se han encontrado las claves de Azure OCR en el .env ---")
    exit()

# IMPORTANTE: Ahora usamos la libreria correcta
client = DocumentIntelligenceClient(endpoint, AzureKeyCredential(key))

# 2. Configuracion de Embeddings (HuggingFace Local - Ultra Rapido)
from langchain_huggingface import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def procesar_manuales():
    directorio = "./data/manuales/"
    textos_extraidos = []

    if not os.path.exists(directorio):
        print(f"--- Creando carpeta: {directorio} ---")
        os.makedirs(directorio)
        return

    archivos = os.listdir(directorio)
    if not archivos:
        print(f"--- ERROR: No hay manuales en {directorio}. ---")
        return

    for archivo in archivos:
        ruta_archivo = os.path.join(directorio, archivo)
        if archivo.endswith(".pdf") or archivo.endswith(".jpg") or archivo.endswith(".png"):
            print(f"--- Procesando archivo con OCR: {archivo} ... ---")
            try:
                with open(ruta_archivo, "rb") as f:
                    # Enviamos el archivo completo a Azure
                    poller = client.begin_analyze_document("prebuilt-read", f, content_type="application/octet-stream")
                    result = poller.result()
                    textos_extraidos.append(result.content)
            except Exception as e:
                print(f"--- Error al procesar {archivo}: {e} ---")
        elif archivo.endswith(".jpg") or archivo.endswith(".png"):
            print(f"--- Procesando imagen con OCR: {archivo} ... ---")
            try:
                ruta_archivo = os.path.join(directorio, archivo)
                with open(ruta_archivo, "rb") as f:
                    poller = client.begin_analyze_document("prebuilt-read", f, content_type="application/octet-stream")
                    result = poller.result()
                    textos_extraidos.append(result.content)
            except Exception as e:
                print(f"--- Error al procesar {archivo}: {e} ---")

    if not textos_extraidos:
        print("--- No se ha podido extraer texto. ---")
        return

    from langchain_text_splitters import RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, 
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""]
    )
    documentos_divididos = text_splitter.create_documents(textos_extraidos)

    print(f"--- INFO: Se han generado {len(documentos_divididos)} fragmentos de texto ---")
    print(f"--- Guardando fragmentos en ChromaDB local... ---")
    
    try:
        vector_db = Chroma.from_documents(
            documents=documentos_divididos,
            embedding=embeddings,
            persist_directory="./data/chroma_db"
        )
        print("--- EXITO: Ingesta completada en ./data/chroma_db ---")
    except Exception as e:
        print(f"--- Error al guardar: {e} ---")

if __name__ == "__main__":
    procesar_manuales()
