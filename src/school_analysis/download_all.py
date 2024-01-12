import argparse
import school_analysis as sa
import school_analysis.download as dl
import school_analysis.download.abi as abi_dl
import school_analysis.download.genesis as gen_dl
import yaml
import os
import logging

from school_analysis import logger

def download_all(kwargs):
    """Downloads all data from the internet"""    
    # Load config
    skip = False
    if not os.path.exists(sa.CREDENTIAL_PATH):
        skip = True
        logger.log(logging.WARNING, f"Credentials file not found at {sa.CREDENTIAL_PATH}. Skipping Genesis download.")
        
    dl_config = sa.load_download_config()
    
    if not skip:
        with open(sa.CREDENTIAL_PATH, "r") as file:
            credentials = yaml.load(file, Loader=yaml.FullLoader)
    
    # Download data
    logger.log(logging.INFO, "Start downloading all data ...")
    abi_dl.download_all(dl_config["ABI"], keep_raw=kwargs.keep_raw)
    dl.download_all(dl_config["DEFAULT"], keep_raw=kwargs.keep_raw)
    
    # All data with credentials
    if not skip:
        if "GENESIS" not in credentials:
            logger.log(logging.ERROR, f"Credentials file at {sa.CREDENTIAL_PATH} does not contain GENESIS credentials. Skipping Genesis download.")
        else:
            gen_dl.download_all(dl_config["GENESIS"], credentials["GENESIS"], keep_raw=kwargs.keep_raw)
    
    logger.log(logging.INFO, "Downloading finished.")

if __name__ == "__main__":
    
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='Download all data from the internet')
    parser.add_argument('--keep-raw', action='store_true', help='If set, the raw data will be saved')
    kwargs = parser.parse_args()
    download_all(kwargs)