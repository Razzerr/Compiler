import sys
from compiler.lexer import lex
from compiler.parser import bison
from compiler.machine import machine
from compiler.postprocessor import postprocessor

if __name__ == '__main__':
    lexer = lex()
    parser = bison()

    if len(sys.argv) > 1 and 4 > len(sys.argv):
        saveFile = sys.argv[2]
        try:
            file = open(sys.argv[1], 'r')
            data = file.read()
        except FileNotFoundError:
            print("File not found!")
        finally:
            file.close()

        lex_out = lexer.tokenize(data)
        parser_out = parser.parse(lex_out)
        mach = machine(parser_out)
        post = postprocessor(mach._out_.code)
        # print(parser.parse(lexer.tokenize(data)))
        try:
            file = open(saveFile, 'w')
            for i in post.code:
                file.write(i + '\n')
        except IOError:
            print("I/O error")
        finally:
            file.close()
            
    else:
        while(True):
            data = input("input> ")
            for i in lexer.tokenize(data):
                print(i)