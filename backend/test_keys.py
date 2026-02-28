import os
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)
m_key = os.getenv('MISTRAL_API_KEY')
g_key = os.getenv('GEMINI_API_KEY')
print(f"MISTRAL_API_KEY: {m_key[:5] if m_key else 'NONE'}...")
print(f"GEMINI_API_KEY: {g_key[:5] if g_key else 'NONE'}...")
import sys
try:
    from google import genai
    print("Import successful"); sys.stdout.flush()
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    print("Client created successfully"); sys.stdout.flush()
except Exception as e:
    print(f"Error: {e}"); sys.stdout.flush()
