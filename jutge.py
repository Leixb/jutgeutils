#!/usr/bin/python

import argparse

import logging as log

# OS utilities
import re
from os.path import basename,expanduser,isdir
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
    log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
    log.info("Debug output.")
elif args.verbosity == 2:
    log.basicConfig(format="%(levelname)s: %(message)s", level=log.INFO)
    log.info("More Verbose output.")
elif args.verbosity == 1:
    log.basicConfig(format="%(levelname)s: %(message)s", level=log.WARNING)
    log.info("Verbose output.")
# elif args.quiet:
    # log.basicConfig(format="%(levelname)s: %(message)s", level=log.CRITICAL)
    # log.info("Quiet output.")
else:
    log.basicConfig(format="%(levelname)s: %(message)s", level=log.ERROR)

command = args.command

code = args.code
quiet = args.quiet
verbosity = args.verbosity
codeRegex = '(' + args.code_regex + ')'
dbFolder = expanduser(args.dir)

if args.code: files = [0]
elif args.solution: files = args.solution

print(codeRegex)

for prog in files:

    if not args.code :
        baseName = basename(prog.name)
        try:
            code = re.search(codeRegex,baseName).group(1)
        except AttributeError:
            print('Code not found')
            exit(26)    # Without code, we cannot check the cases, so exit
    else:
        print('Error, no code found')
        exit(26)

    if command == 'download':
        import download
        inst = download.download(code,dbFolder,remaining,verbosity,quiet)
        inst.download()
        # download.downloadHTML(web)
        # print(download.getSoup())
        # download.downloadToDB(web,dbFolder,code,force_download)
    elif command == 'get':
        import get
    elif command == 'test':
        import test
    elif command == 'addCases':
        import addCases
    else:
        print("Error, invalid command")
        exit(2)

exit(0)

name = args.solution.name
baseName = basename(name)
command = ['./'+name]

log.debug(args)
log.debug("Name = " + name)

if (name.endswith('.cpp') or args.compile or args.compiler!='g++'): # Compile the program if the file is a .cpp
    
    log.debug("File ends in .cpp")

    compiler = [args.compiler]
    cppFlags=list(filter(None,args.compiler_flags.split(',')))
    objectName = '_'+baseName.split('.')[0]+'.o'
    command = compiler+cppFlags+['-o',objectName,name]

    if (not args.no_compile): 

        log.info('Compiling...')
        log.debug('Running command: ' + ' '.join(command))

        proc = Popen(command, stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()
        eCode = proc.wait()

        if(eCode): # Check if compilation failed
            log.error(err)
            log.error('Compilation failed, compiler returned code: {}'.format(eCode))
            exit(25)
        else:
            log.info('Compiled')

    command = ['./'+objectName]

codeRegex = '('+args.code_regex+')' # Used to get the code from the end of the filename

log.debug('codeRegex = {}'.format(codeRegex))

if (args.code): 
    code = args.code
    try:
        code2 = re.search(codeRegex,code).group(1)
        if (code != code2): log.warning('Provided code doesn\'t match regex')
    except AttributeError:
        log.warning('Provided code doesn\'t match regex') # Do not exit if code is manually specified
else:
    try:
        code = re.search(codeRegex,baseName).group(1)
    except AttributeError:
        log.error('Code not found')
        exit(26)    # Without code, we cannot check the cases, so exit

log.debug('code = '+str(code))

import test
import download

web =args.webpage+'/'+code
soup = download.downloadHTML(web)
print("Name: {}".format(download.getName(soup)))
print("txt: {}".format(download.getTxt(soup)))

diffProgram = args.diff_program        #Default: colordiff
diffFlags = list(filter(None,args.diff_flags.split(','))) #Default: -y  (side by side)

dbFolder = expanduser(args.dir.split(',')[0])
folders = [expanduser(i)+'/'+code for i in args.dir.split(',')]
mainFolder = folders[0]

if(not isdir(dbFolder)): makedirs(dbFolder) # Create DB folder

# If folder is not in the DB, download it. (Only if first folder)
if (not isdir(mainFolder) or args.force_download): 

    log.warning('Main folder not found, proceeding to download')

    web =args.webpage+'/'+code
    soup = download.downloadHTML(web)
    download.downloadZIP(soup,web,dbFolder,code,args.force_download)

[cor,cont] = test.test(folders,command,diffProgram,diffFlags,args.input_suffix,args.output_suffix,args.quiet)

exit(cont-cor)  # Return number is equal to the number of different files

