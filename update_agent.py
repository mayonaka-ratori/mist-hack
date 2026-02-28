import os
import re
import httpx
from dotenv import load_dotenv

load_dotenv("c:/mistral AI/cognibridge/.env")

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_AGENT_ID = os.getenv("MISTRAL_AGENT_ID")

if not MISTRAL_API_KEY or not MISTRAL_AGENT_ID:
    print("API keys not found.")
    exit(1)

url = f"https://api.mistral.ai/v1/agents/{MISTRAL_AGENT_ID}"
headers = {
    "Authorization": f"Bearer {MISTRAL_API_KEY}",
    "Content-Type": "application/json"
}

resp = httpx.get(url, headers=headers)
if resp.status_code != 200:
    print(f"Failed to fetch agent: {resp.text}")
    exit(1)

agent = resp.json()
instructions = agent.get("instructions", "")

new_rule = "- scene_prompt: English only. Describe ONLY the main person and one key object. No rooms, no landscapes, no detailed backgrounds. Example: 'A cheerful elderly man in overalls holding a bright red tomato, smiling warmly. White background, simple watercolor, picture book style.' Keep it short, under 30 words."

pattern = r"- scene_prompt:.*?(?=\n- |$)"
new_instructions = re.sub(pattern, new_rule, instructions, flags=re.DOTALL)

if new_instructions == instructions:
    print("WARNING: Could not find or replace the scene_prompt rule!")
    exit(1)

patch_data = {
    "name": agent.get("name"),
    "instructions": new_instructions
}
if "description" in agent:
    patch_data["description"] = agent["description"]

patch_resp = httpx.patch(url, headers=headers, json=patch_data)
if patch_resp.status_code == 200:
    print("Successfully updated the agent instructions.")
else:
    print(f"Failed to update agent: {patch_resp.status_code}\n{patch_resp.text}")
    exit(1)
