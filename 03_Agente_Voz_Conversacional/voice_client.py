import os
import azure.cognitiveservices.speech as speechsdk
from google.cloud import dialogflow_v2beta1 as dialogflow
from dotenv import load_dotenv

load_dotenv()

# 1. Configurar Credenciales Google
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
PROJECT_ID = os.getenv("GCP_PROJECT_ID")

# 2. Configurar Azure Speech
speech_config = speechsdk.SpeechConfig(
    subscription=os.getenv("AZURE_SPEECH_KEY"), 
    region=os.getenv("AZURE_SPEECH_REGION")
)
speech_config.speech_recognition_language="es-ES"
speech_config.speech_synthesis_voice_name = "es-ES-ElviraNeural"

def hablar(texto):
    print(f"Bot dice: {texto}")
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    synthesizer.speak_text_async(texto).get()

def enviar_a_dialogflow(texto):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(PROJECT_ID, "usuario-unico-123")
    
    text_input = dialogflow.types.TextInput(text=texto, language_code="es-ES")
    query_input = dialogflow.types.QueryInput(text=text_input)
    
    response = session_client.detect_intent(session=session, query_input=query_input)
    hablar(response.query_result.fulfillment_text)

def escuchar():
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    
    print(">>> Diga algo (o diga 'salir' para terminar)...")
    result = recognizer.recognize_once_async().get()
    
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print(f"Has dicho: {result.text}")
        if "salir" in result.text.lower():
            return False
        enviar_a_dialogflow(result.text)
    return True

if __name__ == "__main__":
    hablar("Sistema de soporte Smart Home iniciado. ¿En qué puedo ayudarte?")
    activo = True
    while activo:
        activo = escuchar()
