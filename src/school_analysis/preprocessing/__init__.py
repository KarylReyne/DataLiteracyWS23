import pandas as pd

SCHOOL_TYPE_MAPPING = {
    "Adult education colleges": "Kollegs",
    "Comprehensive schools": "Gesamtschule",
    "Integrated comprehensive schools": "Integrierte Gesamtschulen",
    "Evening grammar schools": "Abendgymnasien",
    "Evening intermediate schools": "Abendrealschulen",
    "Evening secondary schools": "Abendhauptschulen",
    "Evening secondary general schools": "Abendhauptschulen",
    "Free Waldorf Schools": "Freie Waldorfschulen",
    "Grammar schools": "Gymnasien",
    "Grammar schools (8 years of schooling)": "Gymnasien (G8)",
    "Grammar schools (9 years of schooling)": "Gymnasien (G9)",
    "Intermediate schools": "Realschulen",
    "Primary schools": "Grundschulen",
    "Schools with various courses of education": "Schularten mit mehreren Bildungsgängen",
    "Secondary general schools": "Hauptschulen",
    "Special needs schools": "Förderschulen",
    "Special schools": "Förderschulen",
    "Externals": "External Schools",
}

class GenericParser:
    def __init__(self) -> None:
        self.MAPPING: dict[str, function] = {}
        
    def parse(self, raw_data: bytes, table_code: str, *args, **kwargs) -> pd.DataFrame:
        """Parses the raw data and returns a dataframes"""
        return self.MAPPING[table_code](raw_data, *args, **kwargs)
    
    def contains(self, id: str) -> bool:
        """Checks if the parser contains a parser for the given id"""
        return id in self.MAPPING.keys()