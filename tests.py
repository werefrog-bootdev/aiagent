from functions.run_python_file import run_python_file


working_directory = "calculator"


def run_test(filepath):
    result = run_python_file(working_directory, filepath)
    print(result)


cases = [
    "main.py",
    "tests.py",
    "../main.py",
    "nonexistent.py",
]

for filepath in cases:
    run_test(filepath)
