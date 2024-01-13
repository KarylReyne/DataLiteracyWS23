import pandas as pd
import numpy as np

class Aggregation:

    @staticmethod
    def min_mean_max_grouping(df: pd.DataFrame, group: str = None, grouping_cols: list[str] = ["Year", "Type"], agg_col: str = "Percentage", group_col: str = "Federal State") -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Aggregate the data by grouping_cols and calculate the min, mean and max of agg_col. This function uses first
        a prefiltering of the dataframe by group_col and group. If group is None, the dataframe will not be filtered.
        
        Afterwards the dataframe will be grouped by grouping_cols and the min, mean and max of agg_col will be calculated.

        Args:
            df (pd.DataFrame): Dataframe to aggregate.
            group (str, optional): Optional group name to prefilter the dataframe. Defaults to None.
            grouping_cols (list[str], optional): Columns the groupby will use. Defaults to ["Year", "Type"].
            agg_col (str, optional): Column which should be aggregated. Defaults to "Percentage".
            group_col (str, optional): Column specifying pre grouping. Defaults to "Federal State".

        Returns:
            tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: Tuple of the min, mean and max dataframe.
        """
        g = df[df[group_col].isin(group)] if group is not None else df.copy()
        
        # Aggregate the data
        group_min = g.groupby(grouping_cols).apply(lambda x: x[agg_col].min()).reset_index().rename(columns={0: agg_col})
        group_agg = g.groupby(grouping_cols).apply(lambda x: x[agg_col].mean()).reset_index().rename(columns={0: agg_col})
        group_max = g.groupby(grouping_cols).apply(lambda x: x[agg_col].max()).reset_index().rename(columns={0: agg_col})
        
        return group_min, group_agg, group_max