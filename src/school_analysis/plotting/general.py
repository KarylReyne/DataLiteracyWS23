import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import school_analysis as sa


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