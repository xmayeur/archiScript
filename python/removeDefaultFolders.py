import xmltodict
import sys
import os

if len(sys.argv) > 1:
    file = sys.argv[1]

    print('Removing default Archimate folders')
    data = xmltodict.parse(open(file, 'r').read())
    items = data["model"]["organizations"]["item"]
    folders = []
    for i in items:
        if "label" in i:
            label = i["label"]["#text"]
            folders.append(i["item"])

    data["model"]["organizations"]["item"] = folders
    result = xmltodict.unparse(data, pretty=True)
    dir = os.path.dirname(file)
    file = os.path.basename(file)
    # open(os.path.join(dir, file.split('.')[0]+'_conv.xml'), 'w').write(result)
    open(file, 'w').write(result)

