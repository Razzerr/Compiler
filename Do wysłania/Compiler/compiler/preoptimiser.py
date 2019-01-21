import sys
import copy

class optimiserMachine():
    memIndex = 0
    memory = []
    variables = {}
    arrayRanges = {}

    def __init__(self, parseTree):
        self.parseTree = parseTree
        self.loopFlag = False
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
        self.memory += [None]
        self.memIndex += 1

    def declareArray(self, pidentifier, indexLow, indexHigh, lineNo):
        self.variables[pidentifier] = self.memIndex
        self.memory += [None] * (indexHigh - indexLow + 1 + 1)
        self.memIndex += indexHigh - indexLow + 1 + 1 # + place for offset
        self.arrayRanges[pidentifier] = (indexLow, indexHigh)

    def undeclareInt(self, pidentifier):
        self.memory[self.variables[pidentifier]] = None
        self.variables.__delitem__(pidentifier)

    def commands(self, array):
        i = 0
        while i < len(array):
            res = self.commandHandler(array[i])
            if res != []:
                if type(res) == type([]):
                    del array[i]
                    for x in res[::-1]:
                        array.insert(i, x)
                    i += 1 * (len(res) - 1)
                else:
                    array[i] = res
            else:
                del array[i]
                i-=1
            i += 1
        return array

    def commandHandler(self, params):
        res = getattr(self, params[0])(params)
        return res

    #@TODO offset
    def tokenToVal(self, token):
        typeOf = token[0]
        if self.loopFlag:
            return (-1, token)
        if typeOf == 'value':
            if (int(token[1]) > 10000000000000000000000000):
                raise Exception("Overload for instant compiling")
            return (int(token[1]), token)

        elif typeOf == 'integer':
            pidentifier = token[1]
            if self.memory[self.variables[pidentifier]] != -1:
                if (int(self.memory[self.variables[pidentifier]]) > 10000000000000000000000000):
                    raise Exception("Overload for instant compiling")
                return (self.memory[self.variables[pidentifier]], ('value', self.memory[self.variables[pidentifier]]))
            else:
                return (-1, token)
            
        elif typeOf == 'integerArray':
            arrayIdentifier = token[1]
            arrayIndex = token[2]
            typeOfIndex = arrayIndex[0]

            if typeOfIndex == 'value':
                index = int(arrayIndex[1])
                indexLow = int(self.arrayRanges[arrayIdentifier][0])
                if self.memory[self.variables[arrayIdentifier] + index - indexLow + 1] != -1:
                    return (self.memory[self.variables[arrayIdentifier] + index - indexLow + 1], ('value', self.memory[self.variables[arrayIdentifier] + index - indexLow + 1]))
                else:
                    return (-1, token)
            elif typeOfIndex == 'integer':
                pidentifier = arrayIndex[1]
                indexLow = int(self.arrayRanges[arrayIdentifier][0])
                index = int(self.memory[self.variables[pidentifier]])
                if index == -1:
                    return (-1, token)
                else:
                    if self.memory[self.variables[arrayIdentifier] + index - indexLow +1] != -1:
                        return (self.memory[self.variables[arrayIdentifier] + index - indexLow +1], ('value', self.memory[self.variables[arrayIdentifier] + index - indexLow +1]))
                    else:
                        return (-1, ('integerArray', arrayIdentifier, ('value', index)))
        
        elif typeOf == 'add':
            val1tok = self.tokenToVal(token[1])
            val2tok = self.tokenToVal(token[2])
            val1 = val1tok[0]
            val2 = val2tok[0]
            if val1 == -1 or val2 == -1:
                return (-1, ('add', val1tok[1], val2tok[1]))
            elif self.loopFlag:
                return (-1, token)
            else:
                return (val1+val2, ('value', val1+val2))

        elif typeOf == 'sub':
            if token[1] == token[2]:
                return (0, ('value', 0))
            val1tok = self.tokenToVal(token[1])
            val2tok = self.tokenToVal(token[2])
            val1 = val1tok[0]
            val2 = val2tok[0]
            if val1 == -1 or val2 == -1:
                return (-1, ('sub', val1tok[1], val2tok[1]))
            elif self.loopFlag:
                return (-1, token)
            else:
                return (val1-val2, ('value', val1-val2))

        elif typeOf == 'mul':
            val1tok = self.tokenToVal(token[1])
            val2tok = self.tokenToVal(token[2])
            val1 = val1tok[0]
            val2 = val2tok[0]
            if val1 == -1 or val2 == -1:
                return (-1, ('mul', val1tok[1], val2tok[1]))
            elif self.loopFlag:
                return (-1, token)
            else:
                return (val1*val2, ('value', val1*val2))

        elif typeOf == 'div':
            if token[1] == token[2]:
                return (1, ('value', 1))
            val1tok = self.tokenToVal(token[1])
            val2tok = self.tokenToVal(token[2])
            val1 = val1tok[0]
            val2 = val2tok[0]
            if val1 == -1 or val2 == -1:
                return (-1, ('div', val1tok[1], val2tok[1]))
            elif self.loopFlag:
                return (-1, token)
            else:
                return (val1//val2, ('value', val1//val2))

        elif typeOf == 'mod':
            if token[1] == token[2]:
                return (0, ('value', 0))
            val1tok = self.tokenToVal(token[1])
            val2tok = self.tokenToVal(token[2])
            val1 = val1tok[0]
            val2 = val2tok[0]
            if val1 == -1 or val2 == -1:
                return (-1, ('mod', val1tok[1], val2tok[1]))
            elif self.loopFlag:
                return (-1, token)
            else:
                return (val1%val2, ('value', val1%val2))

    def condToReg(self, token):
        typeOf = token[0]
        value1 = token[1]
        value2 = token[2]

        val1tok = self.tokenToVal(value1)
        val2tok = self.tokenToVal(value2)
        val1 = val1tok[0]
        val2 = val2tok[0]

        if typeOf == 'equal':
            if val1 != -1 and val2 != -1:
                if val1 == val2:
                    return True
                return False
            return -1
        elif typeOf == 'notEqual':
            if val1 != -1 and val2 != -1:
                if val1 != val2:
                    return True
                return False
            return -1
        elif typeOf == 'greaterThan':
            if val1 != -1 and val2 != -1:
                if val1 > val2:
                    return True
                return False
            return -1
        elif typeOf == 'greaterEqual':
            if val1 != -1 and val2 != -1:
                if val1 >= val2:
                    return True
                return False
            return -1
        elif typeOf == 'lesserThan':
            if val1 != -1 and val2 != -1:
                if val1 < val2:
                    return True
                return False
            return -1
        elif typeOf == 'lesserEqual':
            if val1 != -1 and val2 != -1:
                if val1 <= val2:
                    return True
                return False
            return -1

    def ifThen(self, params):
        condition = params[1]
        commands = params[2]

        condRes = self.condToReg(condition)
        if condRes == -1:
            commands = self.commands(commands)
            return ('ifThen', condition, commands)
        elif condRes:
            commands = self.commands(commands)
            params = commands
        else:
            params = []
            pass
        
        return params

    
    def ifThenElse(self, params):
        condition = params[1]
        commands1 = params[2]
        commands2 = params[3]

        condRes = self.condToReg(condition)
        if condRes == -1:
            commands1 = self.commands(commands1)
            commands2 = self.commands(commands2)
            params = ('ifThenElse', condition, commands1, commands2)
        elif condRes:
            commands1 = self.commands(commands1)
            params = commands1
        else:
            commands2 = self.commands(commands2)
            params = commands2
        return params

    def whileDo(self, params):
        condition = params[1]
        commands = params[2]
        commandsCopy = copy.deepcopy(commands)
        condRes = self.condToReg(condition)
        if condRes == -1:
            if not self.loopFlag:
                self.loopFlag = True
                commandsCopy = self.commands(commandsCopy)
                self.loopFlag = False
            else:
                commandsCopy = self.commands(commandsCopy) 
            params = ('whileDo', condition, commands)
        else:
            params = []
            while condRes:
                commandsCopy = copy.deepcopy(commands)
                commandsCopy = self.commands(commandsCopy)
                for i in commandsCopy:
                    params += [i]
                condRes = self.condToReg(condition)

        return params

    def doWhile(self, params):
        condition = params[2]
        commands = params[1]

        commands = self.commands(commands)
        commandsCopy = copy.deepcopy(commands)
        condRes = self.condToReg(condition)
        if condRes == -1:
            if not self.loopFlag:
                self.loopFlag = True
                commandsCopy = self.commands(commandsCopy)
                self.loopFlag = False
            else:
                commandsCopy = self.commands(commandscopy)
            params = ('doWhile', condition, commands)
        else:
            params = [commands]
            while condRes:
                commandsCopy = copy.deepcopy(commands)
                commandsCopy = self.commands(commandsCopy)
                params += [commandsCopy]
                condRes = self.condToReg(condition)
        
        return params

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

        if (self.memory[self.variables[pidentifierFrom]] != -1 and self.memory[self.variables[pidentifierTo]] != -1):
            params = []
            for i in range(self.memory[self.variables[pidentifierFrom]], self.memory[self.variables[pidentifierTo]] + 1):
                commandsCopy  = copy.deepcopy(commands)
                commandsCopy = self.commands(commandsCopy)
                for i in commandsCopy:
                    params += [i]
                self.memory[self.variables[pidentifierFrom]] += 1
        else:
            if not self.loopFlag:
                self.loopFlag = True
                commands = self.commands(commands)
                self.loopFlag = False
            else:
                commands = self.commands(commands)
            params = ('forTo', valueFrom, valueTo, commands)
        
        # self.undeclareInt(pidentifierFrom)
        # self.undeclareInt(pidentifierTo)

        return params    

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


        if (self.memory[self.variables[pidentifierFrom]] != -1 and self.memory[self.variables[pidentifierTo]] != -1):
            params = []
            for i in range(self.memory[self.variables[pidentifierFrom]], self.memory[self.variables[pidentifierTo]]-1, -1):
                commandsCopy  = copy.deepcopy(commands)
                commandsCopy = self.commands(commandsCopy)
                for i in commandsCopy:
                    params += [i]
                self.memory[self.variables[pidentifierFrom]] -= 1
        else:
            if not self.loopFlag:
                self.loopFlag = True
                commands = self.commands(commands)
                self.loopFlag = False
            else:
                commands = self.commands(commands)
            params = ('forDownTo', valueFrom, valueTo, commands)

        # self.undeclareInt(pidentifierFrom)
        # self.undeclareInt(pidentifierTo)
        return params

    def assign(self, params):
        identifier = params[1]

        typeOfIdentifier = identifier[0]
        pidentifier = identifier[1]

        expression = params[2]
        lineNo = params[3]
        expression = self.tokenToVal(expression)
        wart = expression[0]
        expression = expression[1]

        if typeOfIdentifier == 'integer':
            self.memory[self.variables[pidentifier]] = wart
            
        elif typeOfIdentifier == 'integerArray':
            index = identifier[2]
            indexType = index[0]

            if indexType == 'value':
                indexValue = int(index[1])
                indexLow = int(self.arrayRanges[pidentifier][0])
                indexHigh = int(self.arrayRanges[pidentifier][1])

                self.memory[self.variables[pidentifier] + indexValue - indexLow + 1] = wart

            elif indexType == 'integer':
                indexIdentifier = index[1]
                indexLow = int(self.arrayRanges[pidentifier][0])
                indexHigh = int(self.arrayRanges[pidentifier][1])

                if self.loopFlag:
                    index = -1
                else:
                    index = int(self.memory[self.variables[indexIdentifier]])
                if index == -1:
                    arrayLow = self.memory[:self.variables[pidentifier] + 1]
                    arrayHigh = self.memory[self.variables[pidentifier] + indexHigh - indexLow + 2 :]
                    arrayMid = [-1] * (indexHigh - indexLow)
                    self.memory = arrayLow 
                    self.memory += arrayMid
                    self.memory += arrayHigh
                else:
                    identifier = ('integerArray', pidentifier, ('value', index), lineNo)
                    self.memory[self.variables[pidentifier] + index - indexLow + 1] = wart
        
        return ('assign', identifier, expression, lineNo)

    def read(self, params):
        lineNo = params[2]
        identifier = params[1]

        typeOfIdentifier = identifier[0]
        pidentifier = identifier[1]

        if typeOfIdentifier == 'integer':   
            self.memory[self.variables[pidentifier]] = -1

        elif typeOfIdentifier == 'integerArray':
            index = identifier[2]
            indexType = index[0]

            if indexType == 'value':
                indexValue = int(index[1])
                indexLow = int(self.arrayRanges[pidentifier][0])
                indexHigh = int(self.arrayRanges[pidentifier][1])

                self.memory[self.variables[pidentifier] + indexValue - indexLow + 1] = -1

            elif indexType == 'integer':
                indexIdentifier = index[1]
                index = int(self.memory[self.variables[indexIdentifier]])
                indexLow = int(self.arrayRanges[pidentifier][0])
                indexHigh = int(self.arrayRanges[pidentifier][1])
                if index == -1:
                    for i in range(indexLow, indexHigh+1):
                        self.memory[self.variables[pidentifier] + i - indexLow + 1] = -1
                else:
                    identifier = ('integerArray', pidentifier, ('value', index), lineNo)
                    self.memory[self.variables[pidentifier] + index + 1 - indexLow] = -1
                    return ('read', identifier)
        return params

    def write(self, params):
        lineNo = params[2]
        identifier = params[1]
        typeOfIdentifier = identifier[0]
        pidentifier = identifier[1]

        if typeOfIdentifier == 'integer':   
            if self.memory[self.variables[pidentifier]] != -1:
                return ('write', ('value', self.memory[self.variables[pidentifier]]), lineNo)
            
        elif typeOfIdentifier == 'integerArray':
            index = identifier[2]
            indexType = index[0]

            if indexType == 'value':
                indexValue = int(index[1])
                indexLow = int(self.arrayRanges[pidentifier][0])

                if self.memory[self.variables[pidentifier] + indexValue - indexLow + 1] != -1:
                    return ('write', ('value', self.memory[self.variables[pidentifier] + indexValue - indexLow + 1]), lineNo)

            elif indexType == 'integer':
                indexIdentifier = index[1]
                indexLow = int(self.arrayRanges[pidentifier][0])
                indexHigh = int(self.arrayRanges[pidentifier][1])

                index = int(self.memory[self.variables[indexIdentifier]])
                if index != -1:
                    if self.memory[self.variables[pidentifier] + index - indexLow + 1] != -1:
                        return ('write', ('value', self.memory[self.variables[pidentifier] + index - indexLow + 1]), lineNo)
        return params