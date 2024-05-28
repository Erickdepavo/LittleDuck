from dataclasses import dataclass
from typing import Any, List, Optional

from .errors import VirtualMachineMemoryError as MemoryError
from .errors import VirtualMachineMemoryErrors as Errors
from .extras import reversed_enumerated
from .vm_memory_scope import MemoryScope, MemoryScopeTemplate


@dataclass
class ActivationRecordTemplate:
    identifier: int # Function ID
    activation_address: int # Intruction where func starts
    return_address: int # Instruction to go back after returning
    arguments: List[int] # Global addresses for arguments
    return_value_address: Optional[int] # Global address to return

class ActivationRecord:
    def __init__(self, template: ActivationRecordTemplate) -> None:
        self.identifier = template.identifier
        self.activation_address = template.activation_address
        self.return_address = template.return_address
        self.arguments = template.arguments
        self.return_value_address = template.return_value_address

        self.arguments_to_load = template.arguments
        self.memory_scopes: List[MemoryScope] = []
        self.scope_offsets: List[int] = []
        self.total_size = 0

    # Push new scopes
    def push(self, template: MemoryScopeTemplate):
        memory_scope = MemoryScope(template)
        self.memory_scopes.append(memory_scope)
        self.scope_offsets.append(self.total_size)
        self.total_size += memory_scope.size
    
    def pop(self) -> MemoryScope:
        memory_scope = self.memory_scopes.pop()
        self.scope_offsets.pop()
        self.total_size -= memory_scope.size
        return memory_scope

    # Read from memory
    def get(self, local_address: int) -> Any:
        i = self.get_stack_frame_index(local_address)
        try:
            return self.memory_scopes[i].get_local(local_address - self.scope_offsets[i])
        except MemoryError as error:
            error.address += self.scope_offsets[i]
            raise error
    
    def allocate(self, local_address: int, value: Any):
        i = self.get_stack_frame_index(local_address)
        try:
            return self.memory_scopes[i].set_local(local_address - self.scope_offsets[i], value)
        except MemoryError as error:
            error.address += self.scope_offsets[i]
            raise error
    
    def deallocate(self, local_address: int):
        return self.allocate(local_address, None)

    def get_type(self, local_address: int):
        i = self.get_stack_frame_index(local_address)
        return self.memory_scopes[i].get_type(local_address - self.scope_offsets[i])

    # Parameter stack
    def parameter_push(self, global_address: int):
        i = self.get_stack_frame_index(global_address)
        self.memory_scopes[i].parameter_store.append(global_address)
    
    def parameter_pop(self) -> List[int]:
        value = self.memory_scopes[-1].parameter_store
        self.memory_scopes[-1].parameter_store = []
        return value
    
    # Checks
    def validate_address_range(self, local_address: int):
        if local_address >= self.total_size or local_address < 0:
            raise MemoryError(Errors.ADDRESS_OUTSIDE_RANGE, local_address)
        
    def is_temp_address(self, local_address: int) -> bool:
        self.validate_address_range(local_address)
        return self.get_type(local_address) is None
    
    def get_stack_frame_index(self, local_address: int) -> int:
        self.validate_address_range(local_address)

        for i, offset in reversed_enumerated(self.scope_offsets):
            if local_address > offset:
                return i

        # NOTE: This should never happen, it would be a VM bug
        raise ValueError("Real address could not be found")
