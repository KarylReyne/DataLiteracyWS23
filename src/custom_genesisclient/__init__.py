from suds.client import Client
import logging
import xml
import os
import sys
import argparse


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
            print("suds parsing failed")
            raise(e)
            
        result = result.decode('utf-8')
        id = result.split("\r\n")[1]
        response_parts = [
            list_elem.replace("><", ">SPLIT<").split("SPLIT")
            for entry in result.split(id) 
            for list_elem in entry.split("\r\n") if list_elem != ""
        ]
        data = None
        for item in response_parts:
            if item[0].startswith("GENESIS-Tabelle:"):
                data = item[0].split('\n')
                # [print(row) for row in data]
                break
        return data


def download(client, args):
    rs = '*'
    path = f"{os.getcwd()}{os.sep}{args.filename}.{args.format}"
    if args.regionalschluessel is not None and args.regionalschluessel != '*':
        rs = args.regionalschluessel
        path = '%s_%s.%s' % (args.download, args.regionalschluessel, args.format)
    print("Downloading to file %s" % path)
    years = args.years.split("-")
    result = client.table_export(
        args.download,
        regionalschluessel=rs,
        format=args.format,
        startjahr=years[0],
        endjahr=years[1]
    )
    with open(path, 'w') as save_file:
        for row in result:
            save_file.write(f"{row}\n")
        save_file.close()


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
