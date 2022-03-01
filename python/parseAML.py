import argparse
from AMLparser import AML
from logger import logging, log


def main():
    """
    Read the XML file given as first argument and convert it to Open Exchange File format
    """

    parser = argparse.ArgumentParser("Convert ARIS AML to Archimate Open Exchange File")
    parser.add_argument('file',
                        help="AML input file")
    parser.add_argument('-s', '--scale', required=False,
                        help='Diagram scale factor')
    parser.add_argument('-xO', '--noOrgs', required=False, action='store_true',
                        help='Exclude organizations structure')
    parser.add_argument('-xE', '--noEmbed', required=False, action='store_true',
                        help="Exclude embedding in visual nodes")
    parser.add_argument('-xV', '--noView', required=False, action='store_true',
                        help="Exclude views and report only concepts & relationships")
    parser.add_argument('-xo', '--noOptimization', required=False, action='store_true',
                        help='Do no remove elements and relationships that are not used in views')
    parser.add_argument('-xC', '--noCorrect', required=False, action='store_true',
                        help='Do no correct inverted relationships in embedded objects')
    parser.add_argument('-o', '--outputfile', required=False, help="Output converted file")
    parser.add_argument('-v', '--verbose', required=False, action='store_true',
                        help="Display DEBUG & INFO log messages")

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

    aris = AML(args.file, name='arisExport', scale_x=scale_x, scale_y=scale_y, skip_bendpoint=False,
               include_organization=False if args.noOrgs else True,
               incl_unions=False if args.noEmbed else True,
               optimize=False if args.noOptimization else True,
               correct_embedded_rels=False if args.noEmbed else True,
               no_view=True if args.noView else False
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