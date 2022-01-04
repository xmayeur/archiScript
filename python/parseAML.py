import argparse
from AMLparser import AML


def main():
    """
    Read the XML file given as first argument and convert it to Open Exchange File format
    """

    parser = argparse.ArgumentParser("Convert ARIS AML to Archimate Open Exchange Fine")
    parser.add_argument('file', help="AML input file")
    parser.add_argument('-s', '--scale', required=False, help='Diagram scale factor')
    parser.add_argument('-o', '--outputfile', required=False, help="Output converted file")

    args = parser.parse_args()
    if args.scale:
        scale = eval(args.scale)
        if isinstance(scale, tuple):
            scale_x, scale_y = scale
        else:
            scale_x = scale
            scale_y = scale
    else:
        scale_x = 0.3
        scale_y = 0.4

    aris = AML(args.file, name='x', scale_x=scale_x, scale_y=scale_y, skip_bendpoint=False)
    result = aris.convert()

    if args.outputfile:
        open(args.outputfile, 'w').write(result)
    else:
        #  print(result)
        outFile = args.file[:-4]+"_OEF.xml"
        open(outFile, 'w').write(result)


if __name__ == "__main__":
    main()