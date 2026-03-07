import os
from dotenv import load_dotenv

load_dotenv(".env")
import google.genai as genai
from google.genai import types

client = genai.Client()

models_to_test = [
    "models/gemini-2.0-flash",
    "models/gemini-2.0-flash-lite-preview-02-05",
]

print("--- Testing Model Availability ---")
for m in models_to_test:
    print(f"\nTrying to generate content with: {m}")
    try:
        response = client.models.generate_content(
            model=m,
            contents="Say hi",
        )
        print(f"SUCCESS! -> {response.text.strip()}")
    except Exception as e:
        print(f"FAILED -> {type(e).__name__}: {str(e)}")
