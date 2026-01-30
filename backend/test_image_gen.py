import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model_name = "gemini-2.0-flash-exp-image-generation" # Trying the one from the list
# The user's list also had models/gemini-2.5-flash-image, but that's likely for input.

print(f"Testing image generation with {model_name}...")

try:
    model = genai.GenerativeModel(model_name)
    # Note: image generation syntax depends on the library version/model.
    # For some "imagen" models in vertex it's different, but for AI Studio it might be generate_images
    # or part of generate_content?
    
    # Actually, the python library usually exposes it via simple prompt if the model supports it?
    # Or specific method.
    
    # Let's try generate_content first as it's the standard.
    response = model.generate_content("A professional studio background for product photography, white marble table, soft lighting", generation_config={"response_mime_type": "image/jpeg"})
    
    print("Response type:", type(response))
    if response.parts:
        print("Parts found.")
        # Check if we have image data
        # Usually response.text fails if it's an image.
        try:
            print(response.text)
        except Exception as e:
            print("Could not print text (expected if image):", e)
            
    print("✅ Success (probably)")

except Exception as e:
    print(f"❌ Error: {e}")
    # Try different model
    try:
         print("Trying gemini-2.5-flash just in case...")
         model = genai.GenerativeModel("gemini-2.5-flash")
         response = model.generate_content("Generate an image of a cat")
         print("Response:", response.text)
    except Exception as e2:
        print(f"❌ Error with 2.5-flash: {e2}")
