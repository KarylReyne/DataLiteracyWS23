import os
import yaml
import importlib.resources
import matplotlib.pyplot as plt
from tueplots import bundles
import logging

plt.rcParams.update(bundles.beamer_moml())
plt.rcParams.update({"figure.dpi": 200})

PACKAGE_PATH = importlib.resources.files("school_analysis")
PROJECT_PATH = os.path.join(PACKAGE_PATH, "..", "..")
CREDENTIAL_PATH = os.path.join(PROJECT_PATH, "config", "credentials.yml")
DOWNLOAD_YAML = os.path.join(PROJECT_PATH, "config", "download.yml")

logger = logging.getLogger("Main Logger")
logger.setLevel(logging.INFO)

def create_non_existing_folders(path):
    """Creates all folders that do not exist"""
    if not os.path.exists(path):
        os.makedirs(path)
            
def delete_dir(path):
    """Deletes the directory and all its content"""
    if os.path.exists(path):
        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            if os.path.isdir(file_path):
                delete_dir(file_path)
            else:
                os.remove(file_path)
        os.rmdir(path)
        
def load_download_config():
    """Loads the download config"""
    with open(DOWNLOAD_YAML, "r") as file:
        dl_config = yaml.load(file, Loader=yaml.FullLoader)
    return dl_config