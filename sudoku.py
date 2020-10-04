import time
import random
import numpy as np
import sys
import math
import re

class Field():

    def __init__(self,number=None,editable=True):
        super().__init__()

        self.isSelected = False
        self.editable= editable

        if number is None:
            self.makeEmpty()
        else:
            self.setNumber(number)
    
    def makeEmpty(self):
        if self.editable:
            self.number = -1
            self.label = ' '
        else:
            raise Exception("not editable")

    def setNumber(self,number,editable=True):
        if self.editable:
            self.number = number
            self.label = str(number)
            self.editable = editable
        else:
            raise Exception("not editable")


    def __str__(self):
        return self.label

    def __format__(self, format_spec):
        
        if format_spec == 'number':
            return self.number
        elif format_spec == 'label':
            return self.label
        elif format_spec == "selection":
            if self.isSelected:
                return "<"
            else:
                return ""
        elif format_spec == "mode":
            if not self.editable:
                return "F"
            else:
                return " "

class Sudoku():

    def __init__(self,fieldsInLine=9,showedNumbersAmount=20,seed=None):

        self.fields = []
        self.startTime = time.time()
        self.solution = None
        self.selectedPositon = (0,0)
        self.selectedField = None
        self.showedNumbersAmount = showedNumbersAmount
        self.solved = False

        self.fieldsInLine = fieldsInLine
        self.sectionsInLine = int(math.sqrt(self.fieldsInLine))

        if seed is not None:
            self.seed = seed
        else:
            self.seed = random.randrange(sys.maxsize)
        self.randomGen = random.Random(seed)

        self.autoSolve = True

        #Look
        self.borderLook = "|"

        #commands
        self.goLeftCommand = "A"
        self.goRightCommand ="D"
        self.goUpCommand = "W"
        self.goDownCommand ="S"
        self.gotoCommand = "GOTO"

        self.solveCommand = "SOLVE"
        self.helpCommand = "HELP"
        self.quitCommand = "QUIT"

        self.modeAutoSolveCommad = "AUTO_SOLVE"
        self.autoFillField = "AUTO_FILL"

        self._initFields()

    def _initFields(self):
        self.generateField(self.fieldsInLine,self.seed)

        showedFields =  []

        possIndices = list(range(0,self.fieldsInLine*self.fieldsInLine))
        for x in range(self.showedNumbersAmount):
            showedFields.append(possIndices[self.randomGen.randint(0,len(possIndices)-1)])

        i = 0
        for y in range(self.fieldsInLine):
            line = []
            for x in range(self.fieldsInLine):
                field = Field()
                if i in showedFields:
                    field.setNumber(self.solution[y][x],editable=False)
                else:
                    field.makeEmpty()
                line.append(field)
                i+= 1
            self.fields.append(line)
        
        self.selectField(0,0)

    def getFieldAsString(self):
        out = " "
        for i in self.borderLook:
            out += " "

        for columnNumber,f in enumerate(self.fields[0]):
            if columnNumber %self.sectionsInLine == 0 and columnNumber != 0:
                out+=" "
            out += ' {} '.format(columnNumber)
        out+= " \n"

        for rowNumber,line in enumerate(self.fields):

            if rowNumber %self.sectionsInLine == 0 and rowNumber != 0:
                out += " "+self.borderLook
                for i in range(self.fieldsInLine):
                    out += '---'
                for i in range(self.sectionsInLine-1):
                    out += '-'
                out+= self.borderLook+"\n"
            
            out+= "{}".format(rowNumber)+self.borderLook

            for i,field in enumerate(line):
                if i %self.sectionsInLine == 0 and i != 0:
                    out+="|"
                out += ' {:label}{:selection}{:mode}'.format(field,field,field)
            out+= self.borderLook+"\n"

        return out

    def printField(self):
        print(self.getFieldAsString())

    def validatePosition(self,pos):
        if pos >= len(self.fields):
            return len(self.fields)-1
        elif pos < 0:
            return 0
        return pos

    def selectField(self,posX,posY):
        
        posX = self.validatePosition(posX)
        posY = self.validatePosition(posY)

        if not self.fields[posY][posX].editable:
            return False

        if self.selectedField is not None:
            self.selectedField.isSelected = False
        self.selectedField = self.fields[posY][posX]
        self.selectedPositon = (posX,posY)
        self.selectedField.isSelected = True
        return True

    def selectInDirection(self,direction):
        x,y = self.selectedPositon
        x += direction[0]
        y += direction[1]

        if not self.selectField(x,y) and x < len(self.fields) and y < len(self.fields):
            self.selectInDirection(direction+1)

    def selectLeft(self):
        self.selectInDirection(np.array([-1,0]))

    def selectRight(self):
        self.selectInDirection(np.array([1,0]))

    def selectUp(self):
        self.selectInDirection(np.array([0,-1]))

    def selectDown(self):
        self.selectInDirection(np.array([0,1]))

    def startGameLoop(self):
        lastInput = ''
        self.solved= False

        while(lastInput != self.quitCommand and not self.solved):
            self.printField()

            print("\nseed = {}".format(self.seed))
            print("(F) this Number is not editable [final], (<) this Number is selected")
            print("insert '{}' for a list of all commands, press Enter to confirm a command".format(self.helpCommand))

            lastInput = input().upper()

            if lastInput == self.goUpCommand:
                self.selectUp()
            elif lastInput == self.goDownCommand:
                self.selectDown()
            elif lastInput == self.goLeftCommand:
                self.selectLeft()
            elif lastInput == self.goRightCommand:
                self.selectRight()
            elif lastInput == self.solveCommand:
                if(self.compareWithSolution()):
                    print("\n\nʕᵔᴥᵔʔ YOU HAVE SOLVED THE GAME ʕᵔᴥᵔʔ\n\n")
                    self.solved = True
                else:
                    print("The Solution is wrong, PRESS ANY KEY TO CONTINUE")
                    input()
            elif lastInput == self.helpCommand:
                print("(W,A,S,D) jump to the [Up,Left,Down or Right] Field")
                print("(GOTO) jump to a field by x and y value")
                print("(1-9)[digit number] insert number to selected field")
                print("PRESS ANY KEY TO CONTINUE")
                input()
            elif lastInput == self.gotoCommand:
                print("insert X Value:")
                x  = int(input())
                print("insert Y Value:")
                y = int (input())
                self.selectField(x,y)
            elif lastInput.isdigit() and self.selectedField is not None:
                num = int(lastInput)
                self.selectedField.setNumber(num)
                if self.autoSolve:
                    if self.solution[self.selectedPositon[1],self.selectedPositon[0]] == num:
                        self.selectedField.editable = False

    def compareWithSolution(self):    
        for line,comLine in zip(self.fields,self.solution):
            for field,cf in zip(line,comLine):
                #print(field.number,cf)
                if field.number != cf:
                    return False
        return True

    def generateField(self,fieldsAmount,seed=None):
        self.solution = np.zeros((fieldsAmount,fieldsAmount),dtype=int)
        self.solution = self.generateNumber(0,list(range(1,10)),self.solution)

    def generateNumber(self,i,possNumbers,field):
        if i == np.size(field):
            return field
        if len(possNumbers) == 0:
            return None

        num = possNumbers[self.randomGen.randint(0,len(possNumbers)-1)]
        y = i//9
        x = i %9

        if self.checkNumber(num,x,y,field):
            field[y][x] = num
            nf = self.generateNumber(i+1,list(range(1,10)),field)
            if nf is not None:
                return nf

        possNumbers.remove(num)
        return self.generateNumber(i,possNumbers,field)


    def checkNumber(self,number,x,y,field):
        return self.checkNumbersInHLine(number,x,y,field) and self.checkNumbersInVLine(number,x,y,field) and self.checkNumberInSection(number,x,y,field)
    
    def checkNumbersInHLine(self,number,x,y,field):
        impossibleNumbers = []
        for posX in range(x):
            if number == self.solution[y,posX]:
                return False
        return True

    def checkNumbersInVLine(self,number,x,y,field):
        impossibleNumbers = []
        for posY in range(y):
            if number == self.solution[posY,x] :
                return False
        return True

    def checkNumberInSection(self,number,x,y,field):
        startX = int((x// self.sectionsInLine) * self.sectionsInLine)
        startY = int((y// self.sectionsInLine) * self.sectionsInLine)

        impossibleNumbers = []

        for posY in range(startY,startY+3):
            
            if y < posY:
                return True

            for posX in range(startX,startX+3):

                if y == posY and x < posX:
                    break
                
                if self.solution[posY][posX] == number:
                    return False

        return True




        




if __name__ == "__main__":
    game = Sudoku(seed=1592111697)
    game.startGameLoop()