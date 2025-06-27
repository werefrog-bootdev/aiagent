from pathlib import Path


def get_files_info(working_directory, directory=None):
    # If the directory argument is None, set it to the current directory
    if directory is None:
        directory = "."
    
    # If the working_directory or directory argument is not a valid directory
    # return an error string:
    try:
        _working_directory = Path(working_directory).resolve(strict=True)
        _directory = Path(_working_directory / directory).resolve(strict=True)
    except FileNotFoundError as err:
        return f"Error: {err}"
    
    # If the directory argument is outside the working_directory
    try:
        _directory.relative_to(_working_directory)
    except ValueError:
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

    # If the directory argument is not a directory, return an error string
    if not _directory.is_dir():
        return f'Error: "{directory}" is not a directory'

    # Build and return a string representing the contents of the directory. It should use this format
    files_info = []
    for item in _directory.iterdir():
        if item.is_file():
            files_info.append(f"{item.name}: file_size={item.stat().st_size} bytes, is_dir=False")
        elif item.is_dir():
            files_info.append(f"{item.name}: file_size={item.stat().st_size} bytes, is_dir=True")
    
    return "\n".join(files_info)

    """If any errors are raised by the standard library functions,
    catch them and instead return a string describing the error. Always prefix error strings with "Error:".
    """
