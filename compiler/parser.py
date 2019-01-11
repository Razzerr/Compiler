from sly import Parser
from .lexer import lex

class bison(Parser):
    tokens = lex.tokens

    @_('DECLARE declarations IN commands END')
    def program(self, p):
        return ('program', p.declarations, p.commands)
    
    @_('declarations PIDENTIFIER SEMICOLON')
    def declarations(self, p):
        tab = (p.declarations if p.declarations != None else [])
        tab.append(("int", p[1], p.lineno))
        return tab

    @_('declarations PIDENTIFIER LPAREN NUMBER COLON NUMBER RPAREN SEMICOLON')
    def declarations(self, p):
        tab = (p.declarations if p.declarations != None else [])
        tab.append(('int[]', p[1], (p[3], p[5]), p.lineno))
        return tab      

    @_('')
    def declarations(self, p):
        pass

    @_('commands command')
    def commands(self, p):
        tab = p.commands
        tab.append(p.command)
        return tab

    @_('command')
    def commands(self, p):
        return [p.command]

    @_('identifier ASSIGN expression SEMICOLON')
    def command(self, p):
        return ('assign', p.identifier, p.expression)
    
    @_('IF condition THEN commands ELSE commands ENDIF')
    def command(self, p):
        return ('if_then_else', p.condition, p.commands0, p.commands1)
    
    @_('IF condition THEN commands ENDIF')
    def command(self, p):
        return ('if_then', p.condition, p.commands)
    
    @_('WHILE condition DO commands ENDWHILE')
    def command(self, p):
        return ('while_do', p.condition, p.commands)
    
    @_('DO commands WHILE condition ENDDO')
    def command(self, p):
        return ('do_while', p.commands, p.condition)

    @_('FOR PIDENTIFIER FROM value TO value DO commands ENDFOR')
    def command(self, p):
        return ('for_to', ('int', p[2], p.lineno), p.value0, p.value1, p.commands)

    @_('FOR PIDENTIFIER FROM value DOWNTO value DO commands ENDFOR')
    def command(self, p):
        return ('for_downto', ('int', p[2], p.lineno), p.value0, p.value1, p.commands)

    @_('READ identifier SEMICOLON')
    def command(self, p):
        return ('read', p.identifier)

    @_('WRITE value SEMICOLON')
    def command(self, p):
        return ('write', p.value)

    @_('value')
    def expression(self, p):
        return p.value

    @_('value PLUS value'
        ,'value MINUS value'
        ,'value TIMES value'
        ,'value DIVIDE value'
        ,'value MODULO value')
    def expression(self, p):
        return (p[1], p.value0, p.value1)

    @_('value EQ value'
        ,'value NEQ value'
        ,'value LT value'
        ,'value GT value'
        ,'value LEQ value'
        ,'value GEQ value')
    def condition(self, p):
        return (p[1], p.value0, p.value1)

    @_('NUMBER')
    def value(self, p):
        return int(p[0])

    @_('identifier')
    def value(self, p):
        return p.identifier
    
    @_('PIDENTIFIER')
    def identifier(self, p):
        return ('int', p[0], p.lineno)
    
    @_('PIDENTIFIER LPAREN PIDENTIFIER RPAREN')
    def identifier(self, p):
        return ('int[]', p[0], ('int', p[2], p.lineno), p.lineno)
    
    @_('PIDENTIFIER LPAREN NUMBER RPAREN')
    def identifier(self, p):
        return ('int[]', p[0], ('int', p[2], p.lineno), p.lineno)



    
    

