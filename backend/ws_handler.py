import json
import uuid
import base64
import asyncio
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
import httpx
import weave

from backend.config import ELEVENLABS_API_KEY
from backend.services.mistral_service import translate_with_mistral
from backend.services.gemini_service import handle_image_generation

router = APIRouter()

conversation_history = []

async def transcribe_audio(audio_data: bytes) -> str:
    """ElevenLabs Scribe v2 (Batch STT)"""
    url = "https://api.elevenlabs.io/v1/speech-to-text"
    headers = {"xi-api-key": ELEVENLABS_API_KEY}
    print(f"[STT] Using header: {headers}", flush=True)
    
    files = {"file": ("audio.webm", audio_data, "audio/webm")}
    data = {"model_id": "scribe_v2", "language_code": "ja"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, files=files, data=data, timeout=30.0)
        response.raise_for_status()
        result = response.json()
        return result.get("text", "")

@router.post("/save-conversation")
async def save_conversation():
    if not conversation_history:
        return {"status": "empty"}
    
    import os
    save_dir = Path(__file__).resolve().parent.parent / "conversations"
    save_dir.mkdir(exist_ok=True)
    
    filename = f"{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.json"
    filepath = save_dir / filename
    
    save_data = []
    for entry in conversation_history:
        save_entry = {k: v for k, v in entry.items() if k != 'image_base64'}
        save_data.append(save_entry)
    
    import json as json_module
    with open(filepath, 'w', encoding='utf-8') as f:
        json_module.dump(save_data, f, ensure_ascii=False, indent=2)
    
    conversation_history.clear()
    return {"status": "saved", "filename": filename}

@router.get("/history")
async def history_page():
    history_path = Path(__file__).resolve().parent.parent / "frontend" / "history.html"
    return FileResponse(history_path)

@router.get("/api/conversations")
async def list_conversations():
    save_dir = Path(__file__).resolve().parent.parent / "conversations"
    if not save_dir.exists():
        return []
    files = sorted(save_dir.glob("*.json"), reverse=True)
    conversations = []
    for f in files:
        import json as json_module
        with open(f, 'r', encoding='utf-8') as fp:
            data = json_module.load(fp)
        conversations.append({
            "filename": f.name,
            "date": f.stem,
            "entries": data
        })
    return conversations

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_language = 'ja'
    try:
        while True:
            message = await websocket.receive()
            if message["type"] == "websocket.disconnect":
                print("Client disconnected gracefully")
                break
            
            card_id = str(uuid.uuid4())
            
            original_text = ""
            current_lang = session_language
            
            if "text" in message:
                try:
                    msg_data = json.loads(message["text"])
                    if msg_data.get("type") == "set_language":
                        session_language = msg_data.get("language", "ja")
                        print(f"[LANG] Language set to: {session_language}")
                        continue
                    elif msg_data.get("type") == "text":
                        original_text = msg_data.get("content", "")
                        current_lang = msg_data.get("language", session_language)
                        print(f"[Web Speech API] Received text: {original_text} (lang: {current_lang})", flush=True)
                except Exception as e:
                    print(f"Failed to parse text message: {e}", flush=True)
            elif "bytes" in message:
                data = message["bytes"]
                print(f"Received audio blob: {len(data)} bytes")
                print("ElevenLabs STT is bypassed. Need JSON text message instead.")
                continue

            if not original_text.strip():
                continue

            try:
                agent_data = await translate_with_mistral(original_text, language=current_lang)
                
                conversation_history.append({
                    "card_id": card_id,
                    "original": original_text,
                    "translated": agent_data.get("translated", ""),
                    "emotion": agent_data.get("emotion", ""),
                    "emoji": agent_data.get("emoji", ""),
                    "scene_prompt": agent_data.get("scene_prompt", ""),
                    "guide": agent_data.get("guide", ""),
                    "image_base64": None,
                    "timestamp": datetime.now().isoformat()
                })
                
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
                print(f"[GUIDE DEBUG] Raw Mistral data keys: {list(agent_data.keys())}")
                print(f"[GUIDE DEBUG] data.get('guide'): '{agent_data.get('guide', 'NOT FOUND')}'")
                await websocket.send_json(instant_payload)
                
                scene_prompt = agent_data.get("scene_prompt", "")
                if scene_prompt:
                    scene_prompt = scene_prompt.rstrip('.')
                    scene_prompt += ". White or very light solid background, minimal scenery, show only the main character(s) and one or two key objects. No detailed environments, no rooms, no landscapes. Simple, clean, picture book style with lots of white space."
                    print(f"Creating background task for image generation (card_id: {card_id})")
                    asyncio.create_task(handle_image_generation(websocket, scene_prompt, card_id))
                else:
                    print("No scene prompt returned by Mistral Agent.")

            except Exception as e:
                print(f"Mistral/Gemini flow error: {e}")
                
    except WebSocketDisconnect:
        print("Client disconnected")
