import sys

class valueType():
    def __init__(self):
        self.typeOf = 'intiger'

class arrayType():
    def __init__(self, indexLow, indexHigh):
        self.typeOf = 'intigerArray'
        self.indexLow = indexLow
        self.indexHigh = indexHigh

class outputCode():
    def __init__(self):
        self.code = []

    #SUB X X
    def clearReg(self, reg):                    
        self.code += ["SUB " + reg + " " + reg]

    #INC X * val
    def setRegValue(self, reg, val):
        self.clearReg(reg)
        while val > 0:
            self.code += ["INC " + reg]
            val -= 1

    def storeReg(self, reg):
        self.code += ['STORE ' + reg]

    def loadToReg(self, reg):
        self.code += ['LOAD ' + reg]

    def addToRegFromReg(self, regTo, regFrom):
        self.code += ['ADD ' + regTo + ' ' + regFrom]

    # X -> &cell
    def setRegToMemCell(self, memCell, reg):
        self.setRegValue('A', memCell)
        self.loadToReg(reg)

    # X -> &cell(&cell)
    def setRegToUnknownIndex(self, arrayCell, indexCell, regTo, regTemp):
        self.setRegValue('A', indexCell)
        self.loadToReg(regTemp)
        self.setRegValue(regTo, arrayCell)
        self.addToRegFromReg(regTo, regTemp)

    # &cell -> X
    def storeRegAtCell(self, reg, cell):
        self.setRegValue('A', cell)
        self.storeReg(reg)

    def storeToMem(self, memCell):
        self.code += ['GET B']
        self.setRegValue('A', memCell)
        self.code += ['STORE B']

    def storeToUnknownCell(self, arrayCell, indexCell):
        self.code += ['GET B']
        self.setRegToUnknownIndex(arrayCell, indexCell, 'A', 'H')
        self.storeReg('B')

    # reg1 - iterator
    def multiplyRegByrReg(self, reg1, reg2, regRes, l1, l2):
        self.clearReg(regRes)
        self.code += [l1 + ":"]
        self.code += ["JZERO " + reg1 + " " + l2]
        self.addToRegFromReg(regRes, reg2)
        self.code += ['DEC ' + reg1]
        self.code += ['JUMP ' + l1]
        self.code += [l2 + ":"]

    def greaterEqual(self, reg1, reg2):
        self.code += ['INC ' + reg1]
        self.code += ['SUB ' + reg1 + " " + reg2]

    def divideRegByReg(self, regDiv, regd, regQuo, regTemp, l1, l2, l3):
        self.code += ['JZERO ' + regd + ' ' + l3]
        self.code += [l1 + ':']
        self.code += ['COPY ' + regTemp + ' ' + regDiv]
        self.greaterEqual(regTemp, regd)
        self.code += ['JZERO ' + regTemp + ' ' + l2]
        self.code += ['INC ' + regQuo]
        self.code += ['SUB ' + regDiv + ' ' + regd]
        self.code += ['JUMP ' + l1]
        self.code += [l3 + ':']
        self.code += ['SUB ' + regDiv + ' ' + regDiv]
        self.code += ['SUB ' + regQuo + ' ' + regQuo]
        self.code += [l2 + ':']


class machine():
    memIndex = 0
    memory = {}
    variables = {}
    registers = {'A': False, 'B': False, 'C': False, 'D': False, 'E': False, 'F': False, 'G': False, 'H': False}
    
    _out_ = outputCode()

    def __init__(self, parseTree):
        self.parseTree = parseTree
        self.machineCode = ''
        self.labels = 0

        # Declarations
        for i in parseTree[1]:
            typeOf = i[0]
            pidentifier = i[1]
            
            if typeOf == 'integer':
                self.variables[pidentifier] = valueType()
                self.memory[pidentifier] = self.memIndex
                self.memIndex += 1
            else:
                indexLow = int(i[2][0][1])
                indexHigh = int(i[2][1][1])
                self.variables[pidentifier] = arrayType(indexLow, indexHigh)
                self.memory[pidentifier] = self.memIndex
                self.memIndex += indexHigh - indexLow + 1

        #Program commands
        for i in parseTree[2]:
            self.commandHandler(i)


        self._out_.code += ['HALT']

        for line in self._out_.code:
            print(line)

    def commandHandler(self, params):
        return getattr(self, params[0])(params)

    def genLabel(self):
        self.labels += 1
        return 'label' + str(self.labels)

    #@TODO offset
    def tokenToReg(self, token, regOut):
        typeOf = token[0]
        if typeOf == 'value':
            value = int(token[1])
            self._out_.setRegValue(regOut, value)

        elif typeOf == 'integer':
            pidentifier = token[1]
            memCell = self.memory[pidentifier]
            self._out_.setRegToMemCell(memCell, regOut)
            
        elif typeOf == 'integerArray':
            arrayIdentifier = token[1]
            arrayCell = self.memory[arrayIdentifier]

            arrayIndex = token[2]
            typeOfIndex = arrayIndex[0]
            if typeOfIndex == 'value':
                indexValue = int(arrayIndex[1])
                self._out_.setRegToMemCell(arrayCell + indexValue, regOut)

            elif typeOfIndex == 'integer':
                indexCell = self.memory[arrayIndex[1]]
                self._out_.setRegToUnknownIndex(arrayCell, indexCell, regOut, 'H')
        
        elif typeOf == 'add':
            self.tokenToReg(token[1], regOut)
            self.tokenToReg(token[2], 'H')
            self._out_.code += ['ADD ' + regOut + ' H']

        elif typeOf == 'sub':
            self.tokenToReg(token[1], regOut)
            self.tokenToReg(token[2], 'H')
            self._out_.code += ['SUB ' + regOut + ' H']

        elif typeOf == 'mul':
            self.tokenToReg(token[1], 'G')
            self.tokenToReg(token[2], 'H')
            self._out_.multiplyRegByrReg('G', 'H', regOut, self.genLabel(), self.genLabel())

        elif typeOf == 'div':
            self.tokenToReg(token[1], 'G')
            self.tokenToReg(token[2], 'H')
            self._out_.divideRegByReg('G', 'H', regOut, 'F', self.genLabel(), self.genLabel(), self.genLabel())

        elif typeOf == 'mod':
            self.tokenToReg(token[1], 'G')
            self.tokenToReg(token[2], 'H')
            self._out_.divideRegByReg('G', 'H', 'F', regOut, self.genLabel(), self.genLabel(), self.genLabel())



    def assign(self, params):
        print(params)
        identifier = params[1]

        typeOfIdentifier = identifier[0]
        pidentifier = identifier[1]

        expression = params[2]
        
        if pidentifier in self.variables:
            self.tokenToReg(expression, 'C')
            identifierCell = self.memory[pidentifier]

            if typeOfIdentifier == 'integer':
                self._out_.storeRegAtCell('C', identifierCell)
            elif typeOfIdentifier == 'integerArray':
                index = identifier[2]
                indexType = index[0]

                if indexType == 'value':
                    indexValue = int(index[1])
                    self._out_.storeRegAtCell('C', identifierCell + indexValue)
                elif indexType == 'integer':
                    indexIdentifier = index[1]
                    indexCell = self.memory[indexIdentifier]
                    self._out_.setRegToUnknownIndex(identifierCell, indexCell, 'A', 'H')
                    self._out_.storeReg('C')

    def read(self, params):
        identifier = params[1]

        typeOfIdentifier = identifier[0]
        pidentifier = identifier[1]
        index = identifier[2]

        arrayCell = self.memory[pidentifier]
        if pidentifier in self.variables:
            if typeOfIdentifier == 'integerArray':
                typeOfIndex = identifierIndex[0]
                if typeOfIndex == 'value':
                    indexValue = int(identifierIndex[1])
                    self._out_.storeToMem(arrayCell + indexValue)
                elif typeOfIndex == 'integer':
                    indexID = identifierIndex[1]
                    indexCell = self.memory[indexID]
                    self._out_.storeToUnknownCell(arrayCell, indexCell)

            elif typeOfIdentifier == 'integer':
                self._out_.storeToMem(arrayCell)
                
