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
        tab.append(("integer", p[1], p.lineno))
        return tab

    @_('declarations PIDENTIFIER LPAREN NUMBER COLON NUMBER RPAREN SEMICOLON')
    def declarations(self, p):
        tab = (p.declarations if p.declarations != None else [])
        tab.append(('integerArray', p[1], (('value', p[3]), ('value', p[5])), p.lineno))
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
        return ('ifThenElse', p.condition, p.commands0, p.commands1)
    
    @_('IF condition THEN commands ENDIF')
    def command(self, p):
        return ('ifThen', p.condition, p.commands)
    
    @_('WHILE condition DO commands ENDWHILE')
    def command(self, p):
        return ('whileDo', p.condition, p.commands)
    
    @_('DO commands WHILE condition ENDDO')
    def command(self, p):
        return ('doWhile', p.commands, p.condition)

    @_('FOR PIDENTIFIER FROM value TO value DO commands ENDFOR')
    def command(self, p):
        return ('forTo', ('assign', ('integer', p[1], p.lineno), p.value0), ('assign', ('integer', p[1] + 'End', p.lineno), p.value1), p.commands)

    @_('FOR PIDENTIFIER FROM value DOWNTO value DO commands ENDFOR')
    def command(self, p):
        return ('forDownTo', ('assign', ('integer', p[1], p.lineno), p.value0), ('assign', ('integer', p[1] + 'End', p.lineno), p.value1), p.commands)

    @_('READ identifier SEMICOLON')
    def command(self, p):
        return ('read', p.identifier)

    @_('WRITE value SEMICOLON')
    def command(self, p):
        return ('write', p.value)

    @_('value')
    def expression(self, p):
        return p.value

    expressions = {'+':'add', '-':'sub', '*':'mul', '/':'div', '%':'mod'}

    @_('value PLUS value'
        ,'value MINUS value'
        ,'value TIMES value'
        ,'value DIVIDE value'
        ,'value MODULO value')
    def expression(self, p):
        return (self.expressions[p[1]], p.value0, p.value1)

    conditions = {'=':'equal', '!=':'notEqual', '<':'lesserThan', '>':'greaterThan', '<=':'lesserEqual', '>=':'greaterEqual'}

    @_('value EQ value'
        ,'value NEQ value'
        ,'value LT value'
        ,'value GT value'
        ,'value LEQ value'
        ,'value GEQ value')
    def condition(self, p):
        return (self.conditions[p[1]], p.value0, p.value1)

    @_('NUMBER')
    def value(self, p):
        return ('value', p[0])

    @_('identifier')
    def value(self, p):
        return p.identifier
    
    @_('PIDENTIFIER')
    def identifier(self, p):
        return ('integer', p[0], p.lineno)
    
    @_('PIDENTIFIER LPAREN PIDENTIFIER RPAREN')
    def identifier(self, p):
        return ('integerArray', p[0], ('integer', p[2], p.lineno), p.lineno)
    
    @_('PIDENTIFIER LPAREN NUMBER RPAREN')
    def identifier(self, p):
        return ('integerArray', p[0], ('value', p[2]), p.lineno)