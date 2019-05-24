from exception import Snixception
import pprint
import re

class NodeBase():
    nodeType = None
    type = None
    file = None
    offset = None
    node = None

    def getNode(self, instruction):
        if (instruction != None):
            if (instruction['_nodetype'] == 'Constant'):
                return ConstantNode(instruction)
            elif (instruction['_nodetype'] == 'Decl'):
                return DeclareNode(instruction)
            elif (instruction['_nodetype'] == 'ID'):
                return IDNode(instruction)
            elif (instruction['_nodetype'] == 'Return'):
                return ReturnNode(instruction)
            elif (instruction['_nodetype'] == 'UnaryOp'):
                return UnaryOpNode(instruction)
            elif (instruction['_nodetype'] == 'Assignment'):
                return AssignmentNode(instruction)
            elif (instruction['_nodetype'] == 'BinaryOp'):
                return BinaryOpNode(instruction)
            elif (instruction['_nodetype'] == 'FuncCall'):
                return FuncCallNode(instruction)
            elif (instruction['_nodetype'] == 'ExprList'):
                return ExprListNode(instruction)
            elif (instruction['_nodetype'] == 'CompoundLiteral'):
                return CompoundLiteralNode(instruction)
            elif (instruction['_nodetype'] == 'InitList'):
                return InitListNode(instruction)
            elif (instruction['_nodetype'] == 'If'):
                return IfNode(instruction)
            elif (instruction['_nodetype'] == 'Compound'):
                return CompoundNode(instruction)
            elif (instruction['_nodetype'] == 'ArrayRef'):
                return ArrayRefNode(instruction)
            elif (instruction['_nodetype'] == 'Cast'):
                return CastNode(instruction)
            elif (instruction['_nodetype'] == 'EmptyStatement'):
                return EmptyStatementNode(instruction)
            elif (instruction['_nodetype'] == 'For'):
                return ForNode(instruction)
            elif (instruction['_nodetype'] == 'DeclList'):
                return DeclListNode(instruction)
            else:
                if (instruction['coord'] != None):
                    raise Snixception(instruction['coord'], "Unknown node type '" + instruction['_nodetype'] + "'")
                else:
                    raise Snixception('?', "Unknown node type '" + instruction['_nodetype'] + "'")
        else:
            return None

    def offsetFix(self):
        if (self.offset == None):
            self.offset = '?'

class ConstantNode(NodeBase):
    value = None

    def __init__(self, instruction):
        self.nodeType = 'Constant'
        self.offset = instruction['coord']
        self.type = instruction['type']
        self.value = self.cleanValue(instruction['value'], self.type)
        self.offsetFix()

    def cleanValue(self, value, type):
        if (type == 'float'):
            clean = re.match(r'([0-9\.]+)', str(value))
            return clean.group(1)
        elif (type == 'int'):
            clean = re.match(r'([0-9]+)', str(value))
            return clean.group(1)
        else:
            return value

class CustomNode(NodeBase):
    def __init__(self):
        self.nodeType = 'Custom'
        self.offset = '?'

class IDNode(NodeBase):
    name = None

    def __init__(self, instruction):
        self.nodeType = 'ID'
        self.offset = instruction['coord']
        self.name = instruction['name']
        self.offsetFix()

class CastNode(NodeBase):
    expression = None
    toType = None

    def __init__(self, instruction):
        self.nodeType = 'Cast'
        self.offset = instruction['coord']
        self.expression = self.getNode(instruction['expr'])
        self.toType = instruction['to_type']['type']['type']['names'][0]
        self.offsetFix()

class ForNode(NodeBase):
    condition = None
    init = None
    next = None
    body = None

    def __init__(self, instruction):
        self.nodeType = 'For'
        self.offset = instruction['coord']
        self.condition = self.getNode(instruction['cond'])
        self.init = self.getNode(instruction['init'])
        self.next = self.getNode(instruction['next'])
        self.body = self.getNode(instruction['stmt'])
        self.offsetFix()

class ArrayRefNode(NodeBase):
    variable = None
    subscript = None

    def __init__(self, instruction):
        self.nodeType = 'ArrayRef'
        self.offset = instruction['coord']
        self.variable = self.getNode(instruction['name'])
        self.subscript = self.getNode(instruction['subscript'])
        self.offsetFix()

class UnaryOpNode(NodeBase):
    value = None
    op = None

    def __init__(self, instruction):
        self.nodeType = 'UnaryOp'
        self.offset = instruction['coord']
        self.op = instruction['op']
        self.value = self.getNode(instruction['expr'])
        self.offsetFix()
        # Remove the p if it exists as we don't use any pointers
        if (self.op[0] == 'p'):
            self.op = self.op[1:]

class BinaryOpNode(NodeBase):
    left = None
    right = None
    op = None

    def __init__(self, instruction):
        self.nodeType = 'BinaryOp'
        self.offset = instruction['coord']
        self.op = instruction['op']
        self.left = self.getNode(instruction['left'])
        self.right = self.getNode(instruction['right'])
        self.offsetFix()
        # Remove the p if it exists as we don't use any pointers
        if (self.op[0] == 'p'):
            self.op = self.op[1:]

class FuncCallNode(NodeBase):
    name = None
    args = None

    def __init__(self, instruction):
        self.nodeType = 'FuncCall'
        self.offset = instruction['coord']
        if (instruction['name']['_nodetype'] != 'ID'):
            raise Snixception(instruction['coord'], "Only named functions can be called!")
        self.name = instruction['name']['name']
        self.args = self.getNode(instruction['args'])
        self.offsetFix()

class IfNode(NodeBase):
    condition = None
    iffalse = None
    iftrue = None

    def __init__(self, instruction):
        self.nodeType = 'If'
        self.offset = instruction['coord']
        self.condition = self.getNode(instruction['cond'])
        self.iffalse = self.getNode(instruction['iffalse'])
        self.iftrue = self.getNode(instruction['iftrue'])
        self.offsetFix()

class CompoundNode(NodeBase):
    instructions = []

    def __init__(self, instruction):
        self.instructions = []
        self.nodeType = 'Compound'
        self.offset = instruction['coord']
        self.parse(instruction)
        self.offsetFix()

    def parse(self, body):
        if (body['block_items'] != None):
            for child in body['block_items']:
                self.instructions.append(self.getNode(child))
        else:
            raise Snixception(body['coord'], "Empty compound bodies are not allowed!")

class EmptyStatementNode(NodeBase):
    def __init__(self, instruction):
        self.nodeType = 'EmptyStatement'
        self.offset = instruction['coord']
        self.offsetFix()

class DeclListNode(NodeBase):
    values = []

    def __init__(self, instruction):
        self.values = []
        self.nodeType = 'DeclList'
        self.offset = instruction['coord']
        self.offsetFix()
        for decl in instruction['decls']:
            self.values.append(self.getNode(decl))

class InitListNode(NodeBase):
    values = []

    def __init__(self, instruction):
        self.values = []
        self.nodeType = 'InitList'
        self.offset = instruction['coord']
        self.offsetFix()
        for expr in instruction['exprs']:
            self.values.append(self.getNode(expr))

class ExprListNode(NodeBase):
    values = []

    def __init__(self, instruction):
        self.values = []
        self.nodeType = 'ExprList'
        self.offset = instruction['coord']
        for expr in instruction['exprs']:
            self.values.append(self.getNode(expr))

class CompoundLiteralNode(NodeBase):
    value = None

    def __init__(self, instruction):
        self.nodeType = 'CompoundLiteral'
        self.offset = instruction['init']['coord']
        self.type = instruction['type']['type']['type']['names'][0]
        self.value = self.getNode(instruction['init'])
        self.offsetFix()

class AssignmentNode(NodeBase):
    left = None
    right = None
    name = None
    op = None

    def __init__(self, instruction):
        self.nodeType = 'Assignment'
        self.offset = instruction['coord']
        self.op = instruction['op']
        self.left = self.getNode(instruction['lvalue'])
        self.right = self.getNode(instruction['rvalue'])
        self.offsetFix()

class ReturnNode(NodeBase):
    value = None

    def __init__(self, instruction):
        self.nodeType = 'Return'
        self.offset = instruction['coord']
        self.value = self.getNode(instruction['expr'])
        self.offsetFix()

class BodyNode(NodeBase):
    instructions = []

    def __init__(self, instruction):
        self.instructions = []
        self.nodeType = 'Body'
        self.offset = instruction['coord']
        self.parse(instruction)
        self.offsetFix()

    def parse(self, body):
        if (body['block_items'] != None):
            for child in body['block_items']:
                self.instructions.append(self.getNode(child))
        else:
            raise Snixception(body['coord'], "Empty bodies are not allowed!")

class DeclareNode(NodeBase):
    value = None

    def __init__(self, stmt):
        self.nodeType = 'Declare'
        self.offset = stmt['coord']
        self.name = stmt['type']['declname']
        self.type = stmt['type']['type']['names'][0]
        self.offsetFix()
        if (stmt['init'] != None):
            self.value = self.getNode(stmt['init'])

class InputNode(NodeBase):
    name = None
    label = None
    value = None

    def __init__(self, stmt):
        self.nodeType = 'Input'
        self.offset = stmt['coord']
        self.offsetFix()

        if (stmt['init'] != None):
            raise Snixception(stmt['coord'], "You can't set a default value for a function parameter in Substance Designer! ('" + \
                                            stmt['type']['declname'] + "' in function '" + self.name + "')")
        if (stmt['_nodetype'] != 'Decl' or stmt['type']['_nodetype'] != 'TypeDecl'):
            raise Snixception(stmt['coord'], "Unknown parameter type for function '" + self.name + "'")

        self.value = DeclareNode(stmt)
        self.name = self.value.name
        self.label = re.sub('_', ' ', self.name).title()

class FunctionNode(NodeBase):
    name = ''
    body = None
    inputs = []
    output = None

    def __init__(self, func):
        self.nodeType = "Function"
        self.type = func['decl']['type']['type']['type']['names'][0]
        self.name = func['decl']['name']
        self.offset = func['coord']
        self.inputs = []
        self.file = ''
        self.body = BodyNode(func['body'])
        self.parseInputs(func)
        self.offsetFix()

    def parseInputs(self, func):
        if (func['decl']['type']['args']):
            params = func['decl']['type']['args']['params']

            for param in params:
                self.inputs.append(InputNode(param))
