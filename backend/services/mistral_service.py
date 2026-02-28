import json
import re
import asyncio
from typing import Optional
from mistralai import Mistral
import weave

from backend.config import MISTRAL_API_KEY, MISTRAL_AGENT_ID

mistral_client = Mistral(api_key=MISTRAL_API_KEY)

async def translate_with_mistral(text: str, language: str = "ja") -> dict:
    """Mistral Agent (Scene Translation & Prompting)"""
    from backend.ws_handler import conversation_history
    print(f"Sending to Mistral... (language: {language})", flush=True)
    
    context = ""
    if conversation_history:
        recent = conversation_history[-3:]
        for i, entry in enumerate(recent, 1):
            context += f"{i}. おじいちゃん:「{entry['original']}」→ こども向け:「{entry['translated']}」/ ガイド:{entry['guide']}\n"

    if language == 'en':
        lang_instruction = """
You are a "Story Translator" for CogniBridge. You hear elderly Japanese speech and translate it into simple English that a 5-year-old child can understand.

Rules:
- translated: Simple English, short sentences (5-10 words). Use easy words only. Example: "Grandpa picked red tomatoes today!"
- emotion: happy/sad/tired/excited/neutral/angry (English)
- emoji: 3 emojis representing place, person, thing. Example: 🌿🍅👴
- scene_prompt: English. Describe ONLY the main person and one key object. No rooms, no landscapes. Example: "A cheerful elderly man holding a bright red tomato. White background, simple watercolor, picture book style." Under 30 words.
- guide: Simple English question or reaction for the child to say back. In quotes. One sentence, under 10 words. Example: "What will you cook with them?"

Return ONLY a JSON with these 5 fields. No other text.
"""
        user_message = f"""[Previous conversation]
{context if context else "(First message)"}

[Current elderly Japanese speech]
「{text}」

Translate and respond with JSON only."""

        def do_en():
            return mistral_client.chat.complete(
                model="mistral-large-latest",
                messages=[
                    {"role": "system", "content": lang_instruction},
                    {"role": "user", "content": user_message}
                ],
                response_format={"type": "json_object"}
            )
        response = await asyncio.to_thread(do_en)
        agent_content = response.choices[0].message.content
    else:
        user_message = f"""[これまでのかいわ]
{context if context else "（はじめてのかいわ）"}

[いまのおじいちゃんのことば]
「{text}」

上の文脈をふまえて、JSONを返してください。guideは前回と違う内容にしてください。"""

        def do_ja():
            return mistral_client.beta.conversations.start(
                agent_id=MISTRAL_AGENT_ID,
                inputs=[{"role": "user", "content": user_message}]
            )
        response = await asyncio.to_thread(do_ja)
        
        agent_content = ""
        if hasattr(response, 'model_dump'):
            outputs = response.model_dump().get('outputs', [])
            if outputs:
                agent_content = outputs[0].get('content', "")
    
    print(f"Raw Mistral Response: {agent_content}")
    
    raw = agent_content.strip()
    raw = re.sub(r'^```json\s*', '', raw, flags=re.IGNORECASE)
    raw = re.sub(r'^```\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    
    raw = re.sub(r',\s*}', '}', raw)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print(f"[MISTRAL] JSON parse failed, attempting repair...")
        start = raw.find('{')
        end = raw.rfind('}')
        if start != -1 and end != -1:
            json_str = raw[start:end+1]
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                print(f"[MISTRAL] Repair failed, extracting fields manually...")
                data = {}
                for field in ['translated', 'emotion', 'emoji', 'scene_prompt', 'guide']:
                    match = re.search(rf'"{field}"\s*:\s*(.*?)(?=\s*(?:,|}}))', json_str, re.DOTALL)
                    if match:
                        val = match.group(1).strip()
                        if val.startswith('"') and val.endswith('"'):
                            val = val[1:-1]
                        data[field] = val
                if not data:
                    print(f"[MISTRAL] Manual extraction also failed")
                    data = {"translated": "...", "emotion": "ふつう", "emoji": "💬", "scene_prompt": "", "guide": ""}
        else:
            data = {"translated": "...", "emotion": "ふつう", "emoji": "💬", "scene_prompt": "", "guide": ""}
            
    return data
