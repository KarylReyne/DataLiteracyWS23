import pandas as pd
import matplotlib.pyplot as plt



class GeneralPlots:
    
    @staticmethod
    def absolute_relative_plot(df: pd.DataFrame, x_column: str, y_column: str, label_column: str, label_types: list[str], grouping: list[str] = ["Year", "Gender"], bbox_to_anchor=(1.4, 0.5)) -> tuple[plt.Figure, plt.Axes]:
        """Generates two plots. The first plot shows the absolute values of the y_column for the label_types. The second plot shows the relative values of the y_column for the label_types.

        Args:
            df (pd.DataFrame): Dataframe to plot.
            x_column (str): Column to plot on the x-axis.
            y_column (str): Column to plot on the y-axis.
            label_column (str): Column to use for the legend and the grouping.
            label_types (list[str]): List of all types to plot.
            grouping (list[str], optional): Grouping for aggregating the data. Defaults to ["Year", "Gender"].

        Returns:
            tuple[plt.Figure, plt.Axes]: Tuple of the figure and the axes.
        """
        
        # Plot the data
        fig, axs = plt.subplots(1, 2, sharex=True)

        # Get the number of students for the most common school label_types
        plot_data = df[df[label_column].isin(label_types)]
        plot_data = df.groupby(grouping + [label_column]).apply(lambda x: x[y_column].sum()).reset_index().rename(columns={0: y_column})
        plot_data["Relative Value"] = plot_data.groupby(grouping)[y_column].transform(lambda x: x / x.sum())
        # Plot the data
        ax = axs[0]

        for ct in label_types:
            plot_data_st = plot_data[plot_data[label_column] == ct]
            ax.plot(plot_data_st[x_column], plot_data_st[y_column], label=ct)
            
        # Other settings
        ax.set_xlabel(x_column)
        ax.set_ylabel(y_column)
        ax.set_title("Absolute {}".format(y_column))
        ax.grid(True)

        ax = axs[1]
        for ct in label_types:
            plot_data_st = plot_data[plot_data[label_column] == ct]
            ax.plot(plot_data_st[x_column], plot_data_st["Relative Value"], label=ct)
        # Other settings
        ax.set_xlabel(x_column)
        ax.set_ylabel("Percents")
        # ax.set_xticks(np.arange(plot_data["Year"].min(), plot_data["Year"].max() + 1, 3))
        ax.set_title("Relative {}".format(y_column))
        ax.grid(True)

        # Build legend
        handles, labels = ax.get_legend_handles_labels()
        fig.legend(handles, labels, loc='right', bbox_to_anchor=bbox_to_anchor, title=label_column)

        return fig, axs