from collections import deque
from typing import List, Optional, Tuple, cast

from .errors import SemanticError
from .nodes import (
    AssignmentNode,
    BinaryOperationNode,
    DeclareVariableNode,
    DoWhileCycleNode,
    ExpressionNode,
    FunctionDeclarationNode,
    FunctionScopeNode,
    IfConditionNode,
    NonVoidFunctionCallNode,
    PrintNode,
    ProgramNode,
    ReadVariableNode,
    ReturnStatementNode,
    ScopeNode,
    StatementNode,
    TypeNode,
    UnaryOperationNode,
    ValueNode,
    VoidFunctionCallNode,
    WhileCycleNode,
)
from .quadruples import (
    Operand,
    PolishExpression,
    PolishValue,
    Quadruple,
    QuadrupleConstVariable,
    QuadrupleIdentifier,
    QuadrupleLineNumber,
    QuadrupleOperation,
    QuadrupleTempVariable,
)
from .scope import FunctionMetadata, GlobalScope, Scope, VariableMetadata
from .semantic_cubes import binary_semantic_cubes, unary_semantic_cubes
from .stack import Stack

AnalyzedProgram = Tuple[List[Quadruple], GlobalScope]

class LittleDuckAnalyzer():
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.module_name = ""

        self.scopes = Stack[Scope]()
        self.types: List[TypeNode] = self.default_types()

        self.quadruples: List[Quadruple] = []
        self.pending_jumps = Stack[int]()

    def analyze(self,
                program: ProgramNode,
                dependencies: AnalyzedProgram = ([], GlobalScope())) -> AnalyzedProgram:
        # Analyze Program
        self.module_name = program.identifier
        global_scope = self.a_ProgramNode(program, dependencies)

        # Return generated quadruples and tables
        return self.quadruples, global_scope

    #
    # Program & Scope handling
    #
    def a_ProgramNode(self, node: ProgramNode, dependencies: AnalyzedProgram) -> GlobalScope:
        self.log("Analyzing program", node.identifier)
        dep_quadruples, dep_scope = dependencies

        # Add startup jump
        self.quadruples.append(
            (QuadrupleOperation.GOTO, None, None, None))
        self.pending_jumps.push(len(self.quadruples) - 1)

        # Create global scope
        global_scope = dep_scope # GlobalScope()
        self.scopes.push(global_scope)
        self.log("Opened scope", "global")

        self.a_DeclareVariableNode(DeclareVariableNode('exit_code', TypeNode('int')))

        # Add previous quadruples
        self.quadruples += dep_quadruples

        # Global variables & functions
        for variable in node.global_vars:
            self.a_DeclareVariableNode(variable)
        for function in node.global_funcs:
            self.a_FunctionDeclarationNode(function)

        # Main function
        self.a_FunctionDeclarationNode(node.main_func)

        # Close global scope
        self.scopes.pop()
        self.log("Closed scope", "global")

        # Create main func call
        self.fill_pending_jump(self.pending_jumps.pop())
        self.quadruples.append(
            (QuadrupleOperation.FUNCTION_CALL, QuadrupleIdentifier('main'), None, QuadrupleIdentifier('exit_code')))

        self.log("Program", node.identifier, "analyzed successfully")

        return global_scope

    def a_ScopeNode(self, node: ScopeNode):
        parent_scope = self.scopes.top()

        # Create scope
        self.scopes.push(Scope(id=len(self.quadruples)))
        self.quadruples.append((QuadrupleOperation.OPEN_STACK_FRAME, None, None, None))
        self.log("Opened scope", node.identifier)

        # Analyze statements
        for statement in node.statements:
            self.analize_statement_node(statement)

        # Close scope
        closed_scope = self.scopes.pop()
        self.quadruples.append((QuadrupleOperation.CLOSE_STACK_FRAME, None, None, None))

        # Save closed scope in parent
        parent_scope.inner_scopes.append(closed_scope)

        self.log("Closed scope", node.identifier)

    def a_FunctionScopeNode(self, node: FunctionScopeNode):
        parent_scope = self.scopes.top()

        # Create scope
        self.scopes.push(Scope(id=len(self.quadruples), function_name=node.identifier))
        self.quadruples.append((QuadrupleOperation.OPEN_STACK_FRAME, QuadrupleIdentifier(node.identifier), None, None))
        self.log("Opened function scope", node.identifier)

        # Build declare quadruples
        for argument in node.arguments:
            self.a_DeclareVariableNode(argument)

        # Build arg loading quadruples
        for argument in reversed(node.arguments):
            assign_quadruple = (QuadrupleOperation.FUNCTION_ARGUMENT, None, None, QuadrupleIdentifier(argument.identifier))
            self.quadruples.append(assign_quadruple)
            self.scopes.top().variables[argument.identifier].is_initialized = True

        # Analyze statements
        for statement in node.statements:
            self.analize_statement_node(statement)

        # Delete scope
        closed_scope = self.scopes.pop()
        self.quadruples.append((QuadrupleOperation.CLOSE_STACK_FRAME, None, None, None))

        # Save closed scope in parent
        parent_scope.inner_scopes.append(closed_scope)

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
                                                    module=self.module_name,
                                                    type=node.type.identifier,
                                                    is_initialized=False,
                                                    is_used=False,
                                                    declare_index=len(self.quadruples)))

        # Build quadruple
        # quadruple = (QuadrupleOperation.DECLARE, QuadrupleIdentifier(node.identifier), None, None)
        # self.quadruples.append(quadruple)

        self.log("Declared variable", node.identifier)
        
    def a_FunctionDeclarationNode(self, node: FunctionDeclarationNode):
        global_scope = cast(GlobalScope, self.scopes.bottom())

        # Check if function already existed
        if global_scope.has_function(node.identifier):
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

        global_scope.add_function(FunctionMetadata(identifier=node.identifier,
                                                   module=self.module_name,
                                                   type=type_identifier,
                                                   parameters=parameter_list,
                                                   returns=False,
                                                   is_used=node.identifier == 'main',
                                                   start_index=len(self.quadruples)))
        
        # Build quadruple
        # quadruple = (QuadrupleOperation.FUNCTION_DECLARATION, QuadrupleIdentifier(node.identifier), None, None)
        # self.quadruples.append(quadruple)

        self.log("Declared function", node.identifier)

        # Analize the body
        self.a_FunctionScopeNode(node.body)

        # Make sure function contains at least one return
        # TODO: Detect return in all paths
        if not global_scope.functions[node.identifier].returns:
            type_name = node.type.identifier if node.type else 'void'
            raise SemanticError(f"Function '{type_name} {node.identifier}' never returns", node)

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
        quadruple = (QuadrupleOperation.ASSIGN, result, None, QuadrupleIdentifier(node.identifier))
        self.quadruples.append(quadruple)

        # Register the variable was initialized
        variable.is_initialized = True

        self.log("Assigned to variable", node.identifier)

    def a_VoidFunctionCallNode(self, node: VoidFunctionCallNode):
        # Prohibit calling main
        if node.identifier == 'main':
            raise SemanticError("Main function cannot be called from within the program", node)

        # Check if function exists
        global_scope = cast(GlobalScope, self.scopes.bottom())
        function = global_scope.get_function(node.identifier)

        if function is None:
            raise SemanticError(f"'{node.identifier}' does not exist in this module", node)
        
        # Check if number of arguments match
        if len(function.parameters) != len(node.arguments):
            raise SemanticError(f"'{node.identifier}' takes {len(function.parameters)}, but {len(node.arguments)} were provided", node)
        
        # Evaluate arguments
        argument_results: List[Operand] = []

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
            
            # Cache result for later
            result = self.process_polish_expression(polish_argument)
            argument_results.append(result)

        # Build argument quadruples
        for result in argument_results:
            argument_quadruple = (QuadrupleOperation.FUNCTION_PARAMETER, result, None, None)
            self.quadruples.append(argument_quadruple)
        
        # Build call quadruple
        quadruple = (QuadrupleOperation.FUNCTION_CALL, QuadrupleIdentifier(node.identifier), None, None)
        self.quadruples.append(quadruple)

        # Register the function was used
        global_scope.functions[node.identifier].is_used = True

        self.log("Called void function", node.identifier)

    def a_PrintNode(self, node: PrintNode):
        # Evaluate arguments
        argument_results: List[Operand] = []

        for argument in node.arguments:
            # Evaluate expression
            polish_argument = self.analize_expression_node(argument)
            self.log("Print argument expression:", ' '.join(map(qstr, polish_argument)))

            # Cache result for later
            result = self.process_polish_expression(polish_argument)
            argument_results.append(result)

        # Build argument quadruples
        for result in argument_results:
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
        if node.condition.type.identifier != 'bool': 
            raise SemanticError("Condition on an If statement must be boolean (type 'bool')", node)
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
        if node.condition.type.identifier != 'bool':
            raise SemanticError("Condition on a While statement must be boolean (type 'bool')", node)
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
        end_quadruple = (QuadrupleOperation.GOTO, None, None, QuadrupleLineNumber(evaluation_quad_index))
        self.quadruples.append(end_quadruple)

        # Fill pending jump to end of while
        self.fill_pending_jump(end_quad_index)
        
        self.log("While statement end")

    def a_DoWhileCycleNode(self, node: DoWhileCycleNode):
        self.log("DoWhile statement begin")

        # Evaluate expression
        # This will populate the 'type' field
        polish_condition = self.analize_expression_node(node.condition)
        self.log("DoWhile condition expression:", ' '.join(map(qstr, polish_condition)))

        if node.condition.type is None:
            raise SemanticError("Type of expression could not be inferred", node.condition)

        # Condition must be boolean (int)
        if node.condition.type.identifier != 'bool':
            raise SemanticError("Condition on a While statement must be boolean (type 'bool')", node)
        self.log("DoWhile condition analyzed")

        # NOTE: Punto neurálgico 1
        # Add pending jump to DO body
        line_to_jump_to = len(self.quadruples)

        # Analyze cycle body
        self.a_ScopeNode(node.body)

        # Generate quadruples for condition
        result = self.process_polish_expression(polish_condition)

        # NOTE: Punto neurálgico 2
        # # Fill pending jump to start of do-while
        # self.fill_pending_jump(self.pending_jumps.pop())

        # Create jump to start of do-while (condtion met)
        condition_quadruple = (QuadrupleOperation.GOTOT, result, None, QuadrupleLineNumber(line_to_jump_to))
        self.quadruples.append(condition_quadruple)
        
        self.log("DoWhile statement end")
    
    def a_ReturnStatementNode(self, node: ReturnStatementNode):
        # Get the function that is returning
        function_name = 'main'
        for scope in self.scopes:
            if scope.function_name is not None:
                function_name = scope.function_name
                break
        
        # Get the data for that function
        global_scope = cast(GlobalScope, self.scopes.bottom())
        function = global_scope.get_function(function_name)

        if function is None:
            # NOTE: This should NEVER happen
            # Getting this means compiler is broken
            print("Global scope:", global_scope.functions)
            raise SemanticError("Return statement is not part of any function", node)
        
        # Check if function type matches return type
        if node.value is not None:
            # Evaluate expression
            # This will populate the 'type' field
            polish = self.analize_expression_node(node.value)
            self.log("Return statement expression:", ' '.join(map(qstr, polish)))

            if node.value.type is None:
                raise SemanticError("Type of expression could not be inferred", node.value)
            
            # Check function type is not void
            if function.type is None:
                raise SemanticError(f"Trying to return {node.value.type.identifier} in void function {function.identifier}", node)

            # Check if types match
            if node.value.type.identifier != function.type:
                raise SemanticError(f"Trying to return {node.value.type.identifier} in {function.type} function {function.identifier}", node.value)

            # Build quadruple
            result = self.process_polish_expression(polish)
            self.quadruples.append((QuadrupleOperation.RETURN, result, None, None))

        else:
            # Trying to return void
            # Check function type is void
            if function.type is not None:
                raise SemanticError(f"Trying to return void in {function.type} function {function.identifier}", node)
            
            # Build quadruple
            self.quadruples.append((QuadrupleOperation.RETURN, None, None, None))

        # Register the function returned
        global_scope.functions[function_name].returns = True

        self.log("Function return statement")

    #
    # Expression analyzers
    # Must return polish expression as a deque
    #
    def a_ValueNode(self, node: ValueNode) -> PolishExpression:
        # Passthrough value type
        node.type = TypeNode(node.value.primitive_type)
        self.log("Literal of type", node.value.primitive_type, ":", qstr(node.value.value))

        # Create const object
        const_var = QuadrupleConstVariable(node.value.primitive_type, node.value.value)

        # Register constant in global scope
        global_scope = cast(GlobalScope, self.scopes.bottom())
        global_scope.constants.add(const_var)

        # Build polish vector to return
        return deque([const_var])

    def a_ReadVariableNode(self, node: ReadVariableNode) -> PolishExpression:
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

        # Check if variable has been initialized
        if not variable.is_initialized:
            raise SemanticError(f"'{node.identifier}' was used before being initialized", node)

        # temp_var = QuadrupleTempVariable(self.current_temp)
        # quadruple = (QuadrupleOperation.READ, QuadrupleIdentifier(node.identifier), None, temp_var)
        # self.current_temp += 1
        # self.quadruples.append(quadruple)

        var = QuadrupleIdentifier(node.identifier)

        # Register the variable was used
        variable.is_used = True
        
        self.log("Got variable", node.identifier)

        # Build polish vector to return
        return deque([var])
    
    def a_NonVoidFunctionCallNode(self, node: NonVoidFunctionCallNode) -> PolishExpression:
        # Prohibit calling main
        if node.identifier == 'main':
            raise SemanticError("Main function cannot be called from within the program", node)

        # Check if function exists
        # Check if function exists
        global_scope = cast(GlobalScope, self.scopes.bottom())
        function = global_scope.get_function(node.identifier)

        if function is None:
            raise SemanticError(f"'{node.identifier}' does not exist in this scope", node)
        
        # Check that function is non-void
        if function.type is None:
            raise SemanticError("Function that returns void cannot be used as an expression", node)

        # Check if number of arguments match
        if len(function.parameters) != len(node.arguments):
            raise SemanticError(f"'{node.identifier}' takes {len(function.parameters)}, but {len(node.arguments)} were provided", node)
        
        # Evaluate arguments
        argument_results: List[Operand] = []

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
            
            # Cache result for later
            result = self.process_polish_expression(polish_argument)
            argument_results.append(result)

        # Build argument quadruples
        for result in argument_results:
            argument_quadruple = (QuadrupleOperation.FUNCTION_PARAMETER, result, None, None)
            self.quadruples.append(argument_quadruple)
        
        # Update type of expression
        node.type = TypeNode(function.type)

        # Build call quadruple
        current_scope = self.scopes.top()
        temp_var = QuadrupleTempVariable(current_scope.current_temp)
        quadruple = (QuadrupleOperation.FUNCTION_CALL, QuadrupleIdentifier(node.identifier), None, temp_var)
        current_scope.current_temp += 1
        self.quadruples.append(quadruple)

        # Register the function was used
        global_scope.functions[node.identifier].is_used = True

        self.log(f"Called {function.type} function", node.identifier)

        # Build polish vector to return
        return deque([temp_var])

    def a_BinaryOperationNode(self, node: BinaryOperationNode) -> PolishExpression:
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
        return self.create_binary_polish(node.operator, polish_left, polish_right)

    def a_UnaryOperationNode(self, node: UnaryOperationNode) -> PolishExpression:
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
        return self.create_unary_polish(node.operator, polish)

    #
    # Operator shortcuts
    #
    def create_binary_polish(self,
                             operator: QuadrupleOperation,
                             polish_left: PolishExpression,
                             polish_right: PolishExpression) -> PolishExpression:
        global_scope = cast(GlobalScope, self.scopes.bottom())

        # Return variation based on shortcutted operator
        if operator == QuadrupleOperation.NOTEQUALS:
            equals = QuadrupleOperation.EQUALS
            false = QuadrupleConstVariable('bool', False)
            global_scope.constants.add(false)

            return deque([equals, equals, *polish_left, *polish_right, false])

        # Standard polish expression
        return deque([operator, *polish_left, *polish_right])

    def create_unary_polish(self,
                            operator: QuadrupleOperation,
                            value: PolishExpression) -> PolishExpression:
        global_scope = cast(GlobalScope, self.scopes.bottom())

        # Get operation and right side const
        if operator == QuadrupleOperation.SUBTRACTION:
            new_operator = QuadrupleOperation.MULTIPLICATION
            const_var = QuadrupleConstVariable('int', -1)
        elif operator == QuadrupleOperation.NOT:
            new_operator = QuadrupleOperation.EQUALS
            const_var = QuadrupleConstVariable('bool', False)
        else:
            raise ValueError("Unary operator", operator, "not implemented")
        
        # Register constant in global scope
        global_scope.constants.add(const_var)

        # Build final polish expression
        return deque([new_operator, *value, const_var])

    #
    # Polish Expression handling
    #
    def process_polish_expression(self, polish: PolishExpression) -> Operand:
        current_scope = self.scopes.top()
        stack = Stack[PolishValue]()

        # Add first item to the stack
        stack.push(polish.popleft())
        
        # If first token is operation, more operations should be coming
        while len(stack) > 1 or isinstance(stack.top(), QuadrupleOperation):
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
                temp_var = QuadrupleTempVariable(current_scope.current_temp)
                quadruple = (operator, left_side_value, right_side_value, temp_var)
                current_scope.current_temp += 1
                self.quadruples.append(quadruple) # type: ignore[arg-type]

                # Save temp var in stack
                stack.push(temp_var)
            else:
                # If no operation is currently possible,
                # get more tokens from polish vector
                stack.push(polish.popleft())
                # NOTE: Should never crash, because if deque has been
                # fully read, all operations should be solvable
                # A crash would indicate this algorithm is wrong

        # At this point, stack will always have only 1 item
        # Process and return that remaining item
        # (remember one item polish vectors skip the while loop entirely)
        return stack.pop() # type: ignore[return-value]

    #
    # Helpers
    #
    # TODO: Warnings
    # def check_closed_scope(self, scope: Scope):
    #     # Check if all variables & functions have been intialized, used, etc
    #     pass

    def fill_pending_jump(self, quad_index: int):
        old_quadruple = self.quadruples[quad_index]
        new_quadruple = (old_quadruple[0], old_quadruple[1], old_quadruple[2], QuadrupleLineNumber(len(self.quadruples)))
        self.quadruples[quad_index] = new_quadruple

    def analize_expression_node(self, node: ExpressionNode) -> PolishExpression:
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
            TypeNode(identifier='bool'),
        ]

    #
    # Debug
    #
    def log(self, *args):
        if self.debug:
            print(*args)

def qstr(value) -> str:
    if isinstance(value, QuadrupleOperation):
        return value.value
    if isinstance(value, str):
        return f'"{value}"'
    return str(value)
