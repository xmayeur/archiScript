from uuid import uuid4
from collections import OrderedDict


def set_id(uuid=None):
    _id = str(uuid4()) if (uuid is None) else uuid
    _id = _id.replace('-', '')
    if _id[:3] != 'set_id-':
        _id = 'set_id-' + _id
    return _id


class OpenExchange:

    def __init__(self, name, uuid=None):
        self.name = name
        self.uuid = set_id(uuid)
        self.OEF = OrderedDict()
        self.OEF = {'model': {
            '@xmlns': 'http://www.opengroup.org/xsd/archimate/3.0/',
            '@xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            '@xsi:schemaLocation': 'http://www.opengroup.org/xsd/archimate/3.0/ '
                                   'http://www.opengroup.org/xsd/archimate/3.1/archimate3_Diagram.xsd',
            '@identifier': self.uuid,  # UUID
            'name': {
                '@xml:lang': 'en',
                '#text': self.name,  # MODEL NAME
            },
            'elements': {'element': []},  # list of elements
            'relationships': {'relationship': []},  # list of relationships
            'propertyDefinitions': {'propertyDefinition': []},
            'views': {'diagrams': {'view': []}}  # list of diagrams
        }
        }

    def add_element(self, *elements):
        if 'elements' not in self.OEF['model']:
            self.OEF['model']['elements'] = {'element': []}
        for e in elements:
            self.OEF['model']['elements']['element'].append(e.element)

    def add_relationship(self, *relationships):
        if 'relationships' not in self.OEF['model']:
            self.OEF['model']['relationships'] = {'relationship': []}
        for r in relationships:
            self.OEF['model']['relationships']['relationship'].append(r.relationship)

    def add_view(self, *views):
        if 'views' not in self.OEF['model']:
            self.OEF['model']['views'] = {'diagrams': {'view': []}}
        for v in views:
            self.OEF['model']['views']['diagrams']['view'].append(v.view)

    def add_property_def(self, propdef):
        self.OEF['model']['propertyDefinitions'] = {'propertyDefinition': propdef.propertyDefinitions}


class Element:

    def __init__(self, name, type, uuid=None):
        self.name = name
        self.type = type
        self.uuid = set_id(uuid)
        self.element = {
            '@identifier': self.uuid,  # UUID
            '@xsi:type': self.type,  # ELEMENT TYPE
            'name': {
                '@xml:lang': 'en',
                '#text': self.name,  # ELEMENT NAME
            },
            # 'properties': []  # LIST OF ELEMENT PROPERTIES
        }

    def add_property(self, *properties):
        if 'properties' not in self.element:
            self.element['properties'] = {'property': []}
        for p in properties:
            self.element['properties']['property'].append(p)


class Property:

    def __init__(self, key: str, value: str, propdef):
        self.value = value
        if not isinstance(propdef, PropertyDefinitions):
            raise ReferenceError('"propdef" is not a PropertyDefinitions class.')
        pdef = propdef.propertyDefinitions
        ref = [x['@identifier'] for x in pdef if x['name'] == key]
        if len(ref) == 0:
            _id = propdef.add(key)
        else:
            _id = ref[0]

        self.property = {
            '@propertyDefinitionRef': _id,  # PROPERTY ID
            'value': {
                '@xml:lang': 'en',
                '#text': self.value  # PROPERTY VALUE
            }
        }


class PropertyDefinitions:

    def __init__(self):
        self.propertyDefinitions = []

    def add(self, key):
        _p = {
            '@identifier': 'propid_' + str(len(self.propertyDefinitions) + 1),
            '@type': 'string',
            'name': key
        }
        self.propertyDefinitions.append(_p)
        return _p['@identifier']


class Relationship:

    def __init__(self, source, target, type='', uuid=None, name='', access_type=None, influcence_strength=None):
        self.uuid = set_id(uuid)
        
        if isinstance(source, Element):
            self.source = source.uuid
        elif isinstance(source, str):
            self.source = source
        else:
            raise ReferenceError("'source' argument is not an instance of 'Element' class.")
            
        if isinstance(target, Element):
            self.target = target.uuid
        elif isinstance(source, str):
            self.target = target
        else:
            raise ReferenceError("'target' argument is not an instance of 'Element' class.")
        self.type = type
        
        self.name = name
        self.relationship = {
            '@identifier': self.uuid,  # RELATIONSHIP UUID
            '@source': self.source,  # SOURCE UUID
            '@target': self.target,  # TARGET UUID
            '@xsi:type': self.type,  # RELATIONSHIP TYPE
            'name': {
                '@xml:lang': 'en',
                '#text': self.name,  # ELEMENT NAME
            },
            # 'properties': {'property':[]}
        }

        if access_type is not None:
            self.relationship['@accessType'] = access_type

        if influcence_strength is not None:
            self.relationship['@modifier'] = influcence_strength

    def add_property(self, *properties):
        if 'properties' not in self.relationship:
            self.relationship['properties'] = {'property': []}
        for p in properties:
            self.relationship['properties']['property'].append(p)


class View:

    def __init__(self, name='', uuid=None):
        self.uuid = set_id(uuid)
        self.name = name
        self.view = {
            '@identifier': self.uuid,  # VIEW UUID
            '@xsi:type': 'Diagram',  # VIEW TYPE
            'name': {
                '@xml:lang': 'en',
                '#text': self.name,  # ELEMENT NAME
            },
            'node': [],  # LIST OF NODES
            'connection': [],  # LIST OF CONNECTIONS
        }

    def add_node(self, *nodes):
        if 'node' not in self.view:
            self.view['node'] = []
        for n in nodes:
            self.view['node'].append(n.node)

    def add_connection(self, *connections):
        if 'connection' not in self.view:
            self.view['connection'] = []
        for c in connections:
            self.view['connection'].append(c.connection)


class Node:

    def __init__(self, ref, x=0, y=0, w=120, h=55, style=None, node=None, uuid=None):
        self.uuid = set_id(uuid)
        if isinstance(ref, Element):
            self.ref = ref.uuid
        elif isinstance(ref, str):
            self.ref = ref
        else:
            raise ReferenceError("'ref' is not an instance of 'Element' class.")
        self.x = int(x)
        self.y = int(y)
        self.w = int(w)
        self.h = int(h)
        self.style = style
        self.node = node
        self.node = {
            '@identifier': self.uuid,  # NODE UUID
            '@elementRef': self.ref,  # ELEMENT UUID
            '@xsi:type': 'Element',
            '@x': str(self.x),  # X CENTER POSITION
            '@y': str(self.y),  # Y CENTER POSITION
            '@w': str(self.w),  # ELEMENT WIDTH
            '@h': str(self.h),  # ELEMENT HEIGHT
            # 'style': self.style,  # STYLE
            # 'node': self.node,  # EMBEDDED NODES
        }

        if isinstance(style, Style) and style is not None:
            self.node['style'] = style.style

    def add_node(self, *nodes):
        if 'node' not in self.node:
            self.node['node'] = []
        for n in nodes:
            self.node['node'].append(n.node)

    def add_connection(self, *connections):
        if 'connection' not in self.node:
            self.node['connection'] = []
        for c in connections:
            self.node['connection'].append(c.connection)

    def add_style(self, style):
        if isinstance(style, Style):
            self.node['style'] = style.style


class Connection:
    def __init__(self, ref, source, target, style=None, bendpoint=None, uuid=None):
        self.uuid = set_id(uuid)

        if isinstance(ref, Relationship):
            self.ref = ref.uuid
        elif isinstance(ref, str):
            self.ref = ref
        else:
            raise ReferenceError("'ref' is not an instance of 'Relationship' class.")

        if isinstance(source, Node):
            self.source = source.uuid
        elif isinstance(source, str):
            self.source = source
        else:
            raise ReferenceError("'source' is not an instance of 'Node' class.")
        
        if isinstance(target, Node):
            self.target = target.uuid
        elif isinstance(target, str):
            self.target = target
        else:
            raise ReferenceError("'target' is not an instance of 'Node' class.")

        self.style = style
        self.bendpoint = bendpoint
        self.connection = {
            '@identifier': self.uuid,  # CONNECTION UUID
            '@relationshipRef': self.ref,  # RELATIONSHIP UUID
            '@xsi:type': 'Relationship',
            '@source': self.source,  # SOURCE UUID
            '@target': self.target,  # TARGET UUID
            # 'style': self.style,  # STYLE
            # 'bendpoint': self.bendpoint  # BENDPOINTS ABSOLUTE X,Y
        }

        if isinstance(style, Style) and style is not None:
            self.connection['style'] = style.style

    def add_bendpoint(self, *bendpoints):
        if 'bendpoint' not in self.connection:
            self.connection['bendpoint'] = []
        for bp in bendpoints:
            self.connection['bendpoint'].append({
                '@x': str(int(bp[0])),
                '@y': str(int(bp[1]))
            })

    def add_style(self, style):
        if isinstance(style, Style):
            self.connection['style'] = style.style


class RGBA:
    r: str
    g: str
    b: str
    a: str

    r = None
    g = None
    b = None
    a = '100'


class Font:
    name: str
    size: str
    color: RGBA

    name = 'Segoe UI'
    size = '9'
    color = None


class Style:

    def __init__(self, fill_color: RGBA, line_color: RGBA, font: Font):
        self.fc = fill_color
        self.lc = line_color
        self. f = font

        self.style = {
            'fillColor': {
                '@r': self.fc.r,  # RED 0-255
                '@g': self.fc.g,  # GREEN
                '@b': self.fc.b,  # BLUE
                '@a': self.fc.a  # OPACITY 0-100
            },
            'lineColor': {
                '@r': self.lc.r,  # RED 0-255
                '@g': self.lc.g,  # GREEN
                '@b': self.lc.b,  # BLUE
                '@a': self.lc.a  # OPACITY 0-100
            },
            'font': {
                '@name': self.f.name,  # FONT NAME
                '@size': self.f.size,  # FONT SIZE
                'color': {
                    '@r': self.f.color.r,  # RED 0-255
                    '@g': self.f.color.g,  # GREEN
                    '@b': self.f.color.b,  # BLUE
                }
            }
        }