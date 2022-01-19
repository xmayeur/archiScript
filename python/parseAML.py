import argparse
from AMLparser import AML
from logger import logging, log


def main():
    """
    Read the XML file given as first argument and convert it to Open Exchange File format
    """

    parser = argparse.ArgumentParser("Convert ARIS AML to Archimate Open Exchange Fine")
    parser.add_argument('file', help="AML input file")
    parser.add_argument('-s', '--scale', required=False, help='Diagram scale factor')
    parser.add_argument('-O', '--orgs', required=False, action='store_true', help='Include organizations structure')
    parser.add_argument('-E', '--embed', required=False, action='store_true',
                        help="Try to embed visual nodes (experimental)")
    parser.add_argument('-xo', '--noOptimization', required=False, action='store_true',
                        help='Do no remove elements and relationships that are not sed in views')
    parser.add_argument('-o', '--outputfile', required=False, help="Output converted file")
    parser.add_argument('-v', '--verbose', required=False, action='store_true', help="Display DEBUG & INFO log messages")

    args = parser.parse_args()

    if args.verbose:
        log.setLevel(logging.DEBUG)

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

    aris = AML(args.file, name='x', scale_x=scale_x, scale_y=scale_y, skip_bendpoint=False,
               include_organization=True if args.orgs else False,
               incl_unions=True if args.embed else False,
               optimize=False if args.noOptimization else True
               )
    result = aris.convert()

    if args.outputfile:
        open(args.outputfile, 'w').write(result)
    else:
        #  print(result)
        outFile = args.file[:-4]+"_OEF.xml"
        open(outFile, 'w').write(result)


if __name__ == "__main__":
    main()