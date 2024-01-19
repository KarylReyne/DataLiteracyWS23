import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from tueplots.constants.color import rgb
from util.plot_util import get_next_tue_plot_color

FEDERAL_STATES= {
    "Old Federal States": ["Schleswig-Holstein", "Niedersachsen", "Bremen", "Hamburg", "Nordrhein-Westfalen", "Hessen", "Rheinland-Pfalz", "Saarland", "Baden-Württemberg", "Bayern"],
    "New Federal States": ["Mecklenburg-Vorpommern", "Brandenburg", "Berlin", "Sachsen", "Sachsen-Anhalt", "Thüringen"]
}


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
    

    def generate_SecEff_001_plots():
        csv_path = f"data{os.sep}genesis{os.sep}SecEff_001_studienberechtigtenquote.csv"
        df = pd.read_csv(csv_path)

        # plotting
        fig1,ax1 = plt.subplots()
        fig2,ax2 = plt.subplots()

        states = df["Unnamed: 0"][df["Unnamed: 0"].index % 4 == 0].to_list()
        states_idx = 0
        states_total = df.loc[df["Unnamed: 0"].index % 4 == 3, df.columns[2:]]

        new_states_mean = np.zeros(len(df.columns[2:]))
        num_new_states = 0
        old_states_mean = np.zeros(len(df.columns[2:]))
        num_old_states = 0
        
        for header in states_total:
            ax1.plot(
                df.columns[2:].to_list(), 
                states_total[header].to_list(), 
                '.-', 
                ms=2, 
                lw=0.75, 
                color=get_next_tue_plot_color(states_idx),
                label=states[states_idx]
            )
            if states[states_idx] in FEDERAL_STATES["New Federal States"]:
                new_states_mean = np.add(new_states_mean, states_total[header].to_list())
                num_new_states += 1
            elif states[states_idx] in FEDERAL_STATES["Old Federal States"]:
                old_states_mean = np.add(old_states_mean, states_total[header].to_list())
                num_old_states += 1
            states_idx += 1

        new_states_mean = [v/num_new_states for v in new_states_mean]
        old_states_mean = [v/num_old_states for v in old_states_mean]
 
        ax2.plot(
            df.columns[2:].to_list(), 
            new_states_mean, 
            '.-', 
            ms=2, 
            lw=0.75, 
            color=get_next_tue_plot_color(1),
            label="New Federal States"
        )
        ax2.plot(
            df.columns[2:].to_list(), 
            old_states_mean, 
            '.-', 
            ms=2, 
            lw=0.75, 
            color=get_next_tue_plot_color(2),
            label="Old Federal States"
        )

        _fontsize = 6
        for ax in [ax1, ax2]:
            ax.set_xlabel("year", fontsize=_fontsize)
            ax.set_ylabel("% of graduates* with university entrance qualification", fontsize=_fontsize)
            # *with allgemeiner Hochschulreife, fachgebundener Hochschulreife or Fachhochschulreife
            ax.legend(bbox_to_anchor=(1.01, 1))

            ax.axhline(0, color=rgb.tue_dark, linewidth=0.5)

            ax.grid(axis="both", color=rgb.tue_dark, linewidth=0.5)
            ax.grid(axis="both", color=rgb.tue_gray, linewidth=0.5)

        fig1.savefig(f"doc{os.sep}report{os.sep}images{os.sep}SecEff_001_PerState-Total.pdf")
        fig2.savefig(f"doc{os.sep}report{os.sep}images{os.sep}SecEff_001_OldVsNewStates-Total.pdf")

    
    def generate_SecEff_002_plots(csv_path: str=f"data{os.sep}genesis{os.sep}SecEff_002_numberOfStudentsPerSubject.csv"):

        # def string_contains(string: str, substring: str):
        #     if substring != "":
        #         return string != string.replace(substring, "")
        #     return True

        # df = pd.read_csv(csv_path)

        # yvalue_dict = {}

        # year = ""
        # per_year_values = {}
        # for i in np.arange(0, len(df["Unnamed: 0"])):
        #     if i % 102 == 1:
        #         yvalue_dict[year] = per_year_values
        #         year = df["Unnamed: 0"][i]
        #         per_year_values = {}
        #     else:
        #         for degree in ["Diplom", "Bachelor", "Master", "Doctor"]:
        #             if string_contains(str(df["Unnamed: 0"][i]), degree):
        #                 num = float(df["Unnamed: 9"][i]) if df["Unnamed: 9"][i] != "-" else 0 #Total Total
        #                 try:
        #                     per_year_values[degree] += num
        #                 except KeyError:
        #                     per_year_values[degree] = num

        # [print(f"{key}: {value}") for key, value in yvalue_dict.items()]
        
        # # plotting
        # fig,ax = plt.subplots()

        # for degree, color in {
        #     "Diplom": rgb.tue_blue, 
        #     "Bachelor": rgb.tue_red, 
        #     "Master": rgb.tue_green, 
        #     "Doctor": rgb.tue_violet
        # }.items():
        #     yvalues = [yvalue_dict[year][degree] for year in yvalue_dict]
        #     ax.plot(yvalue_dict.keys(), yvalues, '.-', ms=2, lw=0.75, color=color, label=degree)

        # _fontsize = 7
        # ax.set_xlabel("year", fontsize=_fontsize)
        # ax.set_ylabel("% of graduates* (mean over all states)", fontsize=_fontsize)
        # ax.legend(loc="center left")

        # ax.axhline(0, color=rgb.tue_dark, linewidth=0.5)

        # ax.grid(axis="both", color=rgb.tue_dark, linewidth=0.5)
        # ax.grid(axis="both", color=rgb.tue_gray, linewidth=0.5)

        # fig.savefig(f"doc{os.sep}report{os.sep}images{os.sep}SecEff_001_GERMANY-Total.pdf")
        pass

    
    def generate_SecEff_003_plots(csv_path: str):
        pass