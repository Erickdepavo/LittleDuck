from ply import lex

# Tokens y palabras reservadas
reserved = {
    'program': 'PROGRAM',
    'main': 'MAIN',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'do': 'DO',
    'end': 'END',
    'print': 'PRINT',
    'var': "VAR",
    'void': 'VOID',
    'int': 'INT',
    'float': 'FLOAT',
    'string': 'STRING',
    'bool': 'BOOL',
}

tokens = [
    'ID', 'ASSIGN', # Identificadores, asignaciones
    'CTE_INT', 'CTE_FLOAT', 'CTE_STRING', 'CTE_BOOL', # Literales de tipos
    'COLON', 'SEMICOLON', 'COMMA', # Separadores
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', # Aritméticos +, -, *, /
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', # Paréntesis y Llaves () {}
    'EQUALS', 'NOTEQUALS', 'LESS', 'GREATER', # Comparadores ==, <, >, !=
    'AND', 'OR', 'NOT', # Lógicos &&, ||, !
] + list(reserved.values())

###
### Lexer
###
class LittleDuckLexer():
    def __init__(self, **kwargs):
        self.reserved = reserved
        self.tokens = tokens
        self.lexer = lex.lex(module=self, **kwargs)

    def input(self, text: str):
        self.lexer.input(text)
        return list(self.lexer)

    # literals = ['+', '-', '*', '/', '(', ')', ';', ',', '=', '!', '<', '>', '{', '}', ':']

    # Expresiones regulares para todos los tokens
    t_COLON = r':'
    t_SEMICOLON = r';'
    t_COMMA = r','
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_AND = r'&&'
    t_OR = r'\|\|'
    t_NOT = r'!'
    t_EQUALS = r'=='
    t_NOTEQUALS = r'!='
    t_LESS = r'<'
    t_GREATER = r'>'
    t_ASSIGN = r'='

    def t_CTE_BOOL(self, t):
        r'true|false'
        t.value = t.value == 'true'
        return t

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        t.type = self.reserved.get(t.value, 'ID') # Checar si es palabra reservada
        return t

    def t_CTE_FLOAT(self, t):
        r'[-]?\d+\.\d+'
        #r'[-]?\d+\.\d+([eE][+-]?\d+)?' FUTURO: Soportar notación científica
        t.value = float(t.value)
        return t

    def t_CTE_INT(self, t):
        r'[-]?\d+'
        t.value = int(t.value)
        return t

    def t_CTE_STRING(self, t):
        r'"(\\.|[^"\\])*"'
        t.value = t.value.strip('"')
        return t

    # Define a rule so we can track line numbers
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_COMMENT_BLOCK(self, t):
        r'\/\*(\*(?!\/)|[^*])*\*\/'
        t.lexer.lineno += len(t.value.split("\n")) - 1
        pass # No return value. Token discarded

    def t_COMMENT_INLINE(self, t):
        r'\/\/.*'
        pass # No return value. Token discarded

    # A string containing ignored characters (spaces and tabs)
    t_ignore  = ' \t'

    # Error handling rule
    def t_error(self, t):
        raise SyntaxError(f"Illegal character {t.value[0]} on line {t.lineno}")
        t.lexer.skip(1)
