import numpy as np
import pandas as pd
import school_analysis as sa
from school_analysis.analysis.aggregation import Aggregation


def get_students_per_teacher(df: pd.DataFrame, types: list[str] = ["Vollzeitbeschäftigte Lehrkräfte", "Teilzeitbeschäftigte Lehrkräfte", "Stundenweise beschäftigte Lehrkräfte"]) -> pd.DataFrame:
    """Get the number of students per teacher for each school type"""
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
    grouping = list(set(df_c.columns.to_list()) -
                    set(["Students", "Number of Teachers", "Contract Type"]))
    merge = list(set(df_c.columns.to_list()) -
                 set(["Students", "Number of Teachers"]))

    grouped_result = df_c.groupby(grouping).apply(apply_fun).reset_index()
    levels = [s for s in grouped_result.columns if s.startswith('level_')]
    grouped_result.drop(levels, axis=1, inplace=True)
    df_c = pd.merge(grouped_result, df_c, how="inner", on=merge)

    return df_c


def get_most_common_school_types(students_per_type: pd.DataFrame, mc_num: int = sa.MC_NUM, school_type_col: str = "Mapped School Type", value_col: str = "Value") -> list[str]:
    """Get the most common school types for the total number of students"""
    df = students_per_type.copy()

    if "Gender" not in students_per_type.columns:
        df["Gender"] = "Total"
    if "Certificate Type" not in students_per_type.columns:
        df["Certificate Type"] = "Total"

    total_students = df[(df["Gender"] == "Total") &
                        (df["Certificate Type"] == "Total")]

    most_common = Aggregation.get_most_common_value(
        total_students, value_col, ["Gender", school_type_col])
    mc_school_types = most_common[school_type_col].values[:mc_num]

    if "Gender" not in students_per_type.columns:
        df.drop("Gender", axis=1)
    if "Certificate Type" not in students_per_type.columns:
        df.drop("Certificate Type", axis=1)

    return mc_school_types


def combine_school_type(df: pd.DataFrame, school_type_col: str = "Mapped School Type", value_col: str | list = "Value", combined_school_types: list = ["Gymnasien (G8)", "Gymnasien (G9)"], new_type: str = "Combined") -> pd.DataFrame:
    """Combine two school types into one

    Args:
        df (pd.DataFrame): Dataframe with the school types.
        school_type_col (str, optional): Column name of the school type. 
        Defaults to "Mapped School Type".
        value_col (str|list, optional): Column name of the aggregated column. Defaults to "Value".
        combined_school_types (list, optional): School Types to combine. 
        Defaults to ["Gymnasien (G8)", "Gymnasien (G9)"].
        new_type (str, optional): New school type name. Defaults to "Combined".

    Returns:
        pd.DataFrame: Dataframe with the combined school types.
    """
    def aggregate_value_cols(group, cols):
        """Aggregate the value columns"""
        for c in cols:
            group[c] = group[c].sum()
        return group

    # Copy the dataframe and get the value columns
    df_c = df.copy()
    value_cols = value_col if isinstance(value_col, list) else [value_col]
    grouped_cols = list(set(df_c.columns.to_list()) -
                        set([school_type_col] + value_cols))

    # Group by all columns except the school type and aggregate the value columns
    grouped = df_c[df_c[school_type_col].isin(combined_school_types)]
    grouped = grouped.groupby(grouped_cols).apply(
        lambda x: aggregate_value_cols(x, value_cols))
    grouped = grouped.reset_index(drop=True).drop_duplicates(grouped_cols)
    grouped[school_type_col] = new_type

    # Drop the old school types
    df_c = df_c[~df_c[school_type_col].isin(combined_school_types)]
    df_c = pd.concat([df_c, grouped], ignore_index=True).reset_index(drop=True)

    return df_c
