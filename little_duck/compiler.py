from typing import Callable, Dict, List, TypeVar

from .analyzer import AnalyzedProgram, LittleDuckAnalyzer, qstr
from .code_generator import LittleDuckCodeGenerator
from .dependency_analyzer import LittleDuckDependencyAnalyzer
from .dependency_graph import DependencyGraph
from .errors import CompileError
from .lexer import LittleDuckLexer
from .parser import LittleDuckParser
from .scope import GlobalScope
from .vm_types import GeneratedCode


class LittleDuckCompiler():
    def __init__(self, debug: bool = False):
        self.debug = debug

    def compile(self,
                main_file_name: str,
                dependency_file_names: List[str]) -> GeneratedCode:
        
        # Main file parsing
        main_module = self.parse_module(main_file_name)

        if dependency_file_names:
            # Compilation has dependencies, let's resolve them
            self.log("Compilation has dependencies:", dependency_file_names)

            # Parse dependencies
            parsed_dependencies = [self.parse_module(file) for file in dependency_file_names]

            # Build dependency graph
            all_modules = [main_module] + parsed_dependencies
            all_module_names = [t[1] for t in all_modules]
            
            deps: Dict[str, List[str]] = {}
            for tree, module_name, dependencies in [main_module] + parsed_dependencies:
                # Check all dependencies exist
                for dependency in dependencies:
                    if dependency not in all_module_names:
                        raise CompileError(f"Module {dependency} not found; imported on {module_name}")
                # Write in graph
                deps[module_name] = dependencies

            dependency_graph = DependencyGraph()
            dependency_graph.build_graph(deps)

            # Detect unused modules
            unused_modules = dependency_graph.remove_unused_modules(main_module[1])

            if unused_modules:
                raise CompileError(f"Modules {', '.join(unused_modules)} are never imported by main module; they're totally unused")
            
            # Detect cycles
            dependency_graph.detect_cycles() # Will raise error if cycle is found

            # Determine compilation order
            sorted_modules = dependency_graph.topological_sort()
            self.log("Compilation order:", sorted_modules)
            
            last_module = sorted_modules.pop(0)
            if last_module != main_module[1]:
                # Main module should be the last one to be compiled
                raise CompileError(f"Invalid dependency graph, {main_module[1]} should be the first to be compiled, not {last_module}")

            # Analyze dependencies
            analyzed_program: AnalyzedProgram = ([], GlobalScope())

            while sorted_modules:
                dep_name = sorted_modules.pop()
                dep_tree = [(t[0]) for t in parsed_dependencies if t[1] == dep_name][0]

                dep_analyzer = LittleDuckDependencyAnalyzer(debug=self.debug)
                analyzed_program = dep_analyzer.analyze(dep_tree, analyzed_program)
        else:
            # Compilation doesn't have dependencies
            self.log("Compilation doesn't have dependencies")
            analyzed_program = ([], GlobalScope())

        # Analyze main module
        analyzer = LittleDuckAnalyzer(debug=self.debug)
        raw_quadruples, tables = analyzer.analyze(main_module[0], analyzed_program)
        self.log("File analyzed successfully")
        
        if self.debug:
            self.log(tables)
            self.log_list(raw_quadruples, lambda q: f"({', '.join(list(map(qstr, q)))})")

        # Generate intermediate code
        code_generator = LittleDuckCodeGenerator(debug=self.debug)
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
    
    def parse_module(self, file_name: str):
        lexer = LittleDuckLexer()
        parser = LittleDuckParser()

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

        # Get some metadata, like module name and dependencies
        return tree, tree.identifier, tree.dependencies

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
