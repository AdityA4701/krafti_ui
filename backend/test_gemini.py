import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"Checking Gemini API Key: {'Found' if api_key else 'Missing'}")
if api_key:
    print(f"Key starts with: {api_key[:5]}...")

try:
    print("\nText Test: Configurating Gemini...")
    genai.configure(api_key=api_key)
    
    print("Listing models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")

    print("\nGenerating text with gemini-1.5-flash...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Hello, can you see me?")
    print(f"✅ Response: {response.text}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
