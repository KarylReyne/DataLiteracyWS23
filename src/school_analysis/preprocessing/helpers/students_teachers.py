import numpy as np
import pandas as pd
import school_analysis as sa
from school_analysis.analysis.aggregation import Aggregation


def get_students_per_teacher(df: pd.DataFrame, types: list[str] = sa.CONTRACT_TYPES) -> pd.DataFrame:
    def apply_fun(group):
        sum_students = group["Students"].values[0]
        sum_teachers = group["Number of Teachers"].sum()
        
        if sum_teachers == 0:
            group["Students per Teacher"] = np.nan
        else:
            group["Students per Teacher"] = sum_students / sum_teachers
        
        group["Sum Teachers"] = sum_teachers
        
        return group[["Students per Teacher", "Sum Teachers", "Contract Type"]]


    # Apply the function to each group and reset the index
    df_c = df.copy()
    df_c = df_c[df_c["Contract Type"].isin(types)]
    grouping = list(set(df_c.columns.to_list()) - set(["Students", "Number of Teachers", "Contract Type"]))
    merge = list(set(df_c.columns.to_list()) - set(["Students", "Number of Teachers"]))
    
    grouped_result = df_c.groupby(grouping).apply(apply_fun).reset_index()
    levels = [s for s in grouped_result.columns if s.startswith('level_')]
    grouped_result.drop(levels, axis=1, inplace=True)
    df_c = pd.merge(grouped_result, df_c, how="inner", on=merge)

    return df_c

def get_most_common_school_types(students_per_type: pd.DataFrame, mc_num: int = sa.MC_NUM, school_type_col: str = "Mapped School Type", value_col: str = "Value") -> list[str]:
    df = students_per_type.copy()
    
    if "Gender" not in students_per_type.columns:
        df["Gender"] = "Total"
    if "Certificate Type" not in students_per_type.columns:
        df["Certificate Type"] = "Total"
    
    total_students = df[(df["Gender"] == "Total") & (df["Certificate Type"] == "Total")]
    
    most_common = Aggregation.get_most_common_value(total_students, value_col, ["Gender", school_type_col])
    mc_school_types = most_common[school_type_col].values[:mc_num]
    
    if "Gender" not in students_per_type.columns:
        df.drop("Gender", axis=1)
    if "Certificate Type" not in students_per_type.columns:
        df.drop("Certificate Type", axis=1)
    
    return mc_school_types