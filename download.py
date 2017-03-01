import logging as log
from tempfile import NamedTemporaryFile

# To get the zip file link from the web
from urllib.parse import urljoin

from urllib.request import urlretrieve
import httplib2 
from bs4 import BeautifulSoup, SoupStrainer 

from os.path import basename
from os import remove
from shutil import move

# To extract the Zip file
from zipfile import ZipFile

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

def downloadHTML(web):
    log.debug('Downloading HTML')

    # The download method and extraction is specific to the jutge.org problems,
    # so there should be changed to be used with other servers.

    # Get html of problem and find the link to the zip file
    http = httplib2.Http()
    status, response = http.request(web)
    soup = BeautifulSoup(response,'lxml')

    log.debug('Got HTML soup = {}'.format(soup))

    return soup

def getName (soup):
   name = soup.find('h1',class_='my-trim') # Get problem title from html tag
   return name.contents[0]

def getTxt (soup):
    # Find statements in html. First paragraph removed cause it contains junk
    txt = soup.find('div',id="txt").find_all('p')[1:] 

    # Merge into a plain html string
    txt = " ".join([str(i) for i in txt])

    # Convert html to plain text using pandoc
    import pypandoc
    txt = pypandoc.convert_text(txt,'plain','html')

    return txt

def downloadZIP (soup,web,dbFolder,code,force_download=False):
    for a in soup.find_all('a', href=True):
        if (basename(a['href'])=='zip'):
            zipUrl = urljoin(web,a['href'])
            log.debug('Link found: ' + zipUrl)
            break # Link found, break

    log.debug('Downloading ZIP form {} ...'.format(zipUrl))

    # Download ZIP into temporary file
    zipFile = NamedTemporaryFile('w+')
    zipFileName = zipFile.name

    urlretrieve(zipUrl, zipFileName) 

    zip_data = ZipFile(zipFileName, 'r')

    log.debug('Extracting ZIP from {} to {} ...'.format(zipFileName,dbFolder))

    # Note that this relies on the zip cointaining a main folder of the form P0000_ca
    zip_data.extractall(dbFolder) 
    zip_data.close()

    # Move folder of the form P00001_ca to P00001
    if (force_download) : rmtree(dbFolder+'/'+code) # Delete previous contents
    move(dbFolder+'/'+zipUrl.split('/')[-2],dbFolder+'/'+code)

    log.info('ZIP file downloaded')

