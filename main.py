import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
api_model = os.environ.get("GEMINI_API_MODEL", "gemini-2.0-flash-001")

client = genai.Client(api_key=api_key)

prompt = "Why is Boot.dev such a great place to learn backend development? Use one paragraph maximum."
response = client.models.generate_content(model=api_model,contents=prompt)
print(response.text)

print("Prompt tokens:", response.usage_metadata.prompt_token_count)
print("Response tokens:", response.usage_metadata.candidates_token_count)
