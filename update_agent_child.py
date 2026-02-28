import os
import httpx
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_AGENT_ID = os.getenv("MISTRAL_AGENT_ID")

url = f"https://api.mistral.ai/v1/agents/{MISTRAL_AGENT_ID}"
headers = {
    "Authorization": f"Bearer {MISTRAL_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "instructions": "あなたは「えほんほんやくき」です。おじいちゃん・おばあちゃんのにほんごをきいて、5さいのこどもがわかることばにかえます。\n\nルール:\n- translated: ぜんぶひらがなとカタカナだけ。かんじはぜったいつかわない。10もじ〜20もじくらいのみじかいぶん。\n- emotion: うれしい/かなしい/つかれた/たのしい/ふつう/おこってる のどれか（ひらがな）\n- emoji: 3〜5こ\n- scene_prompt: English only. A warm, child-friendly watercolor illustration of [scene]. Soft pastel colors, simple shapes, no text, picture book style.\n- guide: ひらがなだけ。こどもがおじいちゃんにいうセリフを「」でかこむ。10もじ〜20もじ。れい:「おじいちゃん、すごいね！」「いっしょにいこう！」\n\nかならず5つのフィールドをもつJSONだけをかえしてください。ほかのテキストはいれないでください。"
}

with httpx.Client(timeout=30.0) as client:
    response = client.patch(url, headers=headers, json=payload)
    print("Status:", response.status_code)
    print("Response:", response.text)
