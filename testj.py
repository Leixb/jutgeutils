#!/usr/bin/python

import argparse

import logging as log

# OS utilities
import re
from os.path import basename,expanduser,isdir
from os import remove,makedirs
from shutil import move, rmtree


# To get the zip file link from the web
from urlparse import urljoin

from urllib import urlretrieve
import httplib2 
from bs4 import BeautifulSoup, SoupStrainer 

# To extract the Zip file
from zipfile import ZipFile

from glob import glob   # To check all sample files

# Call compiler, program and diff
from subprocess import Popen, PIPE, check_output,CalledProcessError

# ANSI color sequences
class ansi:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'

# Parser options

parser = argparse.ArgumentParser(
        description='''
Local client to test online judge problems. By default uses jutge.org, but can
be changed to any other server with minor modifications.
''',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog = '''
Usage examples:
    
testj.py Hello_world_P68688.cpp

    This will compile the file and search for the test cases in the default
    foder (~/Documents/jutge/DB/P68688). If it doesn't exist it will download
    it form https://jutge.org/problems/P68688/zip and add it to the folder.

testj.py Hello_world.cpp -c P68688

    This will do the same but specifing the code as an argument

testj.py Hello_world_P68688.o -d ~/DB/Downloaded_tests,~/DB/Custom_tests --no-download
    
    This will check the tests in the folders ~/DB/Downloaded_tests and
    ~/DB/Custom_tests without downloading the tests if they don't exist

testj.py Hello_world_P68688.cpp --diff-program diff --diff-flags ,--normal

    This command will use the diff command for the differences with the flag
    --normal instead of the deafult (colordiff -y) Note that there is a comma
    before normal to prevent that the parser interpretes it as an arguemnt.
        '''
        )
parser.add_argument('solution', metavar='file.cpp', type=file, 
        help='Filename of either the source file or the compiled version of the program to check, if no code is specifyed, the filname must contain it in just before the filetype extension')
group3 = parser.add_mutually_exclusive_group()
group3.add_argument('-v','--verbosity', action='count', default=0,
        help='Show debuging info')
group3.add_argument('-q','--quiet', action='store_true', default=0,
        help='Do not produce any output (only return code)')
parser.add_argument('-c','--code',
        help='code of the problem to check')
parser.add_argument('-d','--dir', type=str,
        help='Comma separated directories containing the test samples. The first one will be used for download is it doesn\'t contain th correct folder', default='~/Documents/jutge/DB')
download = parser.add_argument_group('Download options')
download.add_argument('-w','--webpage', 
        help='Webpage to use', default='https://jutge.org/problems')
download.add_argument('--force-download', action='store_true',
        help='Force download of the tests from the server and save it to the database folder', default=0)
download.add_argument('--download-all', action='store_true',
        help='Download to all folders that don\'t exist, not only the first one', default=0)
download.add_argument('--no-download', action='store_true',
        help='Do not try to download the tests from the server if they are not in the database', default=0)
parser.add_argument('--input-suffix', 
        help='Specify the suffix of the sample imput files', default='inp')
parser.add_argument('--output-suffix', 
        help='Specify the suffix of the correct output files', default='cor')
parser.add_argument('--code-regex', type=str,
        help='Specify the regex to find the code in the file', default='[PGQ][0-9]{5}')
parser.add_argument('--diff-program', type=str,
        help='Specify the program to use as diff', default='colordiff')
parser.add_argument('--diff-flags', type=str,
        help='A string conatining comma separated flags for the diff program', default='-y')
compile_group = parser.add_mutually_exclusive_group()
compile_group.add_argument('--no-compile', action='store_true',
        help='Do not compile .cpp files automatically (will run object file of type _name.o)', default=0)
compile_group.add_argument('--compile', action='store_true',
        help='Compile the code using a compiler (No need to if file ends in .cpp)', default=0)
parser.add_argument('--compiler', type=str,
        help='Compiler to use', default='g++')
parser.add_argument('--compiler-flags', type=str,
        help='comma separated list of flags for the compiler', default='-g,--std=c++11')

args = parser.parse_args()

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
elif args.quiet:
    log.basicConfig(format="%(levelname)s: %(message)s", level=log.CRITICAL)
    log.info("Quiet output.")
else:
    log.basicConfig(format="%(levelname)s: %(message)s", level=log.ERROR)

name = args.solution.name
baseName = basename(name)
command = ['./'+name]

log.debug(args)
log.debug("Name = " + name)

if (name.endswith('.cpp') or args.compile or args.compiler!='g++'): # Compile the program if the file is a .cpp
    
    log.debug("File ends in .cpp")

    compiler = [args.compiler]
    cppFlags=filter(None,args.compiler_flags.split(','))
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

cont,cor,dirs = 0,0,0  # Count the number of sample files and the number of correct ones

for dbFolder_unex in args.dir.split(','):  # Loop through folders

    dbFolder=expanduser(dbFolder_unex)
    path = dbFolder+'/'+code

    dirs+=1 # Increase dir count

    log.debug(path)

    if (not isdir(path) or args.force_download): 
        # If folder is not in the DB, download it. (Only if first folder)

        if(not isdir(dbFolder)): makedirs(dbFolder) # Create DB folder

        if (args.no_download):
            log.error('Test folder not found, skipping...')
            continue # If doesn't exist, try next

        if (dirs==1 or args.download_all):

            log.debug('Downloading HTML to extract link to the zip file')
            web=args.webpage+'/'+code

            # The download method and extraction is specific to the jutge.org problems,
            # so there should be changed to be used with other servers.

            # Get html of problem and find the link to the zip file
            http = httplib2.Http()
            status, response = http.request(web)
            soup = BeautifulSoup(response,'lxml', parse_only=SoupStrainer('a'))

            log.debug('Got HTML soup = {}'.format(soup))

            for a in soup.find_all('a', href=True):
                if (basename(a['href'])=='zip'):
                    zipUrl = urljoin(web,a['href'])
                    log.debug('Link found: ' + zipUrl)
                    break # Link found, break

            log.debug('Downloading ZIP form {} ...'.format(zipUrl))

            zipFileName = code + '.zip'

            urlretrieve(zipUrl, zipFileName) 

            zip_data = ZipFile(zipFileName, 'r')

            log.debug('Extracting ZIP from {} to {} ...'.format(zipFileName,dbFolder))

            # Note that this relies on the zip cointaining a main folder of the form P0000_ca
            zip_data.extractall(dbFolder) 
            zip_data.close()
            
            log.debug('Deleting ZIP file {} ...'.format(zipFileName))

            remove(zipFileName) # Delete file once extracted

            # Move folder of the form P00001_ca to P00001
            if (args.force_download) : rmtree(dbFolder+'/'+code) # Delete previous contents
            move(dbFolder+'/'+zipUrl.split('/')[-2],dbFolder+'/'+code)

            log.info('ZIP file downloaded')

    elif (not isdir(path)) :
        log.warning("path {} not found!".format(path)) # Only download if it is the first folder specified
        continue

    log.info('Begining tests in directory: {}'.format(dirs))

    diffProgram = args.diff_program        #Default: colordiff
    diffFlags = filter(None,args.diff_flags.split(',')) #Default: -y  (side by side)

    for sample_in in glob(path+'/*.'+args.input_suffix): 

        cont+=1

        sample_cor = sample_in.split('.')
        sample_cor.pop()
        sample_cor = ''.join(sample_cor)+'.'+args.output_suffix
        sample_out = path+'/sample_tmp.out'

        log.debug('Sampe file = {}'.format(sample_in))
        log.debug('Correct file = {}'.format(sample_cor))
        log.debug('Output file = {}'.format(sample_out))

        log.debug('Opening {}'.format(sample_in))
        myinput = open(sample_in,'r');

        log.debug('Opening {}'.format(sample_out))
        myoutput = open(sample_out, 'wb')

        log.debug('Running program ...')
        p = Popen(command, stdin=myinput, stdout=myoutput)
        returnCode = p.wait()

        if returnCode: log.warning('Program returned {}'.format(returnCode))
        else : log.debug('Program returned {}'.format(returnCode))

        myoutput.close()

        while 1:
            try:
                print ansi.OKBLUE, ansi.BOLD, '*** Input {}'.format(cont), ansi.ENDC, ansi.HEADER
                myinput.seek(0)
                print myinput.read(), ansi.ENDC
                out  = check_output([diffProgram]+diffFlags+[myoutput.name,sample_cor])
                print ansi.OKGREEN, ansi.BOLD, '*** The results match :)', ansi.ENDC, ansi.ENDC
                print out
                cor+=1
                myinput.close()
                break
            except CalledProcessError as err:   # Thrown if files doesn't match
                log.debug(err)
                print ansi.FAIL, ansi.BOLD, '*** The results do NOT match :(', ansi.ENDC, ansi.ENDC
                print err.output
                myinput.close()
                break
            except OSError:
                log.error('Program {} not found, is it installed? \n Falling back to diff...'.format(diffProgram))
                if (diffProgram != 'diff') :
                    log.error('Falling back to diff...')
                    diffProgram = 'diff'
                else : 
                    myinput.close()
                    break

    log.debug('Deleting {}'.format(sample_out))
    remove(sample_out)  # Clean the file from the DB

    log.debug('dirs = {};\t cont = {};\t cor = {}'.format(dirs,cont,cor))

if (cont == cor) :  # Show how many are OK from the total tested
    print ansi.BOLD, ansi.OKGREEN, 'All correct. ({}/{})'.format(cor,cont), ansi.ENDC
    exit(0)     # All ok, exit = 0
elif (cor==0):
    print ansi.BOLD, ansi.FAIL, ansi.UNDERLINE, 'ALL tests FAILED. ({}/{})'.format(cor,cont), ansi.ENDC
else :
    print ansi.BOLD, ansi.FAIL, 'Correct: {} out of {}'.format(cor,cont), ansi.ENDC

exit(cont-cor)  # Return number is equal to the number of different files




