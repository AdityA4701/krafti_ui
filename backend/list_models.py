import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

try:
    print("Fetching available Groq models...")
    models = client.models.list()
    
    print("\n--- Available Models ---")
    for model in models.data:
        print(f"- {model.id}")
        
    print("\n-----------------------")
    
except Exception as e:
    print(f"Error fetching models: {e}")
