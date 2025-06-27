from pathlib import Path


MAX_CHARACTERS = 10_000  # Maximum number of characters to read from the file


def get_file_content(working_directory, file_path):
    # If the file_path argument is not a valid file, return an error string
    try:
        _working_directory = Path(working_directory).resolve(strict=True)
        _file_path = Path(_working_directory / file_path).resolve(strict=True)
    except FileNotFoundError as err:
        return f"Error: {err}"

    # If the file_path argument is outside the working_directory
    try:
        _file_path.relative_to(_working_directory)
    except ValueError:
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

    # If the file_path argument is not a file, return an error string
    if not _file_path.is_file():
        return f'Error: File not found or is not a regular file: "{file_path}"'

    # Read and return the content of the file
    try:
        content = _file_path.read_text(encoding='utf-8')
    except Exception as err:
        return f"Error: {err}"
    
    if len(content) > MAX_CHARACTERS:
        content = content[:MAX_CHARACTERS]
        content += f'...File "{file_path}" truncated at 10000 characters'
    
    return content
