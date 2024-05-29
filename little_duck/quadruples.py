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
    # FUNCTION_DECLARATION = 'FUNCTION'
    FUNCTION_PARAMETER = 'PARAM'
    FUNCTION_CALL = 'CALL'
    FUNCTION_ARGUMENT = 'ARG'
    # Acciones de la consola
    PRINT = 'PRINT'
    # Variables
    # DECLARE = 'DECLARE'
    ASSIGN = 'ASSIGN'
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


Operand = QuadrupleConstVariable | QuadrupleTempVariable | QuadrupleIdentifier
Result =  QuadrupleTempVariable | QuadrupleIdentifier | QuadrupleLineNumber

Quadruple = Tuple[QuadrupleOperation, Optional[Operand], Optional[Operand], Optional[Result]]

PolishValue = QuadrupleOperation | Operand
PolishExpression = Deque[PolishValue]
