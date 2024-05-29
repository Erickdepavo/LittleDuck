from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from .quadruples import QuadrupleConstVariable


@dataclass
class VariableMetadata:
    identifier: str
    module: str
    type: str
    is_initialized: bool
    is_used: bool

    declare_index: int

@dataclass
class FunctionMetadata:
    identifier: str
    module: str
    type: Optional[str]
    parameters: List[Tuple[str, str]]
    returns: bool
    is_used: bool

    start_index: int

class Scope:
    def __init__(self, id: int = 0, function_name: Optional[str] = None) -> None:
        self.id = id
        self.function_name = function_name
        self.variables: Dict[str, VariableMetadata] = {}
        self.inner_scopes: List[Scope] = []

        self.current_temp: int = 0

    def has_variable(self, identifier: str) -> bool:
        return identifier in self.variables
    
    def get_variable(self, identifier: str) -> Optional[VariableMetadata]:
        if identifier in self.variables:
            return self.variables[identifier]
        return None

    def add_variable(self, metadata: VariableMetadata):
        if metadata.identifier == 'exit_code':
            metadata.declare_index = 0
        self.variables[metadata.identifier] = metadata

    def child(self, id: int):
        for scope in self.inner_scopes:
            if scope.id == id:
                return scope
        raise ValueError(f"Scope with id {id} not found")
    
    def temp_var_count(self) -> int:
        return self.current_temp

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
    
    def __print_functions(self) -> str:
        text = ""
        sorted_functions = sorted(self.functions.values(), key=lambda f: f.start_index)
        for i, function in enumerate(sorted_functions):
            text += "\n      - "
            text += str(function)
        return text

    def __repr__(self) -> str:
        return f"""
GlobalScope:
  - identifier: {self.id},
  - function_name: {self.function_name or 'None'},
  - functions:{self.__print_functions()},

  - constants={sorted(self.constants).__repr__()},
  - variables={self.variables.__repr__()},
  - inner_scopes={self.inner_scopes})
""".strip()


