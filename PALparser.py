from __future__ import print_function
from sys import stdin
import unittest

'''
Description: PAL Parser for PPL
Author: David Faller
'''

class programList(object):

    class program(object):
        lineList = []

        def __init__(self, startLine, endLine, file):
            self.startLine = startLine
            self.endLine = endLine
            print(file[0])
            for lineNum, line in enumerate(file):
                print(lineNum)
                if (lineNum >= startLine) and (lineNum < endLine):
                    self.lineList.append(line)
                    print(line)


        def lineList(self):
            return self.lineList

    code = []
    programs = []
    startEnd = []

    def __init__(self, fileName):
        self.file = open(fileName)
        self.scanFile(self.file)
        for line in self.code:
            print(line, end='')
        #self.findPrograms(self.file)
        #self.buildPrograms(self.file)

    # scan file into iterable list
    def scanFile(self, file):
        for lineNum, line in enumerate(file):
            self.code.append(line)

    def list(self):
        return self.programs

    # build list of program code blocks
    def buildPrograms(self, file):
        for srtend in self.startEnd:
            self.programs.append(self.program(srtend[1], srtend[3], file))
        for program in self.programs:
            print(program.startLine)

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





'''
class test_weighted_digraph(unittest.TestCase):

    def test_two(self):
        g = weighted_digraph()
        g.add_node(1)
        g.add_node(2)
        self.assertEqual(len(g), 2)

    def test_arent_adjacent(self):
        g = weighted_digraph()
        g.add_nodes(['Denver', 'Boston', 'Milano'])
        g.add_edges([('Denver', 'Boston', 1971.8), ('Boston', 'Denver', 1971.8)])
        self.assertFalse(g.are_adjacent('Denver', 'Milano'))

'''

if '__main__' == __name__:

    programs = programList("palprogs.txt")

    #for program in programs.list():
        #print(program.startLine)
        #a = line.strip().split(" ")
