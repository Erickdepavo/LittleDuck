from enum import Enum
from typing import Tuple

from .nodes import ASTNode


class LittleDuckError(Exception):
    """Little Duck Code Analysis Exception"""
    def __init__(self, message: str, node: ASTNode) -> None:
        super().__init__(message, node)
        self.message = message
        self.node = node

class SemanticError(LittleDuckError):
    """Little Duck Semantic Analysis Exception"""
    pass

class CompileError(Exception):
    """Little Duck Compilation Exception"""
    def __init__(self, message: str, *args) -> None:
        super().__init__(message, *args)
        self.message = message

class VirtualMachineError(Exception):
    """Little Duck Virtual Machine Exception"""
    def __init__(self, code: int, message: str, *args) -> None:
        super().__init__(code, message, *args)
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
                 quadruple: Tuple[int, int | None, int | None, int | None]) -> None:
        super().__init__(*error.value, index)
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
        super().__init__(*error.value, address)
        self.address = address
