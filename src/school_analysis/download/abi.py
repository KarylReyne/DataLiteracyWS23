import argparse
import os
import requests
import pandas as pd
import zipfile
import logging
import school_analysis as sa


DOWNLOAD_DIR = os.path.join("data", "grades")
YEARS_TO_DOWNLOAD = [str(i) for i in range(2014, 2022, 1)] + ["2006_2013"]
URL_SCHNELL_MELDUNG = "https://www.kmk.org/fileadmin/Dateien/pdf/Statistik/Dokumentationen/Schnellmeldung_Abiturnoten_"
URL_ARCHIVE = "https://www.kmk.org/fileadmin/Dateien/pdf/Statistik/Aus_Abiturnoten_"
URL_ARCHIVE2 = "https://www.kmk.org/fileadmin/Dateien/pdf/Statistik/Dokumentationen/Aus_Abiturnoten_"
COLUMNS = ["Grade", "BW", "BY", "BE", "BB", "HB", "HH", "HE", "MV", "NI", "NW", "RP", "SL", "N", "ST", "SH", "TH"]

from school_analysis import logger

class Download:
    
    def __init__(self, years_to_download: list = YEARS_TO_DOWNLOAD, dir: str = DOWNLOAD_DIR, ext: str = ".zip", working_dir: str = os.getcwd()) -> None:
        self._years_to_download = years_to_download
        self._dir = dir
        self._ext = ext
        self._working_dir = working_dir
        
    
    def start(self):
        goal_dir = os.path.join(self._working_dir, self._dir)
        os.makedirs(goal_dir, exist_ok=True)
        self.download()
        self.replace_excel(goal_dir)       
    
    def download(self):
        """Download all zip data"""
        
        # Download data        
        for year in self._years_to_download:
            # Url settings
            url = URL_ARCHIVE if year == "2006_2013" or int(year) < 2017 else URL_SCHNELL_MELDUNG if int(year) == 2022 else URL_ARCHIVE2
            used_ext = self._ext
            filename_download = url + (str(year) if int(year) != 2020 else str(year) + "_Werte") + used_ext
            filename_save = os.path.join(self._working_dir, self._dir, year)
            
            # Get the request
            response = requests.get(filename_download)
            if response.status_code == 200:
                if ".zip" in used_ext:
                    with open(filename_save + used_ext, 'wb') as file:
                        file.write(response.content)
                else:
                    with open(filename_save + used_ext, 'w') as file:
                        file.write(response.text)
                logger.log(logging.INFO, f"Zip file '{filename_download}' downloaded successfully to {filename_save + used_ext}")
                self.unpack_zip(zip_path=filename_save + used_ext)
    
    def replace_excel(self, goal_dir: str):
        """Replace all excel files by the corresponding csv data"""
        files = os.listdir(os.path.join(self._working_dir, self._dir))
        for f in files:
            try:
                self.xls_xlsx_to_csv(os.path.join(goal_dir, f), os.path.join(goal_dir, f.split(".")[0] + "_grades.csv"), sheet_name="Noten")
                self.xls_xlsx_to_csv(os.path.join(goal_dir, f), os.path.join(goal_dir, f.split(".")[0] + "_grades_fail.csv"), sheet_name="Noten", skip=lambda x: x not in range(5, 10), columns=["Meta"] + COLUMNS[1:])
                self.xls_xlsx_to_csv(os.path.join(goal_dir, f), os.path.join(goal_dir, f.split(".")[0] + "_dist.csv"), sheet_name="Verteilung", replace=True)
            except ValueError as e:
                logger.log(logging.ERROR, f"Error while converting {f}: {e}")
                
    def xls_xlsx_to_csv(self, input_file: str, output_file: str, replace: bool = False, skip=10, columns=COLUMNS, **kwargs):
        """Transforms the xls and xlsx data into useable csv files"""
        cols = columns
        df: pd.DataFrame = pd.read_excel(input_file, skiprows=skip, **kwargs)
        df.columns = cols
        df.to_csv(output_file)
        if replace:
            os.remove(input_file)
    
    def unpack_zip(self, zip_path: str):
        """Unpacks the zip files and extracts all data"""
        goal = os.path.join(self._working_dir, self._dir)
        with zipfile.ZipFile(zip_path, "r") as f:
            f.extractall(goal)
        
        # Get all files
        files_in_dir = os.listdir(goal)
        logger.log(logging.INFO, f"Extracting files ... {files_in_dir}")
        
        # Delete all not needed files
        for file in files_in_dir:
            if file.lower().endswith('.pdf') or file.lower().endswith('.zip'):
                file_path = os.path.join(goal, file)
                os.remove(file_path)
            else:
                file_path_before = os.path.join(goal, file)
                file_path_new = os.path.join(goal, file.split("_")[-1])
                os.rename(file_path_before, file_path_new if "Werte" not in file else os.path.join(goal, "2020." + file.split(".")[-1]))
        
        # Remove damaged data
        optional_remove = os.path.join(goal, "2013.xlsx")
        if os.path.exists(optional_remove):
            os.remove(optional_remove)

def download_all(config: dict):
    """Downloads all data from the internet"""
    # Download data
    logger.log(logging.INFO, "Downloading abi data ...")
    years = YEARS_TO_DOWNLOAD if "all" in config["years"] else config["years"]
    download = Download(years_to_download=years, ext=config["ext"], working_dir=sa.PROJECT_PATH)
    download.start()

if __name__ == "__main__":
    # Create an argument parser
    parser = argparse.ArgumentParser(description='Download all Abi data.')

    # Add arguments
    parser.add_argument('years', nargs="*", type=str, help='list of years to be downloaded', default=["all"])
    parser.add_argument('--ext', type=str, help='file extensions to be downloaded', default=".zip")
    parser.add_argument('--dir', type=str, help='target dir', default=DOWNLOAD_DIR)
    parser.add_argument('--working-dir', type=str, help='current working directory', default=os.getcwd())

    # Parse command-line arguments
    args = parser.parse_args()
    
    years = YEARS_TO_DOWNLOAD if "all" in args.years else args.years
    download = Download(years_to_download=years, ext=args.ext, working_dir=args.working_dir)
    download.start()