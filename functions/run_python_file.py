import subprocess

from pathlib import Path


def run_python_file(working_directory, file_path):
    """
    Runs a Python file in the specified working directory.

    Args:
        working_directory (str): The directory in which to run the Python file.
        file_path (str): The path to the Python file to be executed.

    Returns:
        str: The output of the executed Python file.
    """
    # If the file_path argument is not a valid file, return an error string
    try:
        _working_directory = Path(working_directory).resolve(strict=True)
    except FileNotFoundError as err:
        return f"Error: {err}"

    _file_path = Path(_working_directory / file_path).resolve()

    # If the file_path argument is outside the working_directory
    try:
        _file_path.relative_to(_working_directory)
    except ValueError:
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

    # If file not found or is not a file, return an error string
    if not _file_path.is_file():
        return f'Error: File "{file_path}" not found.'
    
    # if the file is not a Python file, return an error string
    if not _file_path.suffix == '.py':
        return f'Error: "{file_path}" is not a Python file.'
    
    # Run the Python file and capture the output
    try:
        result = subprocess.run(
            ['python', _file_path],
            capture_output=True,
            text=True,
            cwd=working_directory,
            timeout=30  # Optional timeout to prevent hanging
        )    
    except subprocess.TimeoutExpired:
        return "Error: Script execution timed out after 30 seconds."
    except Exception as e:
        return f"Error: executing Python file: {e}"
    
    output = []

    if result.stdout.strip():
        output.append("STDOUT:\n" + result.stdout.strip())

    if result.stderr.strip():
        output.append("STDERR:\n" + result.stderr.strip())

    if result.returncode != 0:
        output.append(f"Process exited with code {result.returncode}")

    if not output:
        return "No output produced."

    return "\n\n".join(output)
