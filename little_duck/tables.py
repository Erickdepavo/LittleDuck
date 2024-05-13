from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class VariableMetadata():
    identifier: str
    type: str

@dataclass
class FunctionMetadata():
    identifier: str
    type: Optional[str]
    parameters: List[Tuple[str, str]]

class Scope():
    def __init__(self, id: int = 0) -> None:
        self.id = id
        self.variables: Dict[str, VariableMetadata] = {}
        self.functions: Dict[str, FunctionMetadata] = {}

    def has_variable(self, identifier: str) -> bool:
        return identifier in self.variables
    
    def has_function(self, identifier: str) -> bool:
        return identifier in self.functions
    
    def get_variable(self, identifier: str) -> Optional[VariableMetadata]:
        if identifier in self.variables:
            return self.variables[identifier]
        return None
    
    def get_function(self, identifier: str) -> Optional[FunctionMetadata]:
        if identifier in self.functions:
            return self.functions[identifier]
        return None

    def add_variable(self, metadata: VariableMetadata):
        self.variables[metadata.identifier] = metadata

    def add_function(self, metadata: FunctionMetadata):
        self.functions[metadata.identifier] = metadata

    def __str__(self) -> str:
        return self.__repr__()
    
    def __repr__(self) -> str:
        return f"Scope(id={self.id},variables={self.variables.__repr__()},functions={self.functions.__repr__()})"


