from __future__ import print_function
from sys import stdin
import unittest

'''
Description: PAL Parser for PPL
Author: David Faller
'''

class parseFile(object):

    code = []
    starts = []
    ends = []
    start = False
    vars = [[],[]]
    labels = [[],[]]
    define = False

    def __init__(self, fileName):
        self.file = open(fileName)
        self.scanFile(self.file)
        # check for orphaned unmatched lines in VAR and label lists, mark those that aren't already in error list
        #self.outputErrorFile(self.code)


    # scan file, remove comments, ignore blanks, remove leading whitespace
    def scanFile(self, file):
        for lineNum, line in enumerate(file):
            line = self.removeComment(line)
            line = line.lstrip().rstrip()
            if len(line.strip()) != 0:
                self.parseLine(lineNum, line.strip("\n"))


    # scan line for start/end, labels,
    def parseLine(self, lineNum, line):
        commandUnknown = self.commandCheck(lineNum, line)
        if commandUnknown != None:
            self.code.append([lineNum + 1, line, commandUnknown])
        else:
            startEndError = self.startEnd(lineNum, line)
            if startEndError != None:
                self.code.append([lineNum + 1, line, startEndError])
            else:
                labelError = self.labelBranchCheck(lineNum, line)
                if labelError != None:
                    self.code.append([lineNum + 1, line, labelError])
                else:
                    operationError = self.operationCheck(lineNum, line)
                    if operationError != None:
                        self.code.append([lineNum + 1, line, operationError])
                    else:
                        self.code.append([lineNum + 1, line, ''])


    # checks arithmetic operations
    def operationCheck(self, lineNum, line):
        if ':' in line:
            line = line.split(':', 1)[-1].lstrip()
        if ('MOVE' in line[0:4]):
            line = line[4:].lstrip()
            args = self.get2args(line)
            return

        if ('COPY' in line[0:4]):
            line = line[4:].lstrip()
            args = self.get2args(line)
            return

        if ('ADD' in line[0:3]) or \
                ('SUB' in line[0:3]) or \
                ('MUL' in line[0:3]) or \
                ('DIV' in line[0:3]):
            line = line[3:].lstrip()
            args = self.get3args(line)
            print ("math args:", args)
            return

        if ('INC' in line[0:3]) or \
                ('DEC' in line[0:3]):
            line = line[3:].lstrip()
            if self.isRegister(line) is True:
                return
            else:
                return self.validateLabel(line)





    # finds labels, returns errors
    def labelBranchCheck(self, lineNum, line):
        if ':' in line:
            noLabel = line.split(':', 1)[-1].lstrip()
            if self.branchFind(noLabel):
                branchError = self.checkBranch(noLabel, lineNum)
                if branchError is not None:
                    return branchError
            label = line.split(':', 1)[0]
            labelValidated = self.validateLabel(label)
            if labelValidated is not None:
                return labelValidated
            if self.findLabels("branchFrom", label):
                return "Ambiguous label: \'{0}\' in use multiple times".format(label)
            else:
                self.labels[1].append([label, lineNum + 1])
                return

        if self.branchFind(line):
            return self.checkBranch(line, lineNum)

        if ('DEF' in line[0:3]):
            if self.define is False:
                return "DEF commands must follow SRT or DEF"
            noDEF = line[4:]
            varName = noDEF.split(',', 1)[0]
            varValidated = self.validateLabel(varName)
            if varValidated is not None:
                return  varValidated
            if not self.findVars('defined', varName):
                self.vars[0].append([varName, lineNum + 1])
            else:
                return "Var name already defined in namespace: \'{0}\'".format(varName)
            varLoc = noDEF.split(',', 1)[-1].lstrip()
            if self.validateLoc(varLoc):
                return "{0}: \'{1}\'".format(self.validateLoc(varLoc), varLoc)
            return


    # tests checks branch statement for valid labels and args
    def checkBranch(self, line, lineNum):
        label = self.getBranchLabel(line)
        labelValidated = self.validateLabel(label)
        if labelValidated is not None:
            return  labelValidated
        if not self.findLabels("branchTo", label):
            self.labels[0].append([label, lineNum + 1])
        return self.checkBranchArgs(line, lineNum)


    # returns label from branch line
    def checkBranchArgs(self, line, lineNum):
        if ('BEQ' in line[0:3]) or ('BGT' in line[0:3]):
            args = self.get2args(line[3:].lstrip().rsplit(',', 1)[0])
            return self.validateBranchArgs(args[0], args[1])
        return


    # get 2 args from string
    def get2args(self, string):
        arg1 = string.rsplit(',', 1)[0].lstrip()
        arg2 = string.split(',', 1)[-1].lstrip()
        return [arg1, arg2]


    # get 3 args from string
    def get3args(self, string):
        arg1 = string.split(',', 1)[0]
        arg23 = self.get2args(string.split(',', 1)[-1].lstrip())
        return [arg1, arg23[0], arg23[1]]


    # checks branch statement args for validity
    def validateBranchArgs(self, arg1, arg2):
        if self.isRegister(arg1):
            if self.isRegister(arg2):
                return
            else:
                return self.validateLabel(arg2)
        else:
            arg1Valid = self.validateLabel(arg1)
            if arg1Valid is None:
                if self.isRegister(arg2):
                    return
                else:
                    return self.validateLabel(arg2)
            else:
                return arg1Valid


    # searches given var list for matches
    def findVars(self, type, label):
        if type == 'defined':
            if self.vars[0]:
                for entry in self.vars[0]:
                    if label in entry:
                        return True
                return False
            else:
                return False

        if type == 'inUse':
            if self.vars[1]:
                for entry in self.vars[1]:
                    if label in entry:
                        return True
                return False
            else:
                return False


    # searches given label list for matches
    def findLabels(self, type, label):
        if type == 'branchTo':
            if self.labels[0]:
                for entry in self.labels[0]:
                    if label in entry:
                        return True
                return False
            else:
                return False

        if type == 'branchFrom':
            if self.labels[1]:
                for entry in self.labels[1]:
                    if label in entry:
                        return True
                return False
            else:
                return False


    # finds branches in lines
    def branchFind(self, line):
        if ('BEQ' in line[0:3]) or ('BR' in line[0:2]) or ('BGT' in line[0:3]):
            return True
        else:
            return False


    # validates labels
    def validateLabel(self, label):
        if len(label) > 5 or len(label) < 1:
            return "Variable or Label name length invalid: \'{0}\'".format(label)
        for char in label:
            if self.isLetter(char) is False:
                return "Variable or Label names must be letters only: \'{0}\'".format(label)


    # validates memory locations
    def validateLoc(self, loc):
        if len(loc) < 1:
            return "Memory location length invalid"
        for char in loc:
            if self.isOctalDigit(char) is False:
                return "Memory locations must be octal digits only"


    # returns label from branch line
    def getBranchLabel(self, line):
        if ('BEQ' in line[0:3]) or ('BGT' in line[0:3]):
            label = line.rsplit(',', 1)[-1].lstrip()
        if ('BR' in line[0:2]):
            label = line[2:]
            label = label.lstrip()
        return label


    # find starts and ends, return errors
    def startEnd(self, lineNum, line):
        if ('SRT' in line[0:3]):
            self.starts.append(lineNum)
            if "SRT" == line.replace(' ', ''):
                if self.start == False:
                    self.start = True
                    return None
                else:
                    self.start = True
                    ind = self.starts.index(lineNum)
                    return 'Program already has SRT at line {0}'.format(self.starts[ind - 1] + 1)
            else:
                self.start = True
                ind = self.starts.index(lineNum)
                return 'SRT stmt at line {0} has extra characters'.format(self.starts[ind] + 1)

        if ("END" in line) and ('BEQ' not in line) and ('BR' not in line) and ('BGT' not in line) and ('DEF' not in line):
            self.ends.append(lineNum)
            if 'END' == line.split(':', 1)[-1].lstrip().replace(' ', ''):
                if self.start is True:
                    self.start = False
                else:
                    self.start = False
                    return 'END at line {0} does not have matching SRT'.format(lineNum + 1)
            else:
                self.start = False
                return 'END stmt at line {0} has extra characters'.format(lineNum + 1)


    # remove anything after ';'
    def removeComment(self, line):
        if ';' in line:
            noComment = line.split(';', 1)[0]
            return noComment
        else:
            return line

    # finds letters without regex
    def isLetter(self, char):
        if char == 'A' or \
                char == 'B' or \
                char == 'C' or \
                char == 'C' or \
                char == 'D' or \
                char == 'E' or \
                char == 'F' or \
                char == 'G' or \
                char == 'H' or \
                char == 'I' or \
                char == 'J' or \
                char == 'K' or \
                char == 'L' or \
                char == 'M' or \
                char == 'N' or \
                char == 'O' or \
                char == 'P' or \
                char == 'Q' or \
                char == 'R' or \
                char == 'S' or \
                char == 'T' or \
                char == 'U' or \
                char == 'V' or \
                char == 'W' or \
                char == 'X' or \
                char == 'Y' or \
                char == 'Z':
            return True
        else:
            return False

        # finds octal digits without regex
    def isOctalDigit(self, char):
        if char == '0' or \
                char == '1' or \
                char == '2' or \
                char == '3' or \
                char == '4' or \
                char == '5' or \
                char == '6' or \
                char == '7':
            return True
        else:
            return False

    # checks register validity
    def isRegister(self, string):
        if string == 'R0' or \
                string == 'R1' or \
                string == 'R2' or \
                string == 'R3' or \
                string == 'R4' or \
                string == 'R5' or \
                string == 'R6' or \
                string == 'R7':
            return True
        else:
            return False

    # finds labels, returns errors
    def commandCheck(self, lineNum, line):
        noLabel = line.split(':', 1)[-1].lstrip()
        if noLabel.replace(' ', '') == '':
            return "Label must be followed by a command"
        if ('DEF' in noLabel[0:3]) or \
                ('MOVE' in noLabel[0:4]) or \
                ('COPY' in noLabel[0:4]) or \
                ('SRT' in noLabel[0:3]) or \
                ('ADD' in noLabel[0:3]) or \
                ('INC' in noLabel[0:3]) or \
                ('SUB' in noLabel[0:3]) or \
                ('DEC' in noLabel[0:3]) or \
                ('MUL' in noLabel[0:3]) or \
                ('DIV' in noLabel[0:3]) or \
                ('BEQ' in noLabel[0:3]) or \
                ('BGT' in noLabel[0:3]) or \
                ('BR' in noLabel[0:2]) or \
                ('END' in noLabel[0:3]):
            if ('SRT' in noLabel[0:3]):
                self.define = True
            elif ('DEF' not in noLabel[0:3]):
                self.define = False
            return
        else:
            return "Command unknown"


if '__main__' == __name__:
    fileName = "palprogs"
    fileName +=".pal"
    programs = parseFile(fileName)

    #for entry in programs.vars:
       # print("var",entry)

    for line in programs.code:
        print(str(line[0]).ljust(3), line[1].ljust(25), line[2])