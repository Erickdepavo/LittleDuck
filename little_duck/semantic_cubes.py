from typing import Dict, Optional

SemanticCube = Dict[str, Dict[str, Optional[str]]]

# Suma
# Int: int + int = int, el resto = float
# Float: Con int, float = float
# Strings: Sólo string + string = string
# Booleanos: No compatible (usar operación OR)
addition_matrix: SemanticCube = {
    'int': { 'int': 'int', 'float': 'float', 'string': None, 'bool': None },
    'float': { 'int': 'float', 'float': 'float', 'string': None, 'bool': None },
    'string': { 'int': None, 'float': None, 'string': 'string', 'bool': None },
    'bool': { 'int': None, 'float': None, 'string': None, 'bool': None },
}

# Multiplicación
# Int: int + int = int, el resto = float
# Float: Con float, int = float
# Strings: No compatible
# Booleanos: No compatible (usar operación AND)
multiplication_matrix: SemanticCube = {
    'int': { 'int': 'int', 'float': 'float', 'string': None, 'bool': None },
    'float': { 'int': 'float', 'float': 'float', 'string': None, 'bool': None },
    'string': { 'int': None, 'float': None, 'string': None, 'bool': None },
    'bool': { 'int': None, 'float': None, 'string': None, 'bool': None },
}

# Comparación
# Int: Con int, float, bool = bool
# Float: Con int, float, bool = bool
# Strings: Sólo string < string = bool
# Booleanos: Con int, float, bool = bool
comparison_matrix: SemanticCube = {
    'int': { 'int': 'bool', 'float': 'bool', 'string': None, 'bool': 'bool' },
    'float': { 'int': 'bool', 'float': 'bool', 'string': None, 'bool': 'bool' },
    'string': { 'int': None, 'float': None, 'string': 'bool', 'bool': None },
    'bool': { 'int': 'bool', 'float': 'bool', 'string': None, 'bool': 'bool' },
}

# Lógicos
# Int: Con int, bool = bool
# Float: No compatible
# Strings: No compatible
# Booleanos: Con int, bool = bool
boolean_matrix: SemanticCube = {
    'int': { 'int': 'bool', 'float': None, 'string': None, 'bool': 'bool' },
    'float': { 'int': None, 'float': None, 'string': None, 'bool': None },
    'string': { 'int': None, 'float': None, 'string': None, 'bool': None },
    'bool': { 'int': 'bool', 'float': None, 'string': None, 'bool': 'bool' },
}

binary_semantic_cubes = {
    # Aritmética
    '+': addition_matrix,
    '-': multiplication_matrix,
    '*': multiplication_matrix,
    '/': multiplication_matrix,
    # Comparación
    '==': comparison_matrix,
    '!=': comparison_matrix,
    '<': comparison_matrix,
    '>': comparison_matrix,
    # Booleanos
    '&&': boolean_matrix,
    '||': boolean_matrix,
}

unary_semantic_cubes = {
    # Aritmética
    '-': multiplication_matrix['int'],
    # Booleanos
    '!': boolean_matrix['bool'],
}
