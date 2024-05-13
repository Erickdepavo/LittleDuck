from little_duck import LittleDuckLexer, LittleDuckParser, LittleDuckAnalyzer
from little_duck.errors import SemanticError

#
# Test the compiler
#
if __name__ == "__main__":
    # Build the lexer
    lexer = LittleDuckLexer()
    file_contents = ""

    with open('code.ld', 'r') as file:
        file_contents = file.read()

    tokens = lexer.input(file_contents)
    result = list(map(lambda x: x.type, tokens))
    print(result)
    print("File tokenized successfully")

    # Build the parser
    parser = LittleDuckParser()

    # Test it
    tree = parser.parse(file_contents, lexer=lexer)
    print(tree)

    print("File parsed successfully")

    # Analyze
    analyzer = LittleDuckAnalyzer(debug=True)

    try:
        analyzer.analyze(tree)
        print("File analyzed successfully")
    except SemanticError as error:
        print("SemanticError:", error.message)
