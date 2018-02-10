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
        # check errors listed in VAR and LABEL lists, apply to lines that aren't already in error.
        #self.outputErrorFile(self.code)


    # scan file, remove comments, ignore blanks, remove leading whitespace
    def scanFile(self, file):
        for lineNum, line in enumerate(file):
            line = self.removeComment(line)
            line = line.lstrip()
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
                self.code.append([lineNum+1, line, startEndError])
            else:
                labelError = self.label(lineNum, line)
                if labelError != None:
                    self.code.append([lineNum + 1, line, labelError])
                else:
                    self.code.append([lineNum + 1, line, ''])


    # finds labels, returns errors
    def commandCheck(self, lineNum, line):
        noLabel = line.split(':', 1)[-1].lstrip()
        if noLabel.replace(' ', '') == '':
            return "Label must be followed by a command"
        if ('DEF' in noLabel[0:3]) or \
                ('MOVE' in noLabel[0:4]) or \
                ('COPY' in noLabel[0:4]) or \
                ('SRT' in noLabel[0:3]) or \
                ('DEF' in noLabel[0:3]) or \
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


    # finds labels, returns errors
    def label(self, lineNum, line):
        if ':' in line:
            noLabel = line.split(':', 1)[-1].lstrip()
            if self.branchFind(noLabel):
                branchLabel = self.sanitizeBranch(noLabel)
                if self.validateLabel(branchLabel) is not None:
                    return "{0}: {1}".format(self.validateLabel(branchLabel), branchLabel)
                if not self.findLabels("branchTo", branchLabel):
                    self.labels[0].append([branchLabel, lineNum+1])
            label = line.split(':', 1)[0]
            if self.validateLabel(label) is not None:
                return "{0}: {1}".format(self.validateLabel(label), label)
            if self.findLabels("branchFrom", label):
                return "Ambiguous label: \'{0}\' in use multiple times".format(label)
            else:
                self.labels[1].append([label, lineNum + 1])
                return

        if self.branchFind(line):
            label = self.sanitizeBranch(line)
            if self.validateLabel(label) is not None:
                return  "{0}: {1}".format(self.validateLabel(label), label)
            if not self.findLabels("branchTo", label):
                self.labels[0].append([label, lineNum + 1])
            return

        if ('DEF' in line[0:3]):
            if self.define == False:
                return "DEF commands must follow SRT or DEF"
            noDEF = line[4:]
            varName = noDEF.split(',', 1)[0]
            if self.validateLabel(varName) is not None:
                return  "{0}: {1}".format(self.validateLabel(varName), varName)
            varLoc = noDEF.split(',', 1)[-1].lstrip()
            if self.validateLoc(varLoc):
                return "{0}: \'{1}\'".format(self.validateLoc(varLoc), varLoc)
            print(varLoc)
            #self.vars.append(None)
            return "def yo"


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


    # finds branchs in lines
    def branchFind(self, line):
        if ('BEQ' in line[0:3]) or ('BR' in line[0:2]) or ('BGT' in line[0:3]):
            return True
        else:
            return False


    # validates labels
    def validateLabel(self, label):
        if len(label) > 5 or len(label) < 1:
            return "Variable or Label name length invalid"
        for char in label:
            if self.isLetter(char) == False:
                return "Variable or Label names must be letters only"


    # validates memory locations
    def validateLoc(self, loc):
        if len(loc) < 1:
            return "Memory location length invalid"
        for char in loc:
            if self.isOctalDigit(char) == False:
                return "Memory locations must be octal digits only"


    # returns label from branch line
    def sanitizeBranch(self, line):
        if ('BEQ' in line[0:3]) or ('BGT' in line[0:3]):
            label = line.rsplit(',', 1)[-1].lstrip()
        if ('BR' in line[0:2]):
            label = line.replace('BR', '')
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
                if self.start == True:
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


if '__main__' == __name__:
    fileName = "palprogs"
    fileName +=".pal"
    programs = parseFile(fileName)

    '''for entry in programs.labels:
        print("LISTTTTTT------------")
        for each in entry:
            print(each)'''
    for line in programs.code:
        print(str(line[0]).ljust(3), line[1].ljust(25), line[2])