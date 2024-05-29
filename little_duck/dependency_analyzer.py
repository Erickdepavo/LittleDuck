from .analyzer import AnalyzedProgram, LittleDuckAnalyzer
from .nodes import ProgramNode
from .quadruples import QuadrupleOperation
from .scope import GlobalScope


class LittleDuckDependencyAnalyzer(LittleDuckAnalyzer):
    #
    # Program & Scope handling
    #
    def a_ProgramNode(self, node: ProgramNode, dependencies: AnalyzedProgram) -> GlobalScope:
        self.log("Analyzing dependency", node.identifier)
        dep_quadruples, dep_scope = dependencies

        # Add fake startup jump to avoid messing up
        # line numbers. It will be removed in the end
        self.quadruples.append((QuadrupleOperation.GOTO, None, None, None))

        # Create global scope
        global_scope = dep_scope # GlobalScope()
        self.scopes.push(global_scope)
        self.log("Opened scope", "global")

        # Add previous quadruples
        self.quadruples += dep_quadruples

        # Global variables & functions
        for variable in node.global_vars:
            self.a_DeclareVariableNode(variable)
        for function in node.global_funcs:
            self.a_FunctionDeclarationNode(function)

        # Close global scope
        self.scopes.pop()
        self.log("Closed scope", "global")

        # Remove fake startup jump
        self.quadruples.pop(0)
        self.log("Dependency", node.identifier, "analyzed successfully")

        return global_scope