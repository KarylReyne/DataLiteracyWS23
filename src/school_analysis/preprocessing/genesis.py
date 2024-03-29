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
            "21111-0002": self._parser_21111_0002,
            "12411-0011": self._parser_12411_0011,
            "12411-0042": self._parser_12411_0042,
            "12411-0013": self._parser_12411_0013,
            "21111-0014": self._parser_21111_0014,
            "21111-0008": self._parser_21111_0008,
            "21111-0013": self._parser_21111_0013,
            "21711-0011": self._parser_21711_0011,
            "21711-0010": self._parser_21711_0010,
            "61111-0010": self._parser_61111_0010,
            "21111-0007": self._parser_21111_0007,
            "21111-0002": self._parser_21111_0002,
            "21381-0013": self._parser_21381_0013, # for SecEff_001
            "21311-0004": self._parser_21311_0004, # for SecEff_002
            "21321-0006": self._parser_21321_0006, # for SecEff_003
            # "21311-0001": self._parser_21311_0001, # for SecEff_000
            "21311-0010": self._parser_21311_0001, # for SecEff_000
        }
    
    # ------------------- Parser -------------------
        
    def _parser_21111_0002(self, raw_data, *args, **kwargs) -> pd.DataFrame:
        """Parser school people by school type, gender"""       
        df = pd.read_csv(StringIO(raw_data), sep=";", skiprows=6, skipfooter=3, engine="python", header=None)
        df[0].fillna(method='ffill',inplace=True)
        years = [int(item.split("/")[0]) for item in df.iloc[1].dropna().tolist() if item!='' and item!='\'']
        data = []
        for row in df.iloc[4:,].iterrows():
            for idx,year in enumerate(years):
                school_type = row[1][0]
                grade = row[1][1]        
                male = row[1][2+3*idx]
                female = row[1][3+3*idx]
                total = row[1][4+3*idx]
                record = {
                        'school': school_type,
                        'grade': grade,
                        'year': year,
                        'male': male,
                        'female': female,
                        'total': total,
                    }
                data.append(record)


        melted_df = pd.DataFrame(data)
        melted_df = melted_df[(melted_df['school'] != 'Total') & 
                (melted_df['grade'] != 'Total')]

        return melted_df

    def _parser_21111_0007(self, raw_data, *args, **kwargs) -> pd.DataFrame:
        """Parser special edu support without gender"""
        df = pd.read_csv(StringIO(raw_data), sep=";", skiprows=5, skipfooter=3, engine="python")
        df.rename(columns={"Pupils with special educational support (number)":"school"}, inplace=True)
        df.replace("b'", "", inplace=True, regex=True)
        df.replace("b'", "", inplace=True, regex=True)

        years = [int(item.split("/")[0]) for item in df.iloc[1].dropna().tolist() if item!='' and item!='\'']
        df['school'] = df['school'].fillna(method='ffill')

        df.rename(columns={df.columns[0]: 'school'}, inplace=True)
        df.rename(columns={df.columns[1]: 'effects'}, inplace=True)
        data = []
        for index, row in df.iloc[2:,].iterrows():
            for idx, year in enumerate(years):      
                record = {
                    'school': row[0],
                    'effect': row[1],
                    'year': year,
                    'total': row[2+idx],
                }
                data.append(record)
        melted_df = pd.DataFrame(data)
        melted_df = melted_df[(melted_df['school'] != 'Total') & 
                (melted_df['effect'] != 'Total')]

        melted_df.sort_values(by=['school','year'], inplace=True)
        return melted_df 

    def _parser_21111_0013(self, raw_data, *args, **kwargs) -> pd.DataFrame:
        """Parser for graduates"""
        df = pd.read_csv(StringIO(raw_data), sep=";", skiprows=7, skipfooter=4, engine="python", index_col=None, header=None)
        df.replace("b'", "", inplace=True, regex=True)
        df.replace("'", "", inplace=True, regex=True)
        df.set_index(1, inplace=True)

        df.columns = range(df.shape[1])

        df

        df.replace("b'", "", inplace=True, regex=True)

        df.rename(columns={df.columns[0]: 'state'}, inplace=True)


        df['state'] = df['state'].fillna(method='ffill')

        years = [int(item.split("/")[0]) for item in df.iloc[0].dropna().tolist() if item!='' and item!='\'']

        states = [
            "Baden-Württemberg", 
            "Bayern", 
            "Berlin", 
            "Brandenburg", 
            "Bremen", 
            "Hamburg", 
            "Hessen", 
            "Mecklenburg-Vorpommern", 
            "Niedersachsen", 
            "Nordrhein-Westfalen", 
            "Rheinland-Pfalz", 
            "Saarland", 
            "Sachsen", 
            "Sachsen-Anhalt", 
            "Schleswig-Holstein", 
            "Thüringen"
        ]


        data = []

        for idx,state in enumerate(states):
            part = df.iloc[4+85*idx:]
            part = part[part.index=="Without secondary general school certificate"]
            for row in  part.iterrows():
                for y_idx,year in enumerate(years):
                    male = row[1][1+y_idx*3]
                    female = row[1][2+y_idx*3]
                    total = row[1][3+y_idx*3]           
                    record = {
                        'state': state,
                        'school': row[1]['state'], #state and schol have the same column              
                        'year': year,
                        'male': male,
                        'female':female,
                        'total': total
                    }
                    data.append(record)

        df_melted = pd.DataFrame(data)
        df_melted = df_melted[(df_melted['school'] != 'Total')]
        return df_melted

    def _parser_21111_0008(self, raw_data, *args, **kwargs) -> pd.DataFrame:
        """Parser for students with special educational support"""
        df = pd.read_csv(StringIO(raw_data), sep=";", skiprows=5, skipfooter=4, engine="python")
        df.replace("b'", "", inplace=True, regex=True)

        df.replace("b'", "", inplace=True, regex=True)
        years = [int(item.split("/")[0]) for item in df.iloc[1].dropna().tolist() if item!='' and item!='\'']
        df = df.fillna(method='ffill')

        df.rename(columns={df.columns[0]: 'school'}, inplace=True)
        df.rename(columns={df.columns[1]: 'effects'}, inplace=True)
        data = []
        for index, row in df.iloc[4:,].iterrows():
            for idx, year in enumerate(years):      
                record = {
                    'school': row[0],
                    'effect': row[1],
                    'year': year,
                    'male': row[2+idx*3],
                    'female': row[3+idx*3],
                    'total': row[4+idx*3],
                }
                data.append(record)
        melted_df = pd.DataFrame(data)
        melted_df = melted_df[(melted_df['school'] != 'Total') & 
                (melted_df['effect'] != 'Total')]
        return melted_df
    
    def _parser_21111_0014(self, raw_data, *args, **kwargs) -> pd.DataFrame:
        """Parser for repeaters"""
        df = pd.read_csv(StringIO(raw_data), sep=";", skiprows=5,
                         skipfooter=14, engine="python")
        df.replace("b'", "", inplace=True, regex=True)
        
        df.rename(columns={df.columns[0]: 'state'}, inplace=True)
        df.rename(columns={df.columns[1]: 'grade'}, inplace=True)
        df.rename(columns={df.columns[3]: 'male'}, inplace=True)
        df.rename(columns={df.columns[5]: 'female'}, inplace=True)
        df.rename(columns={df.columns[7]: 'total'}, inplace=True)

        df['state'] = df['state'].ffill()
        df['grade'] = df['grade'].ffill()

        states = [
            "Baden-Württemberg",
            "Bayern",
            "Berlin",
            "Brandenburg",
            "Bremen",
            "Hamburg",
            "Hessen",
            "Mecklenburg-Vorpommern",
            "Niedersachsen",
            "Nordrhein-Westfalen",
            "Rheinland-Pfalz",
            "Saarland",
            "Sachsen",
            "Sachsen-Anhalt",
            "Schleswig-Holstein",
            "Thüringen"
        ]

        data = []
        last_state = ""
        for idx in df.index[3:]:
            row = df.loc[idx]
            if row["state"] in states:
                last_state = row["state"]
                continue
            if row["state"] == "Total":
                last_state = "Total"
                continue

            last_year = ""
            for col in df.columns[2:]:
                if re.match(r"\d{4}/\d{2}", str(df.loc[0][col])):
                    last_year = str(df.loc[0][col]).split("/")[0]

                gender = df.loc[2][col]
                grade = row["grade"]
                school = row["state"]
                record = {
                    'state': last_state,
                    'school': school,  # state and schol have the same column
                    'year': last_year,
                    'grade': grade,
                    'gender': gender,
                    'repeaters': row[col]
                }
                data.append(record)

        df_melted = pd.DataFrame(data)
        df_melted = df_melted.replace("-", np.nan)
        df_melted = df_melted.astype({"year": int, "repeaters": float})
        df_melted = df_melted.pivot_table(values='repeaters', columns="gender", index=[
            "state", "school", "year", "grade"]).reset_index()
        df_melted = df_melted[(df_melted['state'] != 'Total') &
                              (df_melted['school'] != 'Total') &
                              (df_melted['grade'] != 'Total')]
        df_melted = df_melted.rename(columns={
            "Male": "male",
            "Female": "female",
            "Total": "total",
        })
        return df_melted
    
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
        """Parser for the # of graduates by school type of Germany"""
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
    
    def _parser_21111_0002(self, raw_data, *args, **kwargs) -> pd.DataFrame:
        """Parser for the # of children by school type of Germany"""
        df = pd.read_csv(StringIO(raw_data), sep=";", skiprows=7,
                         skipfooter=3, engine="python")
        df = df.rename(
            columns={
                "Unnamed: 0": "School Type",
                "Unnamed: 1": "Grade"
            }
        )
        df = df.loc[1:].reset_index(drop=True)
        temp = pd.DataFrame(
            columns=["Year", "School Type", "Grade", "Students", "Gender"])

        last_school_type = ""
        # Loop over all rows
        for i in df.index[1:]:
            if df.loc[i, "School Type"] is not np.nan:
                last_school_type = df.loc[i, "School Type"]
                continue
            if df.loc[i, "Grade"] is np.nan or df.loc[i, "Grade"] == "Total":
                continue

            grade = df.loc[i, "Grade"]
            last_year = ""

            # Loop over all columns
            for c in df.columns[2:]:
                if re.match(r"\d{4}", str(c)):
                    last_year = c.split("/")[0]
                gender = df.loc[0, c]
                students = df.loc[i, c]
                temp.loc[len(temp)] = [last_year, last_school_type,
                                       grade, students, gender]

        df = temp

        # Right types and columns
        df = df[df["School Type"] != "Total"]
        df.loc[:, "Year"] = df["Year"].astype(int)
        df.loc[:, "Students"] = df["Students"].replace("-", np.nan)
        df.loc[:, "Students"] = df["Students"].astype(float)

        return df

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
    
    def _parser_21711_0011(self, raw_data, *args, **kwargs) -> pd.DataFrame:
        """Parser for the school budgets by child by federal states over the years"""
        df = pd.read_csv(StringIO(raw_data), sep=";", skiprows=4, skipfooter=3, engine="python")
        df = df.rename(columns={"Unnamed: 0": "Federal State"})
        df = df.melt(id_vars=["Federal State"], var_name="Year", value_name="Budget")
        return df
    
    def _parser_61111_0010(self, raw_data, *args, **kwargs) -> pd.DataFrame:
        """Parser for the verbraucherpreisindex by federal states over the years"""
        df = pd.read_csv(StringIO(raw_data), sep=";", skiprows=4, skipfooter=3, engine="python")
        df = df.rename(columns={"Unnamed: 0": "Year"})
        df = df.melt(id_vars=["Year"], var_name="Federal State", value_name="Index")
        df = df.replace(r"^-$", np.nan, regex=True)
        df["Index"] = df["Index"].apply(lambda x: float(x) / 100)
        df["Year Relative"] = 2020        
        return df
    
    def _parser_21711_0010(self, raw_data, *args, **kwargs) -> pd.DataFrame:
        """Parser for the school budgets by federal states over the years and different areas"""
        df = pd.read_csv(StringIO(raw_data), sep=";", skiprows=4, skipfooter=3, engine="python")
        df = df.rename(columns={"Unnamed: 0": "Year/Institution", "Unnamed: 1": "Measure", "Unnamed: 2": "Unit"})
        df = df.drop(df.index[1]).reset_index(drop=True)
        df = df.replace(r"^.$", np.nan, regex=True)
        
        last_year = ""
        last_institution = ""
        temp = pd.DataFrame(columns=["Institution", "Year", "Measure", "Unit", "Value", "Federal State"])
        for i in df.index:
            if re.match(r"\d{4}", str(df.loc[i, "Year/Institution"])):
                last_year = df.loc[i, "Year/Institution"]
                continue
            if df.loc[i, "Year/Institution"] == "Länder":
                continue
            if df.loc[i, "Year/Institution"] is not np.nan:
                last_institution = df.loc[i, "Year/Institution"]
                
            measure = df.loc[i, "Measure"]
            unit = df.loc[i, "Unit"]
                    
            for c in df.columns[3:]:
                federal_state = c
                value = df.loc[i, c]
                temp.loc[len(temp.index)] = [last_institution, int(last_year), measure, unit, float(value), federal_state]
                
        df = temp
        df = df[df["Measure"].isna() == False]
        
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