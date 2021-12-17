import json
from jsonpath_ng import jsonpath, parse
import os
import xmltodict
from archiObjects import *
from type_mapping import type_map
import sys
import yaml
import logging as log


class AML:

    def __init__(self, aml_file: str, name='aris_export'):
        self.data = xmltodict.parse(open(aml_file, 'r').read())
        self.folders = []
        self.name = name
        self.model = OpenExchange(self.name)
        self.pdef = PropertyDefinitions()
        self.pdef.add('UUID')
        self.model.add_property_def(self.pdef)
        self.elements = []
        self.relationships = []
        self.scale = 3

    def get_attributes(self, o):
        o_name = ''
        props = []

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
                    o_name += ' '.join([x.value for x in find_text(ad)])
                    o_name = o_name.encode('ascii', 'replace').decode()

                else:
                    prop_key = ad['@AttrDef.Type'][3]  # skip the 'AT_' prefix
                    prop_val = ' '.join([x.value for x in find_text(ad)])
                    prop_val = prop_val.encode('ascii', 'replace').decode()

                    props.append(Property(prop_key, prop_val, self.pdef))
        return o_name, props

    def parse_folders(self, groups=None):
        if groups is None:
            groups = self.data['AML']

        if 'Group' not in groups:
            return

        groups = groups['Group']
        if not isinstance(groups, list):
            groups = [groups]
        for grp in groups: 
            if 'AttrDef' in grp:
                name, props = self.get_attributes(grp)
                self.folders.append(name)
                # grp['AttrDef']['AttrValue']['StyledElement']['StyledElement']['PlainText']['@TextValue']
            self.parse_folders(grp)
        return

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
                for o in objects:
                    o_type = type_map[o['@SymbolNum']]
                    if o_type == "":
                        o_type = 'label'
                        log.warning("In 'parse_element', empty type found")
                    o_id = o['@ObjDef.ID']
                    o_uuid = o['GUID']
                    o_name, props = self.get_attributes(o)
                    e = Element(name=o_name, type=o_type, uuid=o_id)
                    e.add_property(Property('UUID', o_uuid, self.pdef))
                    e.add_property(*props)
                    self.model.add_element(e)

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
                                r = Relationship(source=o_id, target=r_target, type=r_type, uuid=r_id)
                                # TODO check how to manage access & influence relation metadata
                                self.model.add_relationship(r)
                            else:
                                log.warning(f"In 'parse_element', unknown relationship target {r_target} for element '{o_name}' - {o_id}")
                return

            self.parse_elements(grp)
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
                    view_name, model_props = self.get_attributes(m)
                    view = View(name=view_name, uuid=view_id)
                    self.parse_nodes(m, view)
                    self.model.add_view(view)

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
                # o_type = type_map[o['@SymbolNum']]
                o_id = o['@ObjOcc.ID']
                # o_uuid = o['ExternalGUID']
                o_elem_ref = o['@ObjDef.IdRef']
                pos = o['Position']
                size = o['Size']
                n = Node(
                    ref=o_elem_ref,
                    x=int(pos['@Pos.X']) / self.scale,
                    y=int(pos['@Pos.Y']) / self.scale,
                    w=int(size['@Size.dX']) / self.scale,
                    h=int(size['@Size.dY']) / self.scale,
                    uuid=o_id
                )
                view.add_node(n)

                if 'CxnOcc' in o:
                    conns = o['CxnOcc']
                    if not isinstance(conns, list):
                        conns = [conns]

                    for conn in conns:
                        c_id = conn['@CxnOcc.ID']
                        c_rel_id = conn['@CxnDef.IdRef']
                        c_target = conn['@ToObjOcc.IdRef']
                        c = Connection(ref=c_rel_id, source=o_id, target=c_target, uuid=c_id)
                        # if 'Position' in conn:
                        #     bps = conn['Position']
                        #     for bp in bps:
                        #         c.add_bendpoint(
                        #             str(int(bp['@Pos.X'])+(n.w/2)),
                        #             str(int(bp['@Pos.Y'])+(n.h/2))
                        #         )
                        view.add_connection(c)
            return

        self.parse_nodes(grp)
        return


def main():
    aris_file = None

    if len(sys.argv) > 1:
        aris_file = sys.argv[1]
    else:
        input_path = 'input'
        input_file = 'AppDepPat.xml'
        aris_file = os.path.join(input_path, input_file)

    aris = AML(aris_file)
    # aris.parse_folders()
    aris.parse_elements()
    aris.parse_views()

    #    print(json.dumps(aris.folders))
    #    print(json.dumps(aris.model.OEF, indent=4))

    file = os.path.join('output', 'out.yml')
    yaml.dump(aris.model.OEF, open(file, 'w'), indent=4)
    file = os.path.join('output', 'out.xml')
    xmltodict.unparse(aris.model.OEF, open(file, 'w'), pretty=True)

    file = os.path.join('output', 'IDs.yml')
    yaml.dump(IDs, open(file, 'w'))


if __name__ == "__main__":
    main()
