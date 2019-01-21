import sys

class valueType():
    def __init__(self, lineNo):
        self.typeOf = 'integer'
        self.lineNo = lineNo
        self.initialized = False
        self.forFor = False

class arrayType():
    def __init__(self, indexLow, indexHigh, lineNo):
        self.typeOf = 'integerArray'
        self.indexLow = indexLow
        self.indexHigh = indexHigh
        self.lineNo = lineNo
        self.initialized = False

class errors():
    def __init__(self):
        self.errorOccured = False

    def doubleDeclaration(self, pidentifier, lineNo, lineOrgNo):
        print("[ERROR] Variable of the same name already declared!\n" +
                "\tTrying to declare '" + pidentifier + "' at line " + str(lineNo) + ".\n" +
                "\tExisting variable '" + pidentifier + "' at line " + str(lineOrgNo) + ".")
        self.errorOccured = True

    def wrongIndexing(self, pidentifier, indexLow, indexHigh, lineNo):
        print("[ERROR] Indices of array '" + pidentifier + "' wrongly declared!\n" +
                "\tGiven indices from " + str(indexLow) + " to " + str(indexHigh) + " at line " + str(lineNo) + ".")
        self.errorOccured = True

    def undeclaredVariable(self, pidentifier, lineNo):
        print("[ERROR] Variable not decalred!\n"+
                "\tTrying to access variable '" + pidentifier + "' at line " + str(lineNo) + ".")
        self.errorOccured = True

    def uninitializedVariable(self, pidentifier, lineNo):
        print("[ERROR] Variable not initialized!\n"+
                "\tTrying to get value of variable '" + pidentifier + "' at line " + str(lineNo) + ".")
        self.errorOccured = True

    def outOfBounds(self, arrayIdentifier, index, lineNo):
        print("[ERROR] Index out of bounds!\n"+
                "\tTrying to access index " + str(index) + " of array '" + arrayIdentifier + "' at line " + str(lineNo) + ".")
        self.errorOccured = True

    def wrongTypeReference(self, arrayIdentifier, typeOf, typeOfCorrect, lineNo):
        print("[ERROR] Wrong reference type!\n" + 
                "\tTrying to access '" + arrayIdentifier + "' of type '" + typeOfCorrect + "' as type '" + typeOf + "' at line " + str(lineNo) + ".")
        self.errorOccured = True

    def tryingToOverwriteIterator(self, pidentifier, lineNo):
        print("[ERROR] Trying to overwrite for loop iterator!\n" + 
                "\tTrying to overwrite iterator '" + pidentifier + "' at line " + str(lineNo) + ".")
        self.errorOccured = True

class warnings():
    def noDeclaredVariables():
        print("[HINT] No variables were declared")
    

class errorMachine():
    variables = {}
    
    _warning_ = warnings()

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
                
        else:
            self._warning_.noDeclaredVariables()

        #Program commands
        self.commands(parseTree[2])

    def declareInt(self, pidentifier, lineNo):
        if pidentifier in self.variables:
            self._error_.doubleDeclaration(pidentifier, lineNo, self.variables[pidentifier].lineNo)
        else:
            self.variables[pidentifier] = valueType(lineNo)

    def declareArray(self, pidentifier, indexLow, indexHigh, lineNo):
        if pidentifier in self.variables:
            self._error_.doubleDeclaration(pidentifier, lineNo, self.variables[pidentifier].lineNo)
        elif indexLow > indexHigh:
            self._error_.wrongIndexing(pidentifier, indexLow, indexHigh, lineNo)
        else:
            self.variables[pidentifier] = arrayType(indexLow, indexHigh, lineNo)

    def undeclareInt(self, pidentifier):
        self.variables.__delitem__(pidentifier)

    def commands(self, array):
        for i in array:
            self.commandHandler(i)

    def commandHandler(self, params):
        return getattr(self, params[0])(params)

    #@TODO offset
    def tokenToReg(self, token):
        typeOf = token[0]
        if typeOf == 'value':
            value = int(token[1])

        elif typeOf == 'integer':
            lineNo = token[2]
            pidentifier = token[1]

            if pidentifier not in self.variables:
                self._error_.undeclaredVariable(pidentifier, lineNo)

            else:
                if not self.variables[pidentifier].initialized:
                    self._error_.uninitializedVariable(pidentifier, lineNo)

                if self.variables[pidentifier].typeOf != 'integer':
                    self._error_.wrongTypeReference(pidentifier, 'integer', self.variables[pidentifier].typeOf, lineNo)

            
        elif typeOf == 'integerArray':
            arrayIdentifier = token[1]
            arrayIndex = token[2]
            typeOfIndex = arrayIndex[0]
            lineNo = token[3]

            if arrayIdentifier not in self.variables:
                self._error_.undeclaredVariable(arrayIdentifier, lineNo)

            elif self.variables[arrayIdentifier].typeOf != 'integerArray':
                self._error_.wrongTypeReference(arrayIdentifier, 'integerArray', self.variables[arrayIdentifier].typeOf, lineNo)
            else:
                if typeOfIndex == 'value':
                    index = int(arrayIndex[1])
                    indexLow = int(self.variables[arrayIdentifier].indexLow)
                    indexHigh = int(self.variables[arrayIdentifier].indexHigh)

                    if index > indexHigh or index < indexLow:
                        self._error_.outOfBounds(arrayIdentifier, index, lineNo)

                elif typeOfIndex == 'integer':
                    pidentifier = arrayIndex[1]

                    if pidentifier not in self.variables:
                        self._error_.undeclaredVariable(pidentifier, lineNo)
                    else:
                        if not self.variables[pidentifier].initialized:
                            self._error_.uninitializedVariable(pidentifier, lineNo)

                        if self.variables[pidentifier].typeOf != 'integer':
                            self._error_.wrongTypeReference(pidentifier, 'integer', self.variables[pidentifier].typeOf, lineNo)
        
        elif typeOf == 'add':
            self.tokenToReg(token[1])
            self.tokenToReg(token[2])

        elif typeOf == 'sub':
            self.tokenToReg(token[1])
            self.tokenToReg(token[2])

        elif typeOf == 'mul':
            self.tokenToReg(token[1])
            self.tokenToReg(token[2])

        elif typeOf == 'div':
            self.tokenToReg(token[1])
            self.tokenToReg(token[2])

        elif typeOf == 'mod':
            self.tokenToReg(token[1])
            self.tokenToReg(token[2])

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

        self.tokenToReg(expression)

        if pidentifier not in self.variables:
            self._error_.undeclaredVariable(pidentifier, lineNo)   

        elif typeOfIdentifier == 'integer':   
            if self.variables[pidentifier].typeOf != 'integer':
                self._error_.wrongTypeReference(pidentifier, 'integer', self.variables[pidentifier].typeOf, lineNo)
            else:
                if self.variables[pidentifier].forFor:
                    self._error_.tryingToOverwriteIterator(pidentifier, lineNo)
                else:
                    self.variables[pidentifier].initialized = True

        elif typeOfIdentifier == 'integerArray':
            index = identifier[2]
            indexType = index[0]

            if self.variables[pidentifier].typeOf != 'integerArray':
                self._error_.wrongTypeReference(pidentifier, 'integerArray', self.variables[pidentifier].typeOf, lineNo)

            elif indexType == 'value':
                indexValue = int(index[1])
                indexLow = int(self.variables[pidentifier].indexLow)
                indexHigh = int(self.variables[pidentifier].indexHigh)

                if indexValue > indexHigh or indexValue < indexLow:
                    self._error_.outOfBounds(pidentifier, indexValue, lineNo)

            elif indexType == 'integer':
                indexIdentifier = index[1]

                if indexIdentifier not in self.variables:
                    self._error_.undeclaredVariable(indexIdentifier, lineNo)

                else:
                    if not self.variables[indexIdentifier].initialized:
                        self._error_.uninitializedVariable(indexIdentifier, lineNo)

                    if self.variables[indexIdentifier].typeOf != 'integer':
                        self._error_.wrongTypeReference(indexIdentifier, 'integer', self.variables[indexIdentifier].typeOf, lineNo)

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
