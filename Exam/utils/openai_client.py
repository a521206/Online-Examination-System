import os
import openai

# This ensures the API key is set at application startup.
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("The OPENAI_API_KEY environment variable is not set.")

# Initialize the client once and reuse it across the application.
# This is more efficient than creating a new client for each request.
client = openai.OpenAI(api_key=api_key) 