from stanza import shell

while True:
    text = input("stanza >> ")
    result, error = shell.run("<stdin>", text)
    if not error:
        if result:
            print(result)
    else:
        print(error.as_string())
