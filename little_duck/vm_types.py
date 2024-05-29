from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

from .vm_memory_scope import MemoryScopeTemplate

Quadruple = Tuple[int, Optional[int], Optional[int], Optional[int]]

@dataclass
class FunctionDirectoryEntry:
    identifier: int # Function ID
    address: int # Intruction where func starts

Constant = Tuple[int, Any]
GeneratedCode = Tuple[List[FunctionDirectoryEntry], List[MemoryScopeTemplate],
                      List[Constant], List[Quadruple]]
