from typing import Callable, List, TypeVar

from .analyzer import LittleDuckAnalyzer, qstr
from .code_generator import LittleDuckCodeGenerator
from .lexer import LittleDuckLexer
from .parser import LittleDuckParser
from .vm_types import GeneratedCode


class LittleDuckCompiler():
    def __init__(self, debug: bool = False):
        self.debug = debug

    def compile(self, file_name: str) -> GeneratedCode:
        lexer = LittleDuckLexer()
        parser = LittleDuckParser()
        analyzer = LittleDuckAnalyzer(debug=self.debug)
        code_generator = LittleDuckCodeGenerator(debug=self.debug)

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
        raw_quadruples, tables = analyzer.analyze(tree)
        self.log("File analyzed successfully")
        
        if self.debug:
            self.log(tables)
            self.log_list(raw_quadruples, lambda q: f"({', '.join(list(map(qstr, q)))})")

        # Generate intermediate code
        code = code_generator.generate(tables, raw_quadruples)

        if self.debug:
            func_dir, mem_list, constants, quadruples = code

            self.log("Constants:")
            self.log_list(constants, str)

            self.log("Function directory:")
            self.log_list(func_dir, str)

            self.log("Memory scope templates:")
            self.log_list(mem_list, str)

            self.log("Final Quadruples:")
            self.log_list(quadruples, lambda q: f"({', '.join(list(map(str, q)))})")

        self.log("File compiled successfully")
        return code

    #
    # Debug
    #
    def log(self, *args):
        if self.debug:
            print(*args)

    T = TypeVar('T')
    def log_list(self, values: List[T], text: Callable[[T], str]):
        if not self.debug:
            return
        
        number_width = len(str(len(values)))
        for i, value in enumerate(values):
            amount_of_spaces = number_width - len(str(i))
            spaces = ' ' * amount_of_spaces
            print(f"{i}:{spaces} {text(value)}")
