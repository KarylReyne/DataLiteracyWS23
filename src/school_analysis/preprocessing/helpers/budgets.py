import pandas as pd

def correct_by_verbraucherpreisindex(data: pd.DataFrame, index_df: pd.DataFrame, index_col="Index", value_col="Budget"):
    result = pd.merge(data, index_df, on=["Year", "Federal State"], how="left")
    result["Reference {}".format(value_col)] = result[value_col] / result[index_col]
    return result