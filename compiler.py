import sys
from compiler.lexer import lex
from compiler.parser import bison

def readList(arr, level):
    level += 1
    for i in arr:
        if type(i) == type([]) or type(i) == type(()):
            readList(i, level)
        else:
            print(' '*level, "|--", end = '')
            print("- ", i)
    print(" "*level, "-----")
    level -= 1

if __name__ == '__main__':
    lexer = lex()
    parser = bison()

    if len(sys.argv) > 1 and 3 > len(sys.argv):
        try:
            file = open(sys.argv[1], 'r')
            data = file.read()
            readList(parser.parse(lexer.tokenize(data)), -1)

            # parser.parse(lexer.tokenize(data))
        except FileNotFoundError:
            print("File not found!")
    else:
        while(True):
            data = input("input> ")
            print(parser.parse(lexer.tokenize(data)))