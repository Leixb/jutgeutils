import logging 

import argparse

from tempfile import NamedTemporaryFile

# To get the zip file link from the web
from urllib.parse import urljoin

from urllib.request import urlretrieve
import httplib2 
from bs4 import BeautifulSoup, SoupStrainer 

import re
from os.path import basename, exists
from os import remove, mkdir
from shutil import move, rmtree

# To extract the Zip file
from zipfile import ZipFile

class download:

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
            description='Download options'
        )
        parser.add_argument('-w','--webpage', 
                help='Webpage to use', default='https://jutge.org/problems')
        parser.add_argument('--force-download', action='store_true',
                help='Force download of the tests from the server and save it to the database folder', default=0)
        args = parser.parse_args(remaining)

        self.web = '{}/{}'.format(args.webpage,code)
        self.force_download=args.force_download

        self.download()

    def download (self):
        logging.debug('Downloading HTML')

        # The download method and extraction is specific to the jutge.org problems,
        # so there should be changed to be used with other servers.

        logging.debug(self.web + ' ' + self.code)
        # Get html of problem and find the link to the zip file
        http = httplib2.Http()
        status, response = http.request(self.web)
        soup = BeautifulSoup(response,'lxml')

        logging.debug('Got HTML soup = {}'.format(soup))

        zip_url= False
        for a in soup.find_all('a', href=True):
            logging.debug(a)
            if (basename(a['href'])=='zip'):
                zip_url = urljoin(self.web,a['href'])
                logging.debug('Link found: ' + zip_url)
                break # Link found, break

        logging.debug('Downloading ZIP form {} ...'.format(zip_url))

        zip_file_name = urlretrieve(zip_url)[0]

        zip_data = ZipFile(zip_file_name, 'r')

        logging.debug("ZIP filelist: {}".format(zip_data.filelist))

        logging.debug('Extracting ZIP from {} to {} ...'.format(zip_file_name,self.db_folder))

        # Note that this relies on the zip cointaining a main folder of the form P0000_ca
        zip_data.extractall(self.db_folder)

        zip_data.close()
        
        try: main_folder = re.search('^(.*)/',zip_data.filelist[0].filename).group(1)
        except AttributeError: main_folder=''

        # Move folder of the form P00001_ca to P00001
        if (not exists(self.db_folder)): mkdir(self.db_folder)
        if exists(self.db_folder+'/'+self.code):
            if self.force_download: rmtree(self.db_folder+'/'+self.code) # Delete previous contents
            else :
                logging.error("Folder alreay in DB, aborting (--force-download) to overwrite it")
                return -1

        if main_folder!='':
            move('{}/{}'.format(self.db_folder,main_folder),'{}/{}'.format(self.db_folder,self.code))

        logging.info('ZIP file downloaded')

        htmlFile = open(self.db_folder+'/'+self.code+'/problem.html','w')

        htmlFile.write(str(soup))
        
        htmlFile.close()

        logging.info('HTML file written')
