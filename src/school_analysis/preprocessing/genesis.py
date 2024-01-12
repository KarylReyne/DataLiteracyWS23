from io import StringIO
import school_analysis as sa
import pandas as pd
import numpy as np
from school_analysis.preprocessing import GenericParser

from school_analysis import logger

class GenesisParser(GenericParser):
    
    def __init__(self) -> None:
        super().__init__()
        
        # Define mapping
        self.MAPPING: dict[str, function] = {
            "21111-0010": self._parser_21111_0010,
            "21111-0004": self._parser_21111_0004,
        }
    
    # ------------------- Parser -------------------
    
    def _parser_21111_0010(self, raw_data, *args, **kwargs) -> pd.DataFrame:
        """Parser for the # of children by federal state of Germany"""
        df = pd.read_csv(StringIO(raw_data), sep=";", skiprows=5, skipfooter=3, engine="python")
        df.replace("b'", "", inplace=True, regex=True)
        df.rename(columns={"Unnamed: 0": "School Year"}, inplace=True)
        df.rename(columns={"Baden-W\\xc3\\xbcrttemberg": "Baden-Württemberg"}, inplace=True)
        df.rename(columns={"Th\\xc3\\xbcringen": "Thüringen"}, inplace=True)
        
    
        # Generate gender column
        num_years = 26
        male = df.iloc[:num_years + 3].index
        female = df.iloc[num_years + 3:].index
        all = df.iloc[2 * num_years + 4:].index
        df["gender"] = ''
        df.iloc[male, -1] = "m"
        df.iloc[female, -1] = "f"
        df.iloc[all, -1] = "all"
        df.drop([1,2,29,56], inplace=True)
        
        # Build own melted table --> may be done better
        temp = pd.DataFrame(columns=["Federal State", "Gender", "Type", "Value", "Year"])
        for col_index in range(1, len(df.columns)-1, 3):
            for index in df.index[1:]:
                year = df.loc[index, "School Year"]
                gender = df.loc[index, "gender"]
                federal_state = df.columns[col_index]
                temp.loc[len(temp)] = [federal_state, gender, "Pupils", df.loc[index][df.columns[col_index]], year]
                temp.loc[len(temp)] = [federal_state, gender, "School beginners", df.loc[index][df.columns[col_index + 1]], year]
                temp.loc[len(temp)] = [federal_state, gender, "School leavers (graduates and dropouts)", df.loc[index][df.columns[col_index + 2]], year]
        df = temp
        
        # Replace missing and false values
        df['Value'] = df['Value'].str.replace("'", '')
        df.replace(" ", np.nan, inplace=True)
        df.replace("-", np.nan, inplace=True)
        df.replace("-", np.nan, inplace=True)
        df.replace("'", "", inplace=True)
        df["Value"] = df["Value"].astype(float)
        df["Year"] = df["Year"].replace("/.*", "", regex=True).astype(int)
        
        # Filter out years
        df = df[df["Year"] >= 1998]
        return df

    def _parser_21111_0004(self, raw_data, *args, **kwargs) -> pd.DataFrame:
        """Parser for the # of children by school type of Germany"""
        df = pd.read_csv(StringIO(raw_data), sep=";", skiprows=7, skipfooter=3, engine="python")
        df.replace("Unnamed: 0", "", inplace=True, regex=True)
        df.rename(columns={"b'": "School Year"}, inplace=True)
        df.rename(columns={"Baden-W\\xc3\\xbcrttemberg": "Baden-Württemberg"}, inplace=True)
        df.rename(columns={"Th\\xc3\\xbcringen": "Thüringen"}, inplace=True)
        df = df.drop([1]).reset_index(drop=True)
        
        # Set school Year
        for col_i in range(2, len(df.columns), 3):
            df.iloc[0, col_i + 1] = df.iloc[0, col_i]
            df.iloc[0, col_i + 2] = df.iloc[0, col_i]
        
        df.iloc[0, 0] = "School Type"
        df.iloc[0, 1] = "Certificate Type"
        df.columns = df.iloc[0, :]
        df = df.drop([0])
        df.loc[df[df.columns[0]] == "", [df.columns[0]]] = np.nan
        
        # Build own melted table --> may be done better
        temp = pd.DataFrame(columns=["School Type", "Certificate Type", "Gender", "Value", "Year"])
        for col_index in range(2, len(df.columns), 3):
            
            def insert_entry(i, c_i, last_school):
                year = df.columns[c_i]
                gender = df.iloc[0, c_i]
                school_type = df.iloc[i, 0]
                school_type = school_type if school_type is not np.nan else last_school
                last_school = school_type
                certificate = df.iloc[i, 1]            
                temp.loc[len(temp)] = [school_type, certificate, gender, df.iloc[i, c_i], year]
                return last_school
            
            lc = ""
            for index in range(len(df.index[1:])):
                lc = insert_entry(index, col_index, lc)
                lc = insert_entry(index, col_index+1, lc)
                lc = insert_entry(index, col_index+2, lc)

        df = temp
        df = df.drop([0])
        df = df[df["School Type"] != ""]
        df = df.replace("-", np.nan)
        df["Year"] = df["Year"].replace("/.*", "", regex=True).astype(int)
        df['Value'] = df['Value'].str.replace("'", '')
        df = df.replace("-", np.nan)
        df["Value"] = df["Value"].astype(float)
        df['Gender'] = df['Gender'].str.replace("'", '')
        df_normal = df[df["School Type"] != "Total"]
        return df_normal
