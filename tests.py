from functions.write_file import write_file


working_directory = "calculator"


def run_test(filepath, content):
    result = write_file(working_directory, filepath, content)
    print(result)


cases = [
    ("lorem.txt", "wait, this isn't lorem ipsum"),
    ("pkg/morelorem.txt", "lorem ipsum dolor sit amet"),
    ("/tmp/temp.txt", "this should not be allowed"),
]
for filepath, content in cases:
    run_test(filepath, content)
