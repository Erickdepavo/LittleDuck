from uuid import uuid4

from ply import yacc

from .lexer import LittleDuckLexer, reserved, tokens
from .nodes import (
    AssignmentNode,
    BinaryOperationNode,
    DeclareVariableNode,
    FloatPrimitiveValueNode,
    FunctionDeclarationNode,
    IfConditionNode,
    IntegerPrimitiveValueNode,
    PrintNode,
    ProgramNode,
    ReadVariableNode,
    ScopeNode,
    StringPrimitiveValueNode,
    TypeNode,
    UnaryOperationNode,
    ValueNode,
    VoidFunctionCallNode,
    WhileCycleNode,
)


###
### Parser
###
class LittleDuckParser():
    def __init__(self, **kwargs):
        self.reserved = reserved
        self.tokens = tokens
        self.parser = yacc.yacc(module=self, **kwargs)

    def parse(self, text: str, lexer: LittleDuckLexer) -> ProgramNode:
        return self.parser.parse(text, lexer=lexer.lexer)

    #
    # Parsing rules
    #
    def p_programa(self, p: yacc.YaccProduction):
        'Programa : PROGRAM ID SEMICOLON VARS FUNCS MAIN Body END SEMICOLON'
        p[0] = ProgramNode(p[2], p[4], p[5], p[7])
        pass

    def p_vars(self, p: yacc.YaccProduction):
        'VARS : VARS VarDeclaration'
        p[0] = p[1] + p[2]
        pass

    def p_vars_empty(self, p: yacc.YaccProduction):
        'VARS : epsilon'
        p[0] = [] # Empty list for combining
        pass

    def p_vars_declaration(self, p: yacc.YaccProduction):
        'VarDeclaration : VAR ListaVars COLON TYPE SEMICOLON'
        p[0] = list(map(lambda id: DeclareVariableNode(id, p[4]), p[2]))
        pass

    def p_lista_vars_multiple(self, p: yacc.YaccProduction):
        'ListaVars : ListaVars COMMA ID'
        p[0] = p[1] + [p[3]]
        pass

    def p_lista_vars_one(self, p: yacc.YaccProduction):
        'ListaVars : ID '
        p[0] = [p[1]]
        pass

    def p_type(self, p: yacc.YaccProduction):
        '''TYPE : INT
                | FLOAT
                | STRING'''
        p[0] = TypeNode(p[1])
        pass

    def p_funcs(self, p: yacc.YaccProduction):
        'FUNCS : Funcion FUNCS'
        p[0] = [p[1]] + p[2] # Combine lists
        pass

    def p_funcs_empty(self, p: yacc.YaccProduction):
        '''FUNCS : epsilon'''
        p[0] = [] # Empty list for combining
        pass

    def p_funcion(self, p: yacc.YaccProduction):
        'Funcion : TipoFunc ID LPAREN Parametros RPAREN COLON Body'
        p[0] = FunctionDeclarationNode(p[2], p[1], p[4], p[7])
        pass

    def p_parametros_multiple(self, p: yacc.YaccProduction):
        'Parametros : Parametro COMMA Parametros'
        p[0] = [p[1]] + p[3] # Combine lists
        pass

    def p_parametros_one(self, p: yacc.YaccProduction):
        'Parametros : Parametro'
        p[0] = [p[1]] # List of one for combining
        pass

    def p_parametros_empty(self, p: yacc.YaccProduction):
        'Parametros : epsilon'
        p[0] = [] # Empty list for combining
        pass

    def p_parametro(self, p: yacc.YaccProduction):
        'Parametro : ID COLON TYPE'
        p[0] = DeclareVariableNode(p[1], p[3])
        pass

    def p_tipofunc_void(self, p: yacc.YaccProduction):
        'TipoFunc : VOID'
        p[0] = None # Void functions return no type
        pass

    def p_tipofunc_type(self, p: yacc.YaccProduction):
        'TipoFunc : TYPE'
        p[0] = p[1] # Passthrough
        pass

    def p_body(self, p: yacc.YaccProduction):
        'Body : LBRACE Statements RBRACE'
        p[0] = ScopeNode(uuid4().hex, p[2])
        pass

    def p_statements(self, p: yacc.YaccProduction):
        'Statements : Statement Statements'
        p[0] = [p[1]] + p[2] # Combine lists
        pass

    def p_statements_vars(self, p: yacc.YaccProduction):
        'Statements : VarDeclaration Statements'
        p[0] = p[1] + p[2] # Combine lists
        pass

    def p_statements_empty(self, p: yacc.YaccProduction):
        'Statements : epsilon'
        p[0] = [] # Empty list for combining
        pass

    def p_statement(self, p: yacc.YaccProduction):
        '''Statement : ASSIGNMENT
                    | CONDITION
                    | CYCLE
                    | F_Call
                    | Print'''
        p[0] = p[1] # Passthrough
        pass

    def p_assignment(self, p: yacc.YaccProduction):
        'ASSIGNMENT : ID ASSIGN Expresion SEMICOLON'
        p[0] = AssignmentNode(p[1], p[3])
        pass

    def p_condition(self, p: yacc.YaccProduction):
        'CONDITION : IF LPAREN Expresion RPAREN Body'
        p[0] = IfConditionNode(p[3], p[5], None)
        pass

    def p_condition_else(self, p: yacc.YaccProduction):
        'CONDITION : IF LPAREN Expresion RPAREN Body ELSE Body'
        p[0] = IfConditionNode(p[3], p[5], p[7])
        pass

    def p_cycle(self, p: yacc.YaccProduction):
        'CYCLE : DO Body WHILE LPAREN Expresion RPAREN SEMICOLON'
        p[0] = WhileCycleNode(condition=p[5], body=p[2])
        pass

    def p_f_call(self, p: yacc.YaccProduction):
        'F_Call : ID LPAREN Expresiones RPAREN SEMICOLON'
        p[0] = VoidFunctionCallNode(p[1], p[3])
        pass

    def p_print(self, p: yacc.YaccProduction):
        'Print : PRINT LPAREN Expresiones RPAREN SEMICOLON'
        p[0] = PrintNode(p[3])
        pass

    def p_expresiones_multiple(self, p: yacc.YaccProduction):
        'Expresiones : Expresion COMMA Expresiones'
        p[0] = [p[1]] + p[3] # Combine lists
        pass

    def p_expresiones_one(self, p: yacc.YaccProduction):
        'Expresiones : Expresion'
        p[0] = [p[1]] # List of one for combining
        pass

    def p_expresiones_empty(self, p: yacc.YaccProduction):
        'Expresiones : epsilon'
        p[0] = [] # Empty list for combining
        pass

    def p_expresion(self, p: yacc.YaccProduction):
        '''Expresion : Expresion NOTEQUALS Exp
                    | Expresion LESS Exp
                    | Expresion GREATER Exp'''
        p[0] = BinaryOperationNode(None, p[2], p[1], p[3])
        pass

    def p_expresion_passthrough(self, p: yacc.YaccProduction):
        '''Expresion : Exp'''
        p[0] = p[1] # Passthrough
        pass

    def p_exp(self, p: yacc.YaccProduction):
        '''Exp : Exp PLUS Term
               | Exp MINUS Term'''
        p[0] = BinaryOperationNode(None, p[2], p[1], p[3])
        pass

    def p_exp_passthrough(self, p: yacc.YaccProduction):
        '''Exp : Term'''
        p[0] = p[1] # Passthrough
        pass

    def p_term(self, p: yacc.YaccProduction):
        '''Term : Term TIMES Factor
                | Term DIVIDE Factor'''
        p[0] = BinaryOperationNode(None, p[2], p[1], p[3])
        pass

    def p_term_passthrough(self, p: yacc.YaccProduction):
        '''Term : Factor'''
        p[0] = p[1] # Passthrough
        pass

    def p_factor_parenthesis(self, p: yacc.YaccProduction):
        'Factor : LPAREN Expresion RPAREN'
        p[0] = p[2] # Passthrough
        pass

    def p_factor_op(self, p: yacc.YaccProduction):
        'Factor : MINUS Subfactor'
        # '''Factor : PLUS Subfactor
        #           | MINUS Subfactor'''
        p[0] = UnaryOperationNode(None, p[1], p[2])
        pass

    def p_factor_subfactor(self, p: yacc.YaccProduction):
        'Factor : Subfactor'
        p[0] = p[1] # Passthrough
        pass
    
    def p_subfactor_cte(self, p: yacc.YaccProduction):
        'Subfactor : CTE'
        p[0] = p[1] # Passthrough
        pass

    def p_subfactor_id(self, p: yacc.YaccProduction):
        'Subfactor : ID'
        p[0] = ReadVariableNode(None, p[1])
        pass

    def p_cte_float(self, p: yacc.YaccProduction):
        'CTE : CTE_FLOAT'
        p[0] = ValueNode(None, FloatPrimitiveValueNode(value=p[1]))
        pass

    def p_cte_int(self, p: yacc.YaccProduction):
        'CTE : CTE_INT'
        p[0] = ValueNode(None, IntegerPrimitiveValueNode(value=p[1]))
        pass

    def p_cte_string(self, p: yacc.YaccProduction):
        'CTE : CTE_STRING'
        p[0] = ValueNode(None, StringPrimitiveValueNode(value=p[1]))
        pass

    def p_epsilon(self, p: yacc.YaccProduction):
        'epsilon :'
        pass

    def p_error(self, p):
        print('Token in error:', p)
        if p:
            print(f"Syntax error '{p.value}' on line {p.lineno} {p}")
            raise SyntaxError(f"Syntax error '{p.value}' on line {p.lineno} {p}")
        else:
            print("Syntax error at EOF")
            raise SyntaxError("Syntax error at EOF")
