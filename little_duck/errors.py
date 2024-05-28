from enum import Enum

from .nodes import ASTNode
from .vm_runner import Quadruple


class LittleDuckError(Exception):
    """Little Duck Code Analysis Exception"""
    def __init__(self, message: str, node: ASTNode) -> None:
        super().__init__(message, node)
        self.message = message
        self.node = node

class SemanticError(LittleDuckError):
    """Little Duck Semantic Analysis Exception"""
    pass


class VirtualMachineError(Exception):
    """Little Duck Virtual Machine Exception"""
    def __init__(self, code: int, message: str) -> None:
        super().__init__(code, message)
        self.code = code
        self.message = message

class VirtualMachineRuntimeErrors(Enum):
    """Little Duck Virtual Machine Runtime Exceptions Enum"""
    NO_MORE_ARGUMENTS = (10, "Tried to load argument after all arguments have been loaded")
    RETURN_VALUE_NOT_FOUND = (11, "Tried to return void in a function that returns a value")
    RETURN_VALUE_IN_VOID = (12, "Tried to return a value in a function that returns void")
    UNLOADED_ARGUMENTS = (13, "Function returned before loading all arguments")

    INSTRUCTION_DOESNT_EXIST = (20, "Instruction _q0_ does not exist")
    FUNCTION_NOT_FOUND = (21, "Function directory data not found")
    STACK_TEMPLATE_NOT_FOUND = (22, "Memory allocation data not found")
    MEMORY_ADDRESS_MISSING = (23, "Memory address not found")
    GOTO_JUMP_MISSING = (24, "GOTO jump line not found")

class VirtualMachineRuntimeError(VirtualMachineError):
    """Little Duck Virtual Machine Runtime Exception"""
    def __init__(self,
                 error: VirtualMachineRuntimeErrors,
                 index: int,
                 quadruple: Quadruple) -> None:
        super().__init__(*error.value)
        self.index = index

class VirtualMachineMemoryErrors(Enum):
    """Little Duck Virtual Machine Memory Exceptions Enum"""
    ADDRESS_OUTSIDE_RANGE = (0, "Attempted to access memory address beyond the range of allocated variables.")
    UNALLOCATED_ACCESS = (1, "Attempted to access unallocated memory.")
    ALLOCATED_CONSTANT = (2, "Attempted to modify the value of a constant.")

class VirtualMachineMemoryError(VirtualMachineError):
    """Little Duck Virtual Machine Runtime Exception"""
    def __init__(self,
                 error: VirtualMachineMemoryErrors,
                 address: int) -> None:
        super().__init__(*error.value)
        self.address = address
