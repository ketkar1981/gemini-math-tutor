import os
from google import genai

# The SDK client will automatically look for the GEMINI_API_KEY
# environment variable if you don't pass an explicit key.
# This is the safest way to use the key in Codespaces.

try:
    # 1. Get the key from the environment variable
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")

    # 2. Initialize the client
    client = genai.Client(api_key=api_key)

    # 3. Use the client
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Explain the best practice for API key security in a brief sentence."
    )
    print(response.text)

except Exception as e:
    print(f"An error occurred: {e}")