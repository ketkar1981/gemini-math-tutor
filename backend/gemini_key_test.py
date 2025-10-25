import os
from google import genai

try:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Explain the best practice for API key security in a brief sentence."
    )
    print(response.text)
except Exception as e:
    print(f"An error occurred: {e}")