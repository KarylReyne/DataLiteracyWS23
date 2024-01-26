import pandas as pd
import os
import numpy as np
import school_analysis as sa
import re

from school_analysis.preprocessing.helpers.pisa import load_subject

ABI_RAW_PATH = os.path.join(sa.PROJECT_PATH, "data", "raw", "abi")

# ------------------- ABI -------------------

def load_grades_per_year(path=ABI_RAW_PATH, pattern=r".*_grades.csv"):
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
    
    return multiindex_df

def load_table_abi_fails(path=ABI_RAW_PATH, pattern=r".*_grades_fail.csv"):
    return load_grades_per_year(path, pattern).unstack(0)

def load_table_abi_grades(path=ABI_RAW_PATH, pattern=r".*_grades.csv"):
    return load_grades_per_year(path, pattern).unstack(0)

# ------------------- Genesis -------------------

def load_table_school_children_by_state() -> pd.DataFrame:
    path = "data/raw/genesis/school_children_by_state.csv"
    df = pd.read_csv(os.path.join(sa.PROJECT_PATH ,path), sep=";", skiprows=5, skipfooter=3, engine="python")
    df.replace("", "", inplace=True, regex=True)
    df.columns = ["School Year"] + df.columns[1:].tolist()
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
    df['Value'] = df['Value'].str.replace("'", '')
    df.replace(" ", np.nan, inplace=True)
    df.replace("-", np.nan, inplace=True)
    df.replace("-", np.nan, inplace=True)
    df.replace("'", "", inplace=True)
    df["Value"] = df["Value"].astype(float)
    df["Year"] = df["Year"].replace("/.*", "", regex=True).astype(int)
    df = df[df["Year"] >= 1998]
    return df

def load_table_school_children_by_type() -> pd.DataFrame:
    path = "data/raw/genesis/school_children_by_type.csv"
    df = pd.read_csv(os.path.join(sa.PROJECT_PATH ,path), sep=";", skiprows=7, skipfooter=3, engine="python")
    df.replace("b'", "", inplace=True, regex=True)
    df.rename(columns={"": "School Year"}, inplace=True)
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
    return df

# ------------------- Others -------------------

def load_table_teachers(path: str = "data/raw/other/allgemeinbildende-schulen.xlsx", sheet_name: str = "Tab. 7.1") -> pd.DataFrame:
    """Load table from destatis excel file"""
    df = pd.read_excel(os.path.join(sa.PROJECT_PATH ,path), sheet_name=sheet_name, header=5, skipfooter=45, engine="openpyxl")
    zmw_col = df.columns[1]
    nested_ser = df[df[zmw_col].isna() == 1][df.columns[0]]
    school_ser = df[df[zmw_col] == "z"][df.columns[0]]
    
    # Preprocess such that all rows have the same values for the columns "School Type", "Contract Type" and "Federal State"
    
    # ---- School Type ----
    df["School Type"] = np.nan
    for index, value in school_ser.items():
        df.iloc[index, -1] = value
        df.iloc[index+1, -1] = value
        df.iloc[index+2, -1] = value
    
    # ---- Contract Type ----
    df["Contract Type"] = np.nan
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
    df["Federal State"] = np.nan
    counter = 0
    for index, value in new_nested_ser.items():
        times = new_nested_ser.index.tolist()[counter + 1] - index - 2 if counter + 1 < len(new_nested_ser) else len(df) - index - 2
        for i in range(times):
            df.iloc[index + 2 + i, -1] = value
        counter += 1
    
    # Preprocess the data into the melted format
    df = df[df["School Type"].isna() == 0]
    df = df[df.columns[-3:].tolist() + df.columns[:-3].tolist()]
    df = df.drop(columns=[df.columns[3]])
    df.rename(columns={df.columns[3]: "Gender"}, inplace=True)
    df.reset_index(drop=True, inplace=True)
    df = df.melt(id_vars=df.columns[:4].tolist(), value_vars=df.columns[4:].tolist(), var_name="Year", value_name="Number of Teachers")
    return df

def load_table_pisa_germany():
    FILE_PATH = os.path.join(sa.PROJECT_PATH, "data", "raw", "other","pisa_germany.xls")
    with open(FILE_PATH, "rb") as f:
        raw = f.read()
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
    math = load_subject(raw, sheet_map_math, col_map_all, col_map_gender, col_map_repeated, "math")
    read = load_subject(raw, sheet_map_read, col_map_all, col_map_gender, col_map_repeated, "read")
    science = load_subject(raw, sheet_map_science, col_map_all, col_map_gender, col_map_repeated, "science")

    # Create data frame with all subjects
    all_subjects = pd.concat([math, read, science], ignore_index=True).reset_index(drop=True)
    all_subjects_clean = all_subjects.dropna().sort_values(["Year", "Type"])
    return all_subjects_clean