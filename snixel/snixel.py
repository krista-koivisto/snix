#!/bin/python
from . import sbswriter as sw
from .nodes import *

class SnixelFunction():
    base = ""
    name = ""
    baseFunction = ""
    type = None
    rootNode = None
    nodes = []
    inputs = []
    baseUID = 1332649438
    functions_uid = 0 # If you want to change this, change it in the Snixel class.
    dependencyUID = 0

    def __init__(self, base, name, dependency, functions_uid, type):
        self.nodes = []
        self.inputs = []
        self.base = base
        self.name = name
        self.type = self.getSizeFromType(type)
        self.functions_uid = functions_uid
        self.dependencyUID = dependency.uid
        self.baseFunction = self.base.addFunction(self.name, self.type)

    def getSizeFromType(self, type):
        if (type == 'bool'):
            return str(4)
        elif (type == 'string'):
            return str(16384)
        else:
            typeData = re.match('^(\w+?)([\d]|$)', type)
            typeName = typeData.group(1)
            typeSize = typeData.group(2)

            if (len(typeSize) == 0):
                typeSize = 1

            if (int(typeSize) > 4 or int(typeSize) < 1):
                raise Exception("Snixel Error: Unknown type '" + type + "'")

            if (typeName == 'float'):
                return str(pow(2, 7 + int(typeSize)))
            elif (typeName == 'int'):
                return str(pow(2, 3 + int(typeSize)))
            else:
                raise Exception("Snixel Error: Unknown type '" + str(type) + "'")

    def addInput(self, input):
        self.baseUID += 1
        self.inputs.append(input)

    def addNode(self, node):
        self.baseUID += 1
        self.nodes.append(node)
        return node

    # Comparison nodes
    def addIf(self, condition, ifNode, elseNode, type):
        return self.addNode(IfNode(self.baseUID, condition, ifNode, elseNode, type))

    def addEquals(self, a, b, type):
        if (type != 'bool'):
            return self.addNode(EqualsNode(self.baseUID, a, b, type))
        else:
            return self.addNode(InstanceNode(self.baseUID, 'Functions/Math/Equality_Boolean', [('A', a), ('B', b)], self.functions_uid))

    def addNotEquals(self, a, b, type):
        if (type != 'bool'):
            return self.addNode(NotEqualsNode(self.baseUID, a, b, type))
        else:
            return self.addNode(InstanceNode(self.baseUID, 'Functions/Math/NotEqual_Boolean', [('A', a), ('B', b)], self.functions_uid))

    def addGreaterThan(self, a, b, type):
        return self.addNode(GreaterThanNode(self.baseUID, a, b, type))

    def addGreaterOrEqual(self, a, b, type):
        return self.addNode(GreaterOrEqualNode(self.baseUID, a, b, type))

    def addLessThan(self, a, b, type):
        return self.addNode(LesserThanNode(self.baseUID, a, b, type))

    def addLessOrEqual(self, a, b, type):
        return self.addNode(LesserOrEqualNode(self.baseUID, a, b, type))

    # Constant nodes
    def addConst(self, value, type):
        return self.addNode(ConstNode(self.baseUID, value, type))

    def addConstFloat(self, value, type):
        return self.addNode(ConstFloatNode(self.baseUID, value, type))

    def addConstInt(self, value, type):
        return self.addNode(ConstIntNode(self.baseUID, value, type))

    def addConstBool(self, value):
        return self.addNode(ConstBoolNode(self.baseUID, value))

    def addConstString(self, value):
        return self.addNode(ConstStringNode(self.baseUID, value))

    # Cast nodes
    def addToFloat(self, value):
        return self.addNode(ToFloatNode(self.baseUID, value))

    def addToInt(self, value):
        return self.addNode(ToIntNode(self.baseUID, value))

    # Variable nodes
    def addSet(self, name, value, type):
        return self.addNode(SetNode(self.baseUID, name, value, type))

    def addGet(self, value, type):
        return self.addNode(GetNode(self.baseUID, value, type))

    # Sample nodes
    def addSampleGrayscale(self, pos):
        return self.addNode(SampleGrayscaleNode(self.baseUID, pos))

    def addSampleColor(self, pos):
        return self.addNode(SampleColorNode(self.baseUID, pos))

    # Vector nodes
    def addVectorFloat(self, componentsin, componentslast, type):
        return self.addNode(VectorFloatNode(self.baseUID, componentsin, componentslast, type))

    def addVectorInt(self, componentsin, componentslast, type):
        return self.addNode(VectorIntNode(self.baseUID, componentsin, componentslast, type))

    def addSwizzleFloat(self, vector, value):
        return self.addNode(SwizzleFloatNode(self.baseUID, vector, value))

    def addSwizzleInt(self, vector, value):
        return self.addNode(SwizzleIntNode(self.baseUID, vector, value))

    # Logic Nodes
    def addAnd(self, a, b):
        return self.addNode(AndNode(self.baseUID, a, b))

    def addNot(self, a):
        return self.addNode(NotNode(self.baseUID, a))

    def addOr(self, a, b):
        return self.addNode(OrNode(self.baseUID, a, b))

    # Math verb nodes
    def addAdd(self, a, b, type):
        return self.addNode(AddNode(self.baseUID, a, b, type))

    def addSubtract(self, a, b, type):
        return self.addNode(SubNode(self.baseUID, a, b, type))

    def addMultiply(self, a, b, type):
        return self.addNode(MulNode(self.baseUID, a, b, type))

    def addDivide(self, a, b, type):
        return self.addNode(DivNode(self.baseUID, a, b, type))

    def addDot(self, a, b, type):
        return self.addNode(DotNode(self.baseUID, a, b, type))

    def addMod(self, a, b, type):
        return self.addNode(ModNode(self.baseUID, a, b, type))

    def addNegate(self, a, type):
        return self.addNode(NegateNode(self.baseUID, a, type))

    def addScalarMultiply(self, a, b, type):
        return self.addNode(MulScalarNode(self.baseUID, a, b, type))

    # Functions
    def addAbs(self, a, type):
        return self.addNode(AbsNode(self.baseUID, a, type))

    def addFloor(self, a, type):
        return self.addNode(FloorNode(self.baseUID, a, type))

    def addCeil(self, a, type):
        return self.addNode(CeilNode(self.baseUID, a, type))

    def addCos(self, a, type):
        return self.addNode(CosNode(self.baseUID, a, type))

    def addSin(self, a, type):
        return self.addNode(SinNode(self.baseUID, a, type))

    def addTan(self, a, type):
        return self.addNode(TanNode(self.baseUID, a, type))

    def addArcTan2(self, a, type):
        return self.addNode(ArcTan2Node(self.baseUID, a, type))

    def addCartesian(self, theta, rho, type):
        return self.addNode(CartesianNode(self.baseUID, theta, rho, type))

    def addSqrt(self, a, type):
        return self.addNode(SqrtNode(self.baseUID, a, type))

    def addLog(self, a, type):
        return self.addNode(LogNode(self.baseUID, a, type))

    def addExp(self, a, type):
        return self.addNode(ExpNode(self.baseUID, a, type))

    def addLog2(self, a, type):
        return self.addNode(Log2Node(self.baseUID, a, type))

    def addPow2(self, a, type):
        return self.addNode(Pow2Node(self.baseUID, a, type))

    def addLerp(self, a, b, x, type):
        return self.addNode(LerpNode(self.baseUID, a, b, x, type))

    def addMin(self, a, b, type):
        return self.addNode(MinNode(self.baseUID, a, b, type))

    def addMax(self, a, b, type):
        return self.addNode(MaxNode(self.baseUID, a, b, type))

    def addRandom(self, a, type):
        return self.addNode(RandomNode(self.baseUID, a, type))

    def addReflect(self, incidence, normal, type):
        return self.addNode(InstanceNode(self.baseUID, 'Functions/Math/reflect', [('i', incidence), ('n', normal)], self.functions_uid))

    def addPow(self, n, x, type):
        return self.addNode(InstanceNode(self.baseUID, 'Functions/Math/Pow', [('n', n), ('x', x)], self.functions_uid))

    # Others
    def addFunctionCall(self, instance_name, connections):
        return self.addNode(InstanceNode(self.baseUID, instance_name, connections, self.dependencyUID))

    def addFunctionInput(self, name, type, label = ""):
        return self.addInput(FunctionInput(self.baseUID, name, type, label))

    def setOutput(self, node):
        self.rootNode = node

    def hasOutput(self):
        if (self.rootNode == None):
            return 0

        return 1

    def compile(self):
        self.baseFunction.setRootNode(str(self.rootNode.uid))

        for input in self.inputs:
            self.baseFunction.addInput(input.base)

        for node in self.nodes:
            for data in node.data:
                funcData = sw.FuncData(data[0])
                funcData.addCustomData(data[1], [(data[2], 'v', data[3])])
                node.base.addFuncData(funcData)

            for connection in node.connections:
                con = sw.Connection(connection[0], str(connection[1].uid))
                node.base.addConnection(con)

            self.baseFunction.addParamNode(node.base)

class Snixel():
    writer = sw.SBSWriter()
    functions = []
    dependency = None
    dependency_uid = 1333113717
    functions_uid = 1290776887

    def __init__(self):
        self.dependency = sw.Dependency('?himself', self.dependency_uid)
        SDFunctions = sw.Dependency('sbs://functions.sbs', self.functions_uid)
        self.writer.package.addDependency(self.dependency)
        self.writer.package.addDependency(SDFunctions)
        sw.debug_level = 0

    def addFunction(self, name, type):
        function = SnixelFunction(self.writer, name, self.dependency, self.functions_uid, type)
        self.functions.append(function)
        return function

    def compile(self, outfile = None):
        for function in self.functions:
            function.compile()

        return self.writer.write(outfile)
