import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.run_python_file import run_python_file
from functions.write_file import write_file


load_dotenv()

env_file = ".env"
if not os.path.exists(env_file):
    print(f"Warning: '{env_file}' file not found. Please create one with GEMINI_API_KEY and GEMINI_API_MODEL variables.")

api_key = os.environ.get("GEMINI_API_KEY")
api_default_model = "gemini-2.0-flash-001"
api_model = os.environ.get("GEMINI_API_MODEL", api_default_model)

default_working_directory = "./calculator"
working_directory = os.environ.get("GEMINI_WORKING_DIRECTORY", default_working_directory)

if not api_key:
    print("Error: environment variable 'GEMINI_API_KEY' is missing.\n"
          "Please set it in your environment or in a '.env' file in the working directory.\n"
          "Example .env file:\n"
          "GEMINI_API_KEY=your_api_key_here\n"
          "GEMINI_API_MODEL=gemini-2.0-flash-001")
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


def call_function(function_call_part, verbose=False):
    if verbose:
        print(f" - Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")
    
    functions_map = {
        "get_files_info": get_files_info,
        "get_file_content": get_file_content,
        "run_python_file": run_python_file,
        "write_file": write_file,
    }

    function_name = function_call_part.name
    if function_name not in functions_map:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )
    function = functions_map[function_name]
    args = function_call_part.args
    function_result = function(working_directory, **args)

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
    )

def ask_question(client, messages, verbose=False):
    return client.models.generate_content(
        model=api_model,
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt
        ),
    )



def get_function_calls(response, user_prompt, is_verbose):
    if not response.candidates:
        return []
    
    return  [
        call_function(part.function_call, is_verbose)
        for candidate in response.candidates
        for part in candidate.content.parts
        if getattr(part, "function_call", False)
    ]


def main(user_prompt, is_verbose=False):
    client = genai.Client(api_key=api_key)
    messages = [types.Content(role="user", parts=[types.Part(text=user_prompt)])]

    if is_verbose:
        print()
        print("User prompt:")
        print(user_prompt)
        print()
        print("Function calls:")
            
    for _ in range(20):  # Retry up to 3 times
        response = ask_question(client, messages, is_verbose)
        messages.extend(candidate.content for candidate in response.candidates)
        
        function_calls = get_function_calls(response, user_prompt, is_verbose)
        if function_calls:
            messages.extend(function_calls)
            response = ask_question(client, messages, is_verbose)
        else:
            print(f"Finale response:")
            print(response.text)
            if is_verbose:
                print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
                print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
            break

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Error: no prompt provided.')
        print('Usage: python main.py "Your prompt here"')
        sys.exit(1)

    is_verbose = len(sys.argv) > 2 and sys.argv[2] == "--verbose"

    main(user_prompt=sys.argv[1], is_verbose=is_verbose)
