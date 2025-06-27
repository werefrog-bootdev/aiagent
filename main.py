import os
import sys

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
api_model = os.environ.get("GEMINI_API_MODEL", "gemini-2.0-flash-001")

if not api_key:
    print("Error: environment variable 'GEMINI_API_KEY' is missing.")
    sys.exit(1)


def ask_question(prompt):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model=api_model,contents=prompt)    
    print(response.text)
    print("Prompt tokens:", response.usage_metadata.prompt_token_count)
    print("Response tokens:", response.usage_metadata.candidates_token_count)


def main(prompt):
    ask_question(prompt)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: no prompt provided.\nUsage: python main.py \"Your prompt here\"")
        sys.exit(1)

    main(prompt=sys.argv[1])
