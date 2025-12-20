import shell

while True:
    text = input("basic > ")
    result, error = shell.run("<stdin>", text)
    if not error:
        print(result)
    else:
        print(error.as_string())
