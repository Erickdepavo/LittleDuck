from collections import deque
from typing import Any, Deque, List, Optional, Tuple

from .errors import SemanticError
from .nodes import (
    AssignmentNode,
    BinaryOperationNode,
    DeclareVariableNode,
    ExpressionNode,
    FunctionDeclarationNode,
    FunctionScopeNode,
    IfConditionNode,
    PrintNode,
    ProgramNode,
    ReadVariableNode,
    ScopeNode,
    StatementNode,
    TypeNode,
    UnaryOperationNode,
    ValueNode,
    VoidFunctionCallNode,
    WhileCycleNode,
)
from .quadruples import PolishVariable, QuadrupleOperation, QuadrupleTempVariable
from .semantic_cubes import binary_semantic_cubes, unary_semantic_cubes
from .stack import Stack
from .tables import FunctionMetadata, Scope, VariableMetadata


class LittleDuckAnalyzer():
    def __init__(self, debug: bool = False):
        self.debug = debug

        self.scopes = Stack[Scope]()
        self.types: List[TypeNode] = self.default_types()

        self.quadruples: List[Tuple] = []
        self.current_temp: int = 0
        self.pending_jumps = Stack[int]()

    def analyze(self, program: ProgramNode) -> List[Tuple]:
        # Analyze Program
        self.a_ProgramNode(program)

        # Return generated quadruples
        return self.quadruples

    #
    # Program & Scope handling
    #
    def a_ProgramNode(self, node: ProgramNode):
        self.log("Analyzing program", node.identifier)

        # Create global scope
        self.scopes.push(Scope())
        self.quadruples.append((QuadrupleOperation.OPEN_STACK_FRAME, None, None, None))
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
        self.quadruples.append((QuadrupleOperation.CLOSE_STACK_FRAME, None, None, None))
        self.log("Closed scope", "global")
        self.log("Program", node.identifier, "analyzed successfully")

    def a_ScopeNode(self, node: ScopeNode):
        # Create scope
        self.scopes.push(Scope(id=self.scopes.size()))
        self.quadruples.append((QuadrupleOperation.OPEN_STACK_FRAME, None, None, None))
        self.log("Opened scope", node.identifier)

        # Analyze statements
        for statement in node.statements:
            self.analize_statement_node(statement)

        # Delete scope
        self.scopes.pop()
        self.quadruples.append((QuadrupleOperation.CLOSE_STACK_FRAME, None, None, None))
        self.log("Closed scope", node.identifier)

    def a_FunctionScopeNode(self, node: FunctionScopeNode):
        # Load args into temp variables
        for i, argument in enumerate(node.arguments):
            # Build load quadruple
            argument_quadruple = (QuadrupleOperation.FUNCTION_LOAD_ARGUMENT, argument.identifier, None, QuadrupleTempVariable(self.current_temp + i))
            self.quadruples.append(argument_quadruple)

        # Create scope
        self.scopes.push(Scope(id=self.scopes.size()))
        self.quadruples.append((QuadrupleOperation.OPEN_STACK_FRAME, None, None, None))
        self.log("Opened function scope", node.identifier)

        # Analyze first statements (argument declaration & assignment)
        for i, argument in enumerate(node.arguments):
            # Build declare quadruple 
            self.a_DeclareVariableNode(argument)

            # Build assign quadruple 
            assign_quadruple = (QuadrupleOperation.ASSIGN, argument.identifier, QuadrupleTempVariable(self.current_temp + i), None)
            self.quadruples.append(assign_quadruple)

        # Increment current temp (because of arg loading)
        self.current_temp += len(node.arguments)

        # Analyze statements
        for statement in node.statements:
            self.analize_statement_node(statement)

        # Delete scope
        self.scopes.pop()
        self.quadruples.append((QuadrupleOperation.CLOSE_STACK_FRAME, None, None, None))
        self.log("Closed function scope", node.identifier)

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

        # Build quadruple
        quadruple = (QuadrupleOperation.DECLARE, node.identifier, None, None)
        self.quadruples.append(quadruple)

        self.log("Declared variable", node.identifier)
        
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
        
        # Build quadruple
        quadruple = (QuadrupleOperation.FUNCTION_DECLARATION, node.identifier, None, None)
        self.quadruples.append(quadruple)

        self.log("Declared function", node.identifier)

        # Analize the body
        self.a_FunctionScopeNode(node.body)

    def a_AssignmentNode(self, node: AssignmentNode):
        # Evaluate expression
        # This will populate the 'type' field
        polish = self.analize_expression_node(node.value)
        self.log("Assignment expression:", ' '.join(map(qstr, polish)))

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
        
        # Build quadruple
        result = self.process_polish_expression(polish)
        quadruple = (QuadrupleOperation.ASSIGN, node.identifier, result, None)
        self.quadruples.append(quadruple)

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
            polish_argument = self.analize_expression_node(argument)
            self.log("Function call argument expression:", ' '.join(map(qstr, polish_argument)))

            if argument.type is None:
                raise SemanticError("Type of expression could not be inferred", argument)

            # Check if types match
            if argument.type.identifier != parameter_type:
                raise SemanticError(f"Parameter '{parameter_name}' is of type '{parameter_type}', not '{argument.type}'", node)
            
            # Build argument quadruple
            result = self.process_polish_expression(polish_argument)
            argument_quadruple = (QuadrupleOperation.FUNCTION_PARAMETER, result, None, None)
            self.quadruples.append(argument_quadruple)
        
        # Build call quadruple
        quadruple = (QuadrupleOperation.FUNCTION_CALL, node.identifier, None, None)
        self.quadruples.append(quadruple)

        self.log("Called void function", node.identifier)

    def a_PrintNode(self, node: PrintNode):
        # Evaluate arguments
        for argument in node.arguments:
            # Evaluate expression
            polish_argument = self.analize_expression_node(argument)
            self.log("Print argument expression:", ' '.join(map(qstr, polish_argument)))

            # Build argument quadruple
            result = self.process_polish_expression(polish_argument)
            argument_quadruple = (QuadrupleOperation.FUNCTION_PARAMETER, result, None, None)
            self.quadruples.append(argument_quadruple)

        # Build print quadruple
        quadruple = (QuadrupleOperation.PRINT, None, None, None)
        self.quadruples.append(quadruple)

        self.log("Printed in console")

    def a_IfConditionNode(self, node: IfConditionNode):
        self.log("If statement begin")

        # Evaluate expression
        # This will populate the 'type' field
        polish_condition = self.analize_expression_node(node.condition)
        self.log("If condition expression:", ' '.join(map(qstr, polish_condition)))

        if node.condition.type is None:
            raise SemanticError("Type of expression could not be inferred", node.condition)

        # Condition must be boolean (int)
        if node.condition.type.identifier != 'int':
            raise SemanticError("Condition on an If statement must be boolean (type 'int')", node)
        self.log("If condition analyzed")

        # NOTE: Punto neurálgico 1
        # Generate quadruples for expression
        result = self.process_polish_expression(polish_condition)
        condition_quadruple = (QuadrupleOperation.GOTOF, result, None, None)
        self.quadruples.append(condition_quadruple)

        # Track pending jump
        self.pending_jumps.push(len(self.quadruples) - 1)

        # Analyze if body
        self.a_ScopeNode(node.body)
        if node.else_body:
            # NOTE: Punto neurálgico 3
            # Create end of if body jump to end of else
            end_quadruple = (QuadrupleOperation.GOTO, None, None, None)
            self.quadruples.append(end_quadruple)

            # Correctly handle pending jumps
            quad_index = self.pending_jumps.pop()
            self.pending_jumps.push(len(self.quadruples) - 1)
            self.fill_pending_jump(quad_index)

            # Analyze else body
            self.a_ScopeNode(node.else_body)

        # NOTE: Punto neurálgico 2
        # Fill pending jump
        self.fill_pending_jump(self.pending_jumps.pop())

        self.log("If statement end")

    def a_WhileCycleNode(self, node: WhileCycleNode):
        self.log("While statement begin")

        # Evaluate expression
        # This will populate the 'type' field
        polish_condition = self.analize_expression_node(node.condition)
        self.log("While condition expression:", ' '.join(map(qstr, polish_condition)))

        if node.condition.type is None:
            raise SemanticError("Type of expression could not be inferred", node.condition)

        # Condition must be boolean (int)
        if node.condition.type.identifier != 'int':
            raise SemanticError("Condition on a While statement must be boolean (type 'int')", node)
        self.log("While condition analyzed")

        # NOTE: Punto neurálgico 1
        # Add pending jump to expression evaluation
        self.pending_jumps.push(len(self.quadruples))

        # Generate quadruples for expression
        result = self.process_polish_expression(polish_condition)

        # NOTE: Punto neurálgico 2
        # Create jump to end of while (condtion not met)
        condition_quadruple = (QuadrupleOperation.GOTOF, result, None, None)
        self.quadruples.append(condition_quadruple)

        # Add pending jump to end of while jump (GOTOF quad)
        self.pending_jumps.push(len(self.quadruples) - 1)

        # Analyze cycle body
        self.a_ScopeNode(node.body)

        # NOTE: Punto neurálgico 3
        # Get where to fill for evaluation and end of while
        end_quad_index = self.pending_jumps.pop()
        evaluation_quad_index = self.pending_jumps.pop()

        # Create filled jump back to expression evaluation after running body
        end_quadruple = (QuadrupleOperation.GOTO, None, None, evaluation_quad_index)
        self.quadruples.append(end_quadruple)

        # Fill pending jump to end of while
        self.fill_pending_jump(end_quad_index)
        
        self.log("While statement end")
    
    #
    # Expression analyzers
    # Must return polish expression as a deque
    #
    def a_ValueNode(self, node: ValueNode) -> Deque[Any]:
        # Passthrough value type
        node.type = TypeNode(node.value.primitive_type)
        self.log("Literal of type", node.value.primitive_type, ":", qstr(node.value.value))
        # Build polish vector to return
        return deque([node.value.value])

    def a_ReadVariableNode(self, node: ReadVariableNode) -> Deque[Any]:
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

        # Build polish vector to return
        return deque([PolishVariable(node.identifier)])

    def a_BinaryOperationNode(self, node: BinaryOperationNode) -> Deque[Any]:
        # Evaluate expressions
        # This will populate the 'type' field
        polish_left = self.analize_expression_node(node.left_side)
        polish_right = self.analize_expression_node(node.right_side)

        if node.left_side.type is None:
            raise SemanticError("Type of expression could not be inferred", node.left_side)
        if node.right_side.type is None:
            raise SemanticError("Type of expression could not be inferred", node.right_side)

        # Check semantic cube for binary operations
        resulting_type = binary_semantic_cubes[node.operator.value][node.left_side.type.identifier][node.right_side.type.identifier]

        if resulting_type is None:
            raise SemanticError(f"Operator '{node.operator.value}' cannot be used with '{node.left_side.type.identifier}','{node.right_side.type.identifier}' operands", node)

        # Update type of expression
        node.type = TypeNode(identifier=resulting_type)
        self.log("Performed binary operation", node.operator.value)

        # Build polish vector to return
        return deque([node.operator]) + polish_left + polish_right

    def a_UnaryOperationNode(self, node: UnaryOperationNode) -> Deque[Any]:
        # Evaluate expression
        # This will populate the 'type' field
        polish = self.analize_expression_node(node.expression)

        if node.expression.type is None:
            raise SemanticError("Type of expression could not be inferred", node.expression)

        # Check semantic cube for unary operations
        resulting_type = unary_semantic_cubes[node.operator.value][node.expression.type.identifier]

        # At the moment, no unary operators can be used with string
        if resulting_type is None:
            raise SemanticError(f"Unary operator '{node.operator.value}' cannot be used with value of type '{node.expression.type.identifier}'", node)
        
        # Update type of expression
        node.type = TypeNode(identifier=resulting_type)
        self.log("Performed unary operation", node.operator.value)

        # Build polish vector to return
        op_deque: Deque[Any] = deque([node.operator])
        unary_deque: Deque[None] = deque([None])
        return op_deque + polish + unary_deque

    # Helpers
    def process_polish_expression(self, polish: Deque[Any]):
        stack = Stack[Any]([polish.popleft()]) # Stack will always have at least one item

        """
        This was the original while condition:
        not (len(stack) == 1 and not isinstance(stack.top(), QuadrupleOperation)):

        Simplified with De Morgan's laws:
        not (A and not B) -> not A or not not B -> not A or B

        Other simplifications:
        not len(stack) == 1 -> len(stack) > 1
        """
        # Avoid exiting if there are pending operations in the stack
        while len(stack) > 1 or isinstance(stack.top(), QuadrupleOperation):
            if isinstance(stack.top(), PolishVariable):
                # Token needs to be processed
                stack.push(self.process_polish_token(stack.pop()))
            
            # See if operation can be processed
            if (
                len(stack) > 2 and \
                isinstance(stack.top(2), QuadrupleOperation) and \
                not isinstance(stack.top(1), QuadrupleOperation) and \
                not isinstance(stack.top(0), QuadrupleOperation)
            ):
                # Operation can be created
                right_side_value = stack.pop()
                left_side_value = stack.pop()
                operator = stack.pop()

                # Create operation
                temp_var = QuadrupleTempVariable(self.current_temp)
                quadruple = (operator, left_side_value, right_side_value, temp_var)
                self.current_temp += 1
                self.quadruples.append(quadruple)

                # Save temp var in stack
                stack.push(temp_var)

            # Read from polish vector if possible
            if polish:
                stack.push(polish.popleft())

        # At this point, stack will always have only 1 item
        # Process and return that remaining item
        # (remember one item polish vectors skip the while loop entirely)
        return self.process_polish_token(stack.pop())

    def process_polish_token(self, value: Any):
        if isinstance(value, QuadrupleTempVariable):
            # Variable has already been added to quadruples
            return value
        elif isinstance(value, PolishVariable):
            # Read variable
            temp_var = QuadrupleTempVariable(self.current_temp)
            quadruple = (QuadrupleOperation.READ, value.identifier, None, temp_var)
            self.current_temp += 1
            self.quadruples.append(quadruple)
            return temp_var
        # elif isinstance(value, PolishFunction):
        # ...
        else:
            # Value here is either temp variable or literal
            return value

    def fill_pending_jump(self, quad_index: int):
        old_quadruple = self.quadruples[quad_index]
        new_quadruple = (old_quadruple[0], old_quadruple[1], old_quadruple[2], len(self.quadruples))
        self.quadruples[quad_index] = new_quadruple

    def analize_expression_node(self, node: ExpressionNode) -> Deque[Any]:
        # Analyze depending on node type
        analyze_node = getattr(self, 'a_' + type(node).__name__)
        return analyze_node(node)

    def analize_statement_node(self, node: StatementNode):
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

def qstr(value) -> str:
    if isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, PolishVariable):
        return value.identifier
    elif isinstance(value, QuadrupleOperation):
        return value.value
    return str(value)
