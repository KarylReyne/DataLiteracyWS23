import os
import importlib.resources
import matplotlib.pyplot as plt
from tueplots import bundles

plt.rcParams.update(bundles.beamer_moml())
plt.rcParams.update({"figure.dpi": 200})

PACKAGE_PATH = importlib.resources.files("src.school_analysis")
PROJECT_PATH = os.path.join(PACKAGE_PATH, "..", "..")
CREDENTIAL_PATH = os.path.join(PROJECT_PATH, "config", "credentials.yml")
DOWNLOAD_YAML = os.path.join(PROJECT_PATH, "config", "download.yml")