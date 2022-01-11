"""
*   Conversion program from ARIS AML xml file to Archimate Open Exchange File format
*   Author: X. Mayeur
*   Date: December 2021
*   Version 0.1
*
*
*   TODO Implement folder structure
*   TODO Implement styles
*
"""
import logging as log
from jsonpath_ng import parse
from archiObjects import *
from type_mapping import type_map
from xml.sax.saxutils import escape


def str2xml_escape(txt):
    return escape(txt, entities={"'": "&apos;", '"': "&quot;", '\r': "&#13;"})


def xml2str_escape(txt):
    txt = txt.replace("&lt;", "<")
    txt = txt.replace("&gt;", ">")
    txt = txt.replace("&amp;", "&")
    txt = txt.replace("&apos;", "'")
    txt = txt.replace("&quot;", '"')
    txt = txt.replace("&#13;", "\r")
    return txt


class AML:
    """
    Class to perform the parsing of ARIS AML data and to generate OpenExchangeFile data
    """

    def __init__(self, aml_file: str, name='aris_export', scale_x=0.3, scale_y=0.3, skip_bendpoint=True):
        """
        Parameters:
             aml_file : str
                file path  to ARIS AML
            name : str
                name of the model
            scale_x : float
                scale factor to enlarge or reduce the diagrams (X-axis)
            scale_x : float
                scale factor to enlarge or reduce the diagrams (Y-axis)
            skip_bendpoint : bool
                flag to indicate whether bendpoints of connections should not be managed

        properties:
            data : orderedDict
                ARIS AML data converted to an ordered dictionary object
            eof_data : XML
                Result of the conversion in XML format
            model : orderedDict
                Result of the conversion as an orderedDict

        methods:

            convert : None
                Convert AML object to OEF one by calling the parsers
            parse_elements : None
                Extract all elements 'ObjDef" from ARIS data
            parse_relationships : None
                Extract all relationships 'CxnDef' between elements from Aris data
                Note that some relationships are not processed as they relates to object in the central Aris database
                not shown in the view. A warning is generated in such case
            parse_view : None
                Extract all views and invokes parse_nodes and parse_connections
            parse_nodes : None
                Extract all nodes 'ObjOcc' and check whether the related target element exists
            parse_connections : None
                Extract all connections between node and check whether the related target node exist
            parse_containers: None
                Extract all rectangle graphical objects and convert them in containers.
                It is a specialization of parse_nodes
            parse_labels : None
                Extract all text label
            parse_labels_in_view : None
                Extract labels meta data (position, style) and convert them as labels.
                It is a specialization of parse_nodes


        """
        self.data = xmltodict.parse(open(aml_file, 'r').read())
        self.organizations = []
        self.name = name
        self.model = OpenExchange(self.name)
        self.pdef = PropertyDefinitions()
        self.pdef.add('UUID')
        self.model.add_property_def(self.pdef)
        self.elements = []
        self.relationships = []
        self.labels = {}
        self.scaleX = float(scale_x)
        self.scaleY = float(scale_y)
        self.skip_bendpoint = skip_bendpoint
        self.oef_data = None

    def convert(self):
        log.info('Parsing Folders')
        self.parse_organizations()
        log.info('Parsing elements')
        self.parse_elements()
        log.info('Parsing relationships')
        self.parse_relationships()
        log.info('Parsing Labels')
        self.parse_labels()
        log.info('Parsing Views')
        self.parse_views()
        log.info('Converting to OEF format')
        self.oef_data = xmltodict.unparse(self.model.OEF, pretty=True)
        return self.oef_data

    def get_attributes(self, o, sep=' '):
        o_name = ''
        props = []
        o_desc = None

        def find_text(arg):
            expr = parse('$[*]..@TextValue')
            return expr.find(arg)

        attribs = o['AttrDef']
        if not isinstance(attribs, list):
            attribs = [attribs]
        for attr in attribs:
            if not isinstance(attr, list):
                attr = [attr]
            for ad in attr:
                if ad['@AttrDef.Type'] == 'AT_NAME':
                    o_name += sep.join([x.value for x in find_text(ad)])
                    o_name = o_name.encode('ascii', 'replace').decode()
                else:
                    attr_type = ad['@AttrDef.Type']
                    prop_key = attr_type
                    prop_val = sep.join([x.value for x in find_text(ad)])
                    prop_val = xml2str_escape(prop_val).encode('ascii', 'replace').decode()
                    props.append(Property(prop_key, prop_val, self.pdef))
                    if attr_type == 'AT_DESC':
                        o_desc = prop_val
        return o_name, props, o_desc

    def parse_organizations(self, groups=None):
        if groups is None:
            groups = self.data['AML']

        if 'Group' not in groups:
            return

        groups = groups['Group']
        if not isinstance(groups, list):
            groups = [groups]
        for grp in groups:

            if '@TypeNum' in grp and 'AttrDef' in grp:
                name, props, desc = self.get_attributes(grp)
                self.organizations.append(name)
                # grp['AttrDef']['AttrValue']['StyledElement']['StyledElement']['PlainText']['@TextValue']
            self.parse_organizations(grp)
        return

    def parse_elements(self, groups=None, orgs=None):
        if groups is None:
            groups = self.data['AML']
            orgs=[]

        if 'Group' not in groups:
            return

        groups = groups['Group']

        if not isinstance(groups, list):
            groups = [groups]

        for grp in groups:
            if '@TypeNum' in grp and 'AttrDef' in grp:
                name, props, desc = self.get_attributes(grp)
                orgs.append(name)

            if 'ObjDef' in grp:
                objects = grp['ObjDef']
                if not isinstance(objects, list):
                    objects = [objects]
                for o in objects:
                    o_type = type_map[o['@SymbolNum']]
                    if o_type == "":
                        o_type = 'label'
                        log.warning("In 'parse_element', empty type found")
                    o_id = o['@ObjDef.ID']
                    o_uuid = o['GUID']
                    o_name, props, o_desc = self.get_attributes(o)
                    e = Element(name=o_name, type=o_type, uuid=o_id, desc=o_desc)
                    e.add_property(Property('UUID', o_uuid, self.pdef))
                    e.add_property(*props)
                    self.model.add_elements(e)
            self.parse_elements(grp)
        return

    def parse_relationships(self, groups=None):
        if groups is None:
            groups = self.data['AML']

        if 'Group' not in groups:
            return

        groups = groups['Group']
        if not isinstance(groups, list):
            groups = [groups]

        for grp in groups:
            if 'ObjDef' in grp:
                objects = grp['ObjDef']
                if not isinstance(objects, list):
                    objects = [objects]
                for o in objects:
                    o_id = o['@ObjDef.ID']
                    o_name, props, desc = self.get_attributes(o)

                    if 'CxnDef' in o:
                        rels = o['CxnDef']
                        if not isinstance(rels, list):
                            rels = [rels]

                        for rel in rels:
                            r_type = type_map[rel['@CxnDef.Type']]
                            r_id = rel['@CxnDef.ID']
                            r_target = rel['@ToObjDef.IdRef']
                            # Check if target is known
                            if r_target in IDs:
                                r = Relationship(source=o_id, target=r_target, type=r_type, uuid=r_id, desc=desc)
                                # TODO check how to manage access & influence relation metadata
                                self.model.add_relationships(r)
                            else:
                                log.warning(f"In 'parse_element', unknown relationship target {r_target} "
                                            f"for element '{o_name}' - {o_id}")
                return

            self.parse_relationships(grp)
        return

    def parse_views(self, groups=None):
        if groups is None:
            groups = self.data['AML']

        if 'Group' not in groups:
            return

        groups = groups['Group']
        if not isinstance(groups, list):
            groups = [groups]

        for grp in groups:
            if 'Model' in grp:
                models = grp['Model']
                if not isinstance(models, list):
                    models = [models]

                for m in models:
                    view_id = m['@Model.ID']
                    view_name, model_props, desc = self.get_attributes(m)
                    view = View(name=view_name, uuid=view_id, desc=desc)
                    self.parse_nodes(m, view)
                    self.parse_connections(m, view)
                    self.parse_containers(m, view)
                    self.parse_labels_in_view(m, view)
                    view.sort_node()
                    self.model.add_views(view)

            self.parse_views(grp)
        return

    def parse_nodes(self, grp=None, view=None):
        if grp is None:
            return

        if 'ObjOcc' not in grp:
            return

        if view is None:
            return

        if not isinstance(view, View):
            raise ValueError("'view' is not an instance of class 'View'")

        if 'ObjOcc' in grp:
            objects = grp['ObjOcc']
            for o in objects:
                o_type = type_map[o['@SymbolNum']]
                o_id = o['@ObjOcc.ID']
                # o_uuid = o['ExternalGUID']
                o_elem_ref = o['@ObjDef.IdRef']
                pos = o['Position']
                size = o['Size']
                n = Node(
                    ref=o_elem_ref,
                    x=int(pos['@Pos.X']) * self.scaleX,
                    y=int(pos['@Pos.Y']) * self.scaleY,
                    w=int(size['@Size.dX']) * self.scaleX,
                    h=int(size['@Size.dY']) * self.scaleY,
                    uuid=o_id
                )
                view.add_node(n)

                if o_type == 'Grouping':
                    fc = RGBA(0, 0, 0, 0)
                    s = Style(fill_color=fc)
                    n.add_style(s)

            # Sort nodes by area, the biggest first

            return

        self.parse_nodes(grp)
        return

    def parse_connections(self, grp=None, view=None):
        if grp is None:
            return

        if 'ObjOcc' not in grp:
            return

        if view is None:
            return

        if not isinstance(view, View):
            raise ValueError("'view' is not an instance of class 'View'")

        if 'ObjOcc' in grp:
            objects = grp['ObjOcc']
            for o in objects:
                o_id = o['@ObjOcc.ID']

                if 'CxnOcc' in o:
                    conns = o['CxnOcc']
                    if not isinstance(conns, list):
                        conns = [conns]

                    for conn in conns:
                        c_id = conn['@CxnOcc.ID']
                        c_rel_id = conn['@CxnDef.IdRef']
                        c_target = conn['@ToObjOcc.IdRef']
                        # if '@Visible' in conn and conn['@Visible'] == 'NO':
                        #     continue
                        c = Connection(ref=c_rel_id, source=o_id, target=c_target, uuid=c_id)
                        if 'Position' in conn and not self.skip_bendpoint:
                            bps = conn['Position']
                            for i in range(1, len(bps) - 1):
                                bp_x = int(bps[i]['@Pos.X'])
                                bp_y = int(bps[i]['@Pos.Y'])

                                c.add_bendpoint(
                                    (bp_x * self.scaleX, bp_y * self.scaleY)
                                )
                        view.add_connection(c)
            return

        self.parse_connections(grp)
        return

    def parse_containers(self, grp=None, view=None):
        if grp is None:
            return

        if 'GfxObj' not in grp:
            return

        if view is None:
            return

        if not isinstance(view, View):
            raise ValueError("'view' is not an instance of class 'View'")

        if 'GfxObj' in grp:
            objects = grp['GfxObj']
            if not isinstance(object, list):
                objects = [objects]
            for o in objects:
                if 'RoundedRectangle' not in o:
                    continue
                pos = o['Position']
                size = o['Size']

                def hex_to_rgb(value):
                    value = value.lstrip('#')
                    lv = len(value)
                    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

                r, g, b = hex_to_rgb(o['Brush']['@Color'])
                line_color = RGBA(r, g, b, 100)
                fc = RGBA(0, 0, 0, 0)
                s = Style(line_color=line_color, fill_color=fc)

                n = Node(
                    ref=None,
                    x=int(pos['@Pos.X']) * self.scaleX,
                    y=int(pos['@Pos.Y']) * self.scaleY,
                    w=int(size['@Size.dX']) * self.scaleX,
                    h=int(size['@Size.dY']) * self.scaleY,
                )
                view.add_container(n, ' ')
                n.add_style(s)
            return

        self.parse_containers(grp)
        return

    def parse_labels(self, groups=None):
        if groups is None:
            groups = self.data['AML']

        if 'FFTextDef' in groups:
            objects = groups['FFTextDef']
            for o in objects:
                o_id = o['@FFTextDef.ID']
                o_name, _ = self.get_attributes(o, '\n')
                self.labels[o_id] = o_name
            return

    def parse_labels_in_view(self, grp=None, view=None):
        if grp is None:
            return
        if 'FFTextOcc' not in grp:
            return
        if view is None:
            return
        if not isinstance(view, View):
            raise ValueError("'view' is not an instance of class 'View'")

        if 'FFTextOcc' in grp:
            objects = grp['FFTextOcc']
            if not isinstance(objects, list):
                objects = [objects]
            for o in objects:
                pos = o['Position']
                lbl = self.labels[o['@FFTextDef.IdRef']]
                # calculate size in function of text
                n = Node(
                    ref=o['@FFTextDef.IdRef'],
                    x=max(int(pos['@Pos.X']) * self.scaleX, 0),
                    y=max(int(pos['@Pos.Y']) * self.scaleY, 0),
                    w=13 * len(max(lbl.split('\n'))),
                    h=30 + 13 * lbl.count('\n')
                )

                line_color = RGBA(0, 0, 0, 0)
                fc = RGBA(0, 0, 0, 0)

                s = Style(line_color=line_color, fill_color=fc)

                view.add_label(n, lbl)
                n.add_style(s)
            return

        self.parse_labels_in_view(grp)
        return
