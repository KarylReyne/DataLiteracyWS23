import pandas as pd
import os
import re
import school_analysis as sa
from school_analysis import logger

class AbiParser():
    def __init__(self) -> None:
        super().__init__()
    
    def parse(self, path) -> list[pd.DataFrame]:
        """Parses the raw data and returns a dataframes
        
        Arguments:
        ----------
            None
            
        Returns:
        --------
            tuple[pd.DataFrame]: A Tuple containing the parsed dataframes [grades per federal state, fails per federal state]
        """
        grades = self._grades_per_year(path=path)
        fails = self._grades_per_year(path=path, pattern=r".*_grades_fail.csv")
        return grades, fails
        
    
    def _grades_per_year(self, path, pattern=r".*_grades.csv"):
        """Creates a dataframe containing the grades per year"""
        # Specific file name pattern
        file_name_pattern = re.compile(pattern)
        # Get a list of all files in the directory matching the pattern
        files = [file for file in os.listdir(path) if file_name_pattern.match(file)]
        grades_per_year = []

        # Load each file into a separate dataframe
        for file in files:
            file_path = os.path.join(path, file)
            dataframe_name = int(os.path.splitext(file)[0].split("_")[0]) + 1 # The year of the exam
            df = pd.read_csv(file_path, index_col=1)
            df = df.drop(columns=['Unnamed: 0'])
            df["File"] = dataframe_name
            grades_per_year.append(df)

        multiindex_df = pd.concat(grades_per_year, keys=[df['File'].iloc[0] for df in grades_per_year]).drop(columns="File")       
        flat_df = multiindex_df.unstack(0)
        return flat_df