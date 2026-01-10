import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GENAI_API_KEY")
if not api_key:
    print("No API key found in .env")
    exit()

client = genai.Client(api_key=api_key)

try:
    print("Fetching available models...")
    # New SDK syntax might be client.models.list(), let's try standard iteration
    pager = client.models.list() 
    for model in pager:
        print(f"Model: {model.name}")
        if "gemini" in model.name.lower():
            print(f" - Supported generation methods: {model.supported_generation_methods}")

except Exception as e:
    print(f"Error listing models: {e}")
