import base64
import asyncio
from fastapi import WebSocket
from google import genai
from google.genai import types

from backend.config import GEMINI_API_KEY

genai_client = genai.Client(api_key=GEMINI_API_KEY)

async def handle_image_generation(websocket: WebSocket, scene_prompt: str, card_id: str):
    """Background task for image generation and delivery via WebSocket"""
    from backend.ws_handler import conversation_history
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
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                image_bytes = part.inline_data.data
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                print(f"[GEMINI] Image size: {len(image_bytes)} bytes")
                print(f"[GEMINI] Base64 length: {len(image_base64)}")
                
                for entry in conversation_history:
                    if entry["card_id"] == card_id:
                        entry["image_base64"] = image_base64
                        break

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
