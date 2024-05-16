from typing import Dict, Optional

SemanticCube = Dict[str, Dict[str, Optional[str]]]

# Suma: Numeros entre ellos, String solo entre sí
addition_matrix: SemanticCube = {
    'int': { 'int': 'int', 'float': 'float', 'string': None },
    'float': { 'int': 'float', 'float': 'float', 'string': None },
    'string': { 'int': None, 'float': None, 'string': 'string' },
}

# Multiplicación: Números entre ellos, String no compatible
multiplication_matrix: SemanticCube = {
    'int': { 'int': 'int', 'float': 'float', 'string': None },
    'float': { 'int': 'float', 'float': 'float', 'string': None },
    'string': { 'int': None, 'float': None, 'string': None },
}

# Comparación: Siempre devuelve int (booleano), Numeros entre ellos, String solo entre sí
comparison_matrix: SemanticCube = {
    'int': { 'int': 'int', 'float': 'int', 'string': None },
    'float': { 'int': 'int', 'float': 'int', 'string': None },
    'string': { 'int': None, 'float': None, 'string': 'int' },
}

# TODO: Booleano: Solo ints
# boolean_matrix: SemanticCube = {
#     'int': { 'int': 'int', 'float': None, 'string': None },
#     'float': { 'int': None, 'float': None, 'string': None },
#     'string': { 'int': None, 'float': None, 'string': None },
# }

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
    # TODO: Booleanos
    # '&&': boolean_matrix,
    # '||': boolean_matrix,
}

unary_semantic_cubes = {
    # Aritmética
    '-': multiplication_matrix['int'],
    # TODO: Booleanos
    # '!': boolean_matrix['bool'],
}
