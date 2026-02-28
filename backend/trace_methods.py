import os
from dotenv import load_dotenv
from google import genai

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print(f"Client: {type(client)}")
print(f"Models: {type(client.models)}")
print(f"Dir(Models): {dir(client.models)}")

try:
    m = client.models.generate_image
    print("Found generate_image directly")
except AttributeError:
    print("Not found generate_image directly")

try:
    m = client.vertexai.models.generate_image
    print("Found generate_image via vertexai")
except Exception as e:
    print(f"Error via vertexai: {e}")
