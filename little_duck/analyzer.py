from typing import List, Optional

from .errors import SemanticError
from .nodes import (
    AssignmentNode,
    ASTNode,
    BinaryOperationNode,
    DeclareVariableNode,
    FunctionDeclarationNode,
    IfConditionNode,
    PrintNode,
    ProgramNode,
    ReadVariableNode,
    ScopeNode,
    TypeNode,
    UnaryOperationNode,
    ValueNode,
    VoidFunctionCallNode,
    WhileCycleNode,
)
from .stack import Stack
from .tables import FunctionMetadata, Scope, VariableMetadata


class LittleDuckAnalyzer():
    def __init__(self, debug: bool = False):
        self.debug = debug

        self.scopes = Stack[Scope]()
        self.types: List[TypeNode] = []

    def analyze(self, program: ProgramNode):
        self.scopes = Stack[Scope]()
        self.types = self.default_types()

        # Analyze Program
        self.a_ProgramNode(program)

        return program # Filled up tree, ready for conversion

    #
    # Program & Scope handling
    #
    def a_ProgramNode(self, node: ProgramNode):
        self.log("Analyzing program", node.identifier)

        # Create global scope
        self.scopes.push(Scope())
        self.log("Opened scope", "global")

        # Global variables & functions
        for variable in node.global_vars:
            self.a_DeclareVariableNode(variable)
        for function in node.global_funcs:
            self.a_FunctionDeclarationNode(function)

        # Main function
        self.a_ScopeNode(node.body)

        # Close global scope
        self.scopes.pop()
        self.log("Closed scope", "global")
        self.log("Program", node.identifier, "analyzed successfully")

    def a_ScopeNode(self, node: ScopeNode):
        # Create scope
        self.scopes.push(Scope(id=self.scopes.size()))
        self.log("Opened scope", node.identifier)

        # Analyze statements
        for statement in node.statements:
            self.analize_node(statement)

        # Delete scope
        self.scopes.pop()
        self.log("Closed scope", node.identifier)

    #
    # Statement analyzers
    #
    def a_DeclareVariableNode(self, node: DeclareVariableNode):
        current_scope = self.scopes.top()

        # Check if variable already existed
        if current_scope.has_variable(node.identifier):
            raise SemanticError(f"Invalid redeclaration of '{node.identifier}'", node)
        
        # Check if type exists
        if self.type_exists(node.type):
            raise SemanticError(f"Type '{node.type.identifier}' does not exist", node)

        # Variable can be added
        current_scope.add_variable(VariableMetadata(identifier=node.identifier,
                                                    type=node.type.identifier))
        self.log("Registered variable", node.identifier)
        
    def a_FunctionDeclarationNode(self, node: FunctionDeclarationNode):
        current_scope = self.scopes.top()

        # Check if function already existed
        if current_scope.has_function(node.identifier):
            raise SemanticError(f"Invalid redeclaration of '{node.identifier}'", node)

        # Check parameter types
        for parameter in node.parameters:
            if self.type_exists(parameter.type):
                raise SemanticError(f"Type '{parameter.type.identifier}' does not exist", parameter)

        # Function can be added
        if node.type is None:
            type_identifier = None
        else:
            type_identifier = node.type.identifier
        parameter_list = list(map(lambda n: (n.identifier, n.type.identifier), node.parameters))

        current_scope.add_function(FunctionMetadata(identifier=node.identifier,
                                                    type=type_identifier,
                                                    parameters=parameter_list))
        self.log("Registered function", node.identifier)

        # Analize the body
        node.body.statements = node.parameters + node.body.statements
        self.a_ScopeNode(node.body)

    def a_AssignmentNode(self, node: AssignmentNode):
        # Evaluate expression
        # This will populate the 'type' field
        self.analize_node(node.value)

        if node.value.type is None:
            raise SemanticError("Type of expression could not be inferred", node.value)

        # Check if variable exists
        variable: Optional[VariableMetadata] = None
        for scope in self.scopes:
            variable = scope.get_variable(node.identifier)
            if variable is not None:
                break
        if variable is None:
            raise SemanticError(f"'{node.identifier}' does not exist in this scope", node)
        
        # Check if types match
        if variable.type != node.value.type.identifier:
            raise SemanticError(f"Value of type '{node.value.type.identifier}' cannot be assigned to variable of type '{variable.type}'", node)
        
        self.log("Assigned to variable", node.identifier)

    def a_VoidFunctionCallNode(self, node: VoidFunctionCallNode):
        # Check if function exists
        function: Optional[FunctionMetadata] = None
        for scope in self.scopes:
            function = scope.get_function(node.identifier)
            if function is not None:
                break
        if function is None:
            raise SemanticError(f"'{node.identifier}' does not exist in this scope", node)
        
        # Check if number of arguments match
        if len(function.parameters) != len(node.arguments):
            raise SemanticError(f"'{node.identifier}' takes {len(function.parameters)}, but {len(node.arguments)} were provided", node)
        
        # Evaluate arguments
        for i, argument in enumerate(node.arguments):
            parameter_name, parameter_type = function.parameters[i]

            # Evaluate expression
            # This will populate the 'type' field
            self.analize_node(argument)

            if argument.type is None:
                raise SemanticError("Type of expression could not be inferred", argument)

            # Check if types match
            if argument.type.identifier != parameter_type:
                raise SemanticError(f"Parameter '{parameter_name}' is of type '{parameter_type}', not '{argument.type}'", node)
            
        self.log("Called void function", node.identifier)

    def a_PrintNode(self, node: PrintNode):
        # Evaluate arguments
        for argument in node.arguments:
            # Evaluate expression
            self.analize_node(argument)

        self.log("Printed in console")

    def a_IfConditionNode(self, node: IfConditionNode):
        self.log("If statement begin")

        # Evaluate expression
        # This will populate the 'type' field
        self.analize_node(node.condition)

        if node.condition.type is None:
            raise SemanticError("Type of expression could not be inferred", node.condition)

        # Condition must be boolean (int)
        if node.condition.type.identifier != 'int':
            raise SemanticError("Condition on an If statement must be boolean (type 'int')", node)
        self.log("If condition analyzed")

        # Analyze if and else bodies
        self.a_ScopeNode(node.body)
        if node.else_body:
            self.a_ScopeNode(node.else_body)

        self.log("If statement end")

    def a_WhileCycleNode(self, node: WhileCycleNode):
        self.log("While statement begin")

        # Evaluate expression
        # This will populate the 'type' field
        self.analize_node(node.condition)

        if node.condition.type is None:
            raise SemanticError("Type of expression could not be inferred", node.condition)

        # Condition must be boolean (int)
        if node.condition.type.identifier != 'int':
            raise SemanticError("Condition on a While statement must be boolean (type 'int')", node)
        self.log("While condition analyzed")
        
        # Analyze cycle body
        self.a_ScopeNode(node.body)
        self.log("While statement end")
    
    #
    # Expression analyzers
    #
    def a_ValueNode(self, node: ValueNode):
        # Passthrough value type
        node.type = TypeNode(node.value.primitive_type)
        self.log("Literal of type", node.value.primitive_type)

    def a_ReadVariableNode(self, node: ReadVariableNode):
        # Check if variable exists
        variable: Optional[VariableMetadata] = None
        for scope in self.scopes:
            variable = scope.get_variable(node.identifier)
            if variable is not None:
                break
        if variable is None:
            raise SemanticError(f"'{node.identifier}' does not exist in this scope", node)
        
        # Update type of expression
        node.type = TypeNode(variable.type)
        
        self.log("Got variable", node.identifier)

    def a_BinaryOperationNode(self, node: BinaryOperationNode):
        # Evaluate expressions
        # This will populate the 'type' field
        self.analize_node(node.left_side)
        self.analize_node(node.right_side)

        if node.left_side.type is None:
            raise SemanticError("Type of expression could not be inferred", node.left_side)
        if node.right_side.type is None:
            raise SemanticError("Type of expression could not be inferred", node.right_side)

        # Check if types match
        if node.left_side.type != node.right_side.type:
            # Types don't match, so attempt to
            types = (node.left_side.type.identifier, node.right_side.type.identifier)
            supported_types = [
                ('float', 'int'),
                ('int', 'float'),
            ]
            if types in supported_types:
                # Cast all ints to floats
                node.left_side.type = TypeNode('float')
                node.right_side.type = TypeNode('float')
            else:
                raise SemanticError(f"Operator '{node.operator}' cannot be used with '{node.left_side.type.identifier}','{node.right_side.type.identifier}' operands", node)
        
        # Update type of expression
        if node.operator in ['<','>','!=']:
            # For boolean operators, output will always be int
            node.type = TypeNode('int')
        else:
            node.type = node.left_side.type

        self.log("Performed binary operation", node.operator)

    def a_UnaryOperationNode(self, node: UnaryOperationNode):
        # Evaluate expression
        # This will populate the 'type' field
        self.analize_node(node.expression)

        if node.expression.type is None:
            raise SemanticError("Type of expression could not be inferred", node.expression)

        # At the moment, no unary operators can be used with string
        if node.expression.type.identifier == 'string':
            raise SemanticError(f"Operator '{node.operator}' cannot be used with value of type '{node.expression.type.identifier}'", node)
        
        # Update type of expression
        node.type = node.expression.type
        self.log("Performed unary operation", node.operator)

    # Helpers
    def analize_node(self, node: ASTNode):
        # Analyze depending on node type
        analyze_node = getattr(self, 'a_' + type(node).__name__)
        analyze_node(node)

    def type_exists(self, type: TypeNode) -> bool:
        return type not in self.types    
    
    def default_types(self) -> List[TypeNode]:
        return [
            # Primitives
            TypeNode(identifier='int'),
            TypeNode(identifier='float'),
            TypeNode(identifier='string'),
        ]

    # Debug
    def log(self, *args):
        if self.debug:
            print(*args)
