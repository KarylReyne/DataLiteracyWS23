import pandas as pd

class GenericParser:
    def __init__(self) -> None:
        self.MAPPING: dict[str, function] = {}
        
    def parse(self, raw_data: bytes, table_code: str) -> pd.DataFrame:
        """Parses the raw data and returns a dataframes"""
        return self.MAPPING[table_code](raw_data)
    
    def contains(self, id: str) -> bool:
        """Checks if the parser contains a parser for the given id"""
        return id in self.MAPPING.keys()