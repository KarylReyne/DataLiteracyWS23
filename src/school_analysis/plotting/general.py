import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from tueplots.constants.color import rgb


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
    

    def generate_SecEff_001_plots(csv_path: str=f"data{os.sep}genesis{os.sep}SecEff_001_studienberechtigtenquote.csv"):
        df = pd.read_csv(csv_path)

        years = df.columns[2:]
        states = df["Unnamed: 0"][0:47:4]

        yvalues_dict = {}

        state_idx = 0
        for s in states:
            for key, modifier in {
                "Entrance qualification for univ. of appl. sciences": 1,
                "University entrance qualification": 2,
                "Total": 3
            }.items():
                data_array = np.array([df[y][state_idx+modifier] for y in years])
                yvalues_dict[f"{s}: {key}"] = data_array
                try:
                    old_array = yvalues_dict[f"GERMANY: {key}"]
                    for i in np.arange(0, len(data_array)):
                        old_array[i].append(data_array[i])
                    yvalues_dict[f"GERMANY: {key}"] = old_array
                except KeyError:
                    yvalues_dict[f"GERMANY: {key}"] = [
                        [data_array[i]] for i in np.arange(0, len(data_array))
                    ]
            state_idx += 4
        
        for v in ["Entrance qualification for univ. of appl. sciences", "University entrance qualification", "Total"]:
            yvalues_dict[f"GERMANY: {v}"] = [np.mean(l)*0.01 for l in yvalues_dict[f"GERMANY: {v}"]]

        # plotting
        fig,ax = plt.subplots()

        for key, value in {
            "Entrance qualification for univ. of appl. sciences": [rgb.tue_blue], 
            "University entrance qualification": [rgb.tue_red], 
            "Total": [rgb.tue_green]
        }.items():
            yvalues = yvalues_dict[f"GERMANY: {key}"]
            ax.plot(years, yvalues, '.-', ms=2, lw=0.75, color=value[0], label=key)

        _fontsize = 7
        ax.set_xlabel("year", fontsize=_fontsize)
        ax.set_ylabel("% of graduates* (mean over all states)", fontsize=_fontsize)
        # *with allgemeiner Hochschulreife, fachgebundener Hochschulreife or Fachhochschulreife
        ax.legend(loc="center left")

        ax.axhline(0, color=rgb.tue_dark, linewidth=0.5)

        ax.grid(axis="both", color=rgb.tue_dark, linewidth=0.5)
        ax.grid(axis="both", color=rgb.tue_gray, linewidth=0.5)

        fig.savefig(f"doc{os.sep}report{os.sep}images{os.sep}SecEff_001_GERMANY-Total.pdf")

    
    def generate_SecEff_002_plots(csv_path: str):
        pass

    
    def generate_SecEff_003_plots(csv_path: str):
        pass