from operator import add, and_, eq, gt, lt, mul, or_, sub, truediv
from typing import Any, Callable, List, Optional, cast

from .errors import VirtualMachineRuntimeError
from .errors import VirtualMachineRuntimeErrors as Errors
from .vm_instructions import VirtualMachineInstruction as Instruction
from .vm_memory import VirtualMachineMemory
from .vm_memory_scope import MemoryScopeTemplate
from .vm_stack_frame import ActivationRecordTemplate
from .vm_types import FunctionDirectoryEntry, Quadruple


class VirtualMachine:
    def __init__(self,
                 function_directory: List[FunctionDirectoryEntry],
                 memory_scope_templates: List[MemoryScopeTemplate],
                 constants: List[Any],
                 instructions: List[Quadruple],
                 debug: bool
    ) -> None:
        self.debug = debug

        self.function_directory = function_directory
        self.memory_scope_templates = memory_scope_templates
        self.constants = constants
        self.instructions = instructions

        self.memory = VirtualMachineMemory(debug=False)
        self.i = 0

    def run(self):
        switch = {
            Instruction.OPEN_STACK_FRAME.value: lambda q: self.OPEN(q[1]),
            Instruction.CLOSE_STACK_FRAME.value: lambda q: self.CLOSE(),

            Instruction.FUNCTION_PARAMETER.value: lambda q: self.FUNCTION_PARAMETER(q[1]),
            Instruction.FUNCTION_ARGUMENT.value: lambda q: self.FUNCTION_ARGUMENT(q[3]),

            Instruction.FUNCTION_CALL.value: lambda q: self.FUNCTION_CALL(q[1], q[3]),
            Instruction.RETURN.value: lambda q: self.RETURN(q[1]),

            Instruction.GOTO.value: lambda q: self.GOTO_all(None, q[1], q[3]),
            Instruction.GOTOT.value: lambda q: self.GOTO_all(True, q[1], q[3]),
            Instruction.GOTOF.value: lambda q: self.GOTO_all(False, q[1], q[3]),

            Instruction.ASSIGN.value: lambda q: self.ASSIGN(q[1], q[3]),

            Instruction.PRINT.value: lambda q: self.PRINT(),

            Instruction.AND.value: lambda q: self.OP_BOOL(and_, q[0], q[1], q[2], q[3]),
            Instruction.OR.value: lambda q: self.OP_BOOL(or_, q[0], q[1], q[2], q[3]),

            Instruction.EQUALS.value: lambda q: self.OP_BOOL(eq, q[0], q[1], q[2], q[3]),
            Instruction.LESSTHAN.value: lambda q: self.OP_BOOL(lt, q[0], q[1], q[2], q[3]),
            Instruction.MORETHAN.value: lambda q: self.OP_BOOL(gt, q[0], q[1], q[2], q[3]),

            Instruction.ADDITION.value: lambda q: self.OP(add, q[0], q[1], q[2], q[3]),
            Instruction.SUBTRACTION.value: lambda q: self.OP(sub, q[0], q[1], q[2], q[3]),
            Instruction.MULTIPLICATION.value: lambda q: self.OP(mul, q[0], q[1], q[2], q[3]),
            Instruction.DIVISION.value: lambda q: self.OP(truediv, q[0], q[1], q[2], q[3]),
        }

        # Allocate constants and global scope
        self.memory.initialize_global_scope(self.constants, self.memory_scope_templates[0])
        self.log(f"Initialized global scope with {len(self.constants)} constants, {self.memory_scope_templates[0].size()} global vars")

        # Run the program
        self.i = 0
        while (self.i < len(self.instructions)):
            instruction = self.instructions[self.i]

            # Action depending on instruction
            action = switch.get(instruction[0], self.not_found)
            should_continue = action(instruction)

            if should_continue:
                continue

            # Go to next instruction
            self.i += 1

        # Get exit code
        exit_code = cast(int, self.memory.global_scope.get_local(0))
        print(f"\nProgram ended with exit code: {exit_code}")

    #
    # CPU instructions
    #
    def OPEN(self, template_i: Optional[int]):
        # Get memory allocation data for new scope
        template_i = self.validate_int(template_i, Errors.STACK_TEMPLATE_NOT_FOUND)            
        template = self.memory_scope_templates[template_i]

        # Allocate memory for new scope in current activation record
        self.memory.top().push(template)

        self.log(f"Opened scope {template_i} of size {template.size()}")
        self.log(f"New scope: {template}")
    
    def CLOSE(self):
        # Deallocate memory for current scope in current activation record
        closed_scope = self.memory.top().pop()

        # TODO: Check if all temp variables have been deallocated
        # ...

        self.log(f"Closed scope at {closed_scope.get_activation_address()}")

    def FUNCTION_PARAMETER(self, relative_address: Optional[int]):
        relative_address = self.validate_int(relative_address, Errors.MEMORY_ADDRESS_MISSING)

        # Temp address is relative to current activation record
        global_address = self.memory.convert_relative_to_global(relative_address, len(self.memory.stack_offsets) - 1)

        # Push global address to parameter stack in current activation record
        self.memory.top().parameter_push(global_address)

        self.log(f"Pushed parameter {relative_address} as global {global_address}")

    def FUNCTION_ARGUMENT(self, result_address: Optional[int]):
        result_address = self.validate_int(result_address, Errors.MEMORY_ADDRESS_MISSING)

        # Get global address from argument stack
        if not self.memory.top().arguments_to_load:
            raise self.get_error(Errors.NO_MORE_ARGUMENTS)
        
        global_address = self.memory.top().arguments_to_load.pop()

        # Get value from memory
        value = self.memory.get_global(global_address)

        # Allocate value inside local context
        self.memory.allocate_relative(result_address, value)

        self.log(f"Loaded argument from global {global_address} to {result_address}")

    def FUNCTION_CALL(self, id: Optional[int], return_value_address: Optional[int]):
        id = self.validate_int(id, Errors.FUNCTION_NOT_FOUND)

        # Get activation record data
        function_data = self.function_directory[id]

        # Get parameters
        if not self.memory.stack_frames:
            # Main function is being called
            # No parameters to load
            parameters: List[int] = []
        else:
            # Other function
            parameters = self.memory.top().parameter_pop()

        # Generate activation record
        activation_record = ActivationRecordTemplate(identifier=id,
                                                     activation_address=self.i,
                                                     return_address=self.i + 1,
                                                     arguments=parameters,
                                                     return_value_address=return_value_address)
        
        # Push new activation record into memory
        self.memory.push(activation_record)

        # Move i to start of function to execute it
        self.log(f"Called function {id}; jumping to {function_data.address}")
        self.i = function_data.address

        return True
    
    def RETURN(self, value_address: Optional[int]):
        # Get return value if given
        return_value = None
        if value_address is not None:
            return_value = self.memory.get_relative(value_address)
        self.log(f"Return with value: {return_value or 'void'}")

        # Pop current activation record
        activation_record = self.memory.pop()

        # Check: not all arguments were loaded
        if activation_record.arguments_to_load:
            self.log("Arguments still to load on return:", activation_record.arguments_to_load)
            raise self.get_error(Errors.UNLOADED_ARGUMENTS)

        # Return value if needed
        if activation_record.return_value_address is not None:
            if return_value is not None:
                # Allocate value to where it was supposed to be returned
                self.memory.allocate_relative(activation_record.return_value_address, return_value)
            else:
                # Function needs value to return, but return statement doesn't have one
                raise self.get_error(Errors.RETURN_VALUE_NOT_FOUND)
        else:
            if return_value is not None:
                # Value was given in a function that returns void
                raise self.get_error(Errors.RETURN_VALUE_IN_VOID)

        # Deallocate temp variables used in arguments
        while activation_record.arguments:
            addr = activation_record.arguments.pop()
            if self.memory.is_temp_global_address(addr):
                self.memory.deallocate_global(addr)

        # Move i back to where program was left off
        self.log(f"Retuned function {activation_record.identifier} to address {self.i}")
        self.i = activation_record.return_address

        return True

    def GOTO_all(self, cond: Optional[bool], address: Optional[int], jump_line: Optional[int]):
        # Get where to jump
        jump_line = self.validate_int(jump_line, Errors.GOTO_JUMP_MISSING)
        
        if cond is None:
            self.log(f"GOTO line {jump_line}")
            self.i = jump_line
            return True

        # Jump to other instruction if condition is met
        address = self.validate_int(address, Errors.MEMORY_ADDRESS_MISSING)

        if self.memory.get_relative(address) == cond:
            self.log(f"GOTO{'T' if cond else 'F'} line {jump_line} with cond {address}")
            self.i = jump_line
        else:
            self.log(f"GOTO{'T' if cond else 'F'} will not jump with cond {address}")
            self.i += 1

        # Deallocate value if value is temp
        if self.memory.is_temp_relative_address(address):
            self.memory.deallocate_relative(address)

        return True

    def ASSIGN(self, temp_address: Optional[int], result_address: Optional[int]):
        self.log(f"Will attempt to assign from {temp_address} to {result_address}")

        temp_address = self.validate_int(temp_address, Errors.MEMORY_ADDRESS_MISSING)
        result_address = self.validate_int(result_address, Errors.MEMORY_ADDRESS_MISSING)
        
        # Copies value from temp variable to variable
        value = self.memory.get_relative(temp_address)
        self.log(f"Got value from address {temp_address}:", value)
        self.memory.allocate_relative(result_address, value)
        
        # Deallocate temp variable
        if self.memory.is_temp_relative_address(temp_address):
            self.memory.deallocate_relative(temp_address)

        self.log(f"Completed assign from {temp_address} to {result_address}")

    def PRINT(self):
        # Get parameters from memory in current activation record
        addresses = self.memory.top().parameter_pop()
        self.log(f"Will print items with addresses {addresses}")

        # Print to console
        print(*(self.memory.get_global(addr) for addr in addresses))

        # Deallocate temp variables used
        while addresses:
            addr = addresses.pop()
            if self.memory.is_temp_global_address(addr):
                self.memory.deallocate_global(addr)
    
    def OP(self, operation: Callable[[Any, Any], Any], id: int, left_address: Optional[int], right_address: Optional[int], result_address: Optional[int]):
        left_address = self.validate_int(left_address, Errors.MEMORY_ADDRESS_MISSING)
        right_address = self.validate_int(right_address, Errors.MEMORY_ADDRESS_MISSING)
        result_address = self.validate_int(result_address, Errors.MEMORY_ADDRESS_MISSING)
        self.log(f"Operation {id} between {left_address}, {right_address} saved in {result_address}")

        # Get operands from memory
        left_value = self.memory.get_relative(left_address)
        right_value = self.memory.get_relative(right_address)

        # Save result
        result_value = operation(left_value, right_value)
        self.memory.allocate_relative(result_address, result_value)

        # Deallocate operands only if temp
        if self.memory.is_temp_relative_address(left_address):
            self.memory.deallocate_relative(left_address)
        if self.memory.is_temp_relative_address(right_address):
            self.memory.deallocate_relative(right_address)

        self.log(f"Preview of operation: {left_value} {Instruction(id).name} {right_value} = {result_value}")
        
    def OP_BOOL(self, operation: Callable[[Any, Any], Any], id: int, left_address: Optional[int], right_address: Optional[int], result_address: Optional[int]):
        left_address = self.validate_int(left_address, Errors.MEMORY_ADDRESS_MISSING)
        right_address = self.validate_int(right_address, Errors.MEMORY_ADDRESS_MISSING)
        result_address = self.validate_int(result_address, Errors.MEMORY_ADDRESS_MISSING)
        self.log(f"Operation {id} between {left_address}, {right_address} saved in {result_address}")
        
        # Get operands from memory
        left_value = self.memory.get_relative(left_address)
        right_value = self.memory.get_relative(right_address)

        # Save result
        result_value = True if operation(left_value, right_value) else False
        self.memory.allocate_relative(result_address, result_value)

        # Deallocate operands only if temp
        if self.memory.is_temp_relative_address(left_address):
            self.memory.deallocate_relative(left_address)
        if self.memory.is_temp_relative_address(right_address):
            self.memory.deallocate_relative(right_address)

        self.log(f"Preview of operation: {left_value} {Instruction(id).name} {right_value} = {result_value}")

    #
    # Helpers
    #
    def validate_int(self, value: Optional[int], error_if_none: Errors) -> int:
        if value is None:
            raise self.get_error(error_if_none)
        return value

    def not_found(self, q: Quadruple):
        raise VirtualMachineRuntimeError(error=Errors.INSTRUCTION_DOESNT_EXIST,
                                         index=self.i,
                                         quadruple=q)
    
    def get_error(self, error: Errors):
        return VirtualMachineRuntimeError(error=error,
                                          index=self.i,
                                          quadruple=self.instructions[self.i])
    
    #
    # Debug
    #
    def log(self, *args):
        if self.debug:
            print(f"{self.i}:", *args)
