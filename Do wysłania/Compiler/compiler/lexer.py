from sly import Lexer

class lex(Lexer):
    tokens = {
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO',
    'EQ', 'NEQ', 'LT', 'GT', 'LEQ', 'GEQ',
    'DECLARE', 'IN', 'END', 'COLON',
    'IF', 'THEN', 'ELSE', 'ENDIF',
    'WHILE', 'DO', 'ENDWHILE', 'ENDDO',
    'FOR', 'FROM', 'DOWNTO', 'TO', 'ENDFOR',
    'READ', 'WRITE',
    'LPAREN', 'RPAREN',
    'ASSIGN',
    'SEMICOLON',
    'PIDENTIFIER',
    'NUMBER'}

    ignore = ' \t\r'
    ignore_newline = r'\n'
    ignore_comment = r'\[[^\]]*\]'

    # Needed!
    DOWNTO = r'DOWNTO'
    #Mathematical statements
    PLUS = r'\+'
    MINUS = r'-'
    TIMES = r'\*'
    DIVIDE = r'/'
    MODULO = r'%'
    #Assign
    ASSIGN = r':='
    #Comparing statements
    LEQ = r'<='
    GEQ = r'>='
    NEQ = r'!='
    EQ = r'='
    LT = r'<'
    GT = r'>'
    #If statements
    ENDIF = r'ENDIF'
    IF = r'IF'
    THEN = r'THEN'
    ELSE = r'ELSE'
    #While statements
    ENDWHILE = r'ENDWHILE'
    ENDDO = r'ENDDO'
    WHILE = r'WHILE'
    DO = r'DO'
    #For statements
    ENDFOR = r'ENDFOR'
    FOR = r'FOR'
    FROM = r'FROM'
    TO = r'TO'
    #IO statements
    READ = r'READ'
    WRITE = r'WRITE'
    #Parenthesis
    LPAREN = r'\('
    RPAREN = r'\)'
    #Endl
    SEMICOLON = r';'
    #Identifiers
    PIDENTIFIER = r'[_a-z]+'
    #Numbers
    NUMBER = r'[0-9]+'
    #Program
    DECLARE = r'DECLARE'
    IN = r'IN'
    END = r'END'
    COLON = r':'

    def ignore_comment(self, t):
        pass
    
    def ignore_newline(self, t):
        self.lineno += len(t.value)
        pass

    def error(self, t):
        print("Syntax error on line", self.lineno)
        print("Invalid token: ", t.value[0])
        self.index += 1
        exit(1)