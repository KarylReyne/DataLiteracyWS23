import argparse
import requests
import os

from tqdm import tqdm
import src.school_analysis as sa
import logging

logger = logging.getLogger(__name__)

class DefaultDownloader:
    
    def __init__(self) -> None:
        pass
    
    def download(self, url: str, target_folder: str, target_name = None):
        target_folder = os.path.join(sa.PROJECT_PATH, target_folder)
        target = os.path.join(target_folder, target_name if target_name is not None else url.split("?")[0].split("/")[-1])
        
        # Check if target folder exists
        if not os.path.exists(target_folder):
            logger.log(logging.INFO, f"Creating folder {target_folder}")
            os.makedirs(target_folder)
            
        # Download file
        logger.log(logging.INFO, f"Downloading {url} to {target}")
        response = requests.get(url)
        if response.status_code == 200:
            with open(target, 'wb') as file:
                file.write(response.content)
            logger.log(logging.INFO, f"Downloaded successfully")
        else:
            logger.log(logging.ERROR, f"Download of {url} failed with status code {response.status_code}")

def download_all(config):
    """Downloads all default files"""
    downloader = DefaultDownloader()
    for file in tqdm(config):
        logger.log(logging.INFO, f"Downloading {file['url']} to {file.get('folder', 'data/raw') + os.sep + file.get('filename', None)}")
        downloader.download(file["url"], file.get("folder", "data/raw"), file.get("filename", None))
          
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Download a simple file.')
    parser.add_argument("url", type=str, help='Url to download')
    parser.add_argument('-tf', dest="target_folder", type=str, help='Target folder', default='data')
    parser.add_argument('-tn', dest="target_name", type=str, help='Target name', default=None)
    
    args = parser.parse_args()
    
    downloader = DefaultDownloader()
    downloader.download(args.url, args.target_folder, args.target_name)
        