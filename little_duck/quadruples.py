from dataclasses import dataclass
from enum import Enum


@dataclass
class PolishVariable:
    identifier: str

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
    # Funciones
    FUNCTION_DECLARATION = 'FUNCTION'
    FUNCTION_LOAD_ARGUMENT = 'ARG'
    FUNCTION_CALL = 'CALL'
    FUNCTION_PARAMETER = 'PARAM'
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
