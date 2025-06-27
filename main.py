import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
api_model = os.environ.get("GEMINI_API_MODEL", "gemini-2.0-flash-001")

if not api_key:
    print("Error: environment variable 'GEMINI_API_KEY' is missing.")
    sys.exit(1)


def ask_question(user_prompt):
    client = genai.Client(api_key=api_key)
    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    response = client.models.generate_content(
        model=api_model,
        contents=messages,
    )    
    print(response.text)
    print("Prompt tokens:", response.usage_metadata.prompt_token_count)
    print("Response tokens:", response.usage_metadata.candidates_token_count)


def main(user_prompt):
    ask_question(user_prompt)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: no prompt provided.\nUsage: python main.py \"Your prompt here\"")
        sys.exit(1)

    main(user_prompt=sys.argv[1])
