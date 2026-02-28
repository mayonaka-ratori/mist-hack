import os
import time
from dotenv import load_dotenv
from google import genai

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

prompt = "A warm, child-friendly watercolor illustration of a smiling elderly Japanese man in a garden pointing at bright red tomatoes. Sunny day, gentle soft style, simple shapes, like a picture book."

print("=== Test 1: gemini-2.5-flash-image ===")
start = time.time()
try:
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt],
    )
    elapsed = time.time() - start
    print(f"Time: {elapsed:.1f} seconds")
    for part in response.parts:
        if part.text is not None:
            print(f"Text: {part.text[:100]}")
        elif part.inline_data is not None:
            image = part.as_image()
            image.save("test_gemini_flash.png")
            print("Image saved as test_gemini_flash.png")
except Exception as e:
    elapsed = time.time() - start
    print(f"Error after {elapsed:.1f}s: {e}")

print("\n=== Test 2: gemini-3.1-flash-image-preview ===")
start = time.time()
try:
    response = client.models.generate_content(
        model="gemini-3.1-flash-image-preview",
        contents=[prompt],
    )
    elapsed = time.time() - start
    print(f"Time: {elapsed:.1f} seconds")
    for part in response.parts:
        if part.text is not None:
            print(f"Text: {part.text[:100]}")
        elif part.inline_data is not None:
            image = part.as_image()
            image.save("test_gemini_31flash.png")
            print("Image saved as test_gemini_31flash.png")
except Exception as e:
    elapsed = time.time() - start
    print(f"Error after {elapsed:.1f}s: {e}")
