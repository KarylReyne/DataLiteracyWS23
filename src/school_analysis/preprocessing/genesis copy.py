from io import StringIO
import re
import school_analysis as sa
import pandas as pd
import numpy as np
from school_analysis.preprocessing import GenericParser, SCHOOL_TYPE_MAPPING

from school_analysis import logger

class GenesisParser(GenericParser):
    
    def __init__(self) -> None:
        super().__init__()
        
        # Define mapping
        self.MAPPING: dict[str, function] = {
            "21111-0010": self._parser_21111_0010,
            "21111-0004": self._parser_21111_0004,
            "12411-0011": self._parser_12411_0011,
            "12411-0042": self._parser_12411_0042,
            "12411-0013": self._parser_12411_0013,
            "21381-0013": self._parser_21381_0013, # for SecEff_001
            "21311-0004": self._parser_21311_0004, # for SecEff_002
            "21321-0006": self._parser_21321_0006, # for SecEff_003
            # "21311-0001": self._parser_21311_0001, # for SecEff_000
            "21311-0010": self._parser_21311_0001, # for SecEff_000
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
        df_mapped = df_normal.copy()
        df_mapped["Mapped School Type"] = df_normal["School Type"].map(SCHOOL_TYPE_MAPPING)
        
        return df_mapped
    
    def _parser_12411_0011(self, raw_data, *args, **kwargs) -> pd.DataFrame:
        """Parser for the Zensus"""
        df = pd.read_csv(StringIO(raw_data), sep=";", skiprows=4, skipfooter=4, engine="python")
        df = df.rename(columns={"Unnamed: 0": "Temp", "Sex": "m", "Unnamed: 2": "f", "Unnamed: 3": "all"})
        
        # Build own melted table --> may be done better
        temp = pd.DataFrame(columns=["Year", "Gender", "Value", "Federal State"])
        last_year = ""
        for i in df.index:
            if df.loc[i, "Temp"] is np.nan:
                continue
            elif re.match(r"\d{4}-\d{2}-\d{2}", df.loc[i, "Temp"]):
                last_year = df.loc[i, "Temp"].split("-")[0]
                continue
        
            fs = df.loc[i, "Temp"]
            for g in ["m", "f", "all"]:
                temp.loc[len(temp.index)] = [last_year, g, df.loc[i, g], fs]
        df = temp
        
        return df
    
    def _parser_12411_0042(self, raw_data, *args, **kwargs) -> pd.DataFrame:
        """Parser for the Zensus - age groups"""
        df = pd.read_csv(StringIO(raw_data), sep=";", skiprows=4, skipfooter=4, engine="python")
        df = df.rename(columns={"Unnamed: 0": "Temp", "Germans": "Germans m", "Unnamed: 2": "Germans f", "Unnamed: 3": "Germans all", "Foreigners": "Foreigners m", "Unnamed: 5": "Foreigners f", "Unnamed: 6": "Foreigners all", "Total": "Total m", "Unnamed: 8": "Total f", "Unnamed: 9": "Total all"})
        
        # Build own melted table --> may be done better
        temp = pd.DataFrame(columns=["Year", "Gender", "Value", "Federal State", "Origin"])
        last_year = ""
        for i in df.index:
            if df.loc[i, "Temp"] is np.nan:
                continue
            elif re.match(r"\d{4}", df.loc[i, "Temp"]):
                last_year = df.loc[i, "Temp"].split("-")[0]
                continue
        
            fs = df.loc[i, "Temp"]
            for g in ["m", "f", "all"]:
                for t in ["Germans", "Foreigners", "Total"]:
                    temp.loc[len(temp.index)] = [last_year, g, df.loc[i, t + " " + g], fs, t]
        df = temp
        
        return df
    
    def _parser_12411_0013(self, raw_data, *args, **kwargs) -> pd.DataFrame:
        """Parser for the Zensus - age groups"""
        df = pd.read_csv(StringIO(raw_data), sep=";", skiprows=4, skipfooter=4, engine="python")
        
        # Rename columns
        last_state = ""
        for i in range(1, len(df.columns)):
            if not re.match("Unnamed: \d", df.columns[i]):
                last_state = df.columns[i]
            df = df.rename(columns={df.columns[i]: last_state + "." + df.iloc[0, i]})
        df = df.drop(df.index[0]).reset_index(drop=True)
        df = df.rename(columns={"Unnamed: 0": "Temp"})
        
        # Build own melted table --> may be done better
        temp = pd.DataFrame(columns=["Year", "Gender", "Value", "Federal State", "Age"])
        last_year = ""
        for i in df.index:
            if df.loc[i, "Temp"] is np.nan:
                continue
            elif re.match(r"\d{4}", df.loc[i, "Temp"]):
                last_year = df.loc[i, "Temp"].split("-")[0]
                continue
        
            age = df.loc[i, "Temp"]
            for c in df.columns[1:]:
                splitted = c.split(".")
                federal_state = splitted[0]
                gender = splitted[1]
                gender = "m" if gender == "Male" else "f" if gender == "Female" else "all"
                value = df.loc[i, c]
                temp.loc[len(temp.index)] = [int(last_year), gender, float(value), federal_state, age]                
        
        # Convert age to int
        def convert_ages(x):
            if x == "under 1 year":
                return 0
            elif x == "90 years and over":
                return 90
            elif x == "Total":
                return -1
            else:
                return int(x.split(" ")[0])
        temp["Age"] = temp["Age"].apply(convert_ages)
        
        df = temp
        
        return df
    

    def _parser_21381_0013(self, raw_data, *args, **kwargs) -> pd.DataFrame:
        """Parser for SecEff_001"""
        df = pd.read_csv(StringIO(raw_data), sep=";", skiprows=5, skipfooter=20, engine="python")

        # print(df)
        return df
    
    def _parser_21311_0004(self, raw_data, *args, **kwargs) -> pd.DataFrame:
        """Parser for SecEff_002"""
        df = pd.read_csv(StringIO(raw_data), sep=";", skiprows=6, skipfooter=4, engine="python")

        # print(df)
        return df
    
    def _parser_21321_0006(self, raw_data, *args, **kwargs) -> pd.DataFrame:
        """Parser for SecEff_003"""
        df = pd.read_csv(StringIO(raw_data), sep=";", skiprows=5, skipfooter=4, engine="python")

        # print(df)
        return df
    
    def _parser_21311_0001(self, raw_data, *args, **kwargs) -> pd.DataFrame:
        """Parser for SecEff_000"""
        df = pd.read_csv(StringIO(raw_data), sep=";", skiprows=5, skipfooter=4, engine="python")

        # print(df)
        return df