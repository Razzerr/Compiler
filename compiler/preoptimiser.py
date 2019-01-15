import sys

class optimiserMachine():
    memIndex = 0
    memory = []
    variables = {}

    def __init__(self, parseTree):
        self.parseTree = parseTree
        self._error_ = errors()
        # Declarations
        if parseTree[1] != None:
            for i in parseTree[1]:
                typeOf = i[0]
                pidentifier = i[1]
                
                if typeOf == 'integer':
                    lineNo = i[2]
                    self.declareInt(pidentifier, lineNo)
                elif typeOf == 'integerArray':
                    lineNo = i[3]
                    indexLow = int(i[2][0][1])
                    indexHigh = int(i[2][1][1])
                    self.declareArray(pidentifier, indexLow, indexHigh, lineNo)
                
        

        #Program commands
        self.commands(parseTree[2])

    def declareInt(self, pidentifier, lineNo):
        self.variables[pidentifier] = self.memIndex
        self.memory += None
        self.memIndex += 1

    def declareArray(self, pidentifier, indexLow, indexHigh, lineNo):
        self.variables[pidentifier] = self.memIndex
        self.memory += [None] * (indexHigh - indexLow + 1 + 1)
        self.memIndex += indexHigh - indexLow + 1 + 1 # + place for offset

    def undeclareInt(self, pidentifier):
        self.memory[self.variables[pidentifier]] = None
        self.variables.__delitem__(pidentifier)

    def commands(self, array):
        for i in array:
            self.commandHandler(i)

    def commandHandler(self, params):
        return getattr(self, params[0])(params)

    #@TODO offset
    def tokenToVal(self, token):
        typeOf = token[0]
        if typeOf == 'value':
            value = int(token[1])
            return value

        elif typeOf == 'integer':
            pidentifier = token[1]
            return self.memory[self.variables[pidentifier]]
            
        elif typeOf == 'integerArray':
            arrayIdentifier = token[1]
            arrayIndex = token[2]
            typeOfIndex = arrayIndex[0]

            if typeOfIndex == 'value':
                index = int(arrayIndex[1])
                indexLow = int(self.variables[arrayIdentifier].indexLow)
                return self.memory[self.variables[arrayIdentifier] + index - indexLow + 1]

            elif typeOfIndex == 'integer':
                pidentifier = arrayIndex[1]
                indexLow = int(self.variables[arrayIdentifier].indexLow)
                index = int(self.memory[self.variables[pidentifier]])
                if index == -1:
                    return -1
                else:
                    return self.memory[self.variables[arrayIdentifier] + index - indexLow +1]
                    
        
        elif typeOf == 'add':
            val1 = self.tokenToReg(token[1])
            val2 = self.tokenToReg(token[2])
            if val1 == -1 or val2 == -1:
                return -1
            else:
                return val1+val2

        elif typeOf == 'sub':
            val1 = self.tokenToReg(token[1])
            val2 = self.tokenToReg(token[2])
            if val1 == -1 or val2 == -1:
                return -1
            else:
                return val1-val2

        elif typeOf == 'mul':
            val1 = self.tokenToReg(token[1])
            val2 = self.tokenToReg(token[2])
            if val1 == -1 or val2 == -1:
                return -1
            else:
                return val1*val2

        elif typeOf == 'div':
            val1 = self.tokenToReg(token[1])
            val2 = self.tokenToReg(token[2])
            if val1 == -1 or val2 == -1:
                return -1
            else:
                return val1/val2

        elif typeOf == 'mod':
            val1 = self.tokenToReg(token[1])
            val2 = self.tokenToReg(token[2])
            if val1 == -1 or val2 == -1:
                return -1
            else:
                return val1%val2

    def condToReg(self, token):
        value1 = token[1]
        value2 = token[2]

        self.tokenToReg(value1)
        self.tokenToReg(value2)

    def ifThen(self, params):
        condition = params[1]
        commands = params[2]

        self.condToReg(condition)
        self.commands(commands)
    
    def ifThenElse(self, params):
        condition = params[1]
        commands1 = params[2]
        commands2 = params[3]

        self.condToReg(condition)
        self.commands(commands1)
        self.commands(commands2)

    def whileDo(self, params):
        condition = params[1]
        commands = params[2]

        self.condToReg(condition)
        self.commands(commands)

    def doWhile(self, params):
        condition = params[2]
        commands = params[1]

        self.commands(commands)
        self.condToReg(condition)

    def forTo(self, params):
        valueFrom = params[1]
        valueTo = params[2]

        pidentifierFrom = valueFrom[1][1]
        pidentifierTo = valueTo[1][1]

        commands = params[3]

        self.declareInt(pidentifierFrom, valueFrom[3])
        self.declareInt(pidentifierTo, valueTo[3])
        self.assign(valueFrom)
        self.assign(valueTo)

        self.commands(commands)

        self.undeclareInt(pidentifierFrom)
        self.undeclareInt(pidentifierTo)

    def forDownTo(self, params):
        valueFrom = params[1]
        valueTo = params[2]

        pidentifierFrom = valueFrom[1][1]
        pidentifierTo = valueTo[1][1]

        commands = params[3]

        self.declareInt(pidentifierFrom, valueFrom[3])
        self.declareInt(pidentifierTo, valueTo[3])
        self.assign(valueFrom)
        self.assign(valueTo)

        self.commands(commands)

        self.undeclareInt(pidentifierFrom)
        self.undeclareInt(pidentifierTo)

    def assign(self, params):
        lineNo = params[3]
        identifier = params[1]

        typeOfIdentifier = identifier[0]
        pidentifier = identifier[1]

        expression = params[2]

        wart = self.tokenToVal(expression)

        elif typeOfIdentifier == 'integer':   
            self.memory[self.variables[pidentifier]] = wart
            
        elif typeOfIdentifier == 'integerArray':
            index = identifier[2]
            indexType = index[0]

            elif indexType == 'value':
                indexValue = int(index[1])
                indexLow = int(self.variables[pidentifier].indexLow)
                indexHigh = int(self.variables[pidentifier].indexHigh)

                self.memory[self.variables[pidentifier] + indexValue - indexLow + 1] = wart

            elif indexType == 'integer':
                indexIdentifier = index[1]
                indexLow = int(self.variables[pidentifier].indexLow)
                indexHigh = int(self.variables[pidentifier].indexHigh)

                index = int(self.memory[self.variables[indexIdentifier]])
                if index == -1:
                    for i in range(indexLow, indexHigh+1):
                        self.memory[self.variables[arrayIdentifier] + i - indexLow + 1] = -1
                else:
                    self.memory[self.variables[arrayIdentifier] + index - indexLow + 1] = wart

    def read(self, params):
        lineNo = params[2]
        identifier = params[1]

        typeOfIdentifier = identifier[0]
        pidentifier = identifier[1]
        identifierIndex = identifier[2]

        
        if pidentifier not in self.variables:
            self._error_.undeclaredVariable(pidentifier, lineNo)   

        elif typeOfIdentifier == 'integerArray':
            typeOfIndex = identifierIndex[0]

            if self.variables[pidentifier].typeOf != 'integerArray':
                self._error_.wrongTypeReference(pidentifier, 'integerArray', self.variables[pidentifier].typeOf, lineNo)

            elif typeOfIndex == 'value':
                indexValue = int(identifierIndex[1])
                indexLow = self.variables[pidentifier].indexLow
                indexHigh = self.variables[pidentifier].indexHigh
                
                if indexValue > indexHigh or indexValue < indexLow:
                    self._error_.outOfBounds(pidentifier, indexValue, lineNo)
                
            elif typeOfIndex == 'integer':
                indexID = identifierIndex[1]

                if indexID not in self.variables:
                    self._error_.undeclaredVariable(indexID, lineNo)

                else:
                    if not self.variables[indexID].initialized:
                        self._error_.uninitializedVariable(indexID, lineNo)

                    if self.variables[indexID].typeOf != 'integer':
                        self._error_.wrongTypeReference(indexID, 'integer', self.variables[indexID].typeOf, lineNo)

        elif typeOfIdentifier == 'integer':
            if self.variables[pidentifier].typeOf != 'integer':
                self._error_.wrongTypeReference(pidentifier, 'integer', self.variables[pidentifier].typeOf, lineNo)

            else:
                if self.variables[pidentifier].forFor:
                    self._error_.tryingToOverwriteIterator(pidentifier, lineNo)
                else:
                    self.variables[pidentifier].initialized = True

    def write(self, params):
        identifier = params[1]

        typeOfIdentifier = identifier[0]

        if typeOfIdentifier == 'integerArray':
            pidentifier = identifier[1]
            identifierIndex = identifier[2]
            typeOfIndex = identifierIndex[0]
            
            lineNo = params[2]

            if pidentifier not in self.variables:
                self._error_.undeclaredVariable(pidentifier, lineNo)

            elif self.variables[pidentifier].typeOf != 'integerArray':
                self._error_.wrongTypeReference(pidentifier, 'integerArray', self.variables[pidentifier].typeOf, lineNo)

            elif typeOfIndex == 'value':
                indexValue = int(identifierIndex[1])
                indexLow = self.variables[pidentifier].indexLow
                indexHigh = self.variables[pidentifier].indexHigh

                if indexValue > indexHigh or indexValue < indexLow:
                    self._error_.outOfBounds(pidentifier, indexValue, lineNo)

            elif typeOfIndex == 'integer':
                indexID = identifierIndex[1]
                
                if indexID not in self.variables:
                    self._error_.undeclaredVariable(indexID, lineNo)

                else:
                    if not self.variables[indexID].initialized:
                        self._error_.uninitializedVariable(indexID, lineNo)

                    if self.variables[indexID].typeOf != 'integer':
                        self._error_.wrongTypeReference(indexID, 'integer', self.variables[indexID].typeOf, lineNo)

        elif typeOfIdentifier == 'integer':
            pidentifier = identifier[1]
            lineNo = params[2]
            
            if pidentifier not in self.variables:
                self._error_.undeclaredVariable(pidentifier, lineNo)
            else:
                if not self.variables[pidentifier].initialized:
                    self._error_.uninitializedVariable(pidentifier, lineNo)

                if self.variables[pidentifier].typeOf != 'integer':
                    self._error_.wrongTypeReference(pidentifier, 'integer', self.variables[pidentifier].typeOf, lineNo)

        elif typeOfIdentifier == 'value':
            value = int(identifier[1])
