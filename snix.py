import parser as sp
import snixel.snixel as sn
from nodes import CustomNode
from exception import Snixception

from argparse import ArgumentParser
import copy
import sys
import re

from pycparser import c_parser, c_ast, parse_file, plyparser
from pycphelper import ast_to_dict

snixel = sn.Snixel()

utfile = 'out.sbs'
source = ''

class SnixCompiler:
    functions = []
    nativeFuncs = []
    nativeVars = []
    sysVars = []
    defines = []
    systemNodes = []

    def __init__(self, defines = None):
        if (defines != None):
            self.defines = defines

    def populateNativeData(self):
        # Functions
        self.nativeFuncs.append(("float", "sample", [['float2']]))
        self.nativeFuncs.append(("float", "sampleGrayscale", [['float2']]))
        self.nativeFuncs.append(("float4", "sampleColor", [['float2']]))
        self.nativeFuncs.append(("input", "abs", [['float', 'float2', 'float3', 'float4', 'int']]))
        self.nativeFuncs.append(("input", "floor", [['float', 'float2', 'float3', 'float4']]))
        self.nativeFuncs.append(("input", "ceil", [['float', 'float2', 'float3', 'float4']]))
        self.nativeFuncs.append(("input", "cos", [['float', 'float2', 'float3', 'float4']]))
        self.nativeFuncs.append(("input", "sin", [['float', 'float2', 'float3', 'float4']]))
        self.nativeFuncs.append(("input", "tan", [['float', 'float2', 'float3', 'float4']]))
        self.nativeFuncs.append(("float", "atan2", [['float2']]))
        self.nativeFuncs.append(("float2", "cartesian", [['float'], ['float']]))
        self.nativeFuncs.append(("input", "sqrt", [['float', 'float2', 'float3', 'float4']]))
        self.nativeFuncs.append(("float", "dot", [['float2', 'float3', 'float4'],
                                                 ['float2', 'float3', 'float4']]))
        self.nativeFuncs.append(("input", "log", [['float', 'float2', 'float3', 'float4']]))
        self.nativeFuncs.append(("input", "exp", [['float', 'float2', 'float3', 'float4']]))
        self.nativeFuncs.append(("input", "log2", [['float', 'float2', 'float3', 'float4']]))
        self.nativeFuncs.append(("input", "pow2", [['float', 'float2', 'float3', 'float4']]))
        self.nativeFuncs.append(("input", "lerp", [['float', 'float2', 'float3', 'float4'],
                                                 ['float', 'float2', 'float3', 'float4'],
                                                 ['float']]))
        self.nativeFuncs.append(("input", "min", [['float', 'float2', 'float3', 'float4',
                                                 'int', 'int2', 'int3', 'int4'],
                                                 ['float', 'float2', 'float3', 'float4',
                                                  'int', 'int2', 'int3', 'int4']]))
        self.nativeFuncs.append(("input", "max", [['float', 'float2', 'float3', 'float4',
                                                 'int', 'int2', 'int3', 'int4'],
                                                 ['float', 'float2', 'float3', 'float4',
                                                  'int', 'int2', 'int3', 'int4']]))
        self.nativeFuncs.append(("float", "random", [['float']]))
        self.nativeFuncs.append(("float3", "reflect", [['float3'], ['float3']]))
        self.nativeFuncs.append(("float", "pow", [['float'], ['float']]))

        # Variables
        self.nativeVars.append(("float2", "$sizelog2"))
        self.nativeVars.append(("float2", "$size"))
        self.nativeVars.append(("float2", "$pos"))
        self.nativeVars.append(("float", "$time"))
        self.nativeVars.append(("float", "$depth"))
        self.nativeVars.append(("float", "$depthpow2"))
        self.nativeVars.append(("float", "$number"))

        # System Variables
        self.sysVars.append(("bool", "true"))
        self.sysVars.append(("bool", "false"))
        self.sysVars.append(("input", "__if__"))
        self.sysVars.append(("input", "__for__"))

    def isBoolOnlyOp(self, op):
        boolOnlyTypes = ['&&', '||', '!', '!=', '==', '>', '<', '>=', '<=']

        if (op in boolOnlyTypes):
            return 1

        return 0

    def isTypeCompatible(self, type1, type2):
        if (type1 == type2 or type1 == 'any' or type2 == 'any'):
            return 1
        else:
            return 0

    def isNativeFunction(self, name):
        for f in self.nativeFuncs:
            if (name == f[1]):
                return 1

        return 0

    def isNativeVariable(self, name):
        for v in self.nativeVars:
            if (name == v[1]):
                return 1

    def isSystemVariable(self, name):
        for v in self.sysVars:
            if (name == v[1]):
                return 1

        return 0

    def isDefinedVariable(self, name):
        if (self.getDefinedVariable(name) != None):
            return 1

        return 0

    def getSystemNode(self, var, function):
        for node in self.systemNodes:
            if (hasattr(node, 'name') and var[1] == node.name):
                return node

        return self.createSystemNode(var, function)


    def verifyNativeFunctionTypes(self, instruction, functionName):
        func = self.getNativeFunctionByName(instruction.name)
        type = func[0]
        name = func[1]
        args = func[2]

        for i, value in enumerate(instruction.args.values):
            acceptedList = ''
            for j in range(len(args[i])):
                acceptedList += args[i][j] + ', '
            if (value.type not in args[i]):
                raise Snixception(instruction.offset, "Parameter '" + str(i + 1) + "' of function '" + name +\
                                    "' accepts type(s) '" + acceptedList[:-2] + "', but type '" + value.type + "' was passed!")

        return 1

    def getNativeFunctionByName(self, name):
        for f in self.nativeFuncs:
            if (name == f[1]):
                return f

    def getNativeVariableByName(self, name, function):
        for v in self.nativeVars:
            if (name == v[1]):
                return self.getSystemNode(v, function)

    def getSystemVariableByName(self, name, function):
        for v in self.sysVars:
            if (name == v[1]):
                return self.getSystemNode(v, function)

    def getDefinedVariable(self, name):
        for define in self.defines:
            if (define[0] == name):
                return define

        return None

    def getDefinedValue(self, name):
        for define in self.defines:
            if (define[0] == name):
                return define[1]

        return None

    def getBaseType(self, type):
        # Get the base type (e.g. float for float2 or float3)
        base = re.match(r'^(\D+?)\d*?$', type)
        return base.group(1)

    def getTypeSize(self, type):
        base = re.match(r'^\D+?(\d)$', type)

        if (base):
            return base.group(1)
        else:
            return 1

    def getInputByName(self, name, function):
        for node in function.inputs:
            if (node.name == name):
                return node

    def findConstantByValue(self, value, type, function):
        for node in function.body.instructions:
            if (hasattr(node, 'value') and hasattr(node.value, 'value')):
                childNode = node.value
                if (childNode.nodeType == 'Constant' and childNode.value == value and childNode.type == type):
                    if (childNode.node != None):
                        return node.value

        for node in self.systemNodes:
            if (hasattr(node, 'value') and node.nodeType == 'Constant' and node.value == value and node.type == type):
                if (node.node != None):
                    return node

    def getOthersByName(self, name, function):
        node = self.getInputByName(name, function)
        if (node == None):
            node = self.getNativeVariableByName(name, function)
        if (node == None):
            node = self.getSystemVariableByName(name, function)

        return node

    def getDeclareInBody(self, name, instruction, function):
        for node in instruction.instructions:
            if (node.nodeType == 'If'):
                ifnode = self.getDeclareInBody(name, node.iftrue, function)
                if (ifnode != None): return ifnode
                ifnode = self.getDeclareInBody(name, node.iffalse, function)
                if (ifnode != None): return ifnode
            if (node.nodeType == 'Declare' and node.name == name):
                return node

    def getLastReferenceInBody(self, name, instruction, function):
        for node in reversed(instruction.instructions):
            if (node.nodeType == 'For'):
                if (hasattr(node.next, 'name') and name == node.next.name):
                    return node.next
                fornode = self.getLastReferenceInBody(name, node.body, function)
                if (fornode != None): return fornode
            if (node.nodeType == 'If'):
                ifnode = self.getLastReferenceInBody(name, node.iftrue, function)
                if (ifnode != None): return ifnode
                ifnode = self.getLastReferenceInBody(name, node.iffalse, function)
                if (ifnode != None): return ifnode
            if (hasattr(node, 'name') and node.name == name):
                return node


    def getVariableDeclare(self, instruction, function, context):
        node = self.getDeclareInBody(instruction.name, function.body, function)

        if (node == None):
            node = self.getOthersByName(instruction.name, function)

        if (node != None):
            return node

        raise Snixception(instruction.offset, "Attempted to use an undeclared variable '" + instruction.name + "'. Snix sad and confused! :(")

    def getLastReference(self, instruction, function, context):
        node = self.getLastReferenceInBody(instruction.name, function.body, function)

        if (node == None):
            node = self.getOthersByName(instruction.name, function)

        if (node != None):
            return node

        raise Snixception(instruction.offset, "Attempted to use an undeclared variable '" + instruction.name + "'. Snix sad and confused! :(")

    def getLastNodeTypeReference(self, nodeType, function):
        for node in reversed(function.body.instructions):
            if (node.nodeType == nodeType):
                return node

        if (node != None):
            return node

        raise Snixception(instruction.offset, "Attempted to reference a non-existing '" + nodeType + "' statement. Snix sad and confused! :(")

    def createSystemNode(self, var, function):
        type = var[0]
        name = var[1]

        if (self.isNativeVariable(name)):
            sysNode = self.createNativeVar(var, function)
        else:
            if (name == 'true'):
                sysNode = self.createConstantWithValue(1, type, function)
                sysNode.name = var[1]
            elif (name == 'false'):
                sysNode = self.createConstantWithValue(0, type, function)
                sysNode.name = var[1]
            elif (name == '__if__'):
                sysNode = self.getLastNodeTypeReference('If', function)
            elif (name == '__for__'):
                sysNode = self.getLastNodeTypeReference('For', function)
            else:
                raise Snixception('Internal', "Attempted to create unknown system node '" + name + "'!")

        return sysNode

    def createNativeVar(self, var, function):
        sysNode = CustomNode()
        type = var[0]
        name = var[1]

        baseType = self.getBaseType(type)

        sysNode.node = function.node.addGet(name, type)
        sysNode.name = name
        sysNode.type = type
        sysNode.nodeType = 'ID'
        self.systemNodes.append(sysNode)

        return sysNode

    def createNativeCall(self, instruction, function, context):
        func = self.getNativeFunctionByName(instruction.name)
        type = func[0]
        name = func[1]
        args = func[2]

        # Some native functions can output multiple types depending on the input
        if (type == 'input'):
            type = instruction.args.type

        instruction.type = type
        instruction.name = name

        if (instruction.args == None):
            argCount = 0
        else:
            argCount = len(instruction.args.values)

        if (argCount != len(args)):
            raise Snixception(instruction.offset, "Function '" + name + "' expects " + str(len(args)) + " parameter(s), but received "\
                              + str(argCount) + "!")

        a = instruction.args.values[0].node
        argType = instruction.args.values[0].type
        if (self.verifyNativeFunctionTypes(instruction, name)):
            if (name == 'sample' or name == 'sampleGrayscale'):
                instruction.node = function.node.addSampleGrayscale(a)
            elif (name == 'sampleColor'):
                instruction.node = function.node.addSampleColor(a)
            elif (name == 'abs'):
                instruction.node = function.node.addAbs(a, argType)
            elif (name == 'floor'):
                instruction.node = function.node.addFloor(a, argType)
            elif (name == 'ceil'):
                instruction.node = function.node.addCeil(a, argType)
            elif (name == 'cos'):
                instruction.node = function.node.addCos(a, argType)
            elif (name == 'sin'):
                instruction.node = function.node.addSin(a, argType)
            elif (name == 'tan'):
                instruction.node = function.node.addTan(a, argType)
            elif (name == 'atan2'):
                instruction.node = function.node.addArcTan2(a, argType)
            elif (name == 'cartesian'):
                b = instruction.args.values[1].node
                instruction.node = function.node.addCartesian(a, b, argType)
            elif (name == 'sqrt'):
                instruction.node = function.node.addSqrt(a, argType)
            elif (name == 'dot'):
                b = instruction.args.values[1].node
                instruction.node = function.node.addDot(a, b, argType)
            elif (name == 'log'):
                instruction.node = function.node.addLog(a, argType)
            elif (name == 'exp'):
                instruction.node = function.node.addExp(a, argType)
            elif (name == 'log2'):
                instruction.node = function.node.addLog2(a, argType)
            elif (name == 'pow2'):
                instruction.node = function.node.addPow2(a, argType)
            elif (name == 'lerp'):
                b = instruction.args.values[1].node
                c = instruction.args.values[2].node
                instruction.node = function.node.addLerp(a, b, c, argType)
            elif (name == 'min'):
                b = instruction.args.values[1].node
                instruction.node = function.node.addMin(a, b, argType)
            elif (name == 'max'):
                b = instruction.args.values[1].node
                instruction.node = function.node.addMax(a, b, argType)
            elif (name == 'random'):
                instruction.node = function.node.addRandom(a, argType)
            elif (name == 'reflect'):
                b = instruction.args.values[1].node
                instruction.node = function.node.addReflect(a, b, argType)
            elif (name == 'pow'):
                b = instruction.args.values[1].node
                instruction.node = function.node.addPow(a, b, argType)
            else:
                raise Snixception(instruction.offset, "Attempted to call undefined native function '" + instruction.name +\
                                    "'. This is an internal error, please report to the developer!")


    def createVectorConnector(self, instruction, function, context):
        node = None
        valueCount = len(instruction.values)

        if (valueCount > 1):
            baseType = instruction.values[0].type

            endDigit = re.match('(\d)$', baseType)
            if (endDigit == None):
                type = str(baseType) + str(valueCount)

            if (valueCount > 4):
                raise Snixception(instruction.offset, "Vector overload: max vector size is 4!")

            # Make sure all values are of the same type
            for value in instruction.values:
                if (value.type != baseType):
                    raise Snixception(instruction.offset, "Vector type mismatch: expected '" + baseType + \
                                                            "' but got '" + value.type + "'")

            # Create the necessary vectors
            if (type == 'float2' or type == 'float3' or type == 'float4'):
                node = function.node.addVectorFloat(instruction.values[0].node, instruction.values[1].node, 'float2')
            if (type == 'float3'):
                node = function.node.addVectorFloat(node, instruction.values[2].node, type)
            if (type == 'float4'):
                node2 = function.node.addVectorFloat(instruction.values[2].node, instruction.values[3].node, 'float2')
                node = function.node.addVectorFloat(node, node2, type)
            if (type == 'int2' or type == 'int3' or type == 'int4'):
                node = function.node.addVectorInt(instruction.values[0].node, instruction.values[1].node, type)
            if (type == 'int3'):
                node = function.node.addVectorInt(node, instruction.values[2].node, type)
            if (type == 'int4'):
                node2 = function.node.addVectorInt(instruction.values[2].node, instruction.values[3].node, 'int2')
                node = function.node.addVectorInt(node, node2, type)
            if (node == None):
                raise Snixception(instruction.offset, "Unknown vector type '" + type + "'")

            instruction.type = type
            instruction.node = node
        elif (valueCount == 1):
            instruction.type = instruction.values[0].type
            instruction.node = instruction.values[0].node

    def createConstantWithValue(self, value, type, function):
        # Use an existing constant if one exists of the same type and value
        existing = self.findConstantByValue(value, type, function)

        if (existing != None):
            return existing
        else:
            sysNode = CustomNode()
            sysNode.nodeType = 'Constant'
            sysNode.type = type
            sysNode.value = value
            sysNode.node = function.node.addConst(value, type)

        self.systemNodes.append(sysNode)
        return sysNode

    def createConstant(self, instruction, function, context):
        type = instruction.type

        # Use an existing constant if one exists of the same type and value
        existing = self.findConstantByValue(instruction.value, instruction.type, function)

        if (existing != None):
            instruction.node = existing.node
        else:
            instruction.node = function.node.addConst(instruction.value, instruction.type)

    def createMathOp(self, instruction, op, function, context):
        scalarMulTypes = ['float2', 'float3', 'float4']
        left = instruction.left.node
        right = instruction.right.node
        type = instruction.left.type
        instruction.type = type

        baseType = self.getBaseType(type)

        if (type == 'int' or baseType == 'float'):
            if (op == '+'):   instruction.node = function.node.addAdd(left, right, type)
            elif (op == '-'): instruction.node = function.node.addSubtract(left, right, type)
            elif (op == '/'): instruction.node = function.node.addDivide(left, right, type)
            elif (op == '%'): instruction.node = function.node.addMod(left, right, type)
            elif (op == '*'):
                if (instruction.left.type == instruction.right.type):
                    instruction.node = function.node.addMultiply(left, right, type)
                elif (instruction.left.type == 'float' and instruction.right.type in scalarMulTypes):
                    instruction.node = function.node.addScalarMultiply(right, left, instruction.right.type)
                    instruction.type = instruction.right.type
                elif (instruction.right.type == 'float' and instruction.left.type in scalarMulTypes):
                    instruction.node = function.node.addScalarMultiply(left, right, instruction.left.type)
                    instruction.type = instruction.left.type
            else: raise Snixception(instruction.offset, "Unsupported operand '" + op + "'")
        else:
            raise Snixception(instruction.offset, "Operand '" + op + "' is incompatible with type '" + type + "'!")

    def createNumericUnaryOp(self, instruction, function, context):
        op = instruction.op
        type = instruction.value.type

        if (op == '-'):
            instruction.node = function.node.addNegate(instruction.value.node, type)
        elif (op == '--' or op == '++'):
            right = self.createConstantWithValue('1', type, function)
            if (op == '++'):
                instruction.node = function.node.addAdd(instruction.value.node, right.node, type)
            else:
                instruction.node = function.node.addSubtract(instruction.value.node, right.node, type)
        else:
            raise Snixception(instruction.offset, "Unknown unary operation '" + instruction.op + "'!")

    def createBinaryOp(self, instruction, function, context):
        ops = ['&&', '||', '!', '!=', '==', '>', '>=', '<', '<=', '+', '-', '*', '/', '%']
        self.createNode(instruction.left, function, context)
        self.createNode(instruction.right, function, context)
        op = instruction.op

        if (instruction.left.type != instruction.right.type and op != '*'):
            raise Snixception(instruction.offset, "Cannot perform binary operation '" + instruction.op + "' on incompatible types '" + \
                                                    instruction.left.type + "' and '" + instruction.right.type + "'")

        type = instruction.left.type
        instruction.type = 'bool'
        left = instruction.left.node
        right = instruction.right.node

        if (self.isTypeCompatible(instruction.left.type, instruction.right.type) or op == '*'):
            baseType = self.getBaseType(type)

            if (type == 'bool'):
                if (op == '&&'):   instruction.node = function.node.addAnd(left, right)
                elif (op == '||'): instruction.node = function.node.addOr(left, right)
                elif (op == '!'):  instruction.node = function.node.addNot(left, right)

            if ((type == 'bool' or type == 'int' or type == 'float') and instruction.node == None):
                if (op == '!='):   instruction.node = function.node.addNotEquals(left, right, type)
                elif (op == '=='): instruction.node = function.node.addEquals(left, right, type)

            if (type == 'int' or type == 'float' and instruction.node == None):
                if (op == '>'):    instruction.node = function.node.addGreaterThan(left, right, type)
                elif (op == '>='): instruction.node = function.node.addGreaterOrEqual(left, right, type)
                elif (op == '<'):  instruction.node = function.node.addLessThan(left, right, type)
                elif (op == '<='): instruction.node = function.node.addLessOrEqual(left, right, type)

            if ((type == 'int' or baseType == 'float') and instruction.node == None):
                self.createMathOp(instruction, op, function, context)

            if (instruction.node == None):
                if (op == '&&' or op == '||' or op == '!'):
                    exception = "Can only compare boolean values with '" + op + "'!"
                elif (op in ops):
                    exception = "Operand '" + op + "' is incompatible with type '" + type + "'!"
                else:
                    exception = "Unsupported binary operation '" + op + "'!"

                raise Snixception(instruction.offset, exception)
        else:
            raise Snixception(instruction.offset, "Cannot perform binary operation on incompatible types!")

    def createUnaryOp(self, instruction, function, context):
        self.createNode(instruction.value, function, context)
        type = instruction.value.type

        if (self.isBoolOnlyOp(instruction.op) and type != 'bool'):
            raise Snixception(instruction.offset, "Unary operation '" + instruction.op + "' can only be applied to booleans!")

        # Make last use references point to this node
        if (hasattr(instruction.value, 'name')):
            instruction.name = instruction.value.name
        instruction.type = type
        baseType = self.getBaseType(type)

        if (baseType == 'float' or type == 'int'):
            self.createNumericUnaryOp(instruction, function, context)
        elif (instruction.op == '!'):
            instruction.node = function.node.addNot(instruction.value.node)
        else:
            raise Snixception(instruction.offset, "Unknown unary operation '" + instruction.op + "'!")

        if (context == 'For'):
            instruction.node = function.node.addSet(instruction.name, instruction.node, instruction.type);

    def getMaxForLoops(self, instruction, function, context):
        loops = None
        initVal = None
        cond = instruction.condition
        init = instruction.init
        next = instruction.next

        # Try to figure out the max amount of loops to create
        if (cond.right.nodeType == 'Constant' and cond.nodeType == 'BinaryOp' and init.nodeType == 'Assignment'):
            if (next.nodeType == 'UnaryOp'):
                op = next.op
                var = next.value.name
                condOp = cond.op
                if (cond.left.nodeType == 'UnaryOp' and cond.left.value.nodeType == 'ID' and cond.right.nodeType == 'Constant'):
                    condVar = cond.left.value.name
                    condVal = int(cond.right.value)
                    if (init.right.nodeType == 'Constant' and init.left.name == var and condVar == var):
                        initVal = int(init.right.value)

        if (isinstance(initVal, int)):
            if (condOp[0] == '<' and op == '++'):
                if (initVal <= condVal):
                    if (condOp == '<'):
                        loops = condVal - initVal - 1
                    elif (condOp == '<='):
                        loops = condVal - initVal
                else:
                    raise Snixception(instruction.offset, "That for loop looks like it would create an infinite number of loops!")
            if (condOp[0] == '>' and op == '++'):
                    raise Snixception(instruction.offset, "That for loop doesn't look right!")
            if (condOp[0] == '>' and op == '--'):
                if (initVal >= condVal):
                    if (condOp == '>'):
                        loops = initVal - condVal - 1
                    elif (condOp == '>'):
                        loops = initVal - condVal
                else:
                    raise Snixception(instruction.offset, "That for loop looks like it would create an infinite number of loops!")
            if (condOp[0] == '<' and op == '--'):
                raise Snixception(instruction.offset, "That for loop doesn't look right!")

        if (loops == None):
            loops = int(self.getDefinedValue('LOOP_MAX'))
            print("Notice: Unable to discern loop max value, max loops will be LOOP_MAX. (LOOP_MAX = '" + str(loops) + "')")

        if (loops >= 100):
            print("Notice: That number of loops per pixel can get dangerously slow!")

        return loops

    def createFor(self, instruction, function, context):
        self.createNode(instruction.condition, function, instruction.nodeType)
        self.createNode(instruction.init, function, instruction.nodeType)
        #self.createNode(instruction.next, function, instruction.nodeType)
        self.createNode(instruction.body, function, instruction.nodeType)

        if (instruction.condition.nodeType == 'ExprList' or
            instruction.init.nodeType == 'ExprList' or
            instruction.next.nodeType == 'ExprList'):
            raise Snixception(instruction.offset, "For loops only support single init, next and condition statements at the moment!")

        finalNode = instruction.body.instructions[len(instruction.body.instructions) - 1]
        type = finalNode.type;

        zeroNode = self.createConstantWithValue(0, type, function)

        instruction.node = function.node.addIf(instruction.condition.node, finalNode.node, zeroNode.node, type)
        instruction.condition.left = instruction.next

        loops = self.getMaxForLoops(instruction, function, context)

        for i in range(loops):
            self.createNode(instruction.condition, function, instruction.nodeType)
            self.createNode(instruction.body, function, instruction.nodeType)
            instruction.node = function.node.addIf(instruction.condition.node, finalNode.node, instruction.node, type)

        instruction.type = type

    def createIf(self, instruction, function, context):
        self.createNode(instruction.iftrue, function, context)
        self.createNode(instruction.iffalse, function, context)
        self.createNode(instruction.condition, function, context)

        if (instruction.iftrue.nodeType != 'Compound' or instruction.iffalse.nodeType != 'Compound'):
            raise Snixception(instruction.offset, 'If statements need full compound bodies with curly brackets for both the true and false statements!')

        nodeType = instruction.condition.nodeType
        if (instruction.condition.type == 'bool'):
            # Get the final nodes for connecting with the If node
            trueNode = instruction.iftrue.instructions[len(instruction.iftrue.instructions) - 1]
            falseNode = instruction.iffalse.instructions[len(instruction.iffalse.instructions) - 1]

            if (not self.isTypeCompatible(trueNode.type, falseNode.type)):
                raise Snixception(instruction.offset, "'If' statement expects type '" + trueNode.type + "', but else outputs type '" + falseNode.type + "'!")

            instruction.type = trueNode.type
            instruction.node = function.node.addIf(instruction.condition.node, trueNode.node, falseNode.node, instruction.type)
        else:
            raise Snixception(instruction.offset, "Cannot compare type '" + instruction.condition.type + "' in if statement, boolean needed!")

    def createCast(self, instruction, function, context):
        self.createNode(instruction.expression, function, context)

        type = instruction.expression.type
        toType = instruction.toType

        if (type == 'int' and toType == 'float'):
            instruction.node = function.node.addToFloat(instruction.expression.node)
        elif (type == 'float' and toType == 'int'):
            instruction.node = function.node.addToInt(instruction.expression.node)
        elif (type == toType):
            instruction.node = instruction.expression.node
        else:
            raise Snixception(instruction.offset, "Cannot cast from: type '" + type + "' to '" + toType + "'")

        if (hasattr(instruction.expression, 'name')):
            instruction.name = instruction.expression.name

        instruction.type = toType

    def createArrayRef(self, instruction, function, context):
        self.createNode(instruction.variable, function, context)

        if (instruction.subscript.nodeType != 'Constant' or instruction.subscript.type != 'int'):
            raise Snixception(instruction.offset, "Subscript index has to be a constant integer, Substance Designer does not support abstract indexing.")

        index = int(instruction.subscript.value)
        type = instruction.variable.type
        baseType = self.getBaseType(type)
        typeSize = int(self.getTypeSize(instruction.variable.type))

        if (index > typeSize or index < 0):
            raise Snixception(instruction.offset, "Index out of bounds: '" + str(index) +\
                              "' (variable '" + instruction.variable.name + "' is size '" + str(typeSize - 1) + "')")
        else:
            if (baseType == 'float'):
                instruction.node = function.node.addSwizzleFloat(instruction.variable.node, str(index))
            elif (baseType == 'int'):
                instruction.node = function.node.addSwizzleInt(instruction.variable.node, str(index))
            else:
                raise Snixception(instruction.offset, "Accessing indices is only supported on float and int type variables!")

        instruction.type = baseType

    def createCompound(self, instruction, function, context):
        childCount = len(instruction.instructions)
        if (childCount > 0):
            for child in instruction.instructions:
                self.createNode(child, function, context)
            # Return the first value as type for ifs and type-adaptive native functions
            instruction.type = instruction.instructions[0].type

    def createDeclList(self, instruction, function, context):
        if (len(instruction.values) > 0):
            for value in instruction.values:
                self.createNode(value, function, context)

            # Return the first value as type for type-adaptive native functions
            instruction.type = instruction.values[0].type

    def createInitList(self, instruction, function, context):
        if (len(instruction.values) > 0):
            for value in instruction.values:
                self.createNode(value, function, context)

            self.createVectorConnector(instruction, function, context)

    def createExpressionList(self, instruction, function, context):
        if (len(instruction.values) > 0):
            for value in instruction.values:
                self.createNode(value, function, context)
            # Return the first value as type for type-adaptive native functions
            instruction.type = instruction.values[0].type

    def createCompoundLiteral(self, instruction, function, context):
            self.createNode(instruction.value, function, context)
            instruction.node = instruction.value.node
            instruction.type = instruction.value.type

    def createFunctionCall(self, instruction, function, context):
        self.createNode(instruction.args, function, context)
        name = instruction.name

        if (self.isNativeFunction(name)):
            self.createNativeCall(instruction, function, context)
        else:
            call = None

            if (name == function.name):
                raise Snixception(instruction.offset, "Substance Designer does not allow functions calling themselves! (In function: '" + name + "')")

            for func in self.functions:
                if (func.name == name):
                    call = func
                    break

            if (instruction.args != None):
                args = instruction.args.values
            else:
                args = []

            if (call == None):
                raise Snixception(instruction.offset, "Attempted to call undeclared function '" + name + "'!")
            if (len(args) != len(call.inputs)):
                raise Snixception(instruction.offset, "Function: '" + name + "' takes " +\
                                    str(len(call.inputs)) + " parameter(s), not " + str(len(args)) + ".")

            connections = []

            for i, input in enumerate(call.inputs):
                if (self.isTypeCompatible(args[i].type, input.type)):
                    connections.append((input.name, args[i].node))
                else:
                    raise Snixception(instruction.offset, "Function '" + name + "' parameter '" + input.name + "' is of type '" + \
                                        input.type + "', passed parameter is of type '" + args[i].type + "'")

            instruction.type = call.type
            instruction.name = call.name
            instruction.node = function.node.addFunctionCall(name, connections)


    def createID(self, instruction, function, context):
        declareNode = self.getVariableDeclare(instruction, function, context)
        lastUse = self.getLastReference(instruction, function, context)
        instruction.type = declareNode.type
        instruction.node = lastUse.node

    def createDeclare(self, instruction, function, context):
        if (instruction.value != None):
            self.createNode(instruction.value, function, context)
            if (instruction.type == instruction.value.type):
                instruction.node = instruction.value.node
            else:
                raise Snixception(instruction.offset, "Can't assign type '" + instruction.value.type + "' to type '" + \
                                                        instruction.type + "'")
        else:
            raise Snixception(instruction.offset, "Declaring a variable without a value is not allowed!")

    def createReturn(self, instruction, function, context):
        self.createNode(instruction.value, function, context)
        instruction.type = instruction.value.type

        if (instruction.type == function.type):
            function.output = instruction.value
        else:
            raise Snixception(instruction.offset, "Function '" + function.name + "' of type '" + function.type +\
                                                "' cannot return type '" + instruction.type + "'!")

    def createAssignment(self, instruction, function, context):
        if (context == 'For'): context = 'ForSet'
        self.createNode(instruction.left, function, context)
        if (context == 'ForSet'): context = 'ForGet'
        self.createNode(instruction.right, function, context)
        if (context == 'ForGet'): context = 'For'

        if (instruction.left.nodeType == 'ID'):
            instruction.type = instruction.left.type
            instruction.name = instruction.left.name

            baseOp = re.match('([\+\-\*\/])\=', instruction.op)

            if (instruction.left.type == instruction.right.type):
                if (instruction.op == '='):
                    if (context == 'For'):
                        instruction.node = function.node.addSet(instruction.name, instruction.right.node, instruction.type);
                    else:
                        instruction.node = instruction.right.node
                elif (baseOp):
                    self.createMathOp(instruction, baseOp.group(1), function, context)
                else:
                    raise Snixception(instruction.offset, "Unsupported assign operand: '" + instruction.op + "'")
            else:
                raise Snixception(instruction.offset, "Can't assign type '" + instruction.right.type + "' to type '" + \
                                                        instruction.type + "'")
        else:
            raise Snixception(instruction.offset, "You can only assign values to variables. (Subscripting (assignign to index) also not yet supported.)")

    def createNode(self, instruction, function, context = None):
        if (instruction != None):
            if (instruction.nodeType == 'Declare'):
                self.createDeclare(instruction, function, context)
            elif (instruction.nodeType == 'Constant'):
                self.createConstant(instruction, function, context)
            elif (instruction.nodeType == 'ID'):
                self.createID(instruction, function, context)
            elif (instruction.nodeType == 'Return'):
                self.createReturn(instruction, function, context)
            elif (instruction.nodeType == 'UnaryOp'):
                self.createUnaryOp(instruction, function, context)
            elif (instruction.nodeType == 'Assignment'):
                self.createAssignment(instruction, function, context)
            elif (instruction.nodeType == 'BinaryOp'):
                self.createBinaryOp(instruction, function, context)
            elif (instruction.nodeType == 'FuncCall'):
                self.createFunctionCall(instruction, function, context)
            elif (instruction.nodeType == 'ExprList'):
                self.createExpressionList(instruction, function, context)
            elif (instruction.nodeType == 'CompoundLiteral'):
                self.createCompoundLiteral(instruction, function, context)
            elif (instruction.nodeType == 'InitList'):
                self.createInitList(instruction, function, context)
            elif (instruction.nodeType == 'If'):
                self.createIf(instruction, function, context)
            elif (instruction.nodeType == 'Compound'):
                self.createCompound(instruction, function, context)
            elif (instruction.nodeType == 'ArrayRef'):
                self.createArrayRef(instruction, function, context)
            elif (instruction.nodeType == 'Cast'):
                self.createCast(instruction, function, context)
            elif (instruction.nodeType == 'For'):
                self.createFor(instruction, function, context)
            elif (instruction.nodeType == 'DeclList'):
                self.createDeclList(instruction, function, context)
            elif (instruction.nodeType == 'EmptyStatement'):
                pass
            else:
                raise Snixception(instruction.offset, "Can't create node of unknown type '" + instruction.nodeType + "' (Internal error, please let developer know!)")

    def createFunctionInput(self, function, input):
        function.node.addFunctionInput(input.value.name, input.value.type, input.label)

        # Create the get node
        input.type = input.value.type
        type = input.type
        baseType = self.getBaseType(type)

        input.node = function.node.addGet(input.name, type)

    def createFunction(self, function):
        function.node = snixel.addFunction(function.name, function.type)

        self.systemNodes = []

        for input in function.inputs:
            self.createFunctionInput(function, input)

        for instruction in function.body.instructions:
            self.createNode(instruction, function)

        return function

    def compile(self, functions, outfile = None):
        self.populateNativeData()
        self.functions = []
        for function in functions:
            self.functions.append(self.createFunction(function))

            if (function.output != None and function.output.node != None):
                function.node.setOutput(function.output.node)
            else:
                raise Snixception(function.offset, "Function '" + function.name + "' has no return statement!")

        snixel.compile(outfile)

def parseArgs():
    global outfile, source
    parser = ArgumentParser(description='Snix Compiler.')
    parser.add_argument('source', metavar='SOURCE',
                   help='Snix source file to compile')
    parser.add_argument("-o", "--out", dest="outfile",
                    help="Substance Designer file destination", metavar="OUT")

    args = parser.parse_args()

    source = args.source;

    if (args.outfile):
        outfile = args.outfile

try:
    parseArgs()
    snixparser = sp.SnixParser()
    code = snixparser.readSource(source)

    cparser = c_parser.CParser()
    ast = cparser.parse(code)
    snix_dict = ast_to_dict(ast)

    functions = snixparser.parseFunctions(snix_dict)
    snixpiler = SnixCompiler(snixparser.defines)
    snixpiler.compile(functions, outfile)
except Snixception as e:
    print('[' + e.args[0] + '] Syntax Error: ' + e.args[1])
except plyparser.ParseError as e:
    err = re.match(r'^(.*?:[0-9]+?:[0-9]+?): (.*?)$', str(e))
    print('[' + err.group(1) + '] Parser Error: ' + err.group(2))
else:
    print("Compiled to file '" + outfile + "'")
