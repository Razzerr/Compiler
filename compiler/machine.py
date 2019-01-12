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
  
    #a = val
    def storeValAtCell(self, memCell, val):
        self.setRegValue('B', val)
        self.setRegValue('A', memCell)
        self.storeReg('B')

    # a(b) = val (b - user input)
    def storeValAtUnknownCell(self, arrayCell, indexCell, val):
        self.setRegValue('C', val)
        self.setRegToUnknownIndex(arrayCell, indexCell, 'A', 'B')
        self.storeReg('C')

    # a = c (c - user input)
    def storeUnknownValAtCell(self, memCell, valMemCell):
        self.setRegValue('A', valMemCell)
        self.loadToReg('B')
        self.setRegValue('A', memCell)
        self.storeReg('B')

    # a(b) = c (b, c - user inputs)
    def storeUnknownValAtUnknownCell(self, arrayCell, indexCell, valMemCell):
        self.setRegValue('A', valMemCell) 
        self.loadToReg('C') # C -> val
        self.setRegToUnknownIndex(arrayCell, indexCell, 'A', 'B') # A -> &a(b)
        self.storeReg('C') # &a(b) -> val

    # a = c(d) (d - user input)
    def storeUnknownArrValAtCell(self, memCell, valArrayCell, valIndexCell):
        self.setRegToUnknownIndex(valArrayCell, valIndexCell, 'A', 'B') # A -> &c(d)
        self.loadToReg('B') # B -> val
        self.setRegValue('A', memCell) # A -> &a
        self.storeReg('B') # &a -> val 

    # a(b) = c(d) (b, d - user inputs)
    def storeUnknownArrValAtUnknownCell(self, arrayCell, indexCell, valArrayCell, valIndexCell):
        self.setRegToUnknownIndex(valArrayCell, valIndexCell, 'A', 'B') # A -> &c(d)
        self.loadToReg('C') # C -> val
        self.setRegToUnknownIndex(arrayCell, indexCell, 'A', 'B') # A -> &a(b)
        self.storeReg('C') # &a(b) -> val

    def readToMem(self, memCell):
        self.code += ['GET B']
        self.setRegValue('A', memCell)
        self.code += ['STORE B']

class machine():
    memIndex = 0
    memory = {}
    variables = {}
    registers = {'A': False, 'B': False, 'C': False, 'D': False, 'E': False, 'F': False, 'G': False, 'H': False}
    
    _out_ = outputCode()

    def __init__(self, parseTree):
        self.parseTree = parseTree
        self.machineCode = ''

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

    #@TODO offset
    def tokenToReg(self, token, reg):
        typeOf = token[0]

        if typeOf == 'value':
            value = int(token[1])
            self._out_.setRegValue(reg, value)

        elif typeOf == 'integer':
            pidentifier = token[1]
            memCell = self.memory[pidentifier]
            self._out_.setRegToMemCell(memCell, reg)
            
        elif typeOf == 'integerArray':
            arrayIdentifier = token[1]
            arrayCell = self.memory[arrayIdentifier]

            arrayIndex = token[2]
            typeOfIndex = arrayIndex[0]
            if typeOfIndex == 'value':
                indexValue = int(token[1])
                self._out_.setRegToMemCell(arrayCell + indexValue, reg)

            elif typeOfIndex == 'integer':
                indexCell = self.memory[arrayIndex[1]]
                self._out_.setRegToUnknownIndex(arrayCell, indexCell, reg, 'H')

    def assign(self, params):
        identifier = params[1]

        typeOfIdentifier = identifier[0]
        pidentifier = identifier[1]

        expression = params[2]
        typeOfExpression = expression[0]
        
        if (typeOfExpression in ['value', 'integer', 'integerArray']) and pidentifier in self.variables:
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
            

    def assign_old(self, params):
        identifier = params[1]
        typeOf = identifier[0]

        if typeOf == 'integer':
            self.assignInt(params)
        elif typeOf == 'integerArray':
            self.assignArray(params)

    def assignInt(self, params):
        identifier = params[1]
        pidentifier = identifier[1]

        expression = params[2]
        typeOf = expression[0]
        if pidentifier in self.variables:
            # Expression is a number
            if typeOf == 'value':
                self._out_.storeValAtCell(self.memory[pidentifier], int(expression[1]))
            # Expression is a variable
            elif typeOf == 'integer':
                identifierValue = expression[1]
                self._out_.storeUnknownValAtCell(self.memory[pidentifier], self.memory[identifierValue])
            # Expression is an array
            elif typeOf == 'integerArray':
                identifierValue = expression[1]
                typeOfIndex = expression[2][0]
                if typeOfIndex == 'value':
                    identifierValueIndex = int(expression[2][1])
                    self._out_.storeUnknownValAtCell(self.memory[pidentifier], self.memory[identifierValue] + identifierValueIndex)
                elif typeOfIndex == 'integer':
                    identifierValueIndex = expression[2][1]
                    self._out_.storeUnknownArrValAtCell(self.memory[pidentifier], self.memory[identifierValue], self.memory[identifierValueIndex])

    def assignArray(self, params):
        identifier = params[1]
        pidentifier = identifier[1]

        identifierIndex = identifier[2]
        typeOfIdentifierIndex = identifierIndex[0]

        expression = params[2]
        typeOfIndex = expression[0]

        if pidentifier in self.variables:
            if typeOfIdentifierIndex == 'value':
                identifierIndex = int(identifierIndex[1])
                # Expression is a number
                if typeOfIndex == 'value':
                    self._out_.storeValAtCell(self.memory[pidentifier] + identifierIndex - self.variables[pidentifier].indexLow,
                     int(expression[1]))
                # Expression is a variable
                elif typeOfIndex == 'integer':
                    pidentifierValue = expression[1]
                    self._out_.storeUnknownValAtCell(self.memory[pidentifier] + identifierIndex - self.variables[pidentifier].indexLow,
                     self.memory[pidentifierValue])
                # Expression is an array
                elif typeOfIndex == 'integerArray':
                    pidentifierValue = expression[1]
                    typeOfValueIndex = expression[2][0]
                    if typeOfValueIndex == 'value':
                        pidentifierIndex = int(expression[2][1])
                        self._out_.storeUnknownValAtCell(self.memory[pidentifier] + identifierIndex - self.variables[pidentifier].indexLow,
                         self.memory[pidentifierValue] + pidentifierIndex)
                    elif typeOfValueIndex == 'integer':
                        pidentifierIndex = expression[2][1]
                        self._out_.storeUnknownArrValAtCell(self.memory[pidentifier] + identifierIndex - self.variables[pidentifier].indexLow,
                         self.memory[pidentifierValue], self.memory[pidentifierIndex])

            if typeOfIdentifierIndex == 'integer':
                pidentifierIdentifierIndex = self.memory[identifierIndex[1]]
                # Expression is a number
                if typeOfIndex == 'value':
                    self._out_.storeValAtUnknownCell(self.memory[pidentifier] - self.variables[pidentifier].indexLow,
                     pidentifierIdentifierIndex, int(expression[1]))
                # Expression is a variable
                elif typeOfIndex == 'integer':
                    pidentifierValue = expression[1]
                    print(pidentifierIdentifierIndex)
                    self._out_.storeUnknownValAtUnknownCell(self.memory[pidentifier]- self.variables[pidentifier].indexLow,
                     pidentifierIdentifierIndex, self.memory[pidentifierValue])
                # Expression is an array
                elif typeOfIndex == 'integerArray':
                    pidentifierValue = expression[1]
                    typeOfValueIndex = expression[2][0]
                    if typeOfValueIndex == 'value':
                        pidentifierIndex = int(expression[2][1])
                        self._out_.storeUnknownValAtUnknownCell(self.memory[pidentifier]- self.variables[pidentifier].indexLow,
                         pidentifierIdentifierIndex, self.memory[pidentifierValue] + pidentifierIndex)
                    elif typeOfValueIndex == 'integer':
                        pidentifierIndex = expression[2][1]
                        self._out_.storeUnknownArrValAtUnknownCell(self.memory[pidentifier]- self.variables[pidentifier].indexLow,
                         pidentifierIdentifierIndex, self.memory[pidentifierValue], self.memory[pidentifierIndex])

    def read(self, params):
        identifier = params[1]

        typeOf = identifier[0]
        pidentifier = identifier[1]
        identifierIndex = identifier[2]

        if pidentifier in self.variables:
            if typeOf == 'integerArray':
                typeOfIndex = identifierIndex[0]
                if typeOfIndex == 'value':
                    identifierIndex = int(identifierIndex[1])
                    self._out_.readToMem(self.memory[pidentifier] + identifierIndex - self.variables[pidentifier].indexLow)
                elif typeOfIndex == 'integer':
                    pass

            elif typeOf == 'integer':
                self._out_.readToMem(self.memory[pidentifier])
                
