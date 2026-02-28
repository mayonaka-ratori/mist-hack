import sys
import os

# Add parent directory to sys.path to run standalone
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.config import MISTRAL_API_KEY, MISTRAL_AGENT_ID
from mistralai import Mistral

def test_mistral():
    print("Testing mistral_client...")
    try:
        client = Mistral(api_key=MISTRAL_API_KEY)
        
        # Test 1: chat.complete
        print("1. chat.complete (en)...")
        resp = client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": "Hello"}],
        )
        print("Success chat.complete:", resp.choices[0].message.content)
        
        # Test 2: conversations.start (agent)
        print("2. conversations.start (ja)...", MISTRAL_AGENT_ID)
        resp2 = client.beta.conversations.start(
            agent_id=MISTRAL_AGENT_ID,
            inputs=[{"role": "user", "content": "おはよう"}]
        )
        print("Success agent start")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_mistral()
