from functions.get_file_content import get_file_content


working_directory = "calculator"


def run_test(filepath):
    result = get_file_content(working_directory, filepath)
    print(result)


directories = ["main.py", "pkg/calculator.py", "/bin/cat",]
for directory in directories:
    run_test(directory)
