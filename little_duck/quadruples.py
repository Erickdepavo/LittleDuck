from dataclasses import dataclass
from enum import Enum
from typing import Any, Deque, Optional, Tuple


@dataclass
class QuadrupleIdentifier:
    identifier: str

    def __str__(self) -> str:
        return self.__repr__()
    
    def __repr__(self) -> str:
        return self.identifier

@dataclass
class QuadrupleLineNumber:
    number: int

    def __str__(self) -> str:
        return self.__repr__()
    
    def __repr__(self) -> str:
        return f"L_{self.number}"

@dataclass(frozen=True, order=True)
class QuadrupleConstVariable:
    type: str
    value: Any

    def __str__(self) -> str:
        return self.__repr__()
    
    def __repr__(self) -> str:
        if isinstance(self.value, str):
            return f'"{self.value}"'
        else:
            return str(self.value)

@dataclass
class QuadrupleTempVariable:
    number: int

    def __str__(self) -> str:
        return self.__repr__()
    
    def __repr__(self) -> str:
        return f"t_{self.number}"

class QuadrupleOperation(Enum):
    # Operaciones básicas (saltos)
    GOTO = "GOTO"
    GOTOT = "GOTOT"
    GOTOF = "GOTOF"
    # Manejo de Stack Frames (Scope)
    OPEN_STACK_FRAME = 'OPEN'
    CLOSE_STACK_FRAME = 'CLOSE'
    # Estatutos de control de flujo
    RETURN = 'RETURN'
    # Funciones
    FUNCTION_DECLARATION = 'FUNCTION'
    FUNCTION_ARGUMENT = 'ARG'
    FUNCTION_CALL = 'CALL'
    FUNCTION_PARAMETER = 'PARAM'
    # Acciones de la consola
    PRINT = 'PRINT'
    # Variables
    DECLARE = 'DECLARE'
    ASSIGN = 'ASSIGN'
    READ = 'READ'
    # Aritmética
    ADDITION = '+'
    SUBTRACTION = '-'
    MULTIPLICATION = '*'
    DIVISION = '/'
    # Comparación
    EQUALS = '=='
    NOTEQUALS = '!='
    LESSTHAN = '<'
    MORETHAN = '>'
    # Boolean
    AND = '&&'
    OR = '||'
    NOT = '!'


Identifier = QuadrupleIdentifier
Operand = QuadrupleConstVariable | QuadrupleTempVariable
Result =  QuadrupleTempVariable | QuadrupleLineNumber

Quadruple = Tuple[QuadrupleOperation, Optional[Operand | Identifier], Optional[Operand], Optional[Result | Identifier]]

PolishValue = QuadrupleOperation | Operand
PolishExpression = Deque[PolishValue]
