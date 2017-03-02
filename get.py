import argparse

import logging 

from bs4 import BeautifulSoup

from glob import glob

class get:

    def __init__(self,command,code,dbFolder,remaining,verbosity,quiet):

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

        parser = argparse.ArgumentParser(
            description='Download options'
        )
        parser.add_argument('--input-suffix', 
                help='Specify the suffix of the sample imput files', default='inp')
        parser.add_argument('--output-suffix', 
                help='Specify the suffix of the correct output files', default='cor')

        args = parser.parse_args(remaining)

        self.code = code
        self.dbFolder = dbFolder
        self.input_suffix = args.input_suffix
        self.output_suffix = args.output_suffix
        
        htmlFile = open('{}/{}/problem.html'.format(dbFolder,code),'r')

        self.soup = BeautifulSoup(htmlFile.read(),"lxml")

        htmlFile.close()

        if command == 'getname':
            print(self.getName())
        elif command == 'getcode':
            print(code)
        elif command == 'getstatement':
            print(self.getStatement())
        elif command == 'getsamples':
            print(self.printSamples())
        else:
            logging.error('Error, invalid command')

    def getName (self):
        name = self.soup.find('h1',class_='my-trim') # Get problem title from html tag
        return name.contents[0]

    def getStatement (self):
        # Find statements in html. First paragraph removed cause it contains junk
        txt = self.soup.find('div',id="txt").find_all('p')[1:] 

        # Merge into a plain html string
        txt = " ".join([str(i) for i in txt])

        # Convert html to plain text using pandoc
        import pypandoc
        txt = pypandoc.convert_text(txt,'plain','html')

        return txt

    def printSamples(self):
        cont=0
        for sample_in in glob('{}/{}/*.{}'.format(self.dbFolder,self.code,self.input_suffix)):
            cont+=1

            sample_cor = ''.join(sample_in.split('.')[:-1])+'.'+self.output_suffix

            print('### Input {}'.format(cont))
            print(open(sample_in,'r').read())
            print('### Output {}'.format(cont))
            print(open(sample_cor,'r').read())

