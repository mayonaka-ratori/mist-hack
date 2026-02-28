import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load API key from ../.env
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

prompt = "A warm, child-friendly watercolor illustration of a smiling elderly Japanese man in a garden pointing at bright red tomatoes. Sunny day, gentle soft style, simple shapes, like a picture book."

def test_imagen(model_id):
    print(f"=== Testing Model: {model_id} ===")
    start = time.time()
    
    # Try multiple methods because of SDK version ambiguity
    methods_to_try = ['generate_image', 'generate_images']
    
    found_method = None
    for method_name in methods_to_try:
        if hasattr(client.models, method_name):
            found_method = getattr(client.models, method_name)
            print(f"Using method: {method_name}")
            break
            
    if not found_method:
        print("Error: No image generation method found in client.models")
        return

    try:
        response = found_method(
            model=model_id,
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
            )
        )
        elapsed = time.time() - start
        print(f"Time: {elapsed:.1f} seconds")
        
        # Determine where images are stored (might be response.generated_images or response.images)
        images = getattr(response, 'generated_images', None)
        if images is None:
            images = getattr(response, 'images', [])
            
        for i, img_obj in enumerate(images):
            image_filename = f"test_{model_id.replace('/', '_').replace('-', '_')}_{i}.png"
            # Some versions return a PIL image, some return bytes in .image
            if hasattr(img_obj, 'image') and hasattr(img_obj.image, 'save'):
                img_obj.image.save(image_filename)
            elif hasattr(img_obj, 'save'):
                img_obj.save(image_filename)
            else:
                print(f"Could not save image object: {type(img_obj)}")
            print(f"Image saved as {image_filename}")
            
    except Exception as e:
        elapsed = time.time() - start
        print(f"Error after {elapsed:.1f}s: {e}")

if __name__ == "__main__":
    # Test with imagen-3 if available, or 4.0 as seen in list
    models = ["imagen-3.0-generate-001", "imagen-3.0-fast-generate-001", "imagen-4.0-fast-generate-001"]
    for m in models:
        test_imagen(m)
        print("\n")
