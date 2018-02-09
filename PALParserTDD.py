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
    vars = []

    def __init__(self, fileName):
        self.file = open(fileName)
        self.scanFile(self.file)
        #self.outputErrorFile(self.code)


    # scan file, remove comments, ignore blanks, remove leading whitespace
    def scanFile(self, file):
        for lineNum, line in enumerate(file):
            line = self.removeComment(line)
            line = line.lstrip();
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
        noLabel = line.split(': ', 1)[-1]
        if noLabel.replace(' ', '') == '':
            return "Label must be followed by a command"
        if ('DEF ' in noLabel[0:4]) or \
                ('MOVE ' in noLabel[0:5]) or \
                ('COPY ' in noLabel[0:5]) or \
                ('SRT' in noLabel[0:3]) or \
                ('DEF ' in noLabel[0:4]) or \
                ('ADD ' in noLabel[0:4]) or \
                ('INC ' in noLabel[0:4]) or \
                ('SUB ' in noLabel[0:4]) or \
                ('DEC ' in noLabel[0:4]) or \
                ('MUL ' in noLabel[0:4]) or \
                ('DIV ' in noLabel[0:4]) or \
                ('BEQ ' in noLabel[0:4]) or \
                ('BGT ' in noLabel[0:4]) or \
                ('BR ' in noLabel[0:3]) or \
                ('END' in noLabel[0:3]):
            return
        else:
            return "Command unknown"


    # finds labels, returns errors
    def label(self, lineNum, line):
        noLabel = line.split(': ', 1)[-1]
        if ('DEF' in noLabel[0:3]):
            noDEF = noLabel[4:]
            varName = noDEF.split(',', 1)[0]
            if len(varName) > 5 or len(varName) < 1:
                return "Variable name length invalid"
            for char in varName:
                if self.isLetter(char) == False:
                    return "Variable names must be letters only"
            #self.vars.append(None)
            return "def yo"


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
                    return '!!! Program already has SRT at line {0}'.format(self.starts[ind - 1] + 1)
            else:
                self.start = True
                ind = self.starts.index(lineNum)
                return '!!! SRT stmt at line {0} has extra characters'.format(self.starts[ind] + 1)

        if ("END" in line) and ('BEQ' not in line) and ('BR' not in line) and ('BGT' not in line) and ('DEF' not in line):
            self.ends.append(lineNum)
            if 'END' == line.split(': ', 1)[-1].replace(' ', ''):
                if self.start == True:
                    self.start = False
                else:
                    self.start = False
                    return '!!! END at line {0} does not have matching SRT'.format(lineNum + 1)
            else:
                self.start = False
                return '!!! END stmt at line {0} has extra characters'.format(lineNum + 1)


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

    for line in programs.code:
        print(str(line[0]).ljust(3), line[1].ljust(25), line[2])

    #for program in programs.list():
        #print(program.startLine)
        #a = line.strip().split(" ")
