import sys
from compiler.lexer import lex
from compiler.parser import bison
from compiler.errors import errorMachine
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
        print("--------------------- Beginning of compilation ---------------------")
        lex_out = lexer.tokenize(data)
        parser_out = parser.parse(lex_out)
        if parser_out == None:
            exit()

        err = errorMachine(parser_out)
        if not err._error_.errorOccured:
            mach = machine(parser_out)
            post = postprocessor(mach._out_.code)
            try:
                file = open(saveFile, 'w')
                for i in post.code:
                    file.write(i + '\n')
            except IOError:
                print("I/O error")
            finally:
                file.close()
        # print(parser.parse(lexer.tokenize(data)))
        print("--------------------- End of compilation ---------------------")
            
    else:
        while(True):
            data = input("input> ")
            for i in lexer.tokenize(data):
                print(i)