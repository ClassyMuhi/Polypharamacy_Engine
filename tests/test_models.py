import os
import traceback
from dotenv import load_dotenv

load_dotenv(".env")
import google.genai as genai

try:
    client = genai.Client()
    print("Listing models with 'flash' or 'pro' in the name:")
    for m in client.models.list():
        if "flash" in m.name or "pro" in m.name:
            print(f" -> {m.name}")
except Exception as e:
    print("Failed to list models:")
    print(traceback.format_exc())
