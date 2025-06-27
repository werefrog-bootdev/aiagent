from pathlib import Path


def write_file(working_directory, file_path, content):
    # If the file_path argument is not a valid file, return an error string
    try:
        _working_directory = Path(working_directory).resolve(strict=True)
        _file_path = Path(_working_directory / file_path).resolve()
    except FileNotFoundError as err:
        return f"Error: {err}"

    # If the file_path argument is outside the working_directory
    try:
        _file_path.relative_to(_working_directory)
    except ValueError:
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

    # Write the content to the file
    try:
        _file_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure parent directories exist
        _file_path.write_text(content, encoding='utf-8')
    except Exception as err:
        return f"Error: {err}"

    return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
