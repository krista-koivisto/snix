from . import sbswriter as sw
import re

class TypeHelper:
    def isTypeAllowed(self, type, onlyTypes):
        if (onlyTypes != None):
            if (type in onlyTypes):
                return 1
            else:
                return 0

        return 1

    def verifyType(self, type, onlyTypes):
        if (not self.isTypeAllowed(type, onlyTypes)):
            raise Exception("Snixel Error: Type '" + str(type) + "' is not allowed here!")

    def getSize(self, type):
        if (type == 'bool'):
            return 1
        elif (type == 'string'):
            return 1
        else:
            typeData = re.match('^(\w+?)([\d]|$)', type)
            typeName = typeData.group(1)
            typeSize = typeData.group(2)

            if (len(typeSize) == 0):
                typeSize = 1

            if (int(typeSize) > 4 or int(typeSize) < 1):
                raise Exception("Snixel Error: Unknown type '" + type + "'")

            if (typeName == 'float'):
                return typeSize
            elif (typeName == 'int'):
                return typeSize
            else:
                raise Exception("Snixel Error: Unknown type '" + type + "'")

    def getBaseType(self, type):
        return re.sub('\d', '', type);

    def getVectorSize(self, type):
        typeSize = re.match('\D+?(\d)', type)

        if (typeSize == None):
            return 1
        else:
            return typeSize.group(1)


    def getType(self, type, onlyTypes = None):
        if (self.isTypeAllowed(type, onlyTypes)):
            if (type == 'bool'):
                return str(4)
            elif (type == 'string'):
                return str(16384)
            else:
                typeName = re.sub('\d', '', type)
                typeSize = self.getSize(type)

                if (typeName == 'float'):
                    return str(pow(2, 7 + int(typeSize)))
                elif (typeName == 'int'):
                    return str(pow(2, 3 + int(typeSize)))
                else:
                    raise Exception("Snixel Error: Unknown type '" + str(type) + "'")
        else:
            raise Exception("Snixel Error: Type '" + str(type) + "' is not allowed here!")

class BaseNode:
    uid = 0
    base = 0
    type = 256
    connections = []
    data = []
    helper = TypeHelper()

    def addConnection(self, name, connector):
        self.connections.append((name, connector))

    def addData(self, name, group, value_name, value):
        self.data.append((name, group, value_name, value))

class BaseInput:
    uid = ""
    type = 256
    name = ''
    label = ''
    constValue = ''
    size = 0
    helper = TypeHelper()

    def init(self, type, uid, name, constValue, size, label):
        self.uid = str(uid)
        self.type = str(type)
        self.name = name
        self.size = size
        self.label = label
        self.constValue = constValue
        self.base = sw.ParamInput(self.name, self.uid, self.type, self.constValue, self.size, self.label)

# ----------------
# Comparison nodes
# ----------------

class IfNode(BaseNode):
    def __init__(self, uid, conditionNode, ifNode, elseNode, type):
        self.uid = uid
        self.type = self.helper.getType(type)
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('ifelse', str(self.uid), str(self.type))
        self.addConnection('condition', conditionNode)
        self.addConnection('ifpath', ifNode)
        self.addConnection('elsepath', elseNode)

class EqualsNode(BaseNode):
    def __init__(self, uid, a, b, type):
        self.helper.verifyType(type, ['int', 'float'])
        self.uid = uid
        self.type = 4
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('eq', str(self.uid), str(self.type))
        self.addConnection('a', a)
        self.addConnection('b', b)

class NotEqualsNode(BaseNode):
    def __init__(self, uid, a, b, type):
        self.helper.verifyType(type, ['int', 'float'])
        self.uid = uid
        self.type = 4
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('noteq', str(self.uid), str(self.type))
        self.addConnection('a', a)
        self.addConnection('b', b)

class GreaterThanNode(BaseNode):
    def __init__(self, uid, a, b, type):
        self.helper.verifyType(type, ['int', 'float'])
        self.uid = uid
        self.type = 4
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('gt', str(self.uid), str(self.type))
        self.addConnection('a', a)
        self.addConnection('b', b)

class GreaterOrEqualNode(BaseNode):
    def __init__(self, uid, a, b, type):
        self.helper.verifyType(type, ['int', 'float'])
        self.uid = uid
        self.type = 4
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('gteq', str(self.uid), str(self.type))
        self.addConnection('a', a)
        self.addConnection('b', b)

class LesserThanNode(BaseNode):
    def __init__(self, uid, a, b, type):
        self.helper.verifyType(type, ['int', 'float'])
        self.uid = uid
        self.type = 4
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('lr', str(self.uid), str(self.type))
        self.addConnection('a', a)
        self.addConnection('b', b)

class LesserOrEqualNode(BaseNode):
    def __init__(self, uid, a, b, type):
        self.helper.verifyType(type, ['int', 'float'])
        self.uid = uid
        self.type = 4
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('lreq', str(self.uid), str(self.type))
        self.addConnection('a', a)
        self.addConnection('b', b)

# --------------
# Constant nodes
# --------------

class ConstNode(BaseNode):
    def __init__(self, uid, value, type):
        vectorSize = self.helper.getVectorSize(type)
        baseType = self.helper.getBaseType(type)
        size = str(self.helper.getSize(type))
        name = 'const_' + baseType + str(vectorSize)
        valueName = 'constantValue' + baseType.title() + str(vectorSize)
        values = ''
        for i in range(int(vectorSize)):
            values += str(value) + ' '

        self.uid = uid
        self.type = self.helper.getType(type)
        self.connections = []
        self.data = []
        self.base = sw.ParamNode(name, str(self.uid), str(self.type))
        self.addData(name, 'constantValue', valueName, values[:-1])

class ConstFloatNode(BaseNode):
    def __init__(self, uid, value, type):
        size = str(self.helper.getSize(type))
        name = 'const_float' + size
        allowedTypes = ['float', 'float2', 'float3', 'float4']
        self.uid = uid
        self.type = self.helper.getType(type, allowedTypes)
        self.connections = []
        self.data = []
        self.base = sw.ParamNode(name, str(self.uid), str(self.type))
        self.addData(name, 'constantValue', 'constantValueFloat' + size, str(value))

class ConstIntNode(BaseNode):
    def __init__(self, uid, value, type):
        size = str(self.helper.getSize(type))
        name = 'const_int' + size
        allowedTypes = ['int', 'int2', 'int3', 'int4']
        self.uid = uid
        self.type = self.helper.getType(type, allowedTypes)
        self.connections = []
        self.data = []
        self.base = sw.ParamNode(name, str(self.uid), str(self.type))
        self.addData(name, 'constantValue', 'constantValueInt' + size, str(value))

class ConstBoolNode(BaseNode):
    def __init__(self, uid, value):
        self.uid = uid
        self.type = 4
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('const_bool', str(self.uid), str(self.type))
        self.addData('const_bool', 'constantValue', 'constantValueBool', str(value))

class ConstStringNode(BaseNode):
    def __init__(self, uid, value):
        self.uid = uid
        self.type = 16384
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('const_string', str(self.uid), str(self.type))
        self.addData('const_string', 'constantValue', 'constantValueString', str(value))

# --------------
# Function nodes
# --------------

class InstanceNode(BaseNode):
    def __init__(self, uid, instance_name, connections, dependency_uid):
        self.uid = uid
        self.type = 16
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('instance', str(self.uid), str(self.type))
        instance_str = "pkg:///" + instance_name + "?dependency=" + str(dependency_uid)
        self.addData('instance', 'constantValue', 'constantValueString', instance_str)

        for connection in connections:
            self.addConnection(connection[0], connection[1])

class FunctionInput(BaseInput):
    def __init__(self, uid, name, type, label):
        size = self.helper.getSize(type)
        if (type == 'bool' or type == 'string'):
            constValue = 'constantValueString'
        else:
            constValue = 'constantValue' + str(self.helper.getBaseType(type)).title() + str(self.helper.getSize(type))
        self.init(self.helper.getType(type), uid, name, constValue, size, label)

class AbsNode(BaseNode):
    def __init__(self, uid, a, type):
        allowedTypes = ['float', 'float2', 'float3', 'float4',
                        'int']
        self.uid = uid
        self.type = self.helper.getType(type, allowedTypes)
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('abs', str(self.uid), str(self.type))
        self.addConnection('a', a)

class FloorNode(BaseNode):
    def __init__(self, uid, a, type):
        allowedTypes = ['float', 'float2', 'float3', 'float4']
        self.uid = uid
        self.type = self.helper.getType(type, allowedTypes)
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('floor', str(self.uid), str(self.type))
        self.addConnection('a', a)

class CeilNode(BaseNode):
    def __init__(self, uid, a, type):
        allowedTypes = ['float', 'float2', 'float3', 'float4']
        self.uid = uid
        self.type = self.helper.getType(type, allowedTypes)
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('ceil', str(self.uid), str(self.type))
        self.addConnection('a', a)

class CosNode(BaseNode):
    def __init__(self, uid, a, type):
        allowedTypes = ['float', 'float2', 'float3', 'float4']
        self.uid = uid
        self.type = self.helper.getType(type, allowedTypes)
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('cos', str(self.uid), str(self.type))
        self.addConnection('a', a)

class SinNode(BaseNode):
    def __init__(self, uid, a, type):
        allowedTypes = ['float', 'float2', 'float3', 'float4']
        self.uid = uid
        self.type = self.helper.getType(type, allowedTypes)
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('sin', str(self.uid), str(self.type))
        self.addConnection('a', a)

class TanNode(BaseNode):
    def __init__(self, uid, a, type):
        allowedTypes = ['float', 'float2', 'float3', 'float4']
        self.uid = uid
        self.type = self.helper.getType(type, allowedTypes)
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('tan', str(self.uid), str(self.type))
        self.addConnection('a', a)

class ArcTan2Node(BaseNode):
    def __init__(self, uid, a, type):
        allowedTypes = ['float2']
        self.helper.verifyType(type, allowedTypes)
        self.uid = uid
        self.type = 256
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('atan2', str(self.uid), str(self.type))
        self.addConnection('a', a)

class CartesianNode(BaseNode):
    def __init__(self, uid, theta, rho, type):
        allowedTypes = ['float']
        self.helper.verifyType(type, allowedTypes)
        self.uid = uid
        self.type = 512
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('cartesian', str(self.uid), str(self.type))
        self.addConnection('theta', theta)
        self.addConnection('rho', rho)

class SqrtNode(BaseNode):
    def __init__(self, uid, a, type):
        allowedTypes = ['float', 'float2', 'float3', 'float4']
        self.uid = uid
        self.type = self.helper.getType(type, allowedTypes)
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('sqrt', str(self.uid), str(self.type))
        self.addConnection('a', a)

class LogNode(BaseNode):
    def __init__(self, uid, a, type):
        allowedTypes = ['float', 'float2', 'float3', 'float4']
        self.uid = uid
        self.type = self.helper.getType(type, allowedTypes)
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('log', str(self.uid), str(self.type))
        self.addConnection('a', a)

class ExpNode(BaseNode):
    def __init__(self, uid, a, type):
        allowedTypes = ['float', 'float2', 'float3', 'float4']
        self.uid = uid
        self.type = self.helper.getType(type, allowedTypes)
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('exp', str(self.uid), str(self.type))
        self.addConnection('a', a)

class Log2Node(BaseNode):
    def __init__(self, uid, a, type):
        allowedTypes = ['float', 'float2', 'float3', 'float4']
        self.uid = uid
        self.type = self.helper.getType(type, allowedTypes)
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('log2', str(self.uid), str(self.type))
        self.addConnection('a', a)

class Pow2Node(BaseNode):
    def __init__(self, uid, a, type):
        allowedTypes = ['float', 'float2', 'float3', 'float4']
        self.uid = uid
        self.type = self.helper.getType(type, allowedTypes)
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('pow2', str(self.uid), str(self.type))
        self.addConnection('a', a)

class LerpNode(BaseNode):
    def __init__(self, uid, a, b, x, type):
        allowedTypes = ['float', 'float2', 'float3', 'float4']
        self.uid = uid
        self.type = self.helper.getType(type, allowedTypes)
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('lerp', str(self.uid), str(self.type))
        self.addConnection('a', a)
        self.addConnection('b', b)
        self.addConnection('x', x)

class MinNode(BaseNode):
    def __init__(self, uid, a, b, type):
        allowedTypes = ['float', 'float2', 'float3', 'float4',
                        'int', 'int2', 'int3', 'int4']
        self.uid = uid
        self.type = self.helper.getType(type, allowedTypes)
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('min', str(self.uid), str(self.type))
        self.addConnection('a', a)
        self.addConnection('b', b)

class MaxNode(BaseNode):
    def __init__(self, uid, a, b, type):
        allowedTypes = ['float', 'float2', 'float3', 'float4',
                        'int', 'int2', 'int3', 'int4']
        self.uid = uid
        self.type = self.helper.getType(type, allowedTypes)
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('max', str(self.uid), str(self.type))
        self.addConnection('a', a)
        self.addConnection('b', b)

class RandomNode(BaseNode):
    def __init__(self, uid, a, type):
        allowedTypes = ['float']
        self.helper.verifyType(type, allowedTypes)
        self.uid = uid
        self.type = 256
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('rand', str(self.uid), str(self.type))
        self.addConnection('a', a)

class SampleGrayscaleNode(BaseNode):
    def __init__(self, uid, pos):
        self.uid = uid
        self.type = 256
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('samplelum', str(self.uid), str(self.type))
        self.addConnection('pos', pos)

class SampleColorNode(BaseNode):
    def __init__(self, uid, pos):
        self.uid = uid
        self.type = 2048
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('samplecol', str(self.uid), str(self.type))
        self.addConnection('pos', pos)

# -----------
# Logic nodes
# -----------

class AndNode(BaseNode):
    def __init__(self, uid, a, b):
        self.uid = uid
        self.type = 4
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('and', str(self.uid), str(self.type))
        self.addConnection('a', a)
        self.addConnection('b', b)

class NotNode(BaseNode):
    def __init__(self, uid, a):
        self.uid = uid
        self.type = 4
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('not', str(self.uid), str(self.type))
        self.addConnection('a', a)

class OrNode(BaseNode):
    def __init__(self, uid, a, b):
        self.uid = uid
        self.type = 4
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('or', str(self.uid), str(self.type))
        self.addConnection('a', a)
        self.addConnection('b', b)

# ----------
# Math nodes
# ----------

class AddNode(BaseNode):
    def __init__(self, uid, a, b, type):
        allowedTypes = ['float', 'float2', 'float3', 'float4',
                        'int', 'int2', 'int3', 'int4']
        self.uid = uid
        self.type = self.helper.getType(type, allowedTypes)
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('add', str(self.uid), str(self.type))
        self.addConnection('a', a)
        self.addConnection('b', b)

class SubNode(BaseNode):
    def __init__(self, uid, a, b, type):
        allowedTypes = ['float', 'float2', 'float3', 'float4',
                        'int', 'int2', 'int3', 'int4']
        self.uid = uid
        self.type = self.helper.getType(type, allowedTypes)
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('sub', str(self.uid), str(self.type))
        self.addConnection('a', a)
        self.addConnection('b', b)

class MulNode(BaseNode):
    def __init__(self, uid, a, b, type):
        allowedTypes = ['float', 'float2', 'float3', 'float4',
                        'int', 'int2', 'int3', 'int4']
        self.uid = uid
        self.type = self.helper.getType(type, allowedTypes)
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('mul', str(self.uid), str(self.type))
        self.addConnection('a', a)
        self.addConnection('b', b)

class DivNode(BaseNode):
    def __init__(self, uid, a, b, type):
        allowedTypes = ['float', 'float2', 'float3', 'float4',
                        'int', 'int2', 'int3', 'int4']
        self.uid = uid
        self.type = self.helper.getType(type, allowedTypes)
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('div', str(self.uid), str(self.type))
        self.addConnection('a', a)
        self.addConnection('b', b)

class DotNode(BaseNode):
    def __init__(self, uid, a, b, type):
        allowedTypes = ['float2', 'float3', 'float4']
        self.uid = uid
        self.type = 256
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('dot', str(self.uid), str(self.type))
        self.addConnection('a', a)
        self.addConnection('b', b)

class ModNode(BaseNode):
    def __init__(self, uid, a, b, type):
        allowedTypes = ['float', 'float2', 'float3', 'float4', 'int']
        self.uid = uid
        self.type = self.helper.getType(type, allowedTypes)
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('mod', str(self.uid), str(self.type))
        self.addConnection('a', a)
        self.addConnection('b', b)

class NegateNode(BaseNode):
    def __init__(self, uid, a, type):
        allowedTypes = ['float', 'float2', 'float3', 'float4', 'int']
        self.uid = uid
        self.type = self.helper.getType(type, allowedTypes)
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('neg', str(self.uid), str(self.type))
        self.addConnection('a', a)

class MulScalarNode(BaseNode):
    def __init__(self, uid, a, b, type):
        allowedTypes = ['float2', 'float3', 'float4']
        self.uid = uid
        self.type = self.helper.getType(type, allowedTypes)
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('mulscalar', str(self.uid), str(self.type))
        self.addConnection('a', a)
        self.addConnection('scalar', b)

# --------------
# Variable nodes
# --------------

class ToFloatNode(BaseNode):
    def __init__(self, uid, value):
        self.uid = uid
        self.type = 256
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('tofloat', str(self.uid), str(self.type))
        self.addConnection('value', value)

class ToIntNode(BaseNode):
    def __init__(self, uid, value):
        self.uid = uid
        self.type = 16
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('toint1', str(self.uid), str(self.type))
        self.addConnection('value', value)

class SetNode(BaseNode):
    def __init__(self, uid, name, value, type):
        self.uid = uid
        self.type = self.helper.getType(type)
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('set', str(self.uid), str(self.type))
        self.addData('set', 'constantValue', 'constantValueString', str(name))
        self.addConnection('value', value)

class GetNode(BaseNode):
    def __init__(self, uid, value, type):
        baseType = self.helper.getBaseType(type)
        if (baseType == 'int'):
            name = 'get_integer' + str(self.helper.getSize(type))
        elif (baseType == 'float'):
            name = 'get_float' + str(self.helper.getSize(type))
        else:
            name = 'get_' + type
        self.uid = uid
        self.type = self.helper.getType(type)
        self.connections = []
        self.data = []
        self.base = sw.ParamNode(name, str(self.uid), str(self.type))
        self.addData(name, 'constantValue', 'constantValueString', str(value))

# ------------
# Vector nodes
# ------------

class VectorFloatNode(BaseNode):
    def __init__(self, uid, componentsin, componentslast, type):
        name = 'vector' + type[-1]
        self.uid = uid
        self.type = self.helper.getType(type, ['float2', 'float3', 'float4'])
        self.connections = []
        self.data = []
        self.base = sw.ParamNode(name, str(self.uid), str(self.type))
        self.addConnection('componentsin', componentsin)
        self.addConnection('componentslast', componentslast)

class VectorIntNode(BaseNode):
    def __init__(self, uid, componentsin, componentslast, type):
        name = 'ivector' + type[-1]
        self.uid = uid
        self.type = self.helper.getType(type, ['int2', 'int3', 'int4'])
        self.connections = []
        self.data = []
        self.base = sw.ParamNode(name, str(self.uid), str(self.type))
        self.addConnection('componentsin', componentsin)
        self.addConnection('componentslast', componentslast)

class SwizzleFloatNode(BaseNode):
    def __init__(self, uid, vector, value):
        self.uid = uid
        self.type = 256
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('swizzle1', str(self.uid), str(self.type))
        self.addData('swizzle1', 'constantValue', 'constantValueInt1', value)
        self.addConnection('vector', vector)

class SwizzleIntNode(BaseNode):
    def __init__(self, uid, vector, value):
        self.uid = uid
        self.type = 16
        self.connections = []
        self.data = []
        self.base = sw.ParamNode('iswizzle1', str(self.uid), str(self.type))
        self.addData('iswizzle1', 'constantValue', 'constantValueInt1', value)
        self.addConnection('vector', vector)
