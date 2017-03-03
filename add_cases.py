import logging 

import argparse
from os.path import isdir
from os import mkdir

import sys

class addcases:

   def __init__(self,code,db_folder,remaining,verbosity,quiet):

        if verbosity >= 3:
            logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
            logging.info("Debug output.")
        elif verbosity == 2:
            logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
            logging.info("More Verbose output.")
        elif verbosity == 1:
            logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.WARNING)
            logging.info("Verbose output.")
        elif quiet:
            logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.CRITICAL)
            logging.info("Quiet output.")
        else:
            logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.ERROR)

        self.code = code
        self.db_folder = db_folder

        parser = argparse.ArgumentParser(
            description='addcases options'
        )
        parser.add_argument('-i','--input-file', metavar='input.cpp', type=argparse.FileType('r'), default=sys.stdin,
                help='Input file')
        parser.add_argument('-o','--output-file', metavar='output.cpp', type=argparse.FileType('r'), default=sys.stdin,
                help='Output file')
        parser.add_argument('-n', '--number', metavar='n', type=int, default = 0,
                help='Number of file')
        parser.add_argument('--input-suffix', 
            help='Specify the suffix of the sample imput files', default='inp')
        parser.add_argument('--output-suffix', 
            help='Specify the suffix of the correct output files', default='cor')
        args = parser.parse_args(remaining)

        logging.debug(code)

        if args.input_file == sys.stdin: print('Enter input:')
        src_inp = args.input_file.read()
        if args.output_file == sys.stdin: print('Enter output:')
        src_cor = args.output_file.read()

        output_suffix = args.output_suffix
        input_suffix = args.input_suffix

        dest_folder ='{}/{}'.format(db_folder,code)
        if not isdir(dest_folder): mkdir(dest_folder) 

        if args.number==0:
            dest = '{}/custom'.format(dest_folder)
        else:
            dest = '{}/custom-{}'.format(dest_folder,args.number)

        dest_inp = dest + '.' + input_suffix
        dest_cor = dest + '.' + output_suffix

        open(dest_inp,'w').write(src_inp)
        open(dest_cor,'w').write(src_cor)

