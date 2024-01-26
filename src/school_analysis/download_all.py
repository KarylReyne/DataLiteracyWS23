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
    
    # Delete old data
    if not kwargs.keep_old and not skip and "all" in kwargs.databases:
        logger.log(logging.INFO, "Deleting old data ...")
        delete_dir = os.path.join(sa.PROJECT_PATH, dl_config["CONFIG"].get("download_path", "data"))
        sa.delete_dir(delete_dir)
        logger.log(logging.INFO, "Deleting finished.")    
    
    # Download data
    logger.log(logging.INFO, "Start downloading all data ...")
    abi_dl.download_all(dl_config["ABI"], keep_raw=kwargs.keep_raw) if kwargs.databases == "all" or "abi" in kwargs.databases else None
    dl.download_all(dl_config["DEFAULT"], keep_raw=kwargs.keep_raw) if kwargs.databases == "all" or "default" in kwargs.databases else None
    
    # All data with credentials
    if not skip:
        if "GENESIS" not in credentials:
            logger.log(logging.ERROR, f"Credentials file at {sa.CREDENTIAL_PATH} does not contain GENESIS credentials. Skipping Genesis download.")
        else:
            gen_dl.download_all(dl_config["GENESIS"], credentials["GENESIS"], keep_raw=kwargs.keep_raw) if kwargs.databases == "all" or "genesis" in kwargs.databases else None
    
    logger.log(logging.INFO, "Downloading finished.")

if __name__ == "__main__":
    
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='Download all data from the internet')
    parser.add_argument('databases', nargs='*', help='The database to download. If not set, all databases will be downloaded', default='all')
    parser.add_argument('--keep-raw', action='store_true', help='If set, the raw data will be saved')
    parser.add_argument('--keep-old', action='store_true', help='If set, the data folder wont be deleted before downloading')
    kwargs = parser.parse_args()
    download_all(kwargs)