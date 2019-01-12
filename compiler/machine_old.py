import sys

class memoryBlock():
    def __init__(self, cell, pidentifier):
        self.cell = cell
        self.pidentifier = pidentifier

class valueType():
    def __init__(self, line, value = None):
        self.line = line
        self.value = value

class arrayType():
    def __init__(self, indexLow, indexHigh, line):
        self.indexLow = indexLow
        self.indexHigh = indexHigh
        self.line = line
        self.value = {}

        for i in range(indexLow, indexHigh+1):
            self.value[i] = None

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

    def setRegToUnknownIndex(self, arrayCell, indexCell, regTo, regTemp):
        self.setRegValue('A', indexCell)
        self.loadToReg(regTemp)
        self.setRegValue(regTo, arrayCell)
        self.addToRegFromReg(regTo, regTemp)
  
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
                line = int(i[2])
                self.variables[pidentifier] = valueType(int(i[2]))

                self.memory[pidentifier] = self.memIndex
                self.memIndex += 1
            else:
                line = int(i[3])
                indexLow = self.commandHandler(i[2][0])
                indexHigh = self.commandHandler(i[2][1])
                self.variables[pidentifier] = arrayType(indexLow, indexHigh, line)
                self.memory[pidentifier] = self.memIndex
                self.memIndex += indexHigh - indexLow + 1
        #Program commands
        for i in parseTree[2]:
            self.commandHandler(i)


        self._out_.code += ['HALT']
        #Print variables
        for var in self.variables:
            print(var, self.variables[var].value)

        for line in self._out_.code:
            print(line)

    def commandHandler(self, params):
        return getattr(self, params[0])(params)

    def integer(self, params):
        return int(self.variables[params[1]].value)

    def value(self, params):
        return int(params[1])

    def integerArray(self, params):
        pidentifier = params[1]
        pidentifierIndex = params[2]

        arrayIndex = self.commandHandler(pidentifierIndex)
        val = self.variables[pidentifier].value[arrayIndex]
        return int(val) if val != None else val 

    def getExpressionAddress(self, params):
        pidentifier = params[1]
        typeOf = params[0]
        print(params)
        if typeOf == 'integer':
            return self.memory[pidentifier]
        else:
            # secondaryExpression = 
            return self.memory[pidentifier]

    def assignInt(self, params):
        identifier = params[1]
        pidentifier = identifier[1]

        expression = params[2]
        expressionValue = self.commandHandler(expression)

        if pidentifier in self.variables:
            #Value of PIDENTIFIER set to expression value (-1 if unknown - user input)
            self.variables[pidentifier].value = (expressionValue if expressionValue != -1 else -1)
            if (expressionValue != -1):
                #Storing number from a known memory cell
                self._out_.storeValAtCell(self.memory[pidentifier], expressionValue)
            else:
                typeOfValue = expression[0]
                pidentifierValue = expression[1]
                if typeOf == 'integer':
                    #Storing number from an unknown memory cell (user input)
                    self._out_.storeUnknownValAtCell(self.memory[pidentifier], self.memory[pidentifierValue])
                elif typeOf == 'integerArray':
                    pidentifierIndex = expression[2][1]
                    self._out_.storeUnknownArrValAtCell(self.memory[pidentifier], self.memory[pidentifierValue], self.memory[pidentifierValueIndex])

    def assignArray(self, params):
        identifier = params[1]
        pidentifier = identifier[1]

        expression = params[2]
        expressionValue = self.commandHandler(expression)

        if pidentifier in self.variables:
            arrIndex = identifier[2]
            arrIndexVal = self.commandHandler(arrIndex)
            #If index not out of bounds
            if arrIndexVal in self.variables[pidentifier].value:
                #Value of PIDENTIFIER[arrIndexVal] set to expression value (-1 if unknown - user input)
                self.variables[pidentifier].value[arrIndexVal] = (expressionValue if expressionValue != -1 else -1)
                if (expressionValue != -1):
                    #Storing number to a known memory cell
                    self._out_.storeNum(self.memory[pidentifier] + arrIndexVal, expressionValue)
                else:
                    #Storing number to an unknown memory cell (user input)
                    self._out_.storeNumFromMem(self.memory[pidentifier], self.getExpressionAddress(expression))
            #Index depends on user input
            elif arrIndexVal == -1:
                arrIndexName = arrIndex[1]
                self._out_.loadFromMemToReg('B', self.memory[arrIndexName])
                self.variables[pidentifier].value[arrIndexVal] = (expressionValue if expressionValue != -1 else -1)
                if (expressionValue != -1):
                    #Storing number to a known memory cell
                    self._out_.storeNum(self.memory[pidentifier] + arrIndexVal, expressionValue)
                else:
                    #Storing number to an unknown memory cell (user input)
                    self._out_.storeNumFromMem(self.memory[pidentifier], self.getExpressionAddress(expression))


                pass
            #Index out of bounds
            else:
                print("Index out of bounds!", file=sys.stderr)

    def assign(self, params):
        identifier = params[1]
        typeOf = identifier[0]

        if typeOf == 'integer':
            self.assignInt(params)
        elif typeOf == 'integerArray':
            self.assignArray(params)


    
    def assign_old(self, params):
        identifier = params[1]
        expression = params[2]

        typeOf = identifier[0]
        pidentifier = identifier[1]

        expressionValue = self.commandHandler(expression)

        if pidentifier in self.variables:
            #If array
            if typeOf == 'integerArray':
                arrIndex = self.commandHandler(identifier[2])
                #If index not out of bounds
                if arrIndex in self.variables[pidentifier].value:
                    #Value of PIDENTIFIER[arrIndex] set to expression value (-1 if unknown - user input)
                    self.variables[pidentifier].value[arrIndex] = (expressionValue if expressionValue != -1 else -1)
                    if (expressionValue != -1):
                        #Storing number to a known memory cell
                        self._out_.storeNum(self.memory[pidentifier] + arrIndex, expressionValue)
                    else:
                        #Storing number to an unknown memory cell (user input)
                        self._out_.storeNumFromMem(self.memory[pidentifier], self.getExpressionAddress(expression))
                #Index out of bounds
                else:
                    print("Index out of bounds!", file=sys.stderr)
            #If integer
            else:
                #Value of PIDENTIFIER set to expression value (-1 if unknown - user input)
                self.variables[pidentifier].value = (expressionValue if expressionValue != -1 else -1)
                if (expressionValue != -1):
                    #Storing number to a known memory cell
                    self._out_.storeNum(self.memory[pidentifier], expressionValue)
                else:
                    #Storing number to an unknown memory cell (user input)
                    self._out_.storeNumFromMem(self.memory[pidentifier], self.getExpressionAddress(expression))


    def read(self, params):
        identifier = params[1]
        typeOf = identifier[0]
        pidentifier = identifier[1]

        if pidentifier in self.variables:
            if typeOf == 'integerArray':
                arrIndex = self.commandHandler(identifier[2])

                if arrIndex in self.variables[pidentifier].value:
                    self.variables[pidentifier].value[arrIndex] = -1
                else:
                    print("Index out of bounds!", file=sys.stderr)                    
            else:
                self.variables[pidentifier].value = -1
                self._out_.read(self.memory[pidentifier])
                
