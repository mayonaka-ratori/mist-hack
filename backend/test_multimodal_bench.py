import os, time, base64
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

# Load API key from ../.env
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

prompt = "A warm, gentle watercolor illustration of a smiling elderly Japanese man in a garden, pointing at bright red tomatoes. Sunny day, soft colors, child-friendly, simple shapes, no text."

# --- Test A: gemini-2.5-flash-image (Nano Banana) ---
print("=== Test A: gemini-2.5-flash-image ===")
try:
    start = time.time()
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE']
        )
    )
    elapsed = time.time() - start
    for part in response.parts:
        if part.text is not None:
            print(f"Text: {part.text[:100]}")
        elif part.inline_data is not None:
            img = part.as_image()
            img.save("test_nano_banana.png")
            print(f"Image saved: test_nano_banana.png")
    print(f"Time: {elapsed:.1f}s")
except Exception as e:
    print(f"Error: {e}")

# --- Test B: gemini-3.1-flash-image-preview (Nano Banana 2) ---
print("\n=== Test B: gemini-3.1-flash-image-preview ===")
try:
    start = time.time()
    response = client.models.generate_content(
        model="gemini-3.1-flash-image-preview",
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE']
        )
    )
    elapsed = time.time() - start
    for part in response.parts:
        if part.text is not None:
            print(f"Text: {part.text[:100]}")
        elif part.inline_data is not None:
            img = part.as_image()
            img.save("test_nano_banana2.png")
            print(f"Image saved: test_nano_banana2.png")
    print(f"Time: {elapsed:.1f}s")
except Exception as e:
    print(f"Error: {e}")

# --- Test C: imagen-4.0-fast (比較用、前回成功済み) ---
print("\n=== Test C: imagen-4.0-fast-generate-001 (比較) ===")
try:
    start = time.time()
    response = client.models.generate_images(
        model="imagen-4.0-fast-generate-001",
        prompt=prompt,
        config=types.GenerateImagesConfig(number_of_images=1)
    )
    elapsed = time.time() - start
    for i, img in enumerate(response.generated_images):
        img.image.save(f"test_imagen4_compare.png")
        print(f"Image saved: test_imagen4_compare.png")
    print(f"Time: {elapsed:.1f}s")
except Exception as e:
    print(f"Error: {e}")
