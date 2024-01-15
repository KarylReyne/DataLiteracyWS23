import pandas as pd
import os
import school_analysis as sa

class Loader():
    
    STD_CONFIG = {
        "sep": ",",
        "encoding": "utf-8",
        "header": [0],
        "index_col": 0
    }
    
    def __init__(self):
        super().__init__()
        
        self._download_config = sa.load_download_config()
        self._mapping = {
            'abi-fails': lambda: self._load_abi('fails'),
            'abi-grades': lambda: self._load_abi('grades'),
            'school-children-by-state': lambda: self._default_loader("GENESIS", "# of school children by federal state (ger)"),
            'school-children-by-type': lambda: self._default_loader("GENESIS", "# of school children by school type (ger)"),
            'teachers-per-schooltype': lambda: self._default_loader("DEFAULT", "Overview destatis german schools 2020/21"),
            'pisa-germany': lambda: self._default_loader("DEFAULT", "Pisa study data for Germany"),
            'zensus': lambda: self._default_loader("GENESIS", "Zensus"),
            'zensus-age': lambda: self._load_age_group("GENESIS", "zensus-"),
        }

    def load(self, name: str):
        if name not in self._mapping:
            raise ValueError(f"Unknown loader {name}")
        
        return self._mapping[name]()
    
    def contains(self, name: str):
        return name in self._mapping
    
    # --- Loader ---
    
    def _load_abi(self, data_set: str):
        # Check if file exists
        if data_set not in self._download_config["ABI"]:
            raise ValueError(f"Unknown data set {data_set}")
        
        path = os.path.join(sa.PROJECT_PATH, "data", self._download_config["ABI"]["dir"], self._download_config["ABI"][data_set]["target"])
        return pd.read_csv(path, **self._download_config["ABI"][data_set]["read_args"])
    
    def _default_loader(self, key: str, dataset: str):
        # Check if file exists
        if key not in self._download_config:
            raise ValueError(f"Unknown key {key}")
        if dataset not in [n["name"] for n in self._download_config[key]]:
            raise ValueError(f"Unknown dataset {dataset}")
        
        i = [n["name"] for n in self._download_config[key]].index(dataset)
        path = os.path.join(sa.PROJECT_PATH, "data", self._download_config[key][i]["folder"], self._download_config[key][i]["filename"].split(".")[0] + ".csv")
        return pd.read_csv(path, **self.STD_CONFIG)
    
    def _load_age_group(self, key: str, filename_prefix: str):
        # Check if file exists
        if key not in self._download_config:
            raise ValueError(f"Unknown key {key}")
        
        # Find file
        dfs = []
        for entry in self._download_config[key]:
            if entry["filename"].startswith(filename_prefix):
                path = os.path.join(sa.PROJECT_PATH, "data", entry["folder"], entry["filename"].split(".")[0] + ".csv")
                dfs.append(pd.read_csv(path, **self.STD_CONFIG))
        
        if len(dfs) == 0:
            raise ValueError(f"Unknown dataset {filename_prefix}")
            
        return pd.concat(dfs, ignore_index=True).reset_index(drop=True)