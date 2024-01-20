import random
import pandas as pd
from school_analysis.preprocessing.helpers.students_teachers import combine_school_type

school_data = pd.DataFrame({
    "School Type": random.choices(["Primary School", "Secondary School", "Gymnasien (G8)", "Gymnasien (G9)"], k=100),
    "Students": random.choices(range(10, 100), k=100),
    "Teachers": random.choices(range(10, 100), k=100),
    "Gender": random.choices(["m", "w", "z"], k=100),
})

# Drop s.t. each school type is only once per gender in the dataframe
school_data.drop_duplicates(["School Type", "Gender"], inplace=True)


def test_combine_school_type():
    """Test the combine_school_type function."""
    combined = combine_school_type(school_data, "School Type", ["Students", "Teachers"], [
                                   "Gymnasien (G8)", "Gymnasien (G9)"])

    assert combined is not school_data, "The function should return a new dataframe."
    assert combined.columns.tolist() == school_data.columns.tolist(
    ), "The columns should be the same."
    assert combined["School Type"].isin(
        ["Gymnasien (G8)", "Gymnasien (G9)"]).sum() == 0, "The combined school types should not be in the dataframe."
    assert combined["School Type"].unique(
    ).shape[0] == 3, "There should be only 3 school types."
    assert combined["Students"].sum() == school_data["Students"].sum(
    ), "The number of students should be the same."
    assert combined["Teachers"].sum() == school_data["Teachers"].sum(
    ), "The number of teachers should be the same."
    assert combined[combined["School Type"] == "Combined"]["Students"].sum(
    ) == school_data[school_data["School Type"].isin(["Gymnasien (G8)", "Gymnasien (G9)"])]["Students"].sum(), "The sum should be the same"
