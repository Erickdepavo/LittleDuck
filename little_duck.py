from ply import lex, yacc

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
}

tokens = [
    'ID', # Identificadores
    'CTE_INT', 'CTE_FLOAT', 'CTE_STRING', # Literales de tipos
    'COLON', 'SEMICOLON', 'COMMA', # Separadores
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', # Aritméticos +, -, *, /
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', # Paréntesis y Llaves () {}
    'ASSIGN', 'NOTEQUALS', 'LESS', 'GREATER', # Símbolos =, <, >, !=
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
    t_ASSIGN = r'='
    t_NOTEQUALS = r'!='
    t_LESS = r'<'
    t_GREATER = r'>'

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

    # A string containing ignored characters (spaces and tabs)
    t_ignore  = ' \t'

    # Error handling rule
    def t_error(self, t):
        raise SyntaxError(f"Illegal character {t.value[0]} on line {t.lineno}")
        t.lexer.skip(1)

###
### Parser
###
class LittleDuckParser():
    def __init__(self, **kwargs):
        self.reserved = reserved
        self.tokens = tokens
        self.parser = yacc.yacc(module=self, **kwargs)

    def parse(self, text: str, lexer: LittleDuckLexer):
        return self.parser.parse(text, lexer=lexer.lexer)

    # dictionary of names (for storing variables)
    names = {}

    def p_programa(self, p):
        'Programa : PROGRAM ID SEMICOLON VARS FUNCS MAIN Body END SEMICOLON'
        # p[0] = ('Programa', p[2], p[4], p[5], p[7])
        print(list(p))
        pass

    def p_vars(self, p):
        '''VARS : VARS VAR ListaVars COLON TYPE SEMICOLON
                | epsilon'''
        pass

    def p_lista_vars(self, p):
        '''ListaVars : ListaVars COMMA ID
                    | ID '''
        pass

    def p_type(self, p):
        '''TYPE : INT
                | FLOAT
                | STRING'''
        pass

    def p_funcs(self, p):
        '''FUNCS : Funcion FUNCS
                | epsilon'''
        pass

    def p_funcion(self, p):
        'Funcion : TipoFunc ID LPAREN Parametros RPAREN COLON Body'
        pass

    def p_tipofunc(self, p):
        '''TipoFunc : VOID
                    | TYPE'''
        pass

    def p_parametros(self, p):
        '''Parametros : ID COLON TYPE COMMA Parametros
                    | ID COLON TYPE
                    | epsilon'''
        pass

    def p_body(self, p):
        'Body : LBRACE Statements RBRACE'
        pass

    def p_statements(self, p):
        '''Statements : Statement Statements
                    | epsilon'''
        pass

    def p_statement(self, p):
        '''Statement : ASSIGNMENT
                    | CONDITION
                    | CYCLE
                    | F_Call
                    | Print'''
        pass

    def p_assignment(self, p):
        'ASSIGNMENT : ID ASSIGN Expresion SEMICOLON'
        pass

    def p_condition(self, p):
        'CONDITION : IF LPAREN Expresion RPAREN Body'
        pass

    def p_condition_else(self, p):
        'CONDITION : IF LPAREN Expresion RPAREN Body ELSE Body'
        pass

    def p_cycle(self, p):
        'CYCLE : DO Body WHILE LPAREN Expresion RPAREN SEMICOLON'
        pass

    def p_f_call(self, p):
        'F_Call : ID LPAREN Expresiones RPAREN SEMICOLON'
        pass

    def p_expresiones(self, p):
        '''Expresiones : Expresion COMMA Expresiones
                    | Expresion
                    | epsilon'''
        pass

    def p_print(self, p):
        'Print : PRINT LPAREN Expresiones RPAREN SEMICOLON'
        pass

    def p_expresion(self, p):
        '''Expresion : Expresion NOTEQUALS Exp
                    | Expresion LESS Exp
                    | Expresion GREATER Exp
                    | Exp'''
        pass

    def p_exp(self, p):
        '''Exp : Exp PLUS Term
            | Exp MINUS Term
            | Term'''
        pass

    def p_term(self, p):
        '''Term : Term TIMES Factor
                | Term DIVIDE Factor
                | Factor'''
        pass

    def p_factor(self, p):
        '''Factor : LPAREN Expresion RPAREN
                | PLUS Subfactor
                | MINUS Subfactor
                | Subfactor'''
        pass

    def p_subfactor(self, p):
        '''Subfactor : CTE
                    | ID'''
        pass

    def p_cte(self, p):
        '''CTE : CTE_FLOAT
            | CTE_INT
            | CTE_STRING'''
        pass

    def p_epsilon(self, p):
        'epsilon :'
        pass

    def p_error(self, p):
        if p:
            print(f"Syntax error '{p.value}' on line {p.lineno} {p}")
            raise SyntaxError(f"Syntax error '{p.value}' on line {p.lineno} {p}")
        else:
            print("Syntax error at EOF")
            raise SyntaxError("Syntax error at EOF")

#
# Execution
#
if __name__ == "__main__":
    # Build the lexer
    lexer = LittleDuckLexer()
    file_contents = ""

    with open('code.ld', 'r') as file:
        file_contents = file.read()

    result = lexer.input(file_contents)
    result = list(map(lambda x: x.type, result))
    # print(result)
    print("File tokenized successfully")

    # Build the parser
    parser = LittleDuckParser()

    # Test it
    parser.parse(file_contents, lexer=lexer)
    print("File parsed successfully")