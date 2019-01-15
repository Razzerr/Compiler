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
        tempCode = []

        while val > 10:
            if val%2==0:
                val = val/2
                tempCode += ['ADD ' + reg + ' ' + reg]
            else:
                val  -= 1
                tempCode += ['INC ' + reg]

        self.code += ["INC " + reg] * int(val)
        self.code += tempCode[::-1]


    def storeReg(self, reg):
        self.code += ['STORE ' + reg]

    def loadToReg(self, reg):
        self.code += ['LOAD ' + reg]

    def addToRegFromReg(self, regTo, regFrom):
        self.code += ['ADD ' + regTo + ' ' + regFrom]

    # X -> &cell
    def loadCellToReg(self, memCell, regIn):
        self.setRegValue('A', memCell)
        self.loadToReg(regIn)

    def loadCellOfKnownArrayIndex(self, arrayCell, indexVal, regIn, regTemp1, regTemp2):
        self.setRegAToKnownArrayIndex(arrayCell, indexVal, regTemp1, regTemp2)
        self.loadToReg(regIn)


    def loadCellOfUnknownArrayIndex(self, arrayCell, indexCell, regIn, regTemp1, regTemp2):
        self.setRegAToUnknownArrayIndex(arrayCell, indexCell, regTemp1, regTemp2)
        self.loadToReg(regIn)


    #####################################################################################
    # Array's offset is always being stored at array(0)! Thus add one to every indexing.#
    #####################################################################################

    def setRegAToUnknownArrayIndex(self, arrayCell, indexCell, reg, regTemp):
        self.code += ['# \/ DEBUG: Store index value at reg ' + regTemp]
        self.setRegValue('A', indexCell)
        self.loadToReg(regTemp)

        self.code += ['# \/ DEBUG: Storing array\'s offset at reg ' + reg]
        self.setRegValue('A', arrayCell)
        self.loadToReg(reg)
        self.code += ['# \/ DEBUG: Add index to array\'s address']
        self.code += ['ADD A ' + regTemp]
        self.code += ['# \/ DEBUG: Subtracting the offset from array\'s address']
        self.code += ['SUB A ' + reg]
        self.code += ['INC A']

    def setRegAToKnownArrayIndex(self, arrayCell, indexVal, reg, regTemp):
        self.code += ['# \/ DEBUG: Store index value at reg ' + regTemp]
        self.setRegValue(regTemp, indexVal)

        self.code += ['# \/ DEBUG: Storing array\'s offset at reg ' + reg]
        self.setRegValue('A', arrayCell)
        self.loadToReg(reg)
        self.code += ['# \/ DEBUG: Add index to array\'s address']
        self.code += ['ADD A ' + regTemp]
        self.code += ['# \/ DEBUG: Subtracting the offset from array\'s address']
        self.code += ['SUB A ' + reg]
        self.code += ['INC A ']

    # &cell(num) -> X ;
    def storeRegAtKnownArrayIndex(self, arrayCell, indexVal, regOut, regTemp1, regTemp2):
        self.setRegAToKnownArrayIndex(arrayCell, indexVal, regTemp1, regTemp2)
        self.code += ['# \/ DEBUG: Store array(0) + index + 1 - offset at reg ' + regOut]
        self.storeReg(regOut)

    def storeRegAtUnknownArrayIndex(self, arrayCell, indexCell, regOut, regTemp1, regTemp2):
        self.setRegAToUnknownArrayIndex(arrayCell, indexCell, regTemp1, regTemp2)
        self.code += ['# \/ DEBUG: Store array(0) + index + 1 - offset at reg ' + regOut]
        self.storeReg(regOut)

    # &cell -> X
    def storeRegAtCell(self, memCell, regOut):
        self.setRegValue('A', memCell)
        self.storeReg(regOut)

    def getToReg(self, reg):
        self.code += ['GET ' + reg]

    def multiplyRegByReg(self, reg1, reg2, regRes, l1, l2, l3, l4):
        self.code += ['SUB ' + regRes + ' ' + regRes]
        self.code += [l1 + ':']
        self.code += ['JZERO ' + reg2 + ' ' + l4]
        self.code += ['JODD ' + reg2 + ' ' + l3]
        self.code += [l2 + ':']
        self.code += ['HALF ' + reg2]
        self.code += ['ADD ' + reg1 + ' ' + reg1]
        self.code += ['JUMP ' + l1]
        self.code += [l3 + ':']
        self.code += ['ADD ' + regRes + ' ' + reg1]
        self.code += ['JUMP ' + l2]
        self.code += [l4 + ':']

    def divideRegByReg(self, regDIV, regd, regRes, regK, regTemp, l1, l2, l3, l4, l5):
        self.clearReg(regRes)
        self.code += ['JZERO ' + regd + ' ' + l5]
        self.clearReg(regK)
        self.code += ['INC ' + regK]
        self.code += [l1 + ':']
        self.code += ['COPY ' + regTemp + ' ' + regDIV]
        self.code += ['INC ' + regTemp]
        self.code += ['SUB ' + regTemp + ' ' + regd]
        self.code += ['JZERO ' + regTemp + ' ' + l2]
        self.code += ['ADD ' + regd + ' ' + regd]
        self.code += ['ADD ' + regK + ' ' + regK]
        self.code += ['JUMP ' + l1]
        self.code += [l2 + ':']
        self.code += ['JZERO ' + regK + ' ' + l4]
        self.code += ['COPY ' + regTemp + ' ' + regDIV]
        self.code += ['INC ' + regTemp]
        self.code += ['SUB ' + regTemp + ' ' + regd]
        self.code += ['JZERO ' + regTemp + ' ' + l3]
        self.code += ['ADD ' + regRes + ' ' + regK]
        self.code += ['SUB ' + regDIV + ' ' + regd]
        self.code += [l3 + ':']
        self.code += ['HALF ' + regK]
        self.code += ['HALF ' + regd]
        self.code += ['JUMP ' + l2]
        self.code += [l5 + ':']
        self.clearReg(regDIV)
        self.code += [l4 + ':']

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
        self.code += ['COPY ' + regTemp + ' ' + reg2]
        self.code += ['SUB ' + regTemp + ' ' + reg1]
        self.code += ['SUB ' + reg1 + ' ' + reg2]
        self.code += ['ADD ' + reg1 + ' ' + regTemp]
        self.code += ['JZERO ' + reg1 + ' ' + l1]
        self.clearReg(reg1)
        self.code += ['JUMP ' + l2]
        self.code += [l1 + ':']
        self.code += ['INC ' + reg1]
        self.code += [l2 + ':']

    def equal_old(self, reg1, reg2, regTemp, l1, l2):
        self.code += ['COPY ' + regTemp + ' ' + reg1]
        self.greaterEqual(reg1, reg2)
        self.code += ['JZERO ' + reg1 + ' ' + l1]
        self.code += ['JUMP ' + l2]
        self.code += [l1 + ':']
        self.code += ['COPY ' + reg1 + ' ' + regTemp]
        self.lesserEqual(reg1, reg2)
        self.code += [l2 + ':']

    def notEqual(self, reg1, reg2, regTemp, l1):
        self.code += ['COPY ' + regTemp + ' ' + reg2]
        self.code += ['SUB ' + regTemp + ' ' + reg1]
        self.code += ['SUB ' + reg1 + ' ' + reg2]
        self.code += ['ADD ' + reg1 + ' ' + regTemp]

    def notEqual_old(self, reg1, reg2, regTemp, l1):
        self.code += ['COPY ' + regTemp + ' ' + reg1]
        self.greater(reg1, reg2)
        self.code += ['JZERO ' + reg1 + ' ' + l1]
        self.code += ['COPY ' + reg1 + ' ' + regTemp]
        self.lesser(reg1, reg2)
        self.code += [l1 + ':']

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
        if parseTree[1] != None:
            for i in parseTree[1]:
                typeOf = i[0]
                pidentifier = i[1]
                
                if typeOf == 'integer':
                    self.declareInt(pidentifier)
                else:
                    indexLow = int(i[2][0][1])
                    indexHigh = int(i[2][1][1])
                    self.declareArray(pidentifier, indexLow, indexHigh)

        #Program commands
        self.commands(parseTree[2])

        self._out_.code += ['HALT']

        # for line in self._out_.code:
        #     print(line)

    def declareInt(self, pidentifier):
        self.variables[pidentifier] = valueType()
        self.memory[pidentifier] = self.memIndex
        self.memIndex += 1

    def declareArray(self, pidentifier, indexLow, indexHigh):
        self.variables[pidentifier] = arrayType(indexLow, indexHigh)
        self.memory[pidentifier] = self.memIndex
        self._out_.code += ['# \/ DEBUG: Set offset at memory cell ' + str(self.memIndex)]
        self.memIndex += indexHigh - indexLow + 1 + 1 # + place for offset
        self._out_.setRegValue('B', indexLow)
        self._out_.storeRegAtCell(self.memory[pidentifier], 'B')

    def undeclareInt(self, pidentifier):
        self.variables.__delitem__(pidentifier)
        self.memory.__delitem__(pidentifier)

    def commands(self, array):
        for i in array:
            self.commandHandler(i)

    def commandHandler(self, params):
        return getattr(self, params[0])(params)

    def genLabel(self):
        self.labels += 1
        return 'label' + str(self.labels)

    #@TODO offset
    def tokenToReg(self, token, reg='B', regTemp1='C', regTemp2='D', regTemp3='E', regTemp4='F'):
        typeOf = token[0]
        if typeOf == 'value':
            value = int(token[1])
            self._out_.setRegValue(reg, value)

        elif typeOf == 'integer':
            pidentifier = token[1]
            memCell = self.memory[pidentifier]
            self._out_.loadCellToReg(memCell, reg)
            
        elif typeOf == 'integerArray':
            arrayIdentifier = token[1]
            arrayCell = self.memory[arrayIdentifier]

            arrayIndex = token[2]
            typeOfIndex = arrayIndex[0]
            if typeOfIndex == 'value':
                indexValue = int(arrayIndex[1])
                self._out_.loadCellOfKnownArrayIndex(arrayCell, indexValue, reg, regTemp1, regTemp2)

            elif typeOfIndex == 'integer':
                indexCell = self.memory[arrayIndex[1]]
                self._out_.loadCellOfUnknownArrayIndex(arrayCell, indexCell, reg, regTemp1, regTemp2)
        
        elif typeOf == 'add':
            self.tokenToReg(token[1], reg)
            self.tokenToReg(token[2], regTemp1)
            self._out_.code += ['ADD ' + reg + regTemp1]

        elif typeOf == 'sub':
            self.tokenToReg(token[1], reg)
            self.tokenToReg(token[2], regTemp1)
            self._out_.code += ['SUB ' + reg + regTemp1]

        elif typeOf == 'mul':
            self.tokenToReg(token[1], regTemp1, 'E', 'F')
            self.tokenToReg(token[2], regTemp2, 'E', 'F')
            self._out_.multiplyRegByReg(regTemp2, regTemp1, reg, self.genLabel(), self.genLabel(), self.genLabel(), self.genLabel())

        elif typeOf == 'div':
            self.tokenToReg(token[1], regTemp1, 'E', 'F')
            self.tokenToReg(token[2], regTemp2, 'E', 'F')
            self._out_.divideRegByReg(regTemp1, regTemp2, reg, regTemp3, regTemp4,
                self.genLabel(), self.genLabel(), self.genLabel(), self.genLabel(), self.genLabel())

        elif typeOf == 'mod':
            self.tokenToReg(token[1], reg, 'E', 'F')
            self.tokenToReg(token[2], regTemp1, 'E', 'F')
            self._out_.divideRegByReg(reg, regTemp1, regTemp2, regTemp3, regTemp4, 
                self.genLabel(), self.genLabel(), self.genLabel(), self.genLabel(), self.genLabel())

    def condToReg(self, token, reg1='B', reg2='C', regTemp1='D', regTemp2='E'):
        typeOf = token[0]
        value1 = token[1]
        value2 = token[2]

        self.tokenToReg(value1, reg1, regTemp1, regTemp2)
        self.tokenToReg(value2, reg2, regTemp1, regTemp2)

        if typeOf == 'equal':
            self._out_.equal(reg1, reg2, regTemp1, self.genLabel(), self.genLabel())
        elif typeOf == 'notEqual':
            self._out_.notEqual(reg1, reg2, regTemp1, self.genLabel())
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

    def whileDo(self, params):
        condition = params[1]
        commands = params[2]
        regRes = 'B'
        labelEnd = self.genLabel()
        labelLoop = self.genLabel()
        
        self._out_.code += ['# \/ DEBUG: Start of while loop. Loop label - ' + labelLoop]
        self._out_.code += [labelLoop + ':']
        self._out_.code += ['# \/ DEBUG: Condition result to register ' + regRes]
        self.condToReg(condition, regRes, 'C')
        self._out_.code += ['# \/ DEBUG: Jump if condition not met to ' + labelEnd]
        self._out_.code += ['JZERO ' + regRes + ' ' + labelEnd]
        self._out_.code += ['# \/ DEBUG: Commands']
        self.commands(commands)
        self._out_.code += ['# \/ DEBUG: Jump back to loop label - ' + labelLoop]
        self._out_.code += ['JUMP ' + labelLoop]
        self._out_.code += ['# \/ DEBUG: End of While loop']
        self._out_.code += [labelEnd + ':']

    def doWhile(self, params):
        condition = params[2]
        commands = params[1]
        regRes = 'B'
        labelLoop = self.genLabel()

        self._out_.code += [labelLoop + ':']
        self.commands(commands)
        self.condToReg(condition, regRes, 'C')
        self._out_.code += ['JZERO ' + regRes + ' ' + labelLoop]  

    def forTo(self, params):
        valueFrom = params[1]
        valueTo = params[2]
        commands = params[3]

        pidentifierFrom = valueFrom[1][1]
        pidentifierTo = valueTo[1][1]
        regRes = 'B'

        self.declareInt(pidentifierFrom)
        self.declareInt(pidentifierTo)
        self.assign(valueFrom, regRes)
        self.assign(valueTo, 'C')

        labelEnd = self.genLabel()
        labelLoop = self.genLabel()

        self._out_.code += [labelLoop + ':']
        self._out_.lesserEqual(regRes, 'C')
        self._out_.code += ['JZERO ' + regRes + ' ' + labelEnd]
        self.commands(commands)
        self._out_.loadCellToReg(self.memory[pidentifierFrom], regRes)
        self._out_.code += ['INC ' + regRes]
        self._out_.code += ['STORE ' + regRes]
        self._out_.loadCellToReg(self.memory[pidentifierTo], 'C')
        self._out_.code += ['JUMP ' + labelLoop]
        self._out_.code += [labelEnd + ':']

        self.undeclareInt(pidentifierFrom)
        self.undeclareInt(pidentifierTo)

    def forDownTo(self, params):
        valueFrom = params[1]
        valueTo = params[2]
        commands = params[3]

        pidentifierFrom = valueFrom[1][1]
        pidentifierTo = valueTo[1][1]
        regRes = 'B'

        self.declareInt(pidentifierFrom)
        self.declareInt(pidentifierTo)
        self.assign(valueFrom, regRes)
        self.assign(valueTo, 'C')

        labelEnd = self.genLabel()
        labelLoop = self.genLabel()
        labelLastIter = self.genLabel()

        self._out_.greaterEqual(regRes, 'C')
        self._out_.code += ['JZERO ' + regRes + ' ' + labelEnd]
        self._out_.code += [labelLoop + ':']
        self.commands(commands)
        self._out_.loadCellToReg(self.memory[pidentifierFrom], regRes)
        self._out_.code += ['JZERO ' + regRes + ' ' + labelEnd]
        self._out_.code += ['DEC ' + regRes]
        self._out_.code += ['STORE ' + regRes]
        self._out_.loadCellToReg(self.memory[pidentifierTo], 'C')
        self._out_.greater(regRes, 'C')
        self._out_.code += ['JZERO ' + regRes + ' ' + labelLastIter]
        self._out_.code += ['JUMP ' + labelLoop]
        self._out_.code += [labelLastIter + ':']
        self.commands(commands)
        self._out_.code += [labelEnd + ':']

        self.undeclareInt(pidentifierFrom)
        self.undeclareInt(pidentifierTo)

    def assign(self, params, reg='B', regTemp1='C', regTemp2='D'):
        identifier = params[1]

        typeOfIdentifier = identifier[0]
        pidentifier = identifier[1]

        expression = params[2]
        
        if pidentifier in self.variables:
            self.tokenToReg(expression, reg)
            identifierCell = self.memory[pidentifier]

            if typeOfIdentifier == 'integer':
                self._out_.storeRegAtCell(identifierCell, reg)
            elif typeOfIdentifier == 'integerArray':
                index = identifier[2]
                indexType = index[0]

                if indexType == 'value':
                    indexValue = int(index[1])
                    self._out_.storeRegAtKnownArrayIndex(identifierCell, indexValue, reg, regTemp1, regTemp2)
                elif indexType == 'integer':
                    indexIdentifier = index[1]
                    indexCell = self.memory[indexIdentifier]
                    self._out_.storeRegAtUnknownArrayIndex(identifierCell, indexCell, reg, regTemp1, regTemp2)

    def read(self, params, regRes='B', regTemp1='C', regTemp2='D'):
        identifier = params[1]

        typeOfIdentifier = identifier[0]
        pidentifier = identifier[1]
        identifierIndex = identifier[2]

        arrayCell = self.memory[pidentifier]
        if pidentifier in self.variables:
            if typeOfIdentifier == 'integerArray':
                typeOfIndex = identifierIndex[0]
                if typeOfIndex == 'value':
                    indexValue = int(identifierIndex[1])
                    self._out_.getToReg(regRes)
                    self._out_.storeRegAtKnownArrayIndex(arrayCell, indexValue, regRes, regTemp1, regTemp2)
                elif typeOfIndex == 'integer':
                    indexID = identifierIndex[1]
                    indexCell = self.memory[indexID]
                    self._out_.getToReg(regRes)
                    self._out_.storeRegAtUnknownArrayIndex(arrayCell, indexCell, regRes, regTemp1, regTemp2)

            elif typeOfIdentifier == 'integer':
                self._out_.getToReg(regRes)
                self._out_.storeRegAtCell(arrayCell, regRes)

    def write(self, params, regRes='B', regTemp1='C', regTemp2='D'):
        identifier = params[1]

        typeOfIdentifier = identifier[0]

        if typeOfIdentifier == 'integerArray':
            pidentifier = identifier[1]
            identifierIndex = identifier[2]
            arrayCell = self.memory[pidentifier]
            typeOfIndex = identifierIndex[0]
            if typeOfIndex == 'value':
                indexValue = int(identifierIndex[1])
                self._out_.loadCellOfKnownArrayIndex(arrayCell, indexValue, regRes, regTemp1, regTemp2)
            elif typeOfIndex == 'integer':
                indexID = identifierIndex[1]
                indexCell = self.memory[indexID]
                self._out_.loadCellOfUnknownArrayIndex(arrayCell, indexCell, regRes, regTemp1, regTemp2)

        elif typeOfIdentifier == 'integer':
            pidentifier = identifier[1]
            varCell = self.memory[pidentifier]
            self._out_.loadCellToReg(varCell, regRes)

        elif typeOfIdentifier == 'value':
            value = int(identifier[1])
            self._out_.setRegValue(regRes, value)
        
        self._out_.code += ['PUT ' + regRes]
