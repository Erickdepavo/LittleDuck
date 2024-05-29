from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from .quadruples import QuadrupleConstVariable


@dataclass
class VariableMetadata:
    identifier: str
    type: str
    is_initialized: bool
    is_used: bool

@dataclass
class FunctionMetadata:
    identifier: str
    type: Optional[str]
    parameters: List[Tuple[str, str]]
    returns: bool
    is_used: bool

class Scope:
    def __init__(self, id: int = 0, function_name: Optional[str] = None) -> None:
        self.id = id
        self.function_name = function_name
        self.variables: Dict[str, VariableMetadata] = {}
        self.inner_scopes: List[Scope] = []

    def has_variable(self, identifier: str) -> bool:
        return identifier in self.variables
    
    def get_variable(self, identifier: str) -> Optional[VariableMetadata]:
        if identifier in self.variables:
            return self.variables[identifier]
        return None

    def add_variable(self, metadata: VariableMetadata):
        self.variables[metadata.identifier] = metadata

    def __str__(self) -> str:
        return self.__repr__()
    
    def __repr__(self) -> str:
        return f"Scope({self.id},{self.function_name},variables={self.variables.__repr__()},inner_scopes={self.inner_scopes})"
    
class GlobalScope(Scope):
    def __init__(self) -> None:
        super().__init__(0, None)
        self.functions: Dict[str, FunctionMetadata] = {}
        self.constants: Set[QuadrupleConstVariable] = set()
    
    def has_function(self, identifier: str) -> bool:
        return identifier in self.functions
    
    def get_function(self, identifier: str) -> Optional[FunctionMetadata]:
        if identifier in self.functions:
            return self.functions[identifier]
        return None

    def add_function(self, metadata: FunctionMetadata):
        self.functions[metadata.identifier] = metadata
    
    def __repr__(self) -> str:
        return f"GlobalScope({self.id},{self.function_name},functions={self.functions.__repr__()},variables={self.variables.__repr__()},inner_scopes={self.inner_scopes})"


