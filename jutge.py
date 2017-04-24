#!/usr/bin/python

import argparse

import logging 

# OS utilities
import re
from os.path import basename,expanduser,isdir,abspath
from os import remove,makedirs
from shutil import move, rmtree

# Call compiler, program and diff
from subprocess import Popen, PIPE, check_output,CalledProcessError

# Parser options

parser = argparse.ArgumentParser(
        description='Utility to test programms against jutge.org sample cases'
        )
parser.add_argument('command', metavar='command', type=str, 
        help='Script command to run (download, test, get, addCases)')
parser.add_argument('-c','--code',type=str,
        help='code of the problem to check')
parser.add_argument('-v','--verbosity', action='count', default=0,
        help='Show debuging info')
parser.add_argument('-q','--quiet', action='store_true', default=0,
        help='Do not produce any output (only return code)')
parser.add_argument('solution', metavar='file.cpp', type=argparse.FileType('r'), default=[],nargs='*',
        help='Filename of either the source file or the compiled version of the program to check, if no code is specifyed, the filname must contain it in just before the filetype extension')
parser.add_argument('--code-regex', type=str,
        help='Specify the regex to find the code in the file', default='[PGQ][0-9]{5}')
parser.add_argument('-d','--dir', type=str,
        help='Comma separated directories containing the test samples. The first one will be used for download is it doesn\'t contain th correct folder', default='~/Documents/jutge/DB')

args, remaining = parser.parse_known_args()

# For verbosity

if args.verbosity >= 3:
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
    logging.info("Debug output.")
elif args.verbosity == 2:
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
    logging.info("More Verbose output.")
elif args.verbosity == 1:
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.WARNING)
    logging.info("Verbose output.")
# elif args.quiet:
    # logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.CRITICAL)
    # logging.info("Quiet output.")
else:
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.ERROR)

command = args.command

code = args.code
quiet = args.quiet
verbosity = args.verbosity
code_regex = '(' + args.code_regex + ')'
db_folder = expanduser(args.dir)

files=[0]

if args.code: 
    logging.debug('Code Specified')
elif args.solution: 
    logging.debug('Solution')
    files = args.solution

logging.debug(args.solution)

logging.debug("files = ")
logging.debug(files)

logging.debug('code_regex = {}'.format(code_regex))

for prog in files:


    if not args.code :

        logging.debug(prog.name)

        logging.debug("No code provided, searching in file")
        base_name = basename(prog.name)
        try:
            code = re.search(code_regex,base_name).group(1)
            logging.debug(re.search(code_regex,base_name))
        except AttributeError:
            print('Code not found')
            exit(26)    # Without code, we cannot check the cases, so exit
    else:
        print('Error, no code found')
        exit(26)
    logging.debug("code = {}".format(code))

    if command == 'download':
        import download
        download.download(code,db_folder,remaining,verbosity,quiet)
    elif command.startswith('get'):
        import get
        get.get(command,code,db_folder,remaining,verbosity,quiet)
    elif command == 'test':
        if prog == 0:
            logging.error('No file found, aborting')
            exit(-1)
        # Compile if CPP file
        if prog.name.endswith('.cpp'):

            logging.info('Compiling...')

            compile_to = '_' + basename(prog.name).split('.')[0]

            proc = Popen(['g++','-g',prog.name,'-o',compile_to], stdout=PIPE, stderr=PIPE)
            out, err = proc.communicate()
            eCode = proc.wait()

            if(eCode): # Check if compilation failed
                logging.error(err)
                logging.error('Compilation failed, compiler returned code: {}'.format(eCode))
                exit(25)
            else:
                logging.info('Compiled')

            executable = ['./'+compile_to]
        else: executable = prog.name
        # if no DB folder, try to download test cases
        if not isdir('{}/{}'.format(db_folder,code)):
            import download
            download.download(code,db_folder,[],verbosity,quiet)
        import test
        test.test(executable,code,db_folder,remaining,verbosity,quiet)
    elif command == 'addcases':
        pass
        import add_cases
        remaining = args.solution[1:] + remaining
        add_cases.addcases(code,db_folder,remaining,verbosity,quiet)
        exit(0)
    else:
        print("Error, invalid command")
        exit(2)

exit(0)
