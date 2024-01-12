import pytest
import test_utils as tu
import test_utils.original_parsers as op

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