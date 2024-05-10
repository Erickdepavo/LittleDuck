import pytest
from little_duck import LittleDuckLexer, LittleDuckParser

class TestLexer:
    def test_lexer1(self):
        lexer = LittleDuckLexer()
        code = \
        """
        program ValidTest;
        main {
            x = 10;
            function1(x);
            print(x, y);
            if (x != y) {
                print(x);
            }
        }
        end;
        """
        expected = [
            'PROGRAM', 'ID', 'SEMICOLON',
            'MAIN', 'LBRACE', 
            'ID', 'ASSIGN', 'CTE_INT', 'SEMICOLON',
            'ID', 'LPAREN', 'ID', 'RPAREN', 'SEMICOLON',
            'PRINT', 'LPAREN', 'ID', 'COMMA', 'ID', 'RPAREN', 'SEMICOLON',
            'IF', 'LPAREN', 'ID', 'NOTEQUALS', 'ID', 'RPAREN', 'LBRACE',
            'PRINT', 'LPAREN', 'ID', 'RPAREN', 'SEMICOLON', 'RBRACE',
            'RBRACE',
            'END', 'SEMICOLON'
        ]
        tokens = lexer.input(code)
        tokens = list(map(lambda x: x.type, tokens))
        assert tokens == expected

    def test_lexer2(self):
        lexer = LittleDuckLexer()
        code = \
        """
        program ValidTest;
        main {
            x, y = 10;
            function1(x);
            print(x, y);
            while (x != y) {
                print(x);
            }
        }
        end;
        """
        expected = [
            'PROGRAM', 'ID', 'SEMICOLON',
            'MAIN', 'LBRACE', 
            'ID', 'COMMA', 'ID', 'ASSIGN', 'CTE_INT', 'SEMICOLON',
            'ID', 'LPAREN', 'ID', 'RPAREN', 'SEMICOLON',
            'PRINT', 'LPAREN', 'ID', 'COMMA', 'ID', 'RPAREN', 'SEMICOLON',
            'WHILE', 'LPAREN', 'ID', 'NOTEQUALS', 'ID', 'RPAREN', 'LBRACE',
            'PRINT', 'LPAREN', 'ID', 'RPAREN', 'SEMICOLON', 'RBRACE',
            'RBRACE',
            'END', 'SEMICOLON'
        ]
        tokens = lexer.input(code)
        tokens = list(map(lambda x: x.type, tokens))
        assert tokens == expected

class TestParser:
    def test_parser1(self):
        lexer = LittleDuckLexer()
        parser = LittleDuckParser()
        code = \
        """
        program ValidTest;
        main {
            x = 10;
            function1(x);
            print(x, y);
            if (x != y) {
                print(x);
            }
        }
        end;
        """
        parser.parse(code, lexer)
            

    def test_parser2(self):
        lexer = LittleDuckLexer()
        parser = LittleDuckParser()
        code = \
        """
        program ValidTest;
        main {
            x, y = 10;
            function1(x);
            print(x, y);
            while (x != y) {
                print(x);
            }
        }
        end;
        """
        try:
            parser.parse(code, lexer)
            assert False
        except:
            assert True

    def test_parser3(self):
        lexer = LittleDuckLexer()
        parser = LittleDuckParser()
        file_contents = ""
        with open('code.ld', 'r') as file:
            file_contents = file.read()
        parser.parse(file_contents, lexer)
        
