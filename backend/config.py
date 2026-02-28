import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
print(f"Loading .env from: {env_path}")
print(f".env exists: {env_path.exists()}")
load_dotenv(env_path)

print(f"ELEVENLABS_API_KEY loaded: {bool(os.getenv('ELEVENLABS_API_KEY'))}")
print(f"MISTRAL_API_KEY loaded: {bool(os.getenv('MISTRAL_API_KEY'))}")
print(f"GEMINI_API_KEY loaded: {bool(os.getenv('GEMINI_API_KEY'))}")

WEAVE_API_KEY = os.getenv("WEAVE_API_KEY")
if WEAVE_API_KEY:
    os.environ["WANDB_API_KEY"] = WEAVE_API_KEY

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MISTRAL_AGENT_ID = os.getenv("MISTRAL_AGENT_ID")
