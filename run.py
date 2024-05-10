from little_duck import LittleDuckLexer, LittleDuckParser

#
# Test the compiler
#
if __name__ == "__main__":
    # Build the lexer
    lexer = LittleDuckLexer()
    file_contents = ""

    with open('code.ld', 'r') as file:
        file_contents = file.read()

    result = lexer.input(file_contents)
    result = list(map(lambda x: x.type, result))
    # print(result)
    print("File tokenized successfully")

    # Build the parser
    parser = LittleDuckParser()

    # Test it
    parser.parse(file_contents, lexer=lexer)
    print("File parsed successfully")