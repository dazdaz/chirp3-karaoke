import asyncio
import io
import json
import logging
import os
import queue
import random
import sys
from typing import Dict

import uvicorn
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from google.api_core.client_options import ClientOptions
from google.cloud import speech_v2, texttospeech, translate_v2 as translate
from google.cloud.speech_v2 import (
    RecognitionConfig,
    RecognitionFeatures,
    SpeechClient,
    StreamingRecognitionConfig,
    StreamingRecognitionFeatures,
    StreamingRecognizeRequest,
    ExplicitDecodingConfig,
)
from pydantic import BaseModel

# --- Configuration ---
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
LOCATION = "us-central1"
RECOGNIZER_NAME = f"projects/{PROJECT_ID}/locations/{LOCATION}/recognizers/_"

# --- FastAPI App Initialization ---
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
app = FastAPI()
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# --- Mount static directories and templates ---
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# --- Google Cloud Clients ---
try:
    if not PROJECT_ID:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is not set")
    
    tts_client = texttospeech.TextToSpeechClient()
    speech_client_options = ClientOptions(api_endpoint=f"{LOCATION}-speech.googleapis.com")
    speech_client = SpeechClient(client_options=speech_client_options)
    translate_client = translate.Client()
    logger.info(f"Google Cloud clients initialized successfully for project: {PROJECT_ID}")
except Exception as e:
    logger.error(f"Error initializing Google Cloud clients: {e}")
    logger.error("Please ensure your Google Cloud credentials are configured correctly.")
    logger.error(f"Current PROJECT_ID: {PROJECT_ID}")
    tts_client = None
    speech_client = None
    translate_client = None


# --- Phrase Lists by Language ---
phrases: Dict[str, list[str]] = {
    "en-US": [
        "Hello world", "How are you", "What is your name", "Good morning",
        "Thank you very much", "Excuse me please", "I am sorry", "Have a nice day",
        "The sky is blue", "I love to travel",
        "The quick brown fox jumps over the lazy dog",
        "An apple a day keeps the doctor away",
        "Never underestimate the power of a good book",
        "The early bird catches the worm", "Actions speak louder than words",
        "Where there is a will, there is a way", "Technology has changed the world we live in",
        "To be or not to be, that is the question", "Every cloud has a silver lining",
        "The best way to predict the future is to create it", "Honesty is the best policy",
        "In the middle of difficulty lies opportunity",
        "The only thing we have to fear is fear itself",
        "That which does not kill us makes us stronger",
        "The journey of a thousand miles begins with a single step",
    ],
    "es-ES": [
        "Hola mundo", "¿Cómo estás?", "¿Cuál es tu nombre?", "Buenos días",
        "Muchas gracias", "Perdón, por favor", "Lo siento", "Que tengas un buen día",
        "El cielo es azul", "Me encanta viajar"
    ],
    "ja-JP": [
        "こんにちは世界", "お元気ですか", "お名前は何ですか", "お���ようございます",
        "ありがとうございます", "すみません", "ごめんなさい", "良い一日を",
        "空は青いです", "旅行が大好きです"
    ],
    "pt-BR": [
        "Olá, mundo", "Como você está?", "Qual é o seu nome?", "Bom dia",
        "Muito obrigado", "Com licença, por favor", "Me desculpe", "Tenha um bom dia",
        "O céu é azul", "Eu amo viajar"
    ],
    "de-DE": [
        "Hallo Welt", "Wie geht es Ihnen?", "Wie heißen Sie?", "Guten Morgen",
        "Vielen Dank", "Entschuldigen Sie bitte", "Es tut mir leid", "Schönen Tag noch",
        "Der Himmel ist blau", "Ich liebe es zu reisen"
    ]
}

VOICE_MAPPING = {
    "en-US": "en-US-Chirp3-HD-Charon",
    "es-ES": "es-ES-Wavenet-B",
    "ja-JP": "ja-JP-Wavenet-A",
    "pt-BR": "pt-BR-Wavenet-A",
    "de-DE": "de-DE-Wavenet-F",
}

# --- Pydantic Models ---
class SynthesizeRequest(BaseModel):
    text: str
    language: str = "en-US"

# =================================================================================
# --- HTTP Routes (from original front-end) ---
# =================================================================================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main application page."""
    logger.debug("Serving index page")
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/status")
async def status():
    """Check API status and configuration."""
    return JSONResponse(content={
        "status": "ok",
        "project_id": PROJECT_ID,
        "location": LOCATION,
        "tts_client": tts_client is not None,
        "speech_client": speech_client is not None,
        "translate_client": translate_client is not None
    })

@app.post("/api/translate")
async def translate_text(request: Request):
    """Translate text to English using Google Translate API."""
    try:
        data = await request.json()
        text = data.get("text", "")
        source_language = data.get("source_language", "auto")
        
        if not text:
            return JSONResponse(content={"error": "No text provided"}, status_code=400)
        
        if not translate_client:
            return JSONResponse(content={"error": "Translation client not initialized"}, status_code=500)
        
        # Translate to English
        result = translate_client.translate(
            text,
            target_language='en',
            source_language=source_language if source_language != 'auto' else None
        )
        
        logger.info(f"Translated '{text[:50]}...' from {result.get('detectedSourceLanguage', source_language)} to English")
        
        return JSONResponse(content={
            "original": text,
            "translated": result['translatedText'],
            "source_language": result.get('detectedSourceLanguage', source_language)
        })
    
    except Exception as e:
        logger.error(f"Translation error: {e}", exc_info=True)
        return JSONResponse(content={"error": f"Translation failed: {str(e)}"}, status_code=500)

@app.get("/api/new-phrase")
async def new_phrase(language: str = "en-US"):
    """Provide a new random phrase in the specified language."""
    language_phrases = phrases.get(language, phrases["en-US"]) # Default to English
    phrase = random.choice(language_phrases)
    logger.debug(f"Returning new phrase in {language}: {phrase[:20]}...")
    return JSONResponse(content={"phrase": phrase})

@app.post("/api/synthesize")
async def synthesize_speech(request_data: SynthesizeRequest):
    """Generate audio from text using Google TTS."""
    logger.debug(f"Synthesizing speech for text: {request_data.text[:50]} in {request_data.language}...")
    
    if not tts_client:
        logger.error("TTS Client not initialized")
        return JSONResponse(content={"error": "TTS Client not initialized"}, status_code=500)

    try:
        synthesis_input = texttospeech.SynthesisInput(text=request_data.text)
        
        voice_name = VOICE_MAPPING.get(request_data.language, VOICE_MAPPING["en-US"])
        
        voice = texttospeech.VoiceSelectionParams(
            language_code=request_data.language, name=voice_name
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        response = tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        logger.info(f"Successfully synthesized {len(response.audio_content)} bytes of audio")
        return StreamingResponse(io.BytesIO(response.audio_content), media_type="audio/mpeg")
    except Exception as e:
        logger.error(f"Error in Google TTS API: {e}", exc_info=True)
        return JSONResponse(content={"error": f"Failed to synthesize speech: {str(e)}"}, status_code=500)

# =================================================================================
# --- WebSocket Logic (from original back-end) ---
# =================================================================================

def audio_request_generator(audio_queue: queue.Queue, recognizer, config):
    """Yields audio chunks from a queue to the gRPC stream."""
    yield StreamingRecognizeRequest(recognizer=recognizer, streaming_config=config)
    while True:
        chunk = audio_queue.get()
        if chunk is None:
            break
        yield StreamingRecognizeRequest(audio=chunk)

def run_grpc_stream(audio_queue: queue.Queue, results_queue: asyncio.Queue, language_code: str):
    """Runs the blocking gRPC stream and puts transcription results in a queue."""
    try:
        streaming_config = StreamingRecognitionConfig(
            config=RecognitionConfig(
                 explicit_decoding_config=ExplicitDecodingConfig(
                    encoding="LINEAR16",
                    sample_rate_hertz=16000,
                    audio_channel_count=1
                ),
                language_codes=[language_code],
                features=RecognitionFeatures(
                    enable_word_time_offsets=True,
                    enable_word_confidence=True,
                    enable_automatic_punctuation=True
                ),
                model="chirp_2"
            ),
            streaming_features=StreamingRecognitionFeatures(interim_results=True),
        )

        requests = audio_request_generator(audio_queue, RECOGNIZER_NAME, streaming_config)
        stream = speech_client.streaming_recognize(requests=requests)
        logger.debug("gRPC stream producer started")

        for response in stream:
            for result in response.results:
                if not result.alternatives:
                    continue
                words_list = [
                    {
                        "word": word.word,
                        "startTime": word.start_offset.total_seconds(),
                        "endTime": word.end_offset.total_seconds(),
                        "confidence": word.confidence,
                    }
                    for word in result.alternatives[0].words
                ] if result.alternatives and result.alternatives[0].words else []

                message: Dict = {
                    "transcript": result.alternatives[0].transcript,
                    "isFinal": result.is_final,
                    "words": words_list,
                }
                results_queue.put_nowait(message)

    except Exception as e:
        logger.error(f"Error in gRPC stream producer: {e}", exc_info=True)
        results_queue.put_nowait({"error": str(e)})
    finally:
        results_queue.put_nowait(None)  # Sentinel value to signal end of stream
        logger.debug("gRPC stream producer ended")

@app.websocket("/listen")
async def websocket_endpoint(websocket: WebSocket, language_code: str = "en-US"):
    """Handle WebSocket connection for real-time transcription."""
    await websocket.accept()
    logger.info(f"WebSocket listener connected with language_code: {language_code}")
    
    if not speech_client:
        logger.error("Speech client not initialized, closing WebSocket")
        await websocket.send_text(json.dumps({"error": "Speech client not initialized"}))
        await websocket.close()
        return

    audio_queue = queue.Queue()
    results_queue = asyncio.Queue()

    async def receive_from_client():
        """Receive audio from the client and put it into the audio_queue."""
        try:
            while True:
                message = await websocket.receive()
                if "bytes" in message:
                    audio_queue.put(message["bytes"])
                elif "text" in message:
                    data = json.loads(message["text"])
                    if data.get("action") == "stop":
                        logger.debug("Received stop signal from client")
                        break
        finally:
            audio_queue.put(None)

    async def send_to_client():
        """Get transcription results from the results_queue and send to the client."""
        while True:
            message = await results_queue.get()
            if message is None:
                break
            await websocket.send_text(json.dumps(message))
        await websocket.close()

    loop = asyncio.get_running_loop()

    try:
        grpc_task = loop.run_in_executor(
            None, run_grpc_stream, audio_queue, results_queue, language_code
        )
        await asyncio.gather(receive_from_client(), send_to_client(), grpc_task)
    except WebSocketDisconnect:
        logger.warning("Client disconnected unexpectedly")
    except Exception as e:
        logger.error(f"An error occurred in WebSocket handler: {e}", exc_info=True)
        try:
            await websocket.send_text(json.dumps({"error": str(e)}))
        except:
            pass
    finally:
        logger.info("Transcription session ended")

# --- Server Startup ---
if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    uvicorn.run(app, host="0.0.0.0", port=port)
