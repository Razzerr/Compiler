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
    
    def clearRegister(self, register):
        self.code += ["SUB " + register + " " + register]

    def setValue(self, register, value):
        self.clearRegister(register)
        while value > 0:
            self.code += ["INC " + register]
            value -= 1
    
    def storeNum(self, memCell, value):
        self.setValue('A', memCell)
        self.setValue('B', value)
        self.code += ['STORE B']

    def storeNumFromMem(self, memCell, memCellFrom):
        self.setValue('A', memCellFrom)
        self.code += ['LOAD B']
        self.setValue('A', memCell)
        self.code += ['STORE B']

    def read(self, memCell):
        self.code += ['GET B']
        self.setValue('A', memCell)
        self.code += ['STORE B']
        

    def loadFromMemToReg(self, reg, memCell):
        self.setValue('A', memCell)
        self.code += ['GET ' + reg]



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
                #Storing number to a known memory cell
                self._out_.storeNum(self.memory[pidentifier], expressionValue)
            else:
                #Storing number to an unknown memory cell (user input)
                self._out_.storeNumFromMem(self.memory[pidentifier], self.getExpressionAddress(expression))

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
                
