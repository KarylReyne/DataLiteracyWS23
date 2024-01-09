import school_analysis as sa
import school_analysis.download as dl
import school_analysis.download.abi as abi_dl
import school_analysis.download.genisis as gen_dl
import yaml
import os
import logging

logger = logging.getLogger(__name__)

def download_all():
    """Downloads all data from the internet"""
    
    # Load config
    skip = False
    if not os.path.exists(sa.CREDENTIAL_PATH):
        skip = True
        logger.log(logging.WARNING, f"Credentials file not found at {sa.CREDENTIAL_PATH}. Skipping Genisis download.")
        
    with open(sa.DOWNLOAD_YAML, "r") as file:
        dl_config = yaml.load(file, Loader=yaml.FullLoader)
    
    if not skip:
        with open(sa.CREDENTIAL_PATH, "r") as file:
            credentials = yaml.load(file, Loader=yaml.FullLoader)
    
    # Download data
    logger.log(logging.INFO, "Start downloading all data ...")
    abi_dl.download_all(dl_config["ABI"])
    dl.download_all(dl_config["DEFAULT"])
    
    # All data with credentials
    if not skip:
        if "GENISIS" not in credentials:
            logger.log(logging.ERROR, f"Credentials file at {sa.CREDENTIAL_PATH} does not contain GENISIS credentials. Skipping Genisis download.")
        else:
            gen_dl.download_all(dl_config["GENISIS"], credentials["GENISIS"])
    
    logger.log(logging.INFO, "Downloading finished.")

if __name__ == "__main__":
    download_all()