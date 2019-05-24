from nodes import *
from exception import Snixception
import pprint
import re

class SnixParser:
    defines = []

    def readSource(self, filename):
        global typedefs

        f = open(filename, "r")
        source = self.prepareSource(f.read())
        return source

    def prepareSource(self, code):
        code = self.clearComments(code)
        code = self.parseDirectives(code)
        return code

    def getDefinedVariable(self, name):
        for i, define in enumerate(self.defines):
            if (define[0] == name):
                return i

        return None

    def parseDirectives(self, code):
        incPattern = r'#include\s*?[\"](.+?)[\"]'
        defPattern = r'^\s*?#define\s*?([\w_]+?)\s+?(.+?)$'
        incSource = ''
        includes = re.finditer(incPattern, code, flags=re.S)
        code = re.sub(incPattern, '', code, flags=re.S)

        for include in includes:
            file = include.group(1)
            incSource += self.readSource(file) + '\n\n'

        code = incSource + code

        defines = re.finditer(defPattern, code, flags=re.M)
        code = re.sub(defPattern, '', code, flags=re.M)

        for define in defines:
            offset = self.getDefinedVariable(define.group(1))
            if (offset == None):
                self.defines.append((define.group(1), define.group(2)))
            else:
                self.defines[offset] = (define.group(1), define.group(2))

        return code

    def clearComments(self, code):
        cleanCode = ""
        multilines = re.sub(r'\/\*.*?\*\/', ' ', code, flags=re.S)
        lines = re.finditer(r'^(.*?)([\/]{2}|$)', multilines, flags=re.M)
        if (lines != None):
            for a in lines:
                cleanCode += a.group(1) + '\n'

        return cleanCode

    def parseFunctions(self, parsed):
        functions = []

        for fn in parsed['ext']:
            if (fn['_nodetype'] == 'FuncDef'):
                func = FunctionNode(fn)
                functions.append(func)

        return functions
