import pandas as pd
from tabulate import tabulate

class Exploration:
    
    @staticmethod
    def describe_counts(df, cols):
        """Pretty print the value counts of a dataframe"""
        value_counts = {}
        for c in cols:
            v_counts = df[c].value_counts()
            value_counts[c] = v_counts.keys().tolist()
            value_counts[c + "_count"] = v_counts.values.tolist()
            
        print(tabulate(value_counts, headers='keys'))
    
    @staticmethod
    def analyse_structure(df, cols = None):
        """Analyse the structure of a dataframe"""
        print("Shape: ", df.shape)
        print("Columns: ", df.columns)
        print("Data types:\n", df.dtypes, "\n")
        print("Missing values:\n", df.isnull().sum(), "\n")
        print("Unique values:\n", df.nunique(), "\n")
        print("Value counts: ")
        Exploration.describe_counts(df, df.columns) if cols is None else Exploration.describe_counts(df, cols)

    @staticmethod
    def analyse_min_max(df, col="Value"):
        most_students = df.loc[df[col].idxmax()]
        least_students = df.loc[df[col].idxmin()]

        # Print some stats as a table
        print("Highest {}: \n{}".format(col, most_students))
        print("-" * 100)
        print("Lowest {}: \n{}".format(col, least_students))
        print("-" * 100)