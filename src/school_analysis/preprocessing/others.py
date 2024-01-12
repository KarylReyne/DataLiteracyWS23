from io import BytesIO
import numpy as np
import pandas as pd
import os
import school_analysis as sa
from school_analysis.preprocessing import GenericParser
from school_analysis.preprocessing.helpers import pisa
from school_analysis import logger

class DefaultParser(GenericParser):
    
    def __init__(self) -> None:
        super().__init__()
        
        # Define mapping
        self.MAPPING: dict[str, function] = {
            "allgemeinbildende-schulen": self._parser_allgemeinbildende_schulen,
            "pisa_germany": self._parser_pisa_germany,
        }

    def _parser_allgemeinbildende_schulen(self, raw_data, *args, **kwargs) -> pd.DataFrame:
        """Parser for the summary table of allgemeinbildende-schulen

        Args:
        -----
            raw_data (bytes): The raw data to parse

        Returns:
        --------
            pd.DataFrame: The parsed data
        """
        parser_args = kwargs.get("parser_args", None)
        if parser_args is None:
            raise ValueError("parser_args must be set")
        
        df = pd.read_excel(BytesIO(raw_data), sheet_name=parser_args.get('sheet'), header=5, skipfooter=45, engine="openpyxl")
        zmw_col = df.columns[1]
        nested_ser = df[df[zmw_col].isna() == 1][df.columns[0]]
        school_ser = df[df[zmw_col] == "z"][df.columns[0]]
        
        # Preprocess such that all rows have the same values for the columns "School Type", "Contract Type" and "Federal State"
        
        # ---- School Type ----
        df["School Type"] = ''
        for index, value in school_ser.items():
            df.iloc[index, -1] = value
            df.iloc[index+1, -1] = value
            df.iloc[index+2, -1] = value
        
        # ---- Contract Type ----
        df["Contract Type"] = ''
        counter = 0
        new_nested_ser = nested_ser.copy()
        for index, value in nested_ser.items():
            if counter % 4 == 0:
                counter += 1
                continue
            
            times = nested_ser.index.tolist()[counter + 1] - index - 1 if counter + 1 < len(nested_ser) else len(df) - index - 1
            for i in range(times):
                df.iloc[index + 1 + i, -1] = value
            
            new_nested_ser = new_nested_ser.drop(index)
            counter += 1
        
        # ---- Federal State ----
        df["Federal State"] = ''
        counter = 0
        for index, value in new_nested_ser.items():
            times = new_nested_ser.index.tolist()[counter + 1] - index - 2 if counter + 1 < len(new_nested_ser) else len(df) - index - 2
            for i in range(times):
                df.iloc[index + 2 + i, -1] = value
            counter += 1
        
        # Preprocess the data into the melted format
        df = df[df["School Type"] != '']
        df = df[df.columns[-3:].tolist() + df.columns[:-3].tolist()]
        df = df.drop(columns=[df.columns[3]])
        df.rename(columns={df.columns[3]: "Gender"}, inplace=True)
        df.reset_index(drop=True, inplace=True)
        df = df.melt(id_vars=df.columns[:4].tolist(), value_vars=df.columns[4:].tolist(), var_name="Year", value_name="Number of Teachers")
        
        # Replace numbers at the end of the strings
        for c in ["Federal State", "Contract Type", "School Type"]:
            df[c] = df[c].str.replace(r'\s*\d+$', '', regex=True)
            df[c] = df[c].str.replace(r'\s*\d+$', '', regex=True)
        
        return df
        
    def _parser_pisa_germany(self, raw_data, *args, **kwargs):
        """Parser for the pisa data of Germany
        Args:
        -----
            raw_data (bytes): The raw data to parse
            args (list): A list of arguments
            kwargs (dict): A dictionary of keyword arguments
            
        Returns:
        --------
            pd.DataFrame: The parsed data        
        """
        
        # Define Maps
        col_map_all = {"Year/Study": "Year", "Average": "avg_all", "Standard Error": "std_all"}
        col_map_gender = {"Year/Study": "Year", "Average": "avg_male", "Standard Error": "std_male", "Average.1": "avg_female", "Standard Error.1": "std_female"}
        col_map_repeated = {"Year/Study": "Year", "Average": "avg_never", "Standard Error": "std_never", "Average.1": "avg_once", "Standard Error.1": "std_once"}

        sheet_map_math = {
            "average": "Report 1- Table",
            "gender": "Report 2- Table",
            "repeated": "Report 3- Table",
        }
        sheet_map_read = {
            "average": "Report 4- Table",
            "gender": "Report 5- Table",
            "repeated": "Report 6- Table",
        }
        sheet_map_science = {
            "average": "Report 7- Table",
            "gender": "Report 8- Table",
            "repeated": "Report 9- Table",
        }

        # Load subjects
        math = pisa.load_subject(raw_data, sheet_map_math, col_map_all, col_map_gender, col_map_repeated, "math")
        read = pisa.load_subject(raw_data, sheet_map_read, col_map_all, col_map_gender, col_map_repeated, "read")
        science = pisa.load_subject(raw_data, sheet_map_science, col_map_all, col_map_gender, col_map_repeated, "science")

        # Create data frame with all subjects
        all_subjects = pd.concat([math, read, science], ignore_index=True).reset_index(drop=True)
        all_subjects_clean = all_subjects.dropna().sort_values(["Year", "Type"])
        all_subjects_clean
        return all_subjects_clean