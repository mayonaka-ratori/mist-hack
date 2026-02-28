import os
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv(dotenv_path="../.env")
api_key = os.getenv("MISTRAL_API_KEY")

client = Mistral(api_key=api_key)

def test_simple_chat():
    try:
        print(f"Testing simple chat with key: {api_key[:4]}...{api_key[-4:]}")
        response = client.chat.complete(
            model="mistral-tiny",
            messages=[{"role": "user", "content": "say hello"}]
        )
        print("Chat successful!")
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"Simple chat failed: {e}")

if __name__ == "__main__":
    test_simple_chat()
