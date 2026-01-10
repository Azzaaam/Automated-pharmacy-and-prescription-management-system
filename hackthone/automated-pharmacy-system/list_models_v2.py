import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GENAI_API_KEY")
client = genai.Client(api_key=api_key)

try:
    print("--- Listing Models ---")
    pager = client.models.list() 
    for model in pager:
        # Pager yields Model objects, let's try to inspect them safely
        try:
            name = getattr(model, 'name', 'Unknown')
            display = getattr(model, 'display_name', 'No Display Name')
            print(f"Found: {name} ({display})")
        except:
            print(f"Raw Model Object: {model}")

except Exception as e:
    print(f"Error: {e}")
