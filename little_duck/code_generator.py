from dataclasses import dataclass
from typing import Dict, List, Tuple

from .quadruples import (
    Operand,
    QuadrupleConstVariable,
    QuadrupleIdentifier,
    QuadrupleLineNumber,
    QuadrupleTempVariable,
)
from .quadruples import Quadruple as RawQuadruple
from .quadruples import QuadrupleOperation as RawOp
from .scope import GlobalScope, Scope
from .stack import Stack
from .vm_instructions import VirtualMachineInstruction
from .vm_memory_scope import MemoryScopeTemplate
from .vm_types import Constant, FunctionDirectoryEntry, GeneratedCode
from .vm_types import Quadruple as FinalQuadruple

type_map = {
    'int': 0,
    'bool': 1,
    'float': 2,
    'string': 3,
}

class LittleDuckCodeGenerator:
    def __init__(self,
                 debug: bool = False):
        self.debug = debug
        self.tables = GlobalScope()
        self.raw_quadruples: List[RawQuadruple] = []

        self.function_map: Dict[str, int] = {}
        self.scope_stack = Stack[Scope]()
        self.variable_map_stack = Stack[Tuple[Dict[str, int], int, int]]()

        self.function_directory: List[FunctionDirectoryEntry] = []
        self.memory_templates: List[MemoryScopeTemplate] = []
        self.constants: List[Constant] = []
        self.quadruples: List[FinalQuadruple] = []

    def generate(self,
                 tables: GlobalScope,
                 raw_quadruples: List[RawQuadruple]) -> GeneratedCode:
        # Set values
        self.tables = tables
        self.raw_quadruples = raw_quadruples

        # Generate function directory & map
        sorted_functions = sorted(self.tables.functions.values(),
                                  key=lambda f: f.start_index)
        for i, f in enumerate(sorted_functions):
            self.function_directory.append(FunctionDirectoryEntry(i, f.start_index))
            self.function_map[f.identifier] = i

        # Generate constants table
        sorted_constants = sorted(self.tables.constants)
        self.constants = [(type_map[c.type], c.value) for c in sorted_constants]

        # Process global scope
        self.scope_stack.push(self.tables)
        self.variable_map_stack.push(variable_map(len(self.constants), self.tables))
        self.memory_templates.append(count_variables(self.tables))

        # Generate new quadruples
        self.map_raw_quadruples()

        return (self.function_directory, self.memory_templates,
                self.constants, self.quadruples)
    
    def map_raw_quadruples(self):
        for i, raw_quadruple in enumerate(self.raw_quadruples):
            operation, left, right, result = raw_quadruple
            vm_operation = VirtualMachineInstruction[operation.name].value

            #
            # Scope management & Jumps
            #
            if operation == RawOp.OPEN_STACK_FRAME:
                # handle OPEN_STACK_FRAME
                # Get scope based on id (quad number)
                stack = self.scope_stack.top().child(i)
                offset = self.variable_map_stack.top()[2]

                # Add new scope to stack
                self.scope_stack.push(stack)
                self.variable_map_stack.push(variable_map(offset, stack))
                self.memory_templates.append(count_variables(stack))

                self.log(i, "New variable map:", self.variable_map_stack.top())
                self.log(i, "New memory template", len(self.memory_templates) - 1, self.memory_templates[-1])

                # Add quadruple with memory template id
                self.quadruples.append((vm_operation, len(self.memory_templates) - 1, None, None))

            elif operation == RawOp.CLOSE_STACK_FRAME:
                # handle CLOSE_STACK_FRAME
                self.quadruples.append((vm_operation, None, None, None))

                self.scope_stack.pop()
                self.variable_map_stack.pop()

            #
            # Jumps
            #
            elif operation in (RawOp.GOTO, RawOp.GOTOT, RawOp.GOTOF):
                # handle GOTO, GOTOT, GOTOF
                if not isinstance(result, QuadrupleLineNumber):
                    raise ValueError(f"GOTO doesnt end with Line Number: {result}")
                if operation == RawOp.GOTO:
                    self.quadruples.append((vm_operation, None, None, result.number))
                else:
                    # GOTOT/F condition
                    if left is None:
                        raise ValueError(f"Missing value in quadruple {i}: left")
                    value = self.relative_address(left)
                    self.quadruples.append((vm_operation, value, None, result.number))

            #
            # Functions
            #
            elif operation == RawOp.FUNCTION_CALL:
                # handle FUNCTION_CALL
                if not isinstance(left, QuadrupleIdentifier):
                    raise ValueError(f"Invalid value in quadruple {i}: left")
                function_id = self.function_map[left.identifier]

                if result is None or isinstance(result, QuadrupleLineNumber):
                    # Function that returns void
                    self.quadruples.append((vm_operation, function_id, None, None))
                else:
                    # Function that returns a value
                    value = self.relative_address(result)
                    self.quadruples.append((vm_operation, function_id, None, value))

            elif operation == RawOp.RETURN:
                # handle RETURN
                if left is None:
                    self.quadruples.append((vm_operation, None, None, None))
                else:
                    value = self.relative_address(left)
                    self.quadruples.append((vm_operation, value, None, None))

            elif operation == RawOp.FUNCTION_PARAMETER:
                # handle FUNCTION_PARAMETER
                if left is None:
                    raise ValueError(f"Missing value in quadruple {i}: left")
                value = self.relative_address(left)
                self.quadruples.append((vm_operation, value, None, None))

            elif operation == RawOp.FUNCTION_ARGUMENT:
                # handle FUNCTION_ARGUMENT
                if not isinstance(result, QuadrupleIdentifier):
                    raise ValueError(f"Invalid value in quadruple {i}: result")
                value = self.relative_address(result)
                self.quadruples.append((vm_operation, None, None, value))

            #
            # Console
            #
            elif operation == RawOp.PRINT:
                # handle PRINT
                self.quadruples.append((vm_operation, None, None, None))

            #
            # Variables
            #
            elif operation == RawOp.ASSIGN:
                # handle ASSIGN
                if left is None:
                    raise ValueError(f"Missing value in quadruple {i}: left")
                if result is None or isinstance(result, QuadrupleLineNumber):
                    raise ValueError(f"Missing value in quadruple {i}: result")
                
                operand_value = self.relative_address(left)
                result_value = self.relative_address(result)
                self.quadruples.append((vm_operation, operand_value, None, result_value))

            #
            # Binary Operations
            #
            elif operation in (RawOp.AND, RawOp.OR):
                # handle boolean operations
                if left is None:
                    raise ValueError(f"Missing value in quadruple {i}: left")
                if right is None:
                    raise ValueError(f"Missing value in quadruple {i}: right")
                if result is None or isinstance(result, QuadrupleLineNumber):
                    raise ValueError(f"Missing value in quadruple {i}: result")
                
                left_value = self.relative_address(left)
                right_value = self.relative_address(right)
                result_value = self.relative_address(result)
                self.quadruples.append((vm_operation, left_value, right_value, result_value))

            elif operation in (RawOp.EQUALS, RawOp.LESSTHAN, RawOp.MORETHAN):
                # handle comparison operations
                if left is None:
                    raise ValueError(f"Missing value in quadruple {i}: left")
                if right is None:
                    raise ValueError(f"Missing value in quadruple {i}: right")
                if result is None or isinstance(result, QuadrupleLineNumber):
                    raise ValueError(f"Missing value in quadruple {i}: result")
                
                left_value = self.relative_address(left)
                right_value = self.relative_address(right)
                result_value = self.relative_address(result)
                self.quadruples.append((vm_operation, left_value, right_value, result_value))

            elif operation in (RawOp.ADDITION, RawOp.SUBTRACTION, 
                               RawOp.MULTIPLICATION, RawOp.DIVISION):
                # handle arithmetic operations
                if left is None:
                    raise ValueError(f"Missing value in quadruple {i}: left")
                if right is None:
                    raise ValueError(f"Missing value in quadruple {i}: right")
                if result is None or isinstance(result, QuadrupleLineNumber):
                    raise ValueError(f"Missing value in quadruple {i}: result")
                
                left_value = self.relative_address(left)
                right_value = self.relative_address(right)
                result_value = self.relative_address(result)
                self.quadruples.append((vm_operation, left_value, right_value, result_value))

            else:
                raise ValueError(f"Unknown operation: {operation}")

    def relative_address(self, operand: Operand) -> int:
        if isinstance(operand, QuadrupleConstVariable):
            for i, constant in enumerate(self.constants):
                if constant[0] == type_map[operand.type]:
                    if constant[1] == operand.value:
                        return i
            raise ValueError(f"Constant not found: {operand}")

        elif isinstance(operand, QuadrupleTempVariable):
            current_scope = self.variable_map_stack.top()
            temp_offset = current_scope[1]
            return temp_offset + operand.number
        
        elif isinstance(operand, QuadrupleIdentifier):
            for current_scope in self.variable_map_stack:
                variable_map = current_scope[0]
                if operand.identifier in variable_map:
                    return variable_map[operand.identifier]
            raise ValueError(f"Variable not found: {operand}")

        else:
            raise ValueError(f"Operand type not supported: {type(operand)}")
        
    #
    # Debug
    #
    def log(self, *args):
        if self.debug:
            print(*args)
    

@dataclass(frozen=True, order=True)
class VariableMapType:
    type: int
    declare_index: int
    identifier: str

def variable_map(offset: int, scope: Scope) -> Tuple[Dict[str, int], int, int]:
    """
    Generates the local scope variable memory addresses based on type and declaration order.

    Returns tuple with variable map, starting offset for temp variables and final offset for next stack.
    """
    variables = sorted([
        VariableMapType(type_map[v.type], v.declare_index, v.identifier)
        for v in scope.variables.values()])
    temp_offset = offset + len(variables)
    total_count = temp_offset + scope.temp_var_count()
    return {v.identifier: offset + i for i, v in enumerate(variables) }, temp_offset, total_count

def count_variables(scope: Scope) -> MemoryScopeTemplate:
    variables = scope.variables.values()
    def count(type: str) -> int:
        return sum(1 for v in variables if v.type == type)

    return MemoryScopeTemplate(activation_address=scope.id,
                               int_count=count('int'),
                               bool_count=count('bool'),
                               float_count=count('float'),
                               str_count=count('string'),
                               temp_count=scope.temp_var_count())



