import os
import json
import base64
import asyncio
import io
import uuid
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from mistralai import Mistral
from google import genai
from google.genai import types
from PIL import Image
from pathlib import Path

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / ".env"
print(f"Loading .env from: {env_path}")
print(f".env exists: {env_path.exists()}")
load_dotenv(env_path)

print(f"ELEVENLABS_API_KEY loaded: {bool(os.getenv('ELEVENLABS_API_KEY'))}")
print(f"MISTRAL_API_KEY loaded: {bool(os.getenv('MISTRAL_API_KEY'))}")
print(f"GEMINI_API_KEY loaded: {bool(os.getenv('GEMINI_API_KEY'))}")
WEAVE_API_KEY = os.getenv("WEAVE_API_KEY")
if WEAVE_API_KEY:
    import os
    os.environ["WANDB_API_KEY"] = WEAVE_API_KEY

import weave
weave.init("cognibridge")

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MISTRAL_AGENT_ID = os.getenv("MISTRAL_AGENT_ID")

# Initialize API clients
mistral_client = Mistral(api_key=MISTRAL_API_KEY)
genai_client = genai.Client(api_key=GEMINI_API_KEY)

app = FastAPI()

# --- Helpers ---

@weave.op()
async def transcribe_audio(audio_data: bytes) -> str:
    """ElevenLabs Scribe v2 (Batch STT)"""
    url = "https://api.elevenlabs.io/v1/speech-to-text"
    headers = {"xi-api-key": ELEVENLABS_API_KEY}
    print(f"[STT] Using header: {headers}")
    
    # Send as multipart/form-data
    files = {"file": ("audio.webm", audio_data, "audio/webm")}
    data = {"model_id": "scribe_v2", "language_code": "ja"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, files=files, data=data, timeout=30.0)
        response.raise_for_status()
        result = response.json()
        return result.get("text", "")

@weave.op()
async def translate_with_mistral(text: str) -> dict:
    """Mistral Agent (Scene Translation & Prompting)"""
    print("Sending to Mistral Agent...")
    # Using run_in_executor or just call synchronously if it's sync, 
    # but the mistral_client start is currently sync in original code
    response = mistral_client.beta.conversations.start(
        agent_id=MISTRAL_AGENT_ID,
        inputs=[{"role": "user", "content": text}]
    )
    
    # Parse JSON from Agent response
    agent_content = ""
    if hasattr(response, 'model_dump'):
        outputs = response.model_dump().get('outputs', [])
        if outputs:
            agent_content = outputs[0].get('content', "")
    
    print(f"Raw Mistral Response: {agent_content}")
    
    # The agent is expected to return a JSON string
    # Remove markdown code blocks if present
    import re
    raw = agent_content.strip()
    raw = re.sub(r'^```json\s*', '', raw, flags=re.IGNORECASE)
    raw = re.sub(r'^```\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    return json.loads(raw)

async def handle_image_generation(websocket: WebSocket, scene_prompt: str, card_id: str):
    """Background task for image generation and delivery via WebSocket"""
    print(f"[GEMINI] Starting image generation for card: {card_id}")
    print(f"[GEMINI] scene_prompt: {scene_prompt}")
    try:
        # gemini-2.5-flash-image handles prompt -> image in one call
        response = await asyncio.to_thread(
            genai_client.models.generate_content,
            model="gemini-2.5-flash-image",
            contents=[scene_prompt],
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE']
            )
        )
        
        print(f"[GEMINI] Response received, checking parts...")
        # After getting the image from Gemini response parts:
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                image_bytes = part.inline_data.data
                # Convert to base64 directly from raw bytes - no PIL needed
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                print(f"[GEMINI] Image size: {len(image_bytes)} bytes")
                print(f"[GEMINI] Base64 length: {len(image_base64)}")
                # Send to frontend
                await websocket.send_json({
                    "type": "image",
                    "card_id": card_id,
                    "image_base64": image_base64
                })
                print(f"[GEMINI] Image sent for card: {card_id}")
                return
        print("[GEMINI] No image found in response parts")
    except Exception as e:
        print(f"[GEMINI] ERROR: {e}")

# --- Routes ---

@app.get("/")
async def get():
    index_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.websocket("/ws")
@weave.op()
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive generic message
            message = await websocket.receive()
            
            # Generate a unique ID for this utterance
            card_id = str(uuid.uuid4())
            
            original_text = ""
            
            if "text" in message:
                try:
                    msg_data = json.loads(message["text"])
                    if msg_data.get("type") == "text":
                        original_text = msg_data.get("content", "")
                        print(f"[Web Speech API] Received text: {original_text}")
                except Exception as e:
                    print(f"Failed to parse text message: {e}")
            elif "bytes" in message:
                data = message["bytes"]
                print(f"Received audio blob: {len(data)} bytes")
                print("ElevenLabs STT is bypassed. Need JSON text message instead.")
                # Keep STT commented out for later
                # try:
                #     original_text = await transcribe_audio(data)
                #     print(f"Transcription: {original_text}")
                # except Exception as e:
                #     print(f"STT Error: {e}")
                continue

            if not original_text.strip():
                continue

            # 2. Mistral Agent (Scene Translation & Prompting)
            try:
                agent_data = await translate_with_mistral(original_text)
                
                # 3. Send Instant Layer
                instant_payload = {
                    "type": "instant",
                    "card_id": card_id,
                    "original": original_text,
                    "translated": agent_data.get("translated", ""),
                    "emotion": agent_data.get("emotion", ""),
                    "emoji": agent_data.get("emoji", ""),
                    "scene_prompt": agent_data.get("scene_prompt", ""),
                    "guide": agent_data.get("guide", "")
                }
                print(f"Sending instant payload for card_id: {card_id}")
                await websocket.send_json(instant_payload)
                
                # 4. Async Image Generation (Gemini)
                scene_prompt = agent_data.get("scene_prompt", "")
                if scene_prompt:
                    print(f"Creating background task for image generation (card_id: {card_id})")
                    asyncio.create_task(handle_image_generation(websocket, scene_prompt, card_id))
                else:
                    print("No scene prompt returned by Mistral Agent.")

            except Exception as e:
                print(f"Mistral/Gemini flow error: {e}")
                
    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
