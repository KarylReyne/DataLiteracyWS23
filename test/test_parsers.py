import pytest
import test_utils as tu
import test_utils.original_parsers as op
from school_analysis.preprocessing.load import Loader

loader = Loader()

@pytest.mark.parametrize("name,expected", [
    ("abi-fails", op.load_table_abi_fails()),
    ("abi-grades", op.load_table_abi_grades()),
    ("school-children-by-state", op.load_table_school_children_by_state()),
    ("school-children-by-type", op.load_table_school_children_by_type()),
    ("teachers-per-schooltype", op.load_table_teachers()),
    ("pisa-germany", op.load_table_pisa_germany()),
])

def test_parser(name, expected):
    tu.test_parser(name, expected)
    
def test_school_type_mapping():
    children_school_type = loader.load("school-children-by-type")
    
    unmapped = children_school_type[children_school_type["Mapped School Type"].isna()]["School Type"].unique()
    assert len(list(unmapped)) == 0, "There are unmapped school types: {}".format(unmapped)