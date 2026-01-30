import os
import sys
from dotenv import load_dotenv

print("--- DIAGNOSIS STARTED ---")
print("Python executable:", sys.executable)
print("Python version:", sys.version)

# 1. Check Imports
try:
    from groq import Groq
    print("✅ Groq library imported successfully.")
except ImportError as e:
    print(f"❌ Failed to import groq: {e}")
    sys.exit(1)

try:
    import requests
    print("✅ requests library imported successfully.")
except ImportError as e:
    print(f"❌ Failed to import requests: {e}")

# 2. Check Environment Variables
load_dotenv()
groq_key = os.getenv("GROQ_API_KEY")
removebg_key = os.getenv("REMOVEBG_API_KEY")

if not groq_key:
    print("❌ ERROR: GROQ_API_KEY is missing in .env")
else:
    print(f"✅ GROQ_API_KEY found (starts with: {groq_key[:8]}...)")

if not removebg_key:
    print("❌ ERROR: REMOVEBG_API_KEY is missing in .env")
else:
    print(f"✅ REMOVEBG_API_KEY found")

# 3. Test Groq API (Text only first)
if groq_key:
    try:
        print("\nTesting Groq API (Text Model)...")
        client = Groq(api_key=groq_key)
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": "Say hello"}],
            model="llama-3.3-70b-versatile",
        )
        print("✅ Groq API (Text) Success:", completion.choices[0].message.content)
        
        # 4. Test Groq API (Vision Model availability check)
        print("\nTesting Groq API (Vision Model - Text only check)...")
        # We try sending just text to the vision model to check if the model name is valid/accessible
        completion_vision = client.chat.completions.create(
            messages=[{"role": "user", "content": "Describe a cat"}],
            model="llama-3.2-90b-vision-preview",
        )
        print("✅ Groq API (Vision) Success:", completion_vision.choices[0].message.content[:50], "...")
        
    except Exception as e:
        print(f"❌ Groq API Failed: {e}")
        import traceback
        traceback.print_exc()

print("--- DIAGNOSIS FINISHED ---")
