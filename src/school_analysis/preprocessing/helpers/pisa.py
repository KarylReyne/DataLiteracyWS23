from io import BytesIO
import numpy as np
import pandas as pd


def replace_nan_year(local_data: pd.DataFrame, year_lbl: str = "Year") -> pd.DataFrame:
    """Replaces the nan year values with the years of the row before."""
    local_data_c = local_data.copy()
    
    for idx in local_data_c.index:
        current_year = local_data_c.loc[idx][year_lbl]
        if idx == 0:
            assert not np.isnan(current_year), "First year entry should not be none!"
        if np.isnan(current_year):
            local_data_c.loc[idx, year_lbl] = local_data_c.loc[idx - 1][year_lbl]
    
    return local_data_c

def load_sheet(raw, sheet_name:str, column_map: dict, skiprows=11, skipfooter=5, year_lbl: str = "Year") -> pd.DataFrame:
    """Loads a single sheet of the provided excel"""
    loaded_data = pd.read_excel(BytesIO(raw), sheet_name=sheet_name, skiprows=skiprows, skipfooter=skipfooter)
    loaded_data = loaded_data.drop(columns="Unnamed: 0")
    loaded_data = loaded_data.rename(columns=column_map)
    loaded_data = replace_nan_year(loaded_data, year_lbl)
    return loaded_data

def load_subject(raw, sheet_map: dict, map_all: dict, map_gender: dict, map_repeated: dict, subject: str) -> pd.DataFrame:
    """Loads a complete subject"""
    # Load the single sheets
    average_points = load_sheet(raw, sheet_map["average"], map_all)
    gender_points = load_sheet(raw, sheet_map["gender"], map_gender)
    repeated_points = load_sheet(raw, sheet_map["repeated"], map_repeated)

    # Merge all sheets and add the subject
    merged = pd.merge(average_points, gender_points, on=["Jurisdiction", "Year"])
    merged = pd.merge(merged, repeated_points, on=["Jurisdiction", "Year"])
    merged = merged.assign(Subject=[subject for _ in range(len(merged.index))])
    
    # Melt the structure
    merged = pd.melt(
        merged,
        id_vars=['Year', 'Jurisdiction', 'Subject'],
        var_name='Measure_Type',
        value_name='Value'
    )

    # Extract gender from the measure_gender column
    merged[['Measure', 'Type']] = merged['Measure_Type'].str.split('_', expand=True)
    merged = merged.drop(columns="Measure_Type")
    merged.replace(["—", "†"], np.nan, inplace=True)
    merged = merged.replace('¹', '', regex=True)
    merged = merged.replace('once', 'repeated at least once', regex=True)
    merged = merged.replace('never', 'repeated never', regex=True)
    merged["Year"] = merged["Year"].astype(int)
    merged["Value"] = merged["Value"].astype(float)
    
    return merged