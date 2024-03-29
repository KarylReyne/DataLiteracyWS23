"""?DEPRECATED?"""
from helpers.config_util import get_config
import os
import subprocess
import pandas as pd
import suds


DOWNLOAD_DIR = "data"
USE_CUSTOM_CWD = True

def get_cwd():
    cwd = os.getcwd()
    if USE_CUSTOM_CWD:
        cwd = get_config("mapped_share_cwd", file="workspace_config.json")
    return cwd

def get_genesis_table(id: str, download=False):
    config_file = "genesis_login.json"
    client = ClientWrapper(
        site='DESTATIS',
        username=get_config("user", file=config_file),
        password=get_config("pw", file=config_file)
    )
    startyear = "2013"
    endyear = "2023"
    filename = f"genesis_{id}_y{startyear}-{endyear}"
    if download:
        print(f"download_genesis_table: downloading table {id}...")
        client.download_csv(id, filename, startyear, endyear)
        print(f"download_genesis_table: successfully downloaded table {id}")
    
    table = None
    try:
        table = pd.read_csv(
            f"{get_cwd()}{os.sep}{DOWNLOAD_DIR}{os.sep}{filename}.csv",
            skiprows=6,
            sep=";",
            index_col=[0, 1],
            skipfooter=13,
            engine="python",
            decimal=",",
        )
    except FileNotFoundError:
        raise DataNotDownloaded(filename)
    
    return table



class ClientWrapper(object):

    def __init__(self, site: str, username: str, password: str) -> None:
        self.site = site
        self.username = username
        self.password = password

    def download_csv(self, id: str, filename: str, startyear: str="2019", endyear: str="2023"):
        c = f"poetry run python ..{os.sep}src{os.sep}custom_genesisclient{os.sep}__init__.py -s {self.site} -u {self.username} -p {self.password} -d {id} -f csv -fn {filename} -y {startyear}-{endyear}"
        subprocess.check_call(c, cwd=f"{get_cwd()}{os.sep}{DOWNLOAD_DIR}{os.sep}", shell=False)
    

class DataNotDownloaded(Exception):
    """The given data file is not in the ./data folder."""

    def __init__(self, file, *args: object) -> None:
        message = f"The given file '{file}' is not in the data folder."
        super().__init__(message, *args)