from typing import Any, List

from .errors import VirtualMachineMemoryError as MemoryError
from .errors import VirtualMachineMemoryErrors as Errors
from .extras import reversed_enumerated
from .vm_memory_scope import MemoryScope, MemoryScopeTemplate
from .vm_stack_frame import ActivationRecord, ActivationRecordTemplate


class VirtualMachineMemory:
    def __init__(self) -> None:
        self.constants: List[Any] = []

        self.global_scope = MemoryScope(MemoryScopeTemplate(0,0,0,0,0,0))
        self.global_scope_offset = 0

        self.local_scope_offset = 0
        self.stack_frames: List[ActivationRecord] = []
        self.stack_offsets: List[int] = []

        self.total_size = 0

    def initialize_global_scope(self,
                                constants: List[Any],
                                global_scope_template: MemoryScopeTemplate):
        self.constants = constants
        self.global_scope = MemoryScope(global_scope_template)
        self.global_scope_offset = len(constants)
        self.local_scope_offset = len(constants) + self.global_scope.size
        self.total_size = self.local_scope_offset

    #
    # Activation Records handling
    #
    def push(self, template: ActivationRecordTemplate):
        stack_frame = ActivationRecord(template)
        self.stack_frames.append(stack_frame)
        self.stack_offsets.append(self.total_size)
        self.total_size += stack_frame.total_size
    
    def pop(self) -> ActivationRecord:
        stack_frame = self.stack_frames.pop()
        self.stack_offsets.pop()
        self.total_size -= stack_frame.total_size
        return stack_frame

    def top(self) -> ActivationRecord:
        return self.stack_frames[-1]
    
    #
    # Global read (takes into account all activation records)
    #
    def get_global(self, global_address: int) -> Any:
        self.validate_global_address_range(global_address)

        if global_address < self.global_scope_offset:
            # Address belongs to constant
            return self.constants[global_address]
        elif global_address < self.local_scope_offset:
            # Address belongs to global scope
            return self.global_scope.get_local(global_address - self.global_scope_offset)

        # Address belongs to activation record
        i = self.get_stack_frame_index(global_address)
        try:
            return self.stack_frames[i].get(global_address - self.stack_offsets[i])
        except MemoryError as error:
            error.address += self.stack_offsets[i]
            raise error
    
    def allocate_global(self, global_address: int, value: Any):
        self.validate_global_address_range(global_address)

        if global_address < self.global_scope_offset:
            # Address belongs to constant
            raise MemoryError(Errors.ALLOCATED_CONSTANT, global_address)
        elif global_address < self.local_scope_offset:
            # Address belongs to global scope
            return self.global_scope.get_local(global_address - self.global_scope_offset)

        # Address belongs to activation record
        i = self.get_stack_frame_index(global_address)
        try:
            return self.stack_frames[i].allocate(global_address - self.stack_offsets[i], value)
        except MemoryError as error:
            error.address += self.stack_offsets[i]
            raise error
    
    def deallocate_global(self, global_address: int):
        self.validate_global_address_range(global_address)
        return self.allocate_global(global_address, None)

    def get_type_global(self, global_address: int):
        self.validate_global_address_range(global_address)

        if global_address < self.global_scope_offset:
            # Address belongs to constant
            return type(self.constants[global_address])
        elif global_address < self.local_scope_offset:
            # Address belongs to global scope
            return self.global_scope.get_type(global_address - self.global_scope_offset)

        # Address belongs to activation record
        i = self.get_stack_frame_index(global_address)
        return self.stack_frames[i].get_type(global_address - self.stack_offsets[i])
    
    #
    # Relative to current context (most recent activation record)
    #
    def get_relative(self, relative_address: int) -> Any:
        if relative_address < self.local_scope_offset:
            # Address belongs to constant or global scope
            return self.get_global(relative_address)

        # Address belongs to activation record
        try:
            return self.top().get(relative_address - self.local_scope_offset)
        except MemoryError as error:
            error.address += self.stack_offsets[-1]
            raise error
    
    def allocate_relative(self, relative_address: int, value: Any):
        if relative_address < self.local_scope_offset:
            # Address belongs to constant or global scope
            return self.allocate_global(relative_address, value)

        # Address belongs to activation record
        try:
            return self.top().allocate(relative_address - self.local_scope_offset, value)
        except MemoryError as error:
            error.address += self.stack_offsets[-1]
            raise error
    
    def deallocate_relative(self, relative_address: int):
        return self.allocate_relative(relative_address, None)

    def get_type_relative(self, relative_address: int):
        if relative_address < self.local_scope_offset:
            # Address belongs to constant or global scope
            return self.get_type_global(relative_address)

        # Address belongs to activation record
        return self.top().get_type(relative_address - self.local_scope_offset)
    
    # Conversions
    def convert_relative_to_global(self, relative_address: int, stack_frame_index: int) -> int:
        if relative_address < self.local_scope_offset:
            # Address belongs to constant or global scope
            return relative_address
        
        # Address belongs to activation record
        local_address = relative_address - self.local_scope_offset
        return self.stack_offsets[stack_frame_index] + local_address

    # Checks
    def validate_global_address_range(self, global_address: int):
        if global_address >= self.total_size or global_address < 0:
            raise MemoryError(Errors.ADDRESS_OUTSIDE_RANGE, global_address)
        
    def is_temp_global_address(self, global_address: int) -> bool:
        self.validate_global_address_range(global_address)
        return self.get_type_global(global_address) is None
    
    def is_temp_relative_address(self, relative_address: int) -> bool:
        return self.get_type_relative(relative_address) is None
    
    def get_stack_frame_index(self, global_address: int) -> int:
        for i, offset in reversed_enumerated(self.stack_offsets):
            if global_address > offset:
                return i

        # NOTE: This should never happen, it would be a VM bug
        if global_address < self.global_scope_offset:
            raise ValueError(f"Real address could not be found: constant {global_address}")
        elif global_address < self.local_scope_offset:
            # Address belongs to global scope
            raise ValueError(f"Real address could not be found: global {global_address}")
        else:
            raise ValueError(f"Real address could not be found: other {global_address}")
        
