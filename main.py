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

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan.
You can perform the following operations:

- List files and directories

All paths you provide should be relative to the working directory.
You do not need to specify the working directory in your function calls
as it is automatically injected for security reasons.
"""

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their " \
    "sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to " \
                "the working directory. If not provided, lists files in the " \
                "working directory itself.",
            ),
        },
    ),
)

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Retrieves the content of a file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to retrieve, relative to " \
                "the working directory.",
            ),
        },
    ),
)

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the Python file to execute, relative to " \
                "the working directory.",
            ),
        },
    ),
)

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes content to a file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to write, relative to " \
                "the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file.",
            ),
        },
    ),
)

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)


def ask_question(user_prompt, is_verbose=False):
    client = genai.Client(api_key=api_key)
    messages = [types.Content(role="user", parts=[types.Part(text=user_prompt)])]

    response = client.models.generate_content(
        model=api_model,
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt
        ),
    )

    function_calls = [
        part.function_call
        for candidate in response.candidates
        for part in candidate.content.parts
        if getattr(part, "function_call", False)
    ]
    
    function_call_descriptions = "\n".join(
        f"Calling function: {call.name}({call.args})"
        for call in function_calls
    )

    if is_verbose:
        output = [
            f"User prompt: {user_prompt}",
            f"Function calls: {function_call_descriptions or 'None'}",
            f"Gemini response: {response.text}",
            f"Prompt tokens: {response.usage_metadata.prompt_token_count}",
            f"Response tokens: {response.usage_metadata.candidates_token_count}",
        ]
    else:
        output = [response.text]
        if function_calls:
            output.append(function_call_descriptions)

    print(*output, sep="\n")



def main(user_prompt, is_verbose=False):
    ask_question(user_prompt, is_verbose=is_verbose)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Error: no prompt provided.')
        print('Usage: python main.py "Your prompt here"')
        sys.exit(1)

    is_verbose = len(sys.argv) > 2 and sys.argv[2] == "--verbose"

    main(user_prompt=sys.argv[1], is_verbose=is_verbose)
