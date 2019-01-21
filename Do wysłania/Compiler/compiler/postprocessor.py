class postprocessor():
    def __init__(self, machineCode):
        self.code = machineCode
        self.commentsCleanup()
        self.labelAssigner()


    def commentsCleanup(self):
        for i in self.code:
            if i[0] == '#':                 
                self.code.remove(i)

    def labelAssigner(self):
        index = 0
        labels = {}

        while index < len(self.code):
            line = self.code[index]
            if line[0:5] == 'label':
                labels[line[:-1]] = index
                self.code.remove(line)
            else:
                index += 1
        
        index = 0
        for i in self.code:
            if 'label' in i:
                label = i[i.index("label"):]
                self.code[index] = i.replace(label, str(labels[label])).strip()
            index += 1