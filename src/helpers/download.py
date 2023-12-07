from helpers.config_util import get_config
import os
import sys
import subprocess


DOWNLOAD_DIR = "data"

def get_genesis_table(id: str, download=False):
    config_file = "genesis_login.json"
    client = ClientWrapper(
        site='DESTATIS',
        username=get_config("user", file=config_file),
        password=get_config("pw", file=config_file)
    )
    if download:
        print(f"download_genesis_table: downloading table {id}...")
        client.download_csv(id, f"{DOWNLOAD_DIR}{os.sep}genesis_{id}.csv")
        sys.stdout.write("\033[F")
        print(f"download_genesis_table: successfully downloaded table {id}")


class ClientWrapper(object):

    def __init__(self, site: str, username: str, password: str) -> None:
        self.site = site
        self.username = username
        self.password = password

    def download_csv(self, id: str, save_dir: str):
        c = f"genesiscl -s {self.site} -u {self.username} -p {self.password} -d {id} -f csv"
        subprocess.check_call(c, cwd=f"{os.getcwd()}{os.sep}{DOWNLOAD_DIR}{os.sep}")
    

class DataNotDownloaded(Exception):
    """The given data file is not in the ./data folder."""

    def __init__(self, file, *args: object) -> None:
        message = f"The given file '{file}' is not in the data folder."
        super().__init__(message, *args)