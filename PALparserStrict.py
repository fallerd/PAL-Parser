from __future__ import print_function
import sys

'''
Description: PAL Parser for PPL
Author: David Faller
'''

class parseFile(object):

    code = []
    starts = []
    ends = []
    start = False
    varList = [[],[]]
    labels = [[],[]]
    define = False
    index = 0
    errors = [0]*8

    def __init__(self, fileName):
        file = open(fileName + ".pal")
        self.scanFile(file, fileName)


    # scan file, remove comments, ignore blanks, remove leading/trailing whitespace
    def scanFile(self, file, fileName):
        errorLog = open(fileName + ".log", 'w')
        self.errorLogHeader(errorLog, fileName)
        for lineNum, line in enumerate(file):
            line = self.removeComment(line)
            line = line.lstrip().rstrip()
            if len(line.strip()) != 0:
                errorLog.write((str(lineNum + 1) + ".").ljust(4) + line + "\n")
                self.parseLine(lineNum, line.strip("\n"), errorLog)
        self.checkOrphans(errorLog)
        self.errorLogFooter(errorLog)
        errorLog.close()


    # create errorlog header
    def errorLogHeader(self, errorLog, fileName):
        errorLog.write("PAL Program Parser\n")
        errorLog.write("By David Faller - CS 3210\n")
        errorLog.write("    -Input filename:      " + fileName + ".pal\n")
        errorLog.write("    -Output log filename: " + fileName + ".log\n")
        errorLog.write("-------------------------------------------\n\n")
        errorLog.write("PAL Program Listing:\n\n")


    # create errorlog footer
    def errorLogFooter(self, errorLog):
        totalErrors = sum(self.errors)
        errorLog.write("\nSummary: -----------------------------------------------\n")
        errorLog.write("\nTotal errors: " + str(totalErrors))
        if self.errors[0]: errorLog.write("\n    " + str(self.errors[0]) + " - Ill-formed label/variable names")
        if self.errors[1]: errorLog.write("\n    " + str(self.errors[1]) + " - Invalid opcodes" )
        if self.errors[2]: errorLog.write("\n    " + str(self.errors[2]) + " - Too many operands")
        if self.errors[3]: errorLog.write("\n    " + str(self.errors[3]) + " - Too few operands")
        if self.errors[4]: errorLog.write("\n    " + str(self.errors[4]) + " - Ill-formed operands")
        if self.errors[5]: errorLog.write("\n    " + str(self.errors[5]) + " - Wrong operand type")
        if self.errors[6]: errorLog.write("\n    " + str(self.errors[6]) + " - Label/Variable structure problems")
        if self.errors[7]: errorLog.write("\n    " + str(self.errors[7]) + " - Bad code structure (SRT/END/DEF)")
        errorLog.write("\nProcessing Complete: ")
        if totalErrors is not 0:
            errorLog.write("PAL program is not valid")
        else:
            errorLog.write("PAL program is valid")


    # checks var and label lists for orphans and lists them before summary
    def checkOrphans(self, errorLog):
        errorLog.write("\nOrphaned Variables and Branch Labels:\n")
        linkedVar = False
        for variable in self.varList[1]:
            for definedVar in self.varList[0]:
                if definedVar[0] == variable[0]:
                    linkedVar = True
            if not linkedVar:
                self.errors[6]+=1
                errorLog.write("    Line {1}: Variable has invalid DEF stmt or never defined: \'{0}\'\n".format(variable[0], variable[1]))
            else:
                linkedVar = False
        linkedLabel = False
        for label in self.labels[0]:
            for labelled in self.labels[1]:
                if label[0] == labelled[0]:
                    linkedLabel = True
            if not linkedLabel:
                self.errors[6]+=1
                errorLog.write("    Line {1}: Branch label on invalid line or never defined: \'{0}\'\n".format(label[0], label[1]))
            else:
                linkedLabel = False
        return


    # scan line for start/end, labels,
    def parseLine(self, lineNum, line, errorLog):
        commandUnknown = self.commandCheck(lineNum, line)
        if commandUnknown != None:
            self.code.append([lineNum + 1, line, commandUnknown])
            self.index +=1
            errorLog.write("    ** " + commandUnknown + "\n")
        else:
            startEndError = self.startEnd(lineNum, line)
            if startEndError != None:
                self.code.append([lineNum + 1, line, startEndError])
                self.index += 1
                errorLog.write("    ** " + startEndError + "\n")
            else:
                labelError = self.labelBranchCheck(lineNum, line)
                if labelError != None:
                    self.code.append([lineNum + 1, line, labelError])
                    self.index += 1
                    errorLog.write("    ** " + labelError + "\n")
                else:
                    operationError = self.operationCheck(lineNum, line)
                    if operationError != None:
                        self.code.append([lineNum + 1, line, operationError])
                        self.index += 1
                        errorLog.write("    ** " + operationError + "\n")
                    else:
                        self.code.append([lineNum + 1, line, ""])
                        self.index += 1


    # checks arithmetic operations
    def operationCheck(self, lineNum, line):
        if ':' in line:
            line = line.split(':', 1)[-1].lstrip()
        if ('MOVE' in line[0:4]):
            line = line[4:].lstrip()
            operands = line.count(",")
            if operands < 1:
                self.errors[3] += 1
                return "Too few operands"
            elif operands > 1:
                self.errors[2] += 1
                return "Too many operands"
            args = self.get2args(line)
            return self.validateMoveArgs(args[0], args[1], lineNum)

        if ('COPY' in line[0:4]):
            line = line[4:].lstrip()
            operands = line.count(",")
            if operands < 1:
                self.errors[3] += 1
                return "Too few operands"
            elif operands > 1:
                self.errors[2] += 1
                return "Too many operands"
            args = self.get2args(line)
            return self.validate2RegArgs(args[0], args[1], lineNum)

        if ('ADD' in line[0:3]) or \
                ('SUB' in line[0:3]) or \
                ('MUL' in line[0:3]) or \
                ('DIV' in line[0:3]):
            line = line[3:].lstrip()
            operands = line.count(",")
            if operands < 2:
                self.errors[3] += 1
                return "Too few operands"
            elif operands > 2:
                self.errors[2] += 1
                return "Too many operands"
            args = self.get3args(line)
            return self.validate3RegArgs(args[0], args[1], args[2], lineNum)

        if ('INC' in line[0:3]) or \
                ('DEC' in line[0:3]):
            line = line[3:].lstrip()
            operands = line.count(",")
            if operands > 0:
                self.errors[2] += 1
                return "Too many operands"
            if self.isRegister(line) is True:
                return
            else:
                valid = self.validateLabel(line)
                if valid is None:
                    self.varList[1].append([line, lineNum + 1, self.index])
                else:
                    return valid


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
                self.errors[6] += 1
                return "Ambiguous label: \'{0}\' in use multiple times".format(label)
            else:
                self.labels[1].append([label, lineNum + 1])
                return

        if self.branchFind(line):
            return self.checkBranch(line, lineNum)

        if ('DEF' in line[0:3]):
            if self.define is False:
                self.errors[7] += 1
                return "DEF commands must follow SRT or DEF"
            noDEF = line[4:]
            varName = noDEF.split(',', 1)[0]
            varValidated = self.validateLabel(varName)
            if varValidated is not None:
                return  varValidated
            if not self.findVars('defined', varName):
                self.varList[0].append([varName, lineNum + 1])
            else:
                self.errors[6] += 1
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
            self.labels[0].append([label, lineNum + 1, self.index])
        return self.checkBranchArgs(line, lineNum)


    # returns label from branch line
    def checkBranchArgs(self, line, lineNum):
        if ('BEQ' in line[0:3]) or ('BGT' in line[0:3]):
            operands = line.count(",")
            if operands < 2:
                self.errors[3] += 1
                return "Too few operands"
            elif operands > 2:
                self.errors[2] += 1
                return "Too many operands"
            args = self.get2args(line[3:].lstrip().rsplit(',', 1)[0])
            return self.validate2RegArgs(args[0], args[1], lineNum)
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


    # checks 3 regular statement args for vailidity
    def validate3RegArgs(self, arg1, arg2, arg3, lineNum):
        if self.isRegister(arg1):
            return self.validate2RegArgs(arg2, arg3, lineNum)
        else:
            arg1Valid = self.validateLabel(arg1)
            if arg1Valid is None:
                self.varList[1].append([arg1, lineNum+1, self.index])
                return self.validate2RegArgs(arg2, arg3, lineNum)
            else:
                return arg1Valid


    # checks 2 regular statement args for validity
    def validate2RegArgs(self, arg1, arg2, lineNum):
        if self.isRegister(arg1):
            if self.isRegister(arg2):
                return
            else:
                arg2Valid = self.validateLabel(arg2)
                if arg2Valid is None:
                    self.varList[1].append([arg2, lineNum+1, self.index])
                    return
                else:
                    return arg2Valid
        else:
            arg1Valid = self.validateLabel(arg1)
            if arg1Valid is None:
                self.varList[1].append([arg1, lineNum+1, self.index])
                if self.isRegister(arg2):
                    return
                else:
                    arg2Valid = self.validateLabel(arg2)
                    if arg2Valid is None:
                        self.varList[1].append([arg2, lineNum+1, self.index])
                        return
                    else:
                        return arg2Valid
            else:
                return arg1Valid


    # checks args for move command
    def validateMoveArgs(self, arg1, arg2, lineNum):
        if len(arg1) < 1:
            self.errors[4] += 1
            return "Value length invalid"
        for char in arg1:
            if self.isOctalDigit(char) is False:
                self.errors[5] += 1
                return "Values must be octal digits only: \'{0}\'".format(arg1)
        if self.isRegister(arg2):
            return
        else:
            self.varList[1].append([arg2, lineNum+1, self.index])
            return self.validateLabel(arg2)


    # searches given var list for matches
    def findVars(self, type, label):
        if type == 'defined':
            if self.varList[0]:
                for entry in self.varList[0]:
                    if label in entry:
                        return True
                return False
            else:
                return False

        if type == 'inUse':
            if self.varList[1]:
                for entry in self.varList[1]:
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
            self.errors[0] += 1
            return "Variable or Label name length invalid: \'{0}\'".format(label)
        for char in label:
            if self.isLetter(char) is False:
                self.errors[4] += 1
                return "Variable or Label names must be letters only: \'{0}\'".format(label)


    # validates memory locations
    def validateLoc(self, loc):
        if len(loc) < 1:
            self.errors[4] += 1
            return "Memory location length invalid"
        for char in loc:
            if self.isOctalDigit(char) is False:
                self.errors[5] += 1
                return "Memory locations must be octal digits only"


    # returns label from branch line
    def getBranchLabel(self, line):
        if ('BEQ' in line[0:3]) or ('BGT' in line[0:3]):
            label = line.rsplit(',', 1)[-1].lstrip()
            return label
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
                    self.errors[7] += 1
                    return 'Program already has SRT at line {0}'.format(self.starts[ind - 1] + 1)
            else:
                self.start = True
                ind = self.starts.index(lineNum)
                self.errors[7] += 1
                return 'SRT stmt at line {0} has extra characters'.format(self.starts[ind] + 1)

        if ("END" in line) and ('BEQ' not in line) and ('BR' not in line) and ('BGT' not in line) and ('DEF' not in line):
            self.ends.append(lineNum)
            if 'END' == line.split(':', 1)[-1].lstrip().replace(' ', ''):
                if self.start is True:
                    self.start = False
                else:
                    self.start = False
                    self.errors[7]+=1
                    return 'END at line {0} does not have matching SRT'.format(lineNum + 1)
            else:
                self.start = False
                self.errors[7] += 1
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
            self.errors[1] += 1
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
            self.errors[1] += 1
            return "Invalid opcode: Line {0}".format(lineNum+1)


if '__main__' == __name__:
    fileName = sys.argv[1]
    programs = parseFile(fileName)