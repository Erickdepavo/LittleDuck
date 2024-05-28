from dataclasses import dataclass
from typing import Any, List

from .errors import VirtualMachineMemoryError as MemoryError
from .errors import VirtualMachineMemoryErrors as Errors


@dataclass
class MemoryScopeTemplate:
    activation_address: int # Instruction where scope was opened

    int_count: int
    bool_count: int
    float_count: int
    str_count: int
    temp_count: int
    
    def size(self) -> int:
        return (1 + self.int_count + self.bool_count +
                self.float_count + self.str_count + self.temp_count)

class MemoryScope:
    def __init__(self, template: MemoryScopeTemplate) -> None:
        self.int_offset = 1
        self.bool_offset = self.int_offset + template.int_count
        self.float_offset = self.bool_offset + template.bool_count
        self.str_offset = self.float_offset + template.float_count
        self.temp_offset = self.str_offset + template.str_count
        self.size = template.size()

        self.registry: List = [None] * self.size
        self.parameter_store: List[int] = []

        # Save activation address in registry
        self.registry[0] = template.activation_address

    def get_local(self, address: int) -> Any:
        value = self.registry[address]
        if value is None:
            raise MemoryError(Errors.UNALLOCATED_ACCESS, address)
        return value
    
    def set_local(self, address: int, value: Any):
        self.registry[address] = value

    def get_type(self, address: int):
        if address < self.bool_offset:
            return int
        elif address < self.float_offset:
            return bool
        elif address < self.str_offset:
            return float
        elif address < self.temp_offset:
            return str
        else:
            return None
        
    def get_activation_address(self) -> int:
        return self.registry[0]
