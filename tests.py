from functions.get_files_info import get_files_info


working_directory = "calculator"


def run_test(directory):
    result = get_files_info(working_directory, directory)
    print(result)


directories = [".", "pkg", "/bin", "../"]
for directory in directories:
    run_test(directory)
