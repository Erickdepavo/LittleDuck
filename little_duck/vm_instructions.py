from enum import Enum


class VirtualMachineInstruction(Enum):
    #
    # Instrucciones para máquina virtual
    #
    # Manejo de Stack Frames (Scope)
    OPEN_STACK_FRAME = 0
    CLOSE_STACK_FRAME = 1
    # Operaciones básicas (saltos)
    GOTO = 2
    GOTOT = 3
    GOTOF = 4
    # Variables
    # DECLARE = 9
    READ = 5
    ASSIGN = 6
    # Funciones
    # FUNCTION_DECLARATION = 6
    FUNCTION_PARAMETER = 7
    FUNCTION_CALL = 8
    FUNCTION_ARGUMENT = 9
    RETURN = 10
    # Acciones de la consola
    PRINT = 20

    #
    # Operaciones
    #
    # Lógicos
    AND = 11
    OR = 12
    # Comparación
    EQUALS = 13
    LESSTHAN = 14
    MORETHAN = 15
    # Aritmética
    ADDITION = 16
    SUBTRACTION = 17
    MULTIPLICATION = 18
    DIVISION = 19
