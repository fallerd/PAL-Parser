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
    startEnd = []
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
        print(lineNum, line)


    def removeComment(self, line):
        if ';' in line:
            noComment = line.split(';', 1)[0]
            return noComment
        else:
            return line



    #find matching pairs of SRT END and note lines
    def findPrograms(self, file):
        index = 0
        start = False
        for lineNum, line in enumerate(file):
            if "SRT" in line:
                if start == False:
                    self.startEnd.append(['start', lineNum])
                    start = True
                else:
                    print('SRT at line', lineNum, 'does not have matching END')
            if "END" in line and 'BEQ' not in line and 'BR' not in line and 'BGT' not in line:
                if start == True:
                    self.startEnd[index].append('end')
                    self.startEnd[index].append(lineNum)
                    start = False
                    index += 1
                else:
                    print('END at line', lineNum + 1, 'does not have matching SRT')


if '__main__' == __name__:
    fileName = "palprogs"
    fileName +=".pal"
    programs = parseFile(fileName)

    #for program in programs.list():
        #print(program.startLine)
        #a = line.strip().split(" ")
