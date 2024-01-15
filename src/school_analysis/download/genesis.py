from io import StringIO
import pandas as pd
from suds.client import Client
import xml
import os
import sys
import argparse
import logging
import tqdm
import school_analysis as sa
from school_analysis.preprocessing.genesis import GenesisParser

from school_analysis import logger
parser = GenesisParser()
class GenesisClient(object):

    def __init__(self, site, username=None, password=None):
        self.sites = {
            'DESTATIS': {
                'webservice_url': 'https://www-genesis.destatis.de/genesisWS'
            },
        }
        self.endpoints = {
            'DownloadService_2010': '/services/DownloadService_2010?wsdl',
        }
        if site is None:
            raise Exception('No site given')
        if site not in self.sites:
            sitekeys = ", ".join(sorted(self.sites.keys()))
            raise ValueError('Site not known. Use one of %s.' % sitekeys)
        self.site = site
        self.username = None
        self.password = None
        self.service_clients = {}
        if username is not None:
            self.username = username
        if password is not None:
            self.password = password

    def _init_service_client(self, name):
        if name not in self.service_clients:
            url = (self.sites[self.site]['webservice_url']
                  + self.endpoints[name])
            self.service_clients[name] = Client(
                url, 
                retxml=True
            )
        return self.service_clients[name]
    

    def table_export(self, 
            table_code,
            regionalschluessel='',
            format='csv',
            startjahr="2019",
            endjahr="2023"
        ):
        client = self._init_service_client('DownloadService_2010')
        params = dict(kennung=self.username,
                      passwort=self.password,
                      name=table_code,
                      bereich='Alle',
                      format=format,
                      komprimieren=False,
                      transponieren=False,#
                      startjahr=startjahr,#'1900',
                      endjahr=endjahr,#'2100',
                      zeitscheiben='',
                      regionalmerkmal="",#
                      regionalschluessel=regionalschluessel,
                      sachmerkmal='',
                      sachschluessel='',
                      sachmerkmal2='',#
                      sachschluessel2='',#
                      sachmerkmal3='',#
                      sachschluessel3='',#
                      auftrag=True,#
                      stand="",#
                      sprache='en'
                      )
        result = None
        try:
            result = client.service.TabellenDownload(**params)
        except xml.sax._exceptions.SAXParseException as e:
            logger.log(logging.ERROR, "suds parsing failed")
            raise(e)
            
        result = result.decode('utf-8')
        id = result.split("\r\n")[1]
        response_parts = [
            list_elem.replace("><", ">SPLIT<").split("SPLIT")
            for entry in result.split(id) 
            for list_elem in entry.split("\r\n") if list_elem != ""
        ]
        data = [""]
        for item in response_parts:
            if item[0].startswith("GENESIS-Tabelle:"):
                data = item[0].split('\n')
                break
        data = [row.encode("utf-8") for row in data]
        return data


def download(client, args, keep_raw=False):
    rs = args.get("regionalschluessel", '*')
    
    # Build path
    raw_path = os.path.join(sa.PROJECT_PATH, "data", "raw", args["folder"], args['filename'] + '.' + args['format'])
    processed_path = os.path.join(sa.PROJECT_PATH, "data", args["folder"], args['filename'] + '.csv')
    
    if rs is not None and rs != '*':
        raw_path = os.path.join(sa.PROJECT_PATH, "data", "raw", args["folder"], args['download'] + "_" + rs + '.' + args['format'])
        processed_path = os.path.join(sa.PROJECT_PATH, "data", args["folder"], args['download'] + "_" + rs + '.csv')
        
    logger.log(logging.INFO, "Downloading to file %s" % processed_path)
    years = args['years'].split("-")
    result = client.table_export(
        args['download'],
        regionalschluessel=rs,
        format=args['format'],
        startjahr=years[0],
        endjahr=years[1]
    )
    
    result = "\n".join([row.decode("utf-8") for row in result])
    if len(result) < 10:
        logger.log(logging.ERROR, f"Download failed for table {args['download']}.")
        return
    
    if keep_raw or not parser.contains(args["download"]):
        if not parser.contains(args["download"]):
            logger.log(logging.WARNING, f"For Table {args['download']} no parser found. Saving raw data.")
        
        logger.log(logging.INFO, f"Saving raw data to {raw_path} ...")
        with open(raw_path, "w") as f:
            f.write(result)
            
    if parser.contains(args["download"]):
        try:
            df = parser.parse(result, args["download"])
            df.to_csv(processed_path, index=True)
        except Exception as e:            
            logger.log(logging.ERROR, f"Parser failed. Saving raw data.")
            if keep_raw:
                with open(raw_path, "w") as f:
                    f.write(result)
                    

def download_all(config, credentials, keep_raw=False):
    """Downloads all defined tables of the GENESIS service"""
    user = credentials["DESTATIS"]["user"]
    password = credentials["DESTATIS"]["pass"]
    gc_destatis = GenesisClient("DESTATIS", username=user, password=password)
    
    # TODO: Add LDNRW
    
    for table in tqdm.tqdm(config):
        logger.log(logging.INFO, f"Downloading table {table['name']} to {table['filename'] + '.' + table['format']} ...")
        
        # Create folder if not exists
        if keep_raw:
            folder_raw = os.path.join(sa.PROJECT_PATH, "data", "raw", table["folder"])
            sa.create_non_existing_folders(folder_raw)
        
        folder = os.path.join(sa.PROJECT_PATH, "data", table["folder"])
        sa.create_non_existing_folders(folder)
        
        download(gc_destatis, table, keep_raw=keep_raw)

def main():
    # logging.basicConfig(level='DEBUG')
    logging.basicConfig(level='WARN')
    
    parser = argparse.ArgumentParser(description='These are todays options:')
    parser.add_argument('-s', dest='site', default=None,
                   help='Genesis site to connect to (DESTATIS or LDNRW)')
    parser.add_argument('-u', dest='username', default='',
                   help='username for Genesis login')
    parser.add_argument('-p', dest='password', default='',
                   help='username for Genesis login')
    parser.add_argument('-l', '--lookup', dest='lookup', default=None,
                   metavar="FILTER",
                   help='Get information on the table, property etc. with the key named FILTER. * works as wild card.')
    parser.add_argument('-g', '--search', dest='searchterm', default=None,
                   metavar="SEARCHTERM",
                   help='Find an item using an actual search engine. Should accept Lucene syntax.')
    parser.add_argument('-d', '--download', dest='download', default=None,
                   metavar="TABLE_ID",
                   help='Download table with the ID TABLE_ID')
    parser.add_argument('-fn', '--filename', dest='filename', default="table",
                   metavar="FILENAME",
                   help='Save downloaded table as FILENAME (file format is specified separately with -f, default is .csv)')
    parser.add_argument('--rs', dest='regionalschluessel', default=None,
                   metavar="RS", help='Only select data for region key RS')
    parser.add_argument('-f', '--format', dest='format', default='csv',
                   metavar="FORMAT", help='Download data in this format (csv, html, xls). Default is csv.')
    parser.add_argument('-y', '--years', dest='years', default='2019-2023',
                   metavar="YEARS", 
                   help='Specify a time span for the data with YEARS (where startjahr-endjahr). Default is 2019-2023')

    args = parser.parse_args()

    gc = GenesisClient(args.site, username=args.username,
                    password=args.password)
    # test if the service works
    #gc.test_service()

    if args.download is not None:
        download(gc, args)

    sys.exit()


if __name__ == '__main__':
    main()
