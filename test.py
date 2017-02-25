import logging as log
from glob import glob   # To check all sample files
from subprocess import Popen, PIPE, check_output,CalledProcessError

log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
# log.info("Debug output.")
# elif args.verbosity == 2:
# log.basicConfig(format="%(levelname)s: %(message)s", level=log.INFO)
# log.info("More Verbose output.")
# elif args.verbosity == 1:
# log.basicConfig(format="%(levelname)s: %(message)s", level=log.WARNING)
# log.info("Verbose output.")
# elif args.quiet:
# log.basicConfig(format="%(levelname)s: %(message)s", level=log.CRITICAL)
# log.info("Quiet output.")
# else:
# log.basicConfig(format="%(levelname)s: %(message)s", level=log.ERROR)

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


def test (folders,command,diffProgram,diffFlags,input_suffix,output_suffix,quiet=False):
    cont,cor,dirs = 0,0,0  # Count the number of sample files and the number of correct ones

    for path in folders:  # Loop through folders

        dirs+=1 # Increase dir count

        log.info('Begining tests in directory: {}'.format(dirs))

        for sample_in in glob(path+'/*.'+input_suffix): 

            cont+=1

            sample_cor = sample_in.split('.')
            sample_cor.pop()
            sample_cor = ''.join(sample_cor)+'.'+output_suffix

            log.debug('Sample file = {}'.format(sample_in))
            log.debug('Correct file = {}'.format(sample_cor))

            log.debug('Opening {}'.format(sample_in))
            myinput = open(sample_in,'r');

            log.debug('Creating temp output file')

            from tempfile import NamedTemporaryFile

            myoutput = NamedTemporaryFile()

            log.debug('Running program ...')
            p = Popen(command, stdin=myinput, stdout=myoutput,stderr=PIPE)
            returnCode = p.wait()

            if returnCode: log.warning('Program returned {}'.format(returnCode))
            else : log.debug('Program returned {}'.format(returnCode))


            while 1:
                try:
                    if (not quiet) : print(ansi.OKBLUE, ansi.BOLD, '*** Input {}'.format(cont), ansi.ENDC, ansi.HEADER)
                    myinput.seek(0)
                    if (not quiet) : print(myinput.read(), ansi.ENDC)
                    out  = check_output([diffProgram]+diffFlags+[myoutput.name,sample_cor])
                    if (not quiet) : print(ansi.OKGREEN, ansi.BOLD, '*** The results match :)', ansi.ENDC, ansi.ENDC)
                    if (not quiet) : print(out.decode('UTF-8'))
                    cor+=1
                    myinput.close()
                    break
                except CalledProcessError as err:   # Thrown if files doesn't match
                    log.debug(err)
                    if (not quiet) : print(ansi.FAIL, ansi.BOLD, '*** The results do NOT match :(', ansi.ENDC, ansi.ENDC)
                    if (not quiet) : print(err.output.decode('UTF-8'))
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

            myoutput.close()

        log.debug('dirs = {};\t cont = {};\t cor = {}'.format(dirs,cont,cor))

    if (cont == cor) :  # Show how many are OK from the total tested
        if (not quiet) : print(ansi.BOLD, ansi.OKGREEN, 'All correct. ({}/{})'.format(cor,cont), ansi.ENDC)
        exit(0)     # All ok, exit = 0
    elif (cor==0):
        if (not quiet) : print(ansi.BOLD, ansi.FAIL, ansi.UNDERLINE, 'ALL tests FAILED. ({}/{})'.format(cor,cont), ansi.ENDC)
    else :
        if (not quiet) : print(ansi.BOLD, ansi.FAIL, 'Correct: {} out of {}'.format(cor,cont), ansi.ENDC)

    return [cor,cont]

