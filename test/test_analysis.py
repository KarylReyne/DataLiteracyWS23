from school_analysis.preprocessing.load import Loader
from school_analysis.analysis.aggregation import Aggregation
loader = Loader()

def test_most_common():
    students_per_type = loader.load("school-children-by-type")
    most_common = students_per_type[students_per_type["Certificate Type"] == "Total"].groupby(["Gender", "Mapped School Type"]).apply(lambda x: x["Value"].sum()).reset_index().rename(columns={0: "Value"})
    most_common = most_common[most_common["Gender"] == "Total"]
    most_common = most_common.sort_values("Value", ascending=False)
    most_common = most_common.reset_index(drop=True)
    
    df = students_per_type[(students_per_type["Gender"] == "Total") & (students_per_type["Certificate Type"] == "Total")]
    assert Aggregation.get_most_common_value(df, "Value", ["Gender", "Mapped School Type"]).equals(most_common)
    