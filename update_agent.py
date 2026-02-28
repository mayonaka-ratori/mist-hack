import urllib.request
import json
import os
from dotenv import load_dotenv

load_dotenv('c:/mistral AI/cognibridge/.env')
api_key = os.getenv('MISTRAL_API_KEY')
agent_id = os.getenv('MISTRAL_AGENT_ID')
print(f'Using token: {api_key[:5]}')

url = f'https://api.mistral.ai/v1/agents/{agent_id}'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

instr = """あなたは認知翻訳エンジンです。高齢者の日本語発話を受け取り、必ず以下の5つのフィールドを含むJSONのみを返してください。他のテキストは一切含めないでください。

{ "translated": "5〜8歳の子どもが理解できるやさしい日本語に変換した文", "emotion": "嬉しい/悲しい/疲れてる/楽しい/普通/怒ってる のいずれか", "emoji": "内容を表す絵文字を3〜5個（例: 🍅🌞😊）", "scene_prompt": "A warm, child-friendly watercolor illustration of [scene description in English]. Soft colors, simple shapes, no text, picture book style.", "guide": "聞き手（子ども）への返答アドバイス（1文）" }

scene_promptは必ず英語で、温かみのある水彩画風の子ども向けイラストの説明を書いてください。必ず5つ全てのフィールドを含めてください。"""

data = {
    'name': 'CogniBridge Translation Engine',
    'instructions': instr
}

req = urllib.request.Request(url, headers=headers, data=json.dumps(data).encode('utf-8'), method='PATCH')
try:
    with urllib.request.urlopen(req, timeout=30) as response:
        print(response.status)
        print(response.read().decode('utf-8'))
except urllib.error.URLError as e:
    print('Error:', e)
    if hasattr(e, 'read'):
        print(e.read().decode('utf-8'))
