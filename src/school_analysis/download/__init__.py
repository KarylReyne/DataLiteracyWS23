import argparse
import requests
import os

from tqdm import tqdm
from school_analysis.preprocessing.others import DefaultParser
import school_analysis as sa
import logging

logger = logging.getLogger(__name__)
parser = DefaultParser()

class DefaultDownloader:
    
    def __init__(self) -> None:
        pass
    
    def download(self, url: str, target_folder: str, raw_folder: str, parser_id: str, target_name = None, keep_raw: bool = False, **kwargs):
        target_folder = os.path.join(sa.PROJECT_PATH, target_folder)
        raw_folder = os.path.join(sa.PROJECT_PATH, raw_folder)
        target = os.path.join(target_folder, target_name.split(".")[0] + ".csv" if target_name is not None else url.split("?")[0].split("/")[-1].split(".")[0] + ".csv")
        target_raw = os.path.join(raw_folder, target_name if target_name is not None else url.split("?")[0].split("/")[-1])
        # Check if target folder exists
        sa.create_non_existing_folders(target_folder)
        sa.create_non_existing_folders(raw_folder)
            
        # Download file
        logger.log(logging.INFO, f"Downloading {url} to {target}")
        response = requests.get(url)
        if response.status_code == 200:
            failed = True
            
            # Parse data
            if parser.contains(parser_id):
                failed = False
                try:
                    logger.log(logging.INFO, f"Parsing {url} with parser {parser_id}")
                    data = parser.parse(response.content, parser_id, **kwargs)
                    data.to_csv(target, index=False)
                except Exception as e:
                    logger.log(logging.ERROR, f"Parsing of {url} failed with error {e}")
                    failed = True
            
            # Write raw data      
            if keep_raw or failed:
                if failed:
                    logger.log(logging.WARN, f"Saving raw data of {url} to {target} because parsing failed")
                with open(target_raw, 'wb') as file:
                    file.write(response.content)
                    
            logger.log(logging.INFO, f"Downloaded successfully")
        else:
            logger.log(logging.ERROR, f"Download of {url} failed with status code {response.status_code}")

def download_all(config, keep_raw: bool = False):
    """Downloads all default files"""
    downloader = DefaultDownloader()
    for file in tqdm(config):
        logger.log(logging.INFO, f"Downloading {file['url']} to data/{file.get('folder', 'other') + os.sep + file.get('filename', None)}")
        target_folder = os.path.join(sa.PROJECT_PATH, "data", file.get("folder", "other"))
        raw_folder = os.path.join(sa.PROJECT_PATH, "data", "raw", file.get("folder", "other"))
        parser_id = file["filename"].split(".")[0] if file.get("parser_id", None) is None else file.get("parser_id")
        downloader.download(file["url"], target_folder, raw_folder, parser_id, file.get("filename", None), keep_raw=keep_raw, parser_args=file.get("parser_args", None))
          
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Download a simple file.')
    parser.add_argument("url", type=str, help='Url to download')
    parser.add_argument('-tf', dest="target_folder", type=str, help='Target folder', default='data')
    parser.add_argument('-tn', dest="target_name", type=str, help='Target name', default=None)
    
    args = parser.parse_args()
    
    downloader = DefaultDownloader()
    downloader.download(args.url, args.target_folder, args.target_name)
        