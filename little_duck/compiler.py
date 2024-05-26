from .analyzer import LittleDuckAnalyzer, qstr
from .errors import SemanticError
from .lexer import LittleDuckLexer
from .parser import LittleDuckParser


class LittleDuckCompiler():
    def __init__(self, debug: bool = False):
        self.debug = debug

    def compile(self, file_name: str):
        lexer = LittleDuckLexer()
        parser = LittleDuckParser()
        analyzer = LittleDuckAnalyzer(debug=self.debug)

        try:
            # Get the file contents
            file_contents = ""
            with open(file_name, 'r') as file:
                file_contents = file.read()

            # Only lex if token list will be shown
            if self.debug:
                new_lexer = LittleDuckLexer()
                tokens = new_lexer.input(file_contents)
                result = list(map(lambda x: x.type, tokens))
                self.log(result)
                self.log("File tokenized successfully")

            # Parse the code
            tree = parser.parse(file_contents, lexer=lexer)
            self.log(tree)
            self.log("File parsed successfully")

            # Analyze the code
            quadruples, tables = analyzer.analyze(tree)
            self.log("File analyzed successfully")
            
            if self.debug:
                self.log(tables)

                number_width = len(str(len(quadruples)))
                for i, quadruple in enumerate(quadruples):
                    amount_of_spaces = number_width - len(str(i))
                    spaces = ' ' * amount_of_spaces
                    self.log(f"{i}:{spaces} ({', '.join(list(map(qstr, quadruple)))})")

            # Generate intermediate code file
            # ...
            self.log("File compiled successfully")

        except SyntaxError as error:
            print("SyntaxError:", error)

        except SemanticError as error:
            print("SemanticError:", error.message)

    #
    # Debug
    #
    def log(self, *args):
        if self.debug:
            print(*args)
