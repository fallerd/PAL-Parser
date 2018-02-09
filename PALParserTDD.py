from __future__ import print_function
from sys import stdin
import unittest

'''
Description: PAL Parser for PPL
Author: David Faller
'''

class parseFile(object):

    code = []
    programs = []
    starts = []
    ends = []
    start = False

    def __init__(self, fileName):
        self.file = open(fileName)
        self.scanFile(self.file)


    # scan file, remove comments, ignore blanks
    def scanFile(self, file):
        for lineNum, line in enumerate(file):
            line = self.removeComment(line)
            if len(line.strip()) != 0:
                self.parseLine(lineNum, line.strip("\n"))

    # scan line
    def parseLine(self, lineNum, line):
        startEndError = self.startEnd(lineNum, line)
        if startEndError != None:
            self.code.append([lineNum+1, line, startEndError])
        else:
            self.code.append([lineNum+1, line, ''])
        #print(lineNum, line)

    # find starts and ends
    def startEnd(self, lineNum, line):
        if ('SRT' in line) and ('BEQ' not in line) and ('BR' not in line) and ('BGT' not in line) and ('DEF' not in line):
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
            if 'END' == line.split(':', 1)[-1].replace(' ', ''):
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


if '__main__' == __name__:
    fileName = "palprogs"
    fileName +=".pal"
    programs = parseFile(fileName)

    for line in programs.code:
        print(line[0], line[1].ljust(25), line[2])

    #for program in programs.list():
        #print(program.startLine)
        #a = line.strip().split(" ")
