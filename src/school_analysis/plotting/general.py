import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import school_analysis as sa
from school_analysis.preprocessing.helpers.students_teachers import get_most_common_school_types
import os
from tueplots.constants.color import rgb
from scipy.stats import kendalltau
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
    
    @staticmethod
    def school_type_corr_plot(melted_df_type: pd.DataFrame, y_col: str, x_col: str, y_label: str = None, x_label: str = None, xticks: np.ndarray = None, yticks: np.ndarray = None, title: str = None, two_plots: bool = False, melted_df: pd. DataFrame = None, school_types: list[str] = ["Gymnasium", "Realschule", "Hauptschule", "Grundschule"], avg=True):
        """Generates a scatter plot for the given data. The data is grouped by school type and the correlation coefficient is calculated for each school type. The average correlation coefficient is also calculated and plotted."""
        fig, axs = plt.subplots(1, 1 if not two_plots else 2, sharex=True, sharey=True)

        for school in school_types:
            ax = axs if not two_plots else axs[1]
            school_data = melted_df_type[melted_df_type["School Type"] == school]
            ax.scatter(school_data[x_col], school_data[y_col], label=school, s=10)

            # Linear regression
            corr = np.corrcoef(school_data[x_col], school_data[y_col])[0][1]
            X = np.vstack([np.ones(len(school_data[x_col])), school_data[x_col]]).T
            y = school_data[y_col]
            w,res,_,_ = np.linalg.lstsq(X, y, rcond=None)
            minimum = school_data[x_col].min()
            maximum = school_data[x_col].max()
            minimum = 0 if np.isnan(minimum) else minimum
            maximum = 0 if np.isnan(maximum) else maximum
            xp = np.linspace(minimum, maximum, int(abs(maximum - minimum) * 100))
            ax.plot(xp, w[0] + w[1] * xp, "--", label="Linear Regression (corr: {:.2f})".format(corr))

        # Average
        # Linear regression
        if avg:
            if melted_df is None:
                melted_df = melted_df_type
            ax = axs if not two_plots else axs[0]
            corr = np.corrcoef(melted_df[x_col], melted_df[y_col])[0][1]
            X = np.vstack([np.ones(len(melted_df[x_col])), melted_df[x_col]]).T
            y = melted_df[y_col]
            w,res,_,_ = np.linalg.lstsq(X, y, rcond=None)
            minimum = melted_df[x_col].min()
            maximum = melted_df[x_col].max()
            xp = np.linspace(minimum, maximum, int(abs(maximum - minimum) * 100))
            ax.scatter(melted_df[x_col], melted_df[y_col], label="Average", s=10)
            ax.plot(xp, w[0] + w[1] * xp, "--", label="Linear Regression (corr: {:.2f})".format(corr))

        # Settings
        ax.set_ylabel(y_col if y_label is None else y_label)
        axs = [axs] if not two_plots else axs
        for ax in axs:
            ax.set_xlabel(x_col if x_label is None else x_label)
            ax.set_xticks(xticks) if xticks is not None else None
            ax.set_yticks(yticks) if yticks is not None else None
            ax.grid()
            ax.legend(bbox_to_anchor=(1.05, 1))

        fig.suptitle(f"{x_col} vs.  {y_col}" if title is None else title)
        plt.show()
    
    @staticmethod
    def federal_state_corr_plot(melted_df_state: pd.DataFrame, y_col: str, x_col: str, y_label: str = None, x_label: str = None, xticks: np.ndarray = None, yticks: np.ndarray = None, title: str = None, two_plots: bool = False, melted_df: pd. DataFrame = None):
        """Generates a scatter plot for the given data. The data is grouped by federal state and the correlation coefficient is calculated for each state. The average correlation coefficient is also calculated and plotted."""
        fig, axs = plt.subplots(1, 1 if not two_plots else 2, sharex=True, sharey=True)
        

        for i, state in enumerate(sa.NEW_OLD_STATES_MAPPING.keys()):
            ax = axs if not two_plots else axs[1]
            state_data = melted_df_state[melted_df_state["Federal State"].isin(sa.NEW_OLD_STATES_MAPPING[state])]
            ax.scatter(state_data[x_col], state_data[y_col], label=state, s=10)

            # Linear regression
            corr = np.corrcoef(state_data[x_col], state_data[y_col])[0][1]
            X = np.vstack([np.ones(len(state_data[x_col])), state_data[x_col]]).T
            y = state_data[y_col]
            w,res,_,_ = np.linalg.lstsq(X, y, rcond=None)
            minimum = state_data[x_col].min()
            maximum = state_data[x_col].max()
            xp = np.linspace(minimum, maximum, int(abs(maximum - minimum) * 100))
            ax.plot(xp, w[0] + w[1] * xp, "--", label="Linear Regression (corr: {:.2f})".format(corr))

        # Average
        # Linear regression
        if melted_df is None:
            melted_df = melted_df_state
        ax = axs if not two_plots else axs[0]
        corr = np.corrcoef(melted_df[x_col], melted_df[y_col])[0][1]
        X = np.vstack([np.ones(len(melted_df[x_col])), melted_df[x_col]]).T
        y = melted_df[y_col]
        w,res,_,_ = np.linalg.lstsq(X, y, rcond=None)
        minimum = melted_df[x_col].min()
        maximum = melted_df[x_col].max()
        xp = np.linspace(minimum, maximum, int(abs(maximum - minimum) * 100))
        ax.scatter(melted_df[x_col], melted_df[y_col], label="Average", s=10)
        ax.plot(xp, w[0] + w[1] * xp, "--", label="Linear Regression (corr: {:.2f})".format(corr))

        # Settings
        ax.set_ylabel(y_col if y_label is None else y_label)
        axs = [axs] if not two_plots else axs
        for ax in axs:
            ax.set_xlabel(x_col if x_label is None else x_label)
            ax.set_xticks(xticks) if xticks is not None else None
            ax.set_yticks(yticks) if yticks is not None else None
            ax.grid()
            ax.legend()

        fig.suptitle(f"{x_col} vs.  {y_col}" if title is None else title)
        plt.show()


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
                [v*0.01 for v in states_total[header].to_list()], 
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

        new_states_mean = [(v/num_new_states)*0.01 for v in new_states_mean]
        old_states_mean = [(v/num_old_states)*0.01 for v in old_states_mean]
 
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

        _fontsize = 5
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

    
    def generate_SecEff_002_plots():
        # get reference data
        ref_csv_path: str=f"data{os.sep}genesis{os.sep}SecEff_000_studierende.csv"
        df_ref = pd.read_csv(ref_csv_path)
        year_mapper = {}
        for s in df_ref["Unnamed: 0"][df_ref["Unnamed: 0"].index > 0]:
            year_mapper[s] = s.lstrip("WT ").split("/")[0]
        df_ref = df_ref.replace({"Unnamed: 0": year_mapper})

        num_students_total = df_ref["Unnamed: 9"][1:].astype(float).to_list()
        num_students_male = df_ref["Total"][1:].astype(float).to_list()
        num_students_female = df_ref["Unnamed: 8"][1:].astype(float).to_list()
        num_students_german = df_ref["Unnamed: 3"][1:].astype(float).to_list()
        num_students_foreign = df_ref["Unnamed: 6"][1:].astype(float).to_list()

        years = df_ref["Unnamed: 0"][1:].to_list()

        data_csv_path: str=f"data{os.sep}genesis{os.sep}SecEff_002_numberOfStudentsPerSubject.csv"
        df_data = pd.read_csv(data_csv_path)

        # plotting
        fig1,ax1 = plt.subplots()
        fig2,ax2 = plt.subplots()
        fig3,ax3 = plt.subplots()

        data_total = []
        data_male = []
        data_female = []
        data_german = []
        data_foreign = []

        rows_per_year = 102
        for i in np.arange(0, np.floor(len(df_data)/rows_per_year)):
            bool_array_to_select_year = [(idx > i*rows_per_year+1 and idx <= i*rows_per_year+rows_per_year) for idx in df_data["Unnamed: 9"].index]

            data_total.append(df_data["Unnamed: 9"][bool_array_to_select_year].replace("-", "0").astype(float).sum(axis=0))
            data_male.append(df_data["Total"][bool_array_to_select_year].replace("-", "0").astype(float).sum(axis=0))
            data_female.append(df_data["Unnamed: 8"][bool_array_to_select_year].replace("-", "0").astype(float).sum(axis=0))
            data_german.append(df_data["Unnamed: 3"][bool_array_to_select_year].replace("-", "0").astype(float).sum(axis=0))
            data_foreign.append(df_data["Unnamed: 6"][bool_array_to_select_year].replace("-", "0").astype(float).sum(axis=0))


        for ax, [data_list, ref_list, labels] in {
            ax1: (
                [data_male, data_female, data_total],
                [num_students_male, num_students_female, num_students_total],
                ["Male", "Female", "Total"]
            ),
            ax2: (
                [data_german, data_foreign, data_total],
                [num_students_german, num_students_foreign, num_students_total],
                ["Germans", "Foreigners", "Total"]
            )
        }.items():
            for i in range(len(data_list)):
                ax.plot(
                    years, 
                    [data_list[i][j]/ref_list[i][j] for j in range(len(years))], 
                    '.-', 
                    ms=2, 
                    lw=0.75, 
                    color=get_next_tue_plot_color(i),
                    label=labels[i]
                )

        _fontsize = 5
        for ax in [ax1, ax2, ax3]:
            ax.set_xlabel("year", fontsize=_fontsize)
            ax.set_ylabel("% of students that earn a degree", fontsize=_fontsize)
            ax.legend(bbox_to_anchor=(1.01, 1))

            ax.axhline(0, color=rgb.tue_dark, linewidth=0.5)

            ax.grid(axis="both", color=rgb.tue_dark, linewidth=0.5)
            ax.grid(axis="both", color=rgb.tue_gray, linewidth=0.5)

        fig1.savefig(f"doc{os.sep}report{os.sep}images{os.sep}SecEff_002_MaleVsFemale.pdf")
        fig2.savefig(f"doc{os.sep}report{os.sep}images{os.sep}SecEff_002_GermanVsForeign.pdf")
        fig3.savefig(f"doc{os.sep}report{os.sep}images{os.sep}SecEff_002_HaveTeachingEducation.pdf")
        

    
    def generate_SecEff_003_plots():
        df_student_exam_data = pd.DataFrame()
        for i in range(2, 12):# 2012-2021
            this_data_csv_path = f"data{os.sep}genesis{os.sep}SecEff_003-{i}_numberOfPassesAndFailsPerSubject.csv"
            this_df = pd.read_csv(this_data_csv_path)
            df_student_exam_data = pd.concat([df_student_exam_data, this_df[:][2:]], axis=0, ignore_index=True)

        # relative student pass rate
        rows_per_year = 4704
        student_years = df_student_exam_data["Unnamed: 0"][df_student_exam_data["Unnamed: 0"].index % rows_per_year == 0].to_list()
        student_years.reverse()
        student_exam_passes_per_year = []
        student_exam_total_per_year = []
        for i in np.arange(0, np.floor(len(df_student_exam_data)/rows_per_year)):
            bool_array_to_select_year = [(idx > i*rows_per_year and idx <= i*rows_per_year+rows_per_year) for idx in df_student_exam_data["Unnamed: 0"].index]

            student_exam_passes_per_year.append(df_student_exam_data[["Germans", "Unnamed: 4", "Foreigners", "Unnamed: 8"]][bool_array_to_select_year].replace("-", "0").astype(float).sum(axis=0).sum(axis=0))
            student_exam_total_per_year.append(df_student_exam_data[["Germans","Unnamed: 3","Unnamed: 4","Unnamed: 5","Foreigners","Unnamed: 7","Unnamed: 8","Unnamed: 9"]][bool_array_to_select_year].replace("-", "0").astype(float).sum(axis=0).sum(axis=0))
        
        relative_student_passes_per_year = [student_exam_passes_per_year[i]/student_exam_total_per_year[i] for i in range(len(student_years))]
        relative_student_passes_per_year.reverse()
        # print(student_years)
        # print(relative_student_passes_per_year)

        # relative abi pass rate
        df_abitur_data = pd.read_csv(f"data{os.sep}abi{os.sep}fails.csv")
        df_abitur_data.columns = df_abitur_data.iloc[0].replace(np.nan, 0).astype(int)
        abitur_years = list(range(2007, 2017))
        relative_abitur_passes_per_year = []
        for year in abitur_years:
            absolute_passes = df_abitur_data[year][df_abitur_data[year].index == 2].sum(axis=1).to_list()[0]
            absolute_fails = df_abitur_data[year][df_abitur_data[year].index == 3].sum(axis=1).to_list()[0]
            relative_abitur_passes_per_year.append(absolute_passes/(absolute_passes+absolute_fails))
        # print(abitur_years)
        # print(relative_abitur_passes_per_year)

        combined_years = [f"{abitur_years[i]}/{int(student_years[i])-2000}" for i in range(len(abitur_years))]

        # plotting
        fig,ax = plt.subplots()
        ax.plot(
            combined_years, 
            relative_abitur_passes_per_year,
            '.-', 
            ms=2, 
            lw=0.75, 
            color=get_next_tue_plot_color(0),
            label="abitur"
        )
        ax.plot(
            combined_years, 
            relative_student_passes_per_year,
            '.-', 
            ms=2, 
            lw=0.75, 
            color=get_next_tue_plot_color(1),
            label="higher education"
        )
        _fontsize = 6
        ax.set_xlabel("year: abitur/higher education", fontsize=_fontsize)
        ax.set_ylabel("% of students that earn the corresponding degree", fontsize=_fontsize)
        ax.legend(bbox_to_anchor=(1.01, 1))

        ax.set_ylim(0.94, 1.0)

        # ax.axhline(0, color=rgb.tue_dark, linewidth=0.5)

        ax.grid(axis="both", color=rgb.tue_dark, linewidth=0.5)
        ax.grid(axis="both", color=rgb.tue_gray, linewidth=0.5)

        fig.savefig(f"doc{os.sep}report{os.sep}images{os.sep}SecEff_003_abiturVsHigherEducation.pdf")


        # correlation
        fig,ax = plt.subplots()
        m, b = np.polyfit(relative_abitur_passes_per_year, relative_student_passes_per_year, 1)
        ax.scatter(
            [float(e) for e in relative_abitur_passes_per_year], 
            [float(e) for e in relative_student_passes_per_year],
            color=get_next_tue_plot_color(0),
            label="(% that passed abitur, % that passed higher education)\u1d40"
        )
        ax.plot(
            relative_abitur_passes_per_year, 
            [m*float(e)+b for e in relative_abitur_passes_per_year],
            '-', 
            ms=2, 
            lw=0.75, 
            color=get_next_tue_plot_color(1),
            label=f"Regression line (Kendall \u03c4 {kendalltau(relative_abitur_passes_per_year, relative_student_passes_per_year).statistic:.2f})"
        )
        _fontsize = 8
        ax.set_xlabel("% that passed abitur", fontsize=_fontsize)
        ax.set_ylabel("% that passed higher education", fontsize=_fontsize)
        ax.legend(bbox_to_anchor=(1.01, 1))

        # ax.set_ylim(0.94, 1.0)

        # ax.axhline(0, color=rgb.tue_dark, linewidth=0.5)

        ax.grid(axis="both", color=rgb.tue_dark, linewidth=0.5)
        ax.grid(axis="both", color=rgb.tue_gray, linewidth=0.5)

        fig.savefig(f"doc{os.sep}report{os.sep}images{os.sep}SecEff_003_abiturVsHigherEducationCorrelation.pdf")
        