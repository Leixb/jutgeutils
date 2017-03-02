import logging as log

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

    def __init__(self,code,dbFolder,remaining,verbosity,quiet):
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
        self.code = code
        self.dbFolder = dbFolder
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

    def download (self):
        log.debug('Downloading HTML')

        # The download method and extraction is specific to the jutge.org problems,
        # so there should be changed to be used with other servers.

        log.debug(self.web + ' ' + self.code)
        # Get html of problem and find the link to the zip file
        http = httplib2.Http()
        status, response = http.request(self.web)
        soup = BeautifulSoup(response,'lxml')

        log.debug('Got HTML soup = {}'.format(soup))

        zipUrl= False
        for a in soup.find_all('a', href=True):
            log.debug(a)
            if (basename(a['href'])=='zip'):
                zipUrl = urljoin(self.web,a['href'])
                log.debug('Link found: ' + zipUrl)
                break # Link found, break

        log.debug('Downloading ZIP form {} ...'.format(zipUrl))

        zipFileName, trash = urlretrieve(zipUrl)

        zip_data = ZipFile(zipFileName, 'r')

        log.debug("ZIP filelist: {}".format(zip_data.filelist))

        log.debug('Extracting ZIP from {} to {} ...'.format(zipFileName,self.dbFolder))

        # Note that this relies on the zip cointaining a main folder of the form P0000_ca
        zip_data.extractall(self.dbFolder)

        zip_data.close()
        
        try: mainFolder = re.search('^(.*)/',zip_data.filelist[0].filename).group(1)
        except AttributeError: mainFolder=''

        # Move folder of the form P00001_ca to P00001
        if (not exists(self.dbFolder)): mkdir(self.dbFolder)
        if exists(self.dbFolder+'/'+self.code):
            if self.force_download: rmtree(self.dbFolder+'/'+self.code) # Delete previous contents
            else :
                log.error("Folder alreay in DB, aborting (--force-download) to overwrite it")
                return -1

        if mainFolder!='':
            move('{}/{}'.format(self.dbFolder,mainFolder),'{}/{}'.format(self.dbFolder,self.code))

        log.info('ZIP file downloaded')

        htmlFile = open(self.dbFolder+'/'+self.code+'/problem.html','w')

        htmlFile.write(str(soup))
        
        htmlFile.close()

        log.info('HTML file written')
