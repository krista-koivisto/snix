import xml.etree.ElementTree as ET
from xml.dom import minidom
debug_level = 2
function_uid = 1342649436

def debug_print(text, level = 1):
    global debug_level

    if (debug_level >= level):
        print(text)

    def printItems(self):
        print(self.items)

class Snixception(RuntimeError):
    def __init__(self, offset, msg):
        self.args = (offset, msg)

class ItemBase:
    items = []

    def addItem(self, item, values = []):
        self.items.append((item, values))

    def compile(self, type):
        raise Exception("SBS Writer: Compile not yet implemented for this object!")

class Option(ItemBase):
    name = ""
    value = ""

    def __init__(self, name, value):
        self.items = []
        self.name = name
        self.value = value
        self.addItem('name', [("v", self.name)])
        self.addItem('value', [("v", self.value)])

    def compile(self, xml_options):
        xml_option = ET.SubElement(xml_options, 'option')
        for item in self.items:
            debug_print('        ' + item[0] + ':')
            xml_item = ET.SubElement(xml_option, item[0])
            for value in item[1]:
                debug_print('            ' + value[0] + ': ' + value[1])
                xml_item.set(value[0], value[1])

class Graph(ItemBase):
    options = [Option("defaultParentSize", "9x9")]
    identifier = ""
    uid = "1332648088"

    def __init__(self, identifier = "Snix Functions"):
        self.items = []
        self.identifier = identifier
        self.addItem('identifier', [("v", self.identifier)])
        self.addItem('uid', [("v", self.uid)])
        self.addItem('graphOutputs')
        self.addItem('compNodes')
        self.addItem('baseParameters')
        self.addItem('options')
        self.addItem('root')

    def compile(self, xml_graph):
            for item in self.items:
                debug_print('    ' + item[0] + ':')
                xml_item = ET.SubElement(xml_graph, item[0])
                for value in item[1]:
                    debug_print('        ' + value[0] + ': ' + value[1])
                    xml_item.set(value[0], value[1])

            debug_print('    Graph options:')
            xml_options = ET.SubElement(xml_graph, 'options')
            for option in self.options:
                option.compile(xml_options)


class Connection(ItemBase):
    identifier = ""
    connRef = "";

    def __init__(self, identifier, connection):
        self.items = []
        self.identifier = identifier
        self.connRef = connection
        self.addItem('identifier', [("v", self.identifier)])
        self.addItem('connRef', [("v", self.connRef)])

    def compile(self, xml_connections):
        for item in self.items:
            debug_print('    ' + item[0] + ':')
            xml_item = ET.SubElement(xml_connections, item[0])
            for value in item[1]:
                debug_print('        ' + value[0] + ': ' + value[1])
                xml_item.set(value[0], value[1])

class Widget(ItemBase):
    type = ''
    stepSize = 1
    options = []

    def __init__(self, type, step = 1, createDefaults = 1):
        self.items = []
        self.type = type
        self.stepSize = step
        self.addItem('name', [("v", self.type)])

        if (createDefaults):
            if (type == 'slider'):
                self.addSliderOptions()
            elif  (type == 'buttons'):
                self.addButtonsOptions()
            elif  (type == 'text'):
                self.addTextOptions()
            else:
                raise Exception("SBS Writer: Unknown widget type '" + type + "'")


    def addOption(self, option):
        self.options.append(option)

    def addSliderOptions(self):
        self.addOption(Option('clamp', '0'))
        self.addOption(Option('default', '0'))
        self.addOption(Option('max', str(self.stepSize * 100)))
        self.addOption(Option('min', '0'))
        self.addOption(Option('step', str(self.stepSize)))

    def addButtonsOptions(self):
        self.addOption(Option('booleditortype', 'pushbuttons'))
        self.addOption(Option('default', '0'))
        self.addOption(Option('label0', 'False'))
        self.addOption(Option('label1', 'True'))

    def addTextOptions(self):
        self.addOption(Option('default', ''))

    def compile(self, xml_connections):
        debug_print('    Widget options:')
        xml_options = ET.SubElement(xml_graph, 'options')
        for option in self.options:
            option.compile(xml_options)

class ParamInput(ItemBase):
    uid = "1332649438"
    name = ""
    label = ""
    size = 1
    type = "256"
    widget = "slider"
    constValue = "constantValueFloat1"
    defaultValue = "1"
    defaultWidget = None
    customData = []

    def __init__(self, name, uid = "1332649438", type = "256", constValue = "constantValueFloat1", size = 1, label = ""):
        self.items = []
        self.customData = []
        self.inputOptions = []
        self.uid = uid
        self.type = type
        self.name = name
        self.label = label
        self.constValue = constValue
        self.defaultValue = ''
        self.addItem('uid', [("v", self.uid)])
        self.addItem('identifier', [("v", self.name)])
        self.addItem('type', [("v", self.type)])

        if (int(type) == 4):
            self.setTypeBool()
        elif (int(type) >= 16 and int(type) <= 128):
            self.setTypeInt(type, size)
        elif (int(type) >= 256 and int(type) <= 4096):
            self.setTypeFloat(type, size)
        elif (int(type) >= 16384):
            self.setTypeString(type, size)

    def setTypeBool(self):
        self.defaultValue = "0"
        self.constValue = 'constantValueBool'
        self.defaultWidget = Widget('buttons')

    def setTypeString(self):
        self.defaultValue = ""
        self.constValue = 'constantValueString'
        self.defaultWidget = Widget('text')

    def setTypeFloat(self, type, size):
        for i in range(int(size)):
            self.defaultValue += '1 '

        self.defaultValue = self.defaultValue[:-1]
        self.defaultWidget = Widget('slider', step=0.01)

    def setTypeInt(self, type, size):
        for i in range(int(size)):
            self.defaultValue += '1 '

        self.defaultValue = self.defaultValue[:-1]
        self.defaultWidget = Widget('slider', step=1)

    def addCustomData(self, item, values = []):
        self.customData.append((item, values))

    def compile(self, xml_paramInput):
        for item in self.items:
            debug_print('    ' + item[0] + ':')
            xml_item = ET.SubElement(xml_paramInput, item[0])
            for value in item[1]:
                debug_print('        ' + value[0] + ': ' + value[1])
                xml_item.set(value[0], value[1])

        debug_print('    Custom Data:')
        for item in self.customData:
            debug_print('        ' + item[0] + ':')
            xml_item = ET.SubElement(xml_paramInput, item[0])
            for value in item[1]:
                debug_print('              ' + value[0] + '.' + value[1] + ': ' + value[2])
                xml_value = ET.SubElement(xml_item, value[0])
                xml_value.set(value[1], value[2])

        debug_print('Attributes:')
        xml_attributes = ET.SubElement(xml_paramInput, 'attributes')
        xml_value = ET.SubElement(xml_attributes, 'label')
        xml_value.set('v', self.label)

        debug_print('Default Value:')
        xml_attributes = ET.SubElement(xml_paramInput, 'defaultValue')
        xml_value = ET.SubElement(xml_attributes, self.constValue)
        xml_value.set('v', str(self.defaultValue))

        debug_print('Default Widget:')
        xml_defaultWidget = ET.SubElement(xml_paramInput, 'defaultWidget')
        xml_widgetName = ET.SubElement(xml_defaultWidget, 'name')
        xml_widgetName.set('v', self.widget)
        xml_widgetOptions = ET.SubElement(xml_defaultWidget, 'options')

        debug_print('Widget Options:')
        for item in self.inputOptions:
            debug_print('        ' + item[0] + ':')
            xml_widgetOption = ET.SubElement(xml_widgetOptions, 'option')
            xml_optionName = ET.SubElement(xml_widgetOption, 'name')
            xml_optionValue = ET.SubElement(xml_widgetOption, 'value')
            xml_optionName.set('v', item[0])
            xml_optionValue.set('v', item[1])

class FuncData(ItemBase):
    name = ""
    customData = []

    def __init__(self, name):
        self.items = []
        self.customData = []
        self.name = name
        self.addItem('name', [("v", self.name)])

    def addCustomData(self, item, values = []):
        self.customData.append((item, values))

    def compile(self, xml_funcData):
        for item in self.items:
            debug_print('    ' + item[0] + ':')
            xml_item = ET.SubElement(xml_funcData, item[0])
            for value in item[1]:
                debug_print('        ' + value[0] + ': ' + value[1])
                xml_item.set(value[0], value[1])

        debug_print('    Custom Data:')
        for item in self.customData:
            debug_print('        ' + item[0] + ':')
            xml_item = ET.SubElement(xml_funcData, item[0])
            for value in item[1]:
                debug_print('              ' + value[0] + '.' + value[1] + ': ' + value[2])
                xml_value = ET.SubElement(xml_item, value[0])
                xml_value.set(value[1], value[2])

class ParamNode(ItemBase):
    uid = "1332649438"
    function = "none"
    type = "256"
    pos = ("192", "50", "1")
    connections = []
    funcDatas = []

    def __init__(self, function, uid = "1332649438", type = "256"):
        self.items = []
        self.connections = []
        self.funcDatas = []
        self.uid = uid
        self.type = type
        self.function = function
        self.addItem('uid', [("v", self.uid)])
        self.addItem('function', [("v", self.function)])
        self.addItem('type', [("v", self.type)])

    def addFuncData(self, funcData):
        self.funcDatas.append(funcData)

    def addConnection(self, connection):
        self.connections.append(connection)

    def compile(self, xml_paramNode):
        for item in self.items:
            debug_print('    ' + item[0] + ':')
            xml_item = ET.SubElement(xml_paramNode, item[0])
            for value in item[1]:
                debug_print('        ' + value[0] + ': ' + value[1])
                xml_item.set(value[0], value[1])

        debug_print('    FuncDatas:')
        xml_funcDatas = ET.SubElement(xml_paramNode, 'funcDatas')
        for funcData in self.funcDatas:
            xml_funcData = ET.SubElement(xml_funcDatas, 'funcData')
            funcData.compile(xml_funcData)

        debug_print('    Connections:')
        xml_connections = ET.SubElement(xml_paramNode, 'connections')
        for connection in self.connections:
            xml_connection = ET.SubElement(xml_connections, 'connection')
            connection.compile(xml_connection)

        debug_print('    GUILayout:', 3)
        xml_GUILayout = ET.SubElement(xml_paramNode, 'GUILayout')
        xml_gpos = ET.SubElement(xml_GUILayout, 'gpos')
        xml_gpos.set('v', self.pos[0] + ' ' + self.pos[1] + ' ' + self.pos[2])

class Function(ItemBase):
    identifier = "snixel"
    uid = "0"
    type = "256"
    rootnode = "0";
    inputs = []
    paramNodes = []

    def __init__(self, name, uid, type):
        self.items = []
        self.inputs = []
        self.paramNodes = []
        self.identifier = name
        self.type = type
        self.uid = uid
        self.addItem('identifier', [("v", self.identifier)])
        self.addItem('uid', [("v", self.uid)])
        self.addItem('type', [("v", self.type)])

    def addParamNode(self, paramNode):
        self.paramNodes.append(paramNode)

    def addInput(self, inputNode):
        self.inputs.append(inputNode)

    def setRootNode(self, rootnode):
        self.rootnode = rootnode

    def compile(self, xml_function):
        for item in self.items:
            debug_print('    ' + item[0] + ':')
            xml_item = ET.SubElement(xml_function, item[0])
            for value in item[1]:
                debug_print('        ' + value[0] + ': ' + value[1])
                xml_item.set(value[0], value[1])

        debug_print('Function Inputs:')
        xml_paramInputs = ET.SubElement(xml_function, 'paraminputs')
        for input in self.inputs:
            debug_print('    ' + input.name + ':')
            xml_paramInput = ET.SubElement(xml_paramInputs, 'paraminput')
            input.compile(xml_paramInput)

        debug_print('Param Nodes:')
        xml_paramValue = ET.SubElement(xml_function, 'paramValue')
        xml_dynamicValue = ET.SubElement(xml_paramValue, 'dynamicValue')
        xml_rootnode = ET.SubElement(xml_dynamicValue, 'rootnode')
        xml_rootnode.set('v', self.rootnode)
        xml_paramNodes = ET.SubElement(xml_dynamicValue, 'paramNodes')

        for node in self.paramNodes:
            debug_print('Node: ' + node.function + '(' + node.uid + '):', 3)
            xml_paramNode = ET.SubElement(xml_paramNodes, 'paramNode')
            node.compile(xml_paramNode)

class Dependency(ItemBase):
    uid = 0
    type = 'package'
    filename = "?himself"
    fileUID = 0
    versionUID = 0

    def __init__(self, filename, uid):
        self.items = []
        self.uid = str(uid);
        self.type = 'package'
        self.filename = str(filename)
        self.fileUID = str(0)
        self.versionUID = str(0)
        self.addItem('filename', [("v", self.filename)])
        self.addItem('uid', [("v", self.uid)])
        self.addItem('type', [("v", self.type)])
        self.addItem('fileUID', [("v", self.fileUID)])
        self.addItem('versionUID', [("v", self.versionUID)])

    def compile(self, xml_dependency):
        for item in self.items:
            debug_print('    ' + item[0] + ':')
            xml_item = ET.SubElement(xml_dependency, item[0])
            for value in item[1]:
                debug_print('        ' + value[0] + ': ' + value[1])
                xml_item.set(value[0], value[1])

class Package(ItemBase):
    identifier = ""
    version = "1.1.0.201804"
    fileUID = "{55849f0d-25a5-427a-9dc9-878a510b4270}"
    versionUID = "0"
    graphs = []
    functions = []
    dependencies = []

    def __init__(self, identifier = "Snix Package"):
        self.items = []
        self.graphs = []
        self.functions = []
        self.identifier = identifier
        self.addItem('identifier', [("v", self.identifier)])
        self.addItem('formatVersion', [("v", self.version)])
        self.addItem('updaterVersion', [("v", self.version)])
        self.addItem('fileUID', [("v", self.fileUID)])
        self.addItem('versionUID', [("v", self.versionUID)])

    def compile(self):
        xml_package = ET.Element('package')
        for item in self.items:
            debug_print('    ' + item[0] + ':')
            xml_item = ET.SubElement(xml_package, item[0])
            for value in item[1]:
                debug_print('        ' + value[0] + ': ' + value[1])
                xml_item.set(value[0], value[1])

        xml_dependencies = ET.SubElement(xml_package, 'dependencies')
        for dependency in self.dependencies:
            debug_print('Dependency: ' + dependency.uid + ':')
            xml_dependency = ET.SubElement(xml_dependencies, 'dependency')
            dependency.compile(xml_dependency)

        debug_print('Content:')
        xml_content = ET.SubElement(xml_package, 'content')

        for graph in self.graphs:
            debug_print('Graph: ' + graph.identifier + ':')
            xml_graph = ET.SubElement(xml_content, 'graph')
            graph.compile(xml_graph)

        for function in self.functions:
            debug_print('Function: ' + function.identifier + ':')
            xml_function = ET.SubElement(xml_content, 'function')
            function.compile(xml_function)

        return xml_package

    def addDependency(self, depenency):
        self.dependencies.append(depenency)

    def addGraph(self, graph):
        self.graphs.append(graph)

    def addFunction(self, function):
        self.functions.append(function)

class SBSWriter:
    package = []

    def __init__(self):
        self.package = Package();
        self.graphs = []
        self.functions = []
        self.addGraph()

    def addGraph(self):
        graph = Graph()
        self.package.addGraph(graph)
        return graph

    def addFunction(self, name, type):
        global function_uid
        function_uid += 1
        function = Function(name, str(function_uid), type)
        self.package.addFunction(function)
        return function

    def write(self, outfile = None):
        debug_print('Package:')
        xml_package = self.package.compile()
        xml_data = ET.tostring(xml_package)

        if (outfile == None):
            outfile = 'out.sbs'

        ET.ElementTree(xml_package).write(outfile, encoding="UTF-8")

        debug_print(xml_data, 2)
        return xml_data
