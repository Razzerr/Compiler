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

    def divideRegByReg(self, regDiv, regd, regQuo, regTemp, l1, l2, l3):
        self.code += ['JZERO ' + regd + ' ' + l3]
        self.code += [l1 + ':']
        self.code += ['COPY ' + regTemp + ' ' + regDiv]
        self.greater(regTemp, regd)
        self.code += ['JZERO ' + regTemp + ' ' + l2]
        self.code += ['INC ' + regQuo]
        self.code += ['SUB ' + regDiv + ' ' + regd]
        self.code += ['JUMP ' + l1]
        self.code += [l3 + ':']
        self.code += ['SUB ' + regDiv + ' ' + regDiv]
        self.code += ['SUB ' + regQuo + ' ' + regQuo]
        self.code += [l2 + ':']

    # Logical statements - if 0 in reg 1 then false
    def greaterEqual(self, reg1, reg2):
        self.code += ['INC ' + reg1]
        self.code += ['SUB ' + reg1 + ' ' + reg2]

    def greater(self, reg1, reg2):
        self.code += ['SUB ' + reg1 + ' ' + reg2]

    def lesserEqual(self, reg1, reg2):
        self.code += ['INC ' + reg2]
        self.code += ['SUB ' + reg2 + " " + reg1]
        self.code += ['COPY ' + reg1 + ' ' + reg2]

    def lesser(self, reg1, reg2):
        self.code += ['SUB ' + reg2 + " " + reg1]
        self.code += ['COPY ' + reg1 + ' ' + reg2]

    def equal(self, reg1, reg2, regTemp, l1, l2):
        self.code += ['COPY ' + regTemp + ' ' + reg1]
        self.greaterEqual(reg1, reg2)
        self.code += ['JZERO ' + reg1 + ' ' + l1]
        self.code += ['JUMP ' + l2]
        self.code += [l1]
        self.code += ['COPY ' + reg1 + ' ' + regTemp]
        self.lesserEqual(reg1, reg2)
        self.code += [l2]

    def notEqual(self, reg1, reg2, regTemp, l1):
        self.code += ['COPY ' + regTemp + ' ' + reg1]
        self.greater(reg1, reg2)
        self.code += ['JZERO ' + reg1 + ' ' + l1]
        self.code += ['COPY ' + reg1 + ' ' + regTemp]
        self.lesser(reg1, reg2)
        self.code += [l1]


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
        self.commands(parseTree[2])

        self._out_.code += ['HALT']

        for line in self._out_.code:
            print(line)

    def commandHandler(self, params):
        return getattr(self, params[0])(params)

    def genLabel(self):
        self.labels += 1
        return 'label' + str(self.labels)

    def commands(self, array):
        for i in array:
            self.commandHandler(i)

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

    def condToReg(self, token, reg1, reg2):
        print(token)
        typeOf = token[0]
        value1 = token[1]
        value2 = token[2]

        self.tokenToReg(value1, reg1)
        self.tokenToReg(value2, reg2)

        if typeOf == 'equal':
            self._out_.equal(reg1, reg2, 'H', self.genLabel(), self.genLabel())
        elif typeOf == 'notEqual':
            self._out_.notEqual(reg1, reg2, 'H', self.genLabel())
        elif typeOf == 'greaterThan':
            self._out_.greater(reg1, reg2)
        elif typeOf == 'greaterEqual':
            self._out_.greaterEqual(reg1, reg2)
        elif typeOf == 'lesserThan':
            self._out_.lesser(reg1, reg2)
        elif typeOf == 'lesserEqual':
            self._out_.lesserEqual(reg1, reg2)

    def ifThen(self, params):
        condition = params[1]
        commands = params[2]
        regRes = 'B'
        label = self.genLabel()

        self.condToReg(condition, regRes, 'C')
        self._out_.code += ['JZERO ' + regRes + ' ' + label]
        self.commands(commands)
        self._out_.code += [label + ':']
    
    def ifThenElse(self, params):
        condition = params[1]
        commands1 = params[2]
        commands2 = params[3]
        regRes = 'B'
        label1 = self.genLabel()
        label2 = self.genLabel()

        self.condToReg(condition, regRes, 'C')
        self._out_.code += ['JZERO ' + regRes + ' ' + label1]
        self.commands(commands1)
        self._out_.code += ['JUMP ' + label2]
        self._out_.code += [label1 + ':']
        self.commands(commands2)
        self._out_.code += [label2 + ':']

    def assign(self, params):
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
                
