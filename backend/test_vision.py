import os
import base64
from dotenv import load_dotenv
from groq import Groq

# Load .env variables
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
print(f"Using API Key: {api_key[:10]}...")

client = Groq(api_key=api_key)

# 1x1 white pixel base64
tiny_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1sAAAAASUVORK5CYII="

try:
    print("Sending test request to Groq Vision (llama-3.2-11b-vision-preview)...")
    completion = client.chat.completions.create(
        model="llama-3.2-11b-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What is this?"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{tiny_image_b64}"
                        },
                    },
                ],
            }
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )
    print("✅ Success! Response:")
    print(completion.choices[0].message.content)

except Exception as e:
    print("\n❌ API Request Failed!")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Message: {e}")
