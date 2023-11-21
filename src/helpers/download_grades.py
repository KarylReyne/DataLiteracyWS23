import os
import requests
import pandas as pd
import zipfile


DOWNLOAD_DIR = os.path.join("data", "grades")
YEARS_TO_DOWNLOAD = [str(i) for i in range(2014, 2022, 1)] + ["2006_2013"]
URL_SCHNELL_MELDUNG = "https://www.kmk.org/fileadmin/Dateien/pdf/Statistik/Dokumentationen/Schnellmeldung_Abiturnoten_"
URL_ARCHIVE = "https://www.kmk.org/fileadmin/Dateien/pdf/Statistik/Aus_Abiturnoten_"
URL_ARCHIVE2 = "https://www.kmk.org/fileadmin/Dateien/pdf/Statistik/Dokumentationen/Aus_Abiturnoten_"
COLUMNS = ["Grade", "BW", "BY", "BE", "BB", "HB", "HH", "HE", "MV", "NI", "NW", "RP", "SL", "N", "ST", "SH", "TH"]

class Download:
    
    def __init__(self, years_to_download: list = YEARS_TO_DOWNLOAD, dir: str = DOWNLOAD_DIR, ext: str = ".zip", working_dir: str = os.getcwd()) -> None:
        self._years_to_download = years_to_download
        self._dir = dir
        self._ext = ext
        self._working_dir = working_dir
        
    
    def start(self):
        os.makedirs(os.path.join(self._working_dir, self._dir), exist_ok=True)
        self.download()
        
    
    def download(self):
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
                print(f"Zip file '{filename_download}' downloaded successfully to {filename_save + used_ext}")
                self.unpack_zip(zip_path=filename_save + used_ext)
        
                
    def xls_xlsx_to_csv(self, input_file: str, output_file: str, replace: bool = False, **kwargs):
        """Transforms the xls and xlsx data into useable csv files"""
        cols = kwargs.get("columns", COLUMNS)
        df: pd.DataFrame = pd.read_excel(input_file, **kwargs)
        df.columns = cols
        print(df.info())
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
        print("Extracted: ", files_in_dir)
        
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
        
            
    
if __name__ == "__main__":
    download = Download()
    download.start()