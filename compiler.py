import sys
from compiler.lexer import lex
from compiler.parser import bison
from compiler.machine import machine
from compiler.postprocessor import postprocessor

if __name__ == '__main__':
    lexer = lex()
    parser = bison()

    if len(sys.argv) > 1 and 3 > len(sys.argv):
        try:
            file = open(sys.argv[1], 'r')
            data = file.read()
            mach = machine(parser.parse(lexer.tokenize(data)))
            post = postprocessor(mach._out_.code)
            # print(parser.parse(lexer.tokenize(data)))
        except FileNotFoundError:
            print("File not found!")
    else:
        while(True):
            data = input("input> ")
            for i in lexer.tokenize(data):
                print(i)