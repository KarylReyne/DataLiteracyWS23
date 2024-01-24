import os
import yaml
import importlib.resources
import matplotlib.pyplot as plt
from tueplots import bundles
import logging

# plt.rcParams.update(bundles.beamer_moml())
plt.rcParams.update({"figure.dpi": 200})

PACKAGE_PATH = importlib.resources.files("school_analysis")
PROJECT_PATH = os.path.join(PACKAGE_PATH, "..", "..")
CREDENTIAL_PATH = os.path.join(PROJECT_PATH, "config", "credentials.yml")
DOWNLOAD_YAML = os.path.join(PROJECT_PATH, "config", "download.yml")

# TEACHERS AND STUDENTS SETTINGS
MC_NUM = 5
CONTRACT_TYPES = ["Vollzeitbeschäftigte Lehrkräfte", "Teilzeitbeschäftigte Lehrkräfte", "Stundenweise beschäftigte Lehrkräfte"]

logger = logging.getLogger("Main Logger")
logger.setLevel(logging.INFO)

# --- Mapping ---

NEW_OLD_STATES_MAPPING= {
    "Old Federal States": ["Schleswig-Holstein", "Niedersachsen", "Bremen", "Hamburg", "Nordrhein-Westfalen", "Hessen", "Rheinland-Pfalz", "Saarland", "Baden-Württemberg", "Bayern"],
    "New Federal States": ["Mecklenburg-Vorpommern", "Brandenburg", "Berlin", "Sachsen", "Sachsen-Anhalt", "Thüringen"]
}

STATE_MAPPING = {
    'BW': 'Baden-Württemberg',
    'BY': 'Bayern',
    'BE': 'Berlin',
    'BB': 'Brandenburg',
    'HB': 'Bremen',
    'HH': 'Hamburg',
    'HE': 'Hessen',
    'MV': 'Mecklenburg-Vorpommern',
    'NI': 'Niedersachsen',
    'NW': 'Nordrhein-Westfalen',
    'RP': 'Rheinland-Pfalz',
    'SL': 'Saarland',
    'N': 'Sachsen',
    'ST': 'Sachsen-Anhalt',
    'SH': 'Schleswig-Holstein',
    'TH': 'Thüringen'
}

GENDER_MAPPING = {
    "z": "all",
    "all": "all",
    "Total": "all",
    "total": "all",
    "m": "m",
    "male": "m",
    "Male": "m",
    "f": "f",
    "w": "f",
    "female": "f",
    "Female": "f"
}

# --- Helper functions ---

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