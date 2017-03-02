import logging as log

import argparse

from glob import glob   # To check all sample files
from subprocess import Popen, PIPE, check_output,CalledProcessError

from os.path import basename

from tempfile import NamedTemporaryFile

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

class test:

    def __init__ (self,command,code,db_folder,remaining,verbosity,quiet):

        if verbosity >= 3:
            log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
            log.info("Debug output.")
        elif verbosity == 2:
            log.basicConfig(format="%(levelname)s: %(message)s", level=log.INFO)
            log.info("More Verbose output.")
        elif verbosity == 1:
            log.basicConfig(format="%(levelname)s: %(message)s", level=log.WARNING)
            log.info("Verbose output.")
        elif quiet:
            log.basicConfig(format="%(levelname)s: %(message)s", level=log.CRITICAL)
            log.info("Quiet output.")
        else:
            log.basicConfig(format="%(levelname)s: %(message)s", level=log.ERROR)

        self.command = command
        self.code = code
        self.db_folder = db_folder
        self.quiet = quiet

        parser = argparse.ArgumentParser(
            description='Test options'
        )
        parser.add_argument('--diff-program', type=str,
            help='Specify the program to use as diff', default='colordiff')
        parser.add_argument('--diff-flags', type=str,
            help='A string conatining comma separated flags for the diff program', default='-y')
        parser.add_argument('--input-suffix', 
            help='Specify the suffix of the sample imput files', default='inp')
        parser.add_argument('--output-suffix', 
            help='Specify the suffix of the correct output files', default='cor')
        parser.add_argument('--use-custom',action='store_true',
            help='Use also custom testcases',default=False)
        args = parser.parse_args(remaining)

        self.diff_program = args.diff_program
        self.diff_flags = args.diff_flags.split(',')
        self.input_suffix = args.input_suffix
        self.output_suffix = args.output_suffix
        self.use_custom = args.use_custom

        self.test()

    def test(self):

        cont,cor,dirs = 0,0,0  # Count the number of sample files and the number of correct ones

        path = '{}/{}'.format(self.db_folder,self.code)

        dirs+=1 # Increase dir count

        log.info('Begining tests in directory: {}'.format(dirs))

        for sample_in in glob(path+'/*.'+self.input_suffix): 

            if basename(sample_in).startswith('custom') :
                if not self.use_custom: 
                    log.debug('Skipping custom test {}'.format(sample_in))
                    continue

            cont+=1

            sample_cor = sample_in.split('.')
            sample_cor.pop()
            sample_cor = ''.join(sample_cor)+'.'+self.output_suffix

            log.debug('Sample file = {}'.format(sample_in))
            log.debug('Correct file = {}'.format(sample_cor))

            log.debug('Opening {}'.format(sample_in))
            myinput = open(sample_in,'r');

            log.debug('Creating temp output file')


            myoutput = NamedTemporaryFile()

            log.debug('Running command {} <{} >{} ...'.format(self.command,myinput.name,myoutput.name))
            p = Popen(self.command, stdin=myinput, stdout=myoutput,stderr=PIPE)
            returnCode = p.wait()

            if returnCode: log.warning('Program returned {}'.format(returnCode))
            else : log.debug('Program returned {}'.format(returnCode))


            while 1:
                try:
                    if (not self.quiet) : print(ansi.OKBLUE, ansi.BOLD, '*** Input {}'.format(cont), ansi.ENDC, ansi.HEADER)
                    myinput.seek(0)
                    if (not self.quiet) : print(myinput.read(), ansi.ENDC)
                    out  = check_output([self.diff_program]+self.diff_flags+[myoutput.name,sample_cor])
                    if (not self.quiet) : print(ansi.OKGREEN, ansi.BOLD, '*** The results match :)', ansi.ENDC, ansi.ENDC)
                    if (not self.quiet) : print(out.decode('UTF-8'))
                    cor+=1
                    myinput.close()
                    break
                except CalledProcessError as err:   # Thrown if files doesn't match
                    log.debug(err)
                    if (not self.quiet) : print(ansi.FAIL, ansi.BOLD, '*** The results do NOT match :(', ansi.ENDC, ansi.ENDC)
                    if (not self.quiet) : print(err.output.decode('UTF-8'))
                    myinput.close()
                    break
                except OSError:
                    log.error('Program {} not found, is it installed? \n Falling back to diff...'.format(self.diff_program))
                    if (self.diff_program != 'diff') :
                        log.error('Falling back to diff...')
                        self.diff_program = 'diff'
                    else : 
                        myinput.close()
                        break

            myoutput.close()

        log.debug('dirs = {};\t cont = {};\t cor = {}'.format(dirs,cont,cor))

        if (cont == cor) :  # Show how many are OK from the total tested
            if (not self.quiet) : print(ansi.BOLD, ansi.OKGREEN, 'All correct. ({}/{})'.format(cor,cont), ansi.ENDC)
        elif (cor==0):
            if (not self.quiet) : print(ansi.BOLD, ansi.FAIL, ansi.UNDERLINE, 'ALL tests FAILED. ({}/{})'.format(cor,cont), ansi.ENDC)
        else :
            if (not self.quiet) : print(ansi.BOLD, ansi.FAIL, 'Correct: {} out of {}'.format(cor,cont), ansi.ENDC)

        return [cor,cont]

