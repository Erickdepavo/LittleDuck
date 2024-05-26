from little_duck import LittleDuckAnalyzer, LittleDuckLexer, LittleDuckParser
from little_duck.analyzer import qstr
from little_duck.errors import SemanticError

#
# Test the compiler
#
if __name__ == "__main__":
    try:
        # file_name = 'code.ld'
        file_name = 'algorithms.ld'

        # Build the lexer
        lexer = LittleDuckLexer()
        file_contents = ""

        with open(file_name, 'r') as file:
            file_contents = file.read()

        tokens = lexer.input(file_contents)
        result = list(map(lambda x: x.type, tokens))
        print(result)
        print("File tokenized successfully")

        # Build the parser
        parser = LittleDuckParser()

        # Test it
        tree = parser.parse(file_contents, lexer=LittleDuckLexer())
        print(tree)

        print("File parsed successfully")

        # Analyze
        analyzer = LittleDuckAnalyzer(debug=True)
        quadruples, tables = analyzer.analyze(tree)

        print("File analyzed successfully")

        print(tables)

        number_width = len(str(len(quadruples)))
        for i, quadruple in enumerate(quadruples):
            amount_of_spaces = number_width - len(str(i))
            spaces = ' ' * amount_of_spaces
            print(f"{i}:{spaces} ({', '.join(list(map(qstr, quadruple)))})")

        print("File compiled successfully")

    except SyntaxError as error:
        print("SyntaxError:", error)

    except SemanticError as error:
        print("SemanticError:", error.message)
