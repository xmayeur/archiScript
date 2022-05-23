"""
*   Conversion program from ARIS AML xml file to Archimate Open Exchange File format
*   Author: X. Mayeur
*   Date: December 2021
*   Version 0.1
*
*   TODO Implement styles
*
"""

import ctypes
from xml.sax.saxutils import escape
from jsonpath_ng import parse
from archiObjects import *
from type_mapping import type_map
import platform

used_elems_id = []


def get_text_size(text, points, font):
    if platform.system() == 'Linux':
        from PIL import ImageFont
        font = ImageFont.truetype('DejaVuSans.ttf', points)
        size = font.getsize('Hello world')
        return size[0], size[1]

    else:
        class SIZE(ctypes.Structure):
            _fields_ = [("cx", ctypes.c_long), ("cy", ctypes.c_long)]

        hdc = ctypes.windll.user32.GetDC(0)
        hfont = ctypes.windll.gdi32.CreateFontA(points, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, font)
        hfont_old = ctypes.windll.gdi32.SelectObject(hdc, hfont)

        size = SIZE(0, 0)
        ctypes.windll.gdi32.GetTextExtentPoint32A(hdc, text, len(text), ctypes.byref(size))

        ctypes.windll.gdi32.SelectObject(hdc, hfont_old)
        ctypes.windll.gdi32.DeleteObject(hfont)

        return size.cx, size.cy


def str2xml_escape(txt):
    return escape(txt, entities={"'": "&apos;", '"': "&quot;", '\r': "&#13;"})


def xml_escape2str(txt):
    txt = txt.replace("&lt;", "<")
    txt = txt.replace("&gt;", ">")
    txt = txt.replace("&amp;", "&")
    txt = txt.replace("&apos;", "'")
    txt = txt.replace("&quot;", '"')
    txt = txt.replace("&#13;", "\r")
    return txt


def idOf(_id):
    return 'id-' + _id.split('.')[1]


class AML:
    """
    Class to perform the parsing of ARIS AML data and to generate OpenExchangeFile data
    """

    def __init__(self, aml_file: str, name='aris_export', scale_x=0.3, scale_y=0.3,
                 skip_bendpoint=True, include_organization=False, incl_unions=False,
                 optimize=True, correct_embedded_rels=False, no_view=False):
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
        self.scaleX = float(scale_x)
        self.scaleY = float(scale_y)
        self.skip_bendpoint = skip_bendpoint
        self.incl_org = include_organization
        self.optimize = optimize
        self.correctEmbed = correct_embedded_rels
        self.no_view = no_view
        if not include_organization:
            del self.model.OEF["model"]["organizations"]
        self.incl_union = incl_unions
        self.oef_data = None

    def convert(self):

        log.info('Parsing elements')
        self.parse_elements()
        log.info('Parsing relationships')
        self.parse_relationships()

        if not self.no_view:
            log.info('Parsing Labels')
            self.parse_labels()
            log.info('Parsing Views')
            self.parse_views()

        log.info('Adding elements')
        self.add_elements()
        log.info('Adding relationships')
        self.add_relationships()

        self.model.generate_xml()
        if len(self.model.OEF["model"]['relationships']['relationship']) == 0:
            del self.model.OEF["model"]['relationships']

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
            attr = attr

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
                    prop_val = xml_escape2str(prop_val).encode('ascii', 'replace').decode()
                    # props.append(Property(prop_key, prop_val, self.pdef))
                    props.append((prop_key, prop_val))
                    if attr_type == 'AT_DESC':
                        o_desc = prop_val


        return o_name, props, o_desc

    def parse_elements(self, groups=None):
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
                    o_type = type_map[o['@SymbolNum']]
                    if o_type == "":
                        o_type = 'label'
                        log.warning("In 'parse_element', empty type found")
                    o_id = o['@ObjDef.ID']
                    o_uuid = 'id-' + o['GUID']
                    o_name, props, o_desc = self.get_attributes(o)
                    # XMA
                    e = Element(name=o_name, type=o_type, uuid=o_uuid, desc=o_desc)
                    # e.add_property(Property('UUID', o_uuid, self.pdef))
                    # e.add_property(('UUID', o_uuid))
                    e.properties['UUID'] = o_uuid
                    for p in props:
                        e.properties[p[0]] = p[1]
                    # e.add_property(*props)
                    elems_list[o_id] = e
                    elems_list[o_uuid] = e

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
                    o_uuid = "id-" + o['GUID']
                    if 'CxnDef' in o:
                        rels = o['CxnDef']

                        if not isinstance(rels, list):
                            rels = [rels]

                        for rel in rels:
                            r_type = type_map[rel['@CxnDef.Type']]
                            r_id = rel['@CxnDef.ID']
                            r_target = elems_list[rel['@ToObjDef.IdRef']].uuid
                            # r_name, props, desc = self.get_attributes(rel)
                            if r_target is not None:
                                r = Relationship(source=o_uuid, target=r_target, type=r_type, uuid=r_id)
                                rels_list[r_id] = r

            self.parse_relationships(grp)

        return

    def parse_unions(self, uu, lst=None):
        if not self.incl_union:
            return []

        uu = uu
        if lst is None:
            lst = []
        ns = []
        if not isinstance(uu, list):
            uu = [uu]
        for u in uu:
            refs = u['@ObjOccs.IdRefs'].strip().split(' ')
            refs = list(map(idOf, refs))
            # Need to look which of the element in the refs list is the parent embedding node
            # meaning has connection references to the others

            for np in refs:
                pp = [rels_list[y].source for y in rels_list
                      if rels_list[y].source == elems_list[nodes_list[np].ref].uuid]
                if elems_list[nodes_list[np].ref].uuid in pp and len(pp) == len(refs):
                    # n: Node = nodes_list[refs[0]]
                    n: Node = nodes_list[np]
                    ns.append(n)
                    # lst.append(n.uuid)
                    # for x in refs[1:]:
                    for x in list(set(refs) - {np}):
                        nn: Node = nodes_list[x]
                        n.add_node(nn)
                        lst.append(nn.uuid)

                    if 'Union' in u:
                        lst, ns = self.parse_unions(u['Union'], lst)
                        for x in ns:
                            n.add_node(x)
                            lst.append(x.uuid)

                    break

        return lst, ns

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
            if not isinstance(objects, list):
                objects = [objects]
            for o in objects:
                o_type = type_map[o['@SymbolNum']]
                # XMA
                o_id = idOf(o['@ObjOcc.ID'])
                o_elem_ref = elems_list[o['@ObjDef.IdRef']].uuid
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
                nodes_list[o_id] = n
                view.add_node(n)

                if o_type == 'Grouping':
                    fc = RGBA(0, 0, 0, 0)
                    s = Style(fill_color=fc)
                    n.add_style(s)
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
            if not isinstance(objects, list):
                objects = [objects]
            for o in objects:
                o_id = idOf(o['@ObjOcc.ID'])
                if 'CxnOcc' in o:
                    conns = o['CxnOcc']

                    if not isinstance(conns, list):
                        conns = [conns]
                    for conn in conns:
                        c_id = idOf(conn['@CxnOcc.ID'])
                        c_rel_id = conn['@CxnDef.IdRef']
                        c_target = idOf(conn['@ToObjOcc.IdRef'])
                        if '@Embedding' in conn and conn['@Embedding'] == 'YES' and self.incl_union is True:

                            # Aris uses reversed relationship when embedding objects,
                            # This gives validation errors when importing into archi...
                            # Swap therefore source and target if needed
                            rel: Relationship = rels_list[c_rel_id]
                            x = rel.target

                            # check if the relationship target is the related element of the visual object and swap
                            n: Node = nodes_list[c_target]
                            t: Element = elems_list[n.ref]
                            s: Element = elems_list[rel.source]

                            if x == t.uuid and self.correctEmbed:
                                log.warning(f"Inverting embedded nodes relationship '{rel.type}' "
                                            f"between nodes '{s.name}' and '{t.name}'")
                                rel.target = rel.source
                                rel.source = x
                                self.model.replace_relationships(c_rel_id, rel.relationship)

                        else:

                            c = Connection(ref=c_rel_id, source=o_id, target=c_target, uuid=c_id)
                            conns_list[c_id] = c
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

            if not isinstance(objects, list):
                objects = [objects]

            for o in objects:
                if 'RoundedRectangle' not in o:
                    continue
                pos = o['Position']
                size = o['Size']

                def hex_to_rgb(value):
                    value = value.lstrip('#')
                    if value == '0':
                        value = '000000'
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

    def parse_labels(self, groups=None):
        if groups is None:
            groups = self.data['AML']

        if 'FFTextDef' in groups:
            objects = groups['FFTextDef']
            for o in objects:
                o_id = idOf(o['@FFTextDef.ID'])
                labels_list[o_id] = o
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
                lbl_ref = idOf(o['@FFTextDef.IdRef'])
                if lbl_ref in labels_list:
                    lbl = labels_list[lbl_ref]
                    # calculate size in function of text
                    o_name, _, _ = self.get_attributes(lbl, '\n')
                    pos = o['Position']
                    w, h = max([get_text_size(x, 9, "Segoe UI") for x in o_name.split('\n')])
                    n = Node(
                        ref=idOf(o['@FFTextDef.IdRef']),
                        x=max(int(pos['@Pos.X']) * self.scaleX, 0),
                        y=max(int(pos['@Pos.Y']) * self.scaleY, 0),
                        w=w,  # 13 * len(max(o_name.split('\n'))),
                        h=30 + (h * 1.5) * (o_name.count('\n') + 1)
                    )

                    line_color = RGBA(0, 0, 0, 0)
                    fc = RGBA(0, 0, 0, 0)

                    s = Style(line_color=line_color, fill_color=fc)

                    view.add_label(n, o_name)
                    n.add_style(s)
            return

        self.parse_labels_in_view(grp)
        return

    def parse_views(self, groups=None, orgs=None):
        if groups is None:
            groups = self.data['AML']
        if orgs is None:
            orgs = []

        if 'Group' not in groups:
            return

        groups = groups['Group']

        if not isinstance(groups, list):
            groups = [groups]

        # Recurse through groups
        for grp in groups:
            # List organizations
            oo = orgs.copy()

            if not isinstance(oo, list):
                oo = [oo]

            if '@TypeNum' in grp and 'AttrDef' in grp:
                name, props, desc = self.get_attributes(grp)
                oo.append(name)

            # Parse models (views)
            if 'Model' in grp:
                refs = []
                models = grp['Model']

                if not isinstance(models, list):
                    models = [models]
                for m in models:
                    view_id = idOf(m['@Model.ID'])
                    views_list[view_id] = m
                    view_name, model_props, desc = self.get_attributes(m)
                    self.model.name = view_name
                    view = View(name=view_name, uuid=view_id, desc=desc)
                    log.info('Parsing & adding nodes')

                    self.parse_nodes(m, view)

                    log.info('Parsing & adding connections')
                    self.parse_connections(m, view)
                    log.info('Parsing and adding container groups')
                    self.parse_containers(m, view)
                    log.info('Parsing and adding labels')
                    self.parse_labels_in_view(m, view)
                    view.sort_node()
                    refs.append(view_id)

                    lst = []
                    # Parse Unions (node embeddings definitions)
                    if 'Union' in m:
                        unions = m['Union']
                        if not isinstance(unions, list):
                            unions = [unions]

                        for u in unions:
                            lst, _ = self.parse_unions(u, lst)

                    for i in range(len(view.view['node']) - 1, 0, -1):
                        if view.view['node'][i]['@identifier'] in lst:
                            view.view['node'].pop(i)

                    self.model.add_views(view)

                if self.incl_org:
                    self.model.add_organizations(oo, refs)

            self.parse_views(grp, oo)
        return

    def add_elements(self, groups=None, orgs=None):
        if groups is None:
            groups = self.data['AML']
        if orgs is None:
            orgs = []

        if 'Group' not in groups:
            return

        groups = groups['Group']

        if not isinstance(groups, list):
            groups = [groups]

        # Recurse through groups
        for grp in groups:
            # List organizations
            oo = orgs.copy()
            if not isinstance(oo, list):
                oo = [oo]
            if '@TypeNum' in grp and 'AttrDef' in grp:
                name, props, desc = self.get_attributes(grp)
                oo.append(name)

            if 'ObjDef' in grp:
                refs = []
                objects = grp['ObjDef']

                if not isinstance(objects, list):
                    objects = [objects]

                for o in objects:
                    o_id = o['@ObjDef.ID']
                    o_uuid = 'id-' + o['GUID']
                    if self.no_view:
                        self.model.add_elements(elems_list[o_id])
                        refs.append(o_id)
                        used_elems_id.append(o_uuid)
                    else:
                        # check if element has one or more nodes in views or is already defined
                        nn = [x for x in nodes_list if nodes_list[x].ref == o_uuid]
                        if (not self.optimize or len(nn) > 0) and o_id in elems_list:
                            self.model.add_elements(elems_list[o_id])
                            refs.append(o_uuid)
                            used_elems_id.append(o_uuid)
                if self.incl_org:
                    self.model.add_organizations(oo, refs)
            self.add_elements(grp, oo)
        return

    def add_relationships(self, groups=None, orgs=None):
        if groups is None:
            groups = self.data['AML']
        if orgs is None:
            orgs = []
        if 'Group' not in groups:
            return
        groups = groups['Group']
        if not isinstance(groups, list):
            groups = [groups]

        # Recurse through groups
        for grp in groups:
            # List organizations
            oo = orgs.copy()
            if not isinstance(oo, list):
                oo = [oo]
            if '@TypeNum' in grp and 'AttrDef' in grp:
                name, props, desc = self.get_attributes(grp)
                oo.append(name)

            if 'ObjDef' in grp:
                refs = []
                objects = grp['ObjDef']

                if not isinstance(objects, list):
                    objects = [objects]

                for o in objects:
                    o_id = o['@ObjDef.ID']
                    o_uuid = 'id-' + o['GUID']
                    if 'CxnDef' in o:
                        rels = o['CxnDef']

                        if not isinstance(rels, list):
                            rels = [rels]

                        for rel in rels:
                            r_id = rel['@CxnDef.ID']
                            # r_id = idOf(rel['@CxnDef.ID'])
                            r: Relationship = rels_list[r_id]
                            r_target = r.target

                            # Check if source & target are known
                            if r_target in used_elems_id and r_id in rels_list and o_uuid in used_elems_id:
                                r.is_simplified_pattern()
                                # TODO check how to manage access & influence relation metadata
                                self.model.add_relationships(r)
                                refs.append(r_id)
                            # else:
                            #     e: Element = elems_list[o_id]
                            #     log.info(f"In 'add_relationships', Skipping relationship between target {r_target} "
                            #              f"and source '{e.name}' - {o_id}")
                if self.incl_org:
                    self.model.add_organizations(oo, refs)

            self.add_relationships(grp)
        return

    # def convert_elem_id(self):
    #     elems = self.model.OEF["model"]['elements']['element']
    #     for e in elems:
    #         id = e['@identifier']
    #         guid = e['properties']['property'][0]['value']['#text']
    #         e['@identifier'] = "id-" + guid
    #         e['properties']['property'][0]['value']['#text'] = id+'|'+guid
    #
    # def convert_other_id(self, data):
    #     # find t and replace ObjDef references
    #     pat = re.compile(r'identifier="(ObjDef\..*?)"')
    #     for id in re.findall(pat, data):
    #         new_id = elems_list[id].guid
    #         data = re.sub(id, new_id, data)
    #
    #     return data
