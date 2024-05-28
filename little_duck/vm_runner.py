from dataclasses import dataclass
from typing import Optional, Tuple

Quadruple = Tuple[int, Optional[int], Optional[int], Optional[int]]

@dataclass
class FunctionDirectoryEntry:
    identifier: int # Function ID
    address: int # Intruction where func starts
