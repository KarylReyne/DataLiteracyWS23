from pandas.core.api import DataFrame as DataFrame
from school_analysis.preprocessing import GenericParser
from school_analysis.preprocessing.abi import AbiParser
from school_analysis.preprocessing.genesis import GenesisParser
from school_analysis.preprocessing.load import Loader
from school_analysis.preprocessing.others import DefaultParser
import os
import school_analysis as sa

class ParserWrapper(GenericParser):
    def __init__(self):
        super().__init__()
        self.MAPPING = {
            "abi-fails": lambda *args, **kwargs: self.abi_parser(os.path.join(sa.PROJECT_PATH, "data", "raw", "abi", *args, **kwargs))[1],
            "abi-grades": lambda *args, **kwargs: self.abi_parser(os.path.join(sa.PROJECT_PATH, "data", "raw", "abi", *args, **kwargs))[0],
            'school-children-by-state': lambda *args, **kwargs: self.genesis_parser(os.path.join(sa.PROJECT_PATH, "data", "raw", "genesis", "school_children_by_state.csv"), "21111-0010", *args, **kwargs),
            'school-children-by-type':lambda *args, **kwargs: self.genesis_parser(os.path.join(sa.PROJECT_PATH, "data", "raw", "genesis", "school_children_by_type.csv"), "21111-0004", *args, **kwargs),
            'teachers-per-schooltype': lambda *args, **kwargs: self.default_parser(os.path.join(sa.PROJECT_PATH, "data", "raw", "other", "allgemeinbildende-schulen.xlsx"), "allgemeinbildende-schulen", *args, parser_args={"sheet": "Tab. 7.1"}, **kwargs),
            'pisa-germany': lambda *args, **kwargs: self.default_parser(os.path.join(sa.PROJECT_PATH, "data", "raw", "other", "pisa_germany.xls"), "pisa_germany", *args, **kwargs),
        }
    def parse(self, table_code: str, *args, **kwargs) -> DataFrame:
        return self.MAPPING[table_code](*args, **kwargs)
    
    def default_parser(self, path: str, table_name: str, action="rb", *args, **kwargs):
        parser = DefaultParser()
        with open(path, action) as f:
            file = f.read()
        return parser.parse(file, table_name, *args, **kwargs)
    
    def abi_parser(self, folder: str):
        parser = AbiParser()
        return parser.parse(folder)
    
    def genesis_parser(self, path: str, table_name: str, action="r",  *args, **kwargs):
        parser = GenesisParser()
        with open(path, action) as f:
            file = f.read()
        return parser.parse(file, table_name , *args, **kwargs)    

def test_loader(id, expected):
    loader = Loader()
    loaded = loader.load(id)
    __generic_df_test(loaded, expected)
                
def test_parser(id, expected):
    parser = ParserWrapper()
    parsed = parser.parse(id)
    __generic_df_test(parsed, expected)
                
def __generic_df_test(given, expected):
    try:
        assert given.equals(expected), "Test failed"
    except:
        print("Test failed")
        # Display the differences
        if len(given.index) != len(expected.index):
            print(f"Lengths differ: {len(given.index)} vs {len(expected.index)}")
        elif not all(given.index == expected.index):
            print("Indices differ")
            print("Difference:", given.index[given.index != expected.index], "vs", expected.index)
        elif not all(given.columns == expected.columns):
            print("Columns differ")
            print("Difference:", given.columns[given.columns != expected.columns], "vs", expected.columns)
        else:
            print("Values differ")
            diff = given.compare(expected, result_names=("Given", "Expected"))
            print(diff)
            if len(diff.index) == 0:
                print("No differences found")
                print("==> Test passed")