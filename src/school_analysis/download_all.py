import school_analysis as sa
import school_analysis.download.abi as abi_dl
import school_analysis.download.genisis as gen_dl
import yaml
import os
import logging

logger = logging.getLogger(__name__)

def download_all():
    """Downloads all data from the internet"""
    
    # Load config
    if not os.path.exists(sa.CREDENTIAL_PATH):
        logger.log(logging.ERROR, f"Credentials file not found at {sa.CREDENTIAL_PATH}")
        return 1
        
    with open(sa.DOWNLOAD_YAML, "r") as file:
        dl_config = yaml.load(file, Loader=yaml.FullLoader)
        
    with open(sa.CREDENTIAL_PATH, "r") as file:
        credentials = yaml.load(file, Loader=yaml.FullLoader)
    
    # Download data
    logger.log(logging.INFO, "Start downloading all data ...")
    abi_dl.download_all(dl_config["ABI"])
    gen_dl.download_all(dl_config["GENISIS"], credentials["GENISIS"])
    
    logger.log(logging.INFO, "Downloading finished.")

if __name__ == "__main__":
    download_all()