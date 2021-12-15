import xmltodict
import os
import json

def main():
    file = os.path.join('input',  'AppDepPat.xml')
    doc = open(file, 'r').read()
    obj  =xmltodict.parse(doc)
    # file = os.path.join('output', 'fromAris.json')
    # json.dump(obj, open(file, 'w'), indent=4)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
