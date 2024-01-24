from tabulate import tabulate
import pandas as pd
import numpy as np
from school_analysis.preprocessing.helpers.students_teachers import combine_school_type
from school_analysis.preprocessing.load import Loader
import school_analysis as sa
from tueplots import bundles
from tueplots.constants.color import rgb
import os
import matplotlib.pyplot as plt
import school_analysis.plotting.germany_heatmap_lib as heatmaplib

DEBUG = False

# Settings and definitions
plt.rcParams.update(bundles.icml2022(
    column="half", nrows=2, ncols=2, usetex=True))


# Define a function to calculate correlation between two columns in a DataFrame
def correlation(data_frame: pd.DataFrame, col1: str, col2: str) -> float:
    return np.corrcoef(data_frame[col1], data_frame[col2])[0][1]

# Initialize a Loader object
loader = Loader()

# Load and preprocess the data for number of repeaters
repeaters = loader.load("number_of_repeaters")
repeaters = repeaters.rename(columns={"state": "Federal State", "school": "School Type",
                                      "year": "Year", "total": "Repeaters", "grade": "Grade"}).drop(columns=["male", "female"])
repeaters["Repeaters"] = repeaters["Repeaters"].replace("-", np.nan).dropna().astype(int)

# Load and preprocess budget data
budget = loader.load("budgets-corrected")
budget = budget.drop(columns=["Year Relative", "Index"])

# Load and preprocess data for students per teacher by state and type
teachers_students_state = loader.load("students-per-teacher-by-state")

# Define contract types for filtering
CONTRACT_TYPE = [
    "Vollzeitbeschäftigte Lehrkräfte",
    "Teilzeitbeschäftigte Lehrkräfte"
]

# Filter and process the teachers_students data
teachers_students_state = teachers_students_state[
    (teachers_students_state["Gender_students"] == "all")
    & (teachers_students_state["Gender_teachers"] == "all")
    & (teachers_students_state["Contract Type"].isin(CONTRACT_TYPE))
    & (teachers_students_state["Type"] == "Pupils")
]
teachers_students_state = teachers_students_state.groupby(["Federal State", "Year"])["Students per Teacher"].mean().reset_index()
teachers_students_state = teachers_students_state[["Federal State", "Year", "Students per Teacher"]].drop_duplicates()

# Merge datasets and calculate average
ts_budget_state = pd.merge(teachers_students_state, budget, on=["Federal State", "Year"]).dropna().drop_duplicates()

# Process repeaters data
repeaters_state = repeaters.groupby(["Federal State", "Year"])["Repeaters"].mean().reset_index()

# Merge datasets and calculate average
ts_repeaters_state = pd.merge(teachers_students_state, repeaters_state, on=["Federal State", "Year"]).dropna().drop_duplicates()

# Analyze and compile results
result = []
for state in teachers_students_state["Federal State"].unique():   
    state_data_budget = ts_budget_state[ts_budget_state["Federal State"] == state]
    state_data_repeaters = ts_repeaters_state[ts_repeaters_state["Federal State"] == state]
    corr = {
        "Budget": correlation(state_data_budget, "Students per Teacher", "Reference Budget"),
        "Repeaters": correlation(state_data_repeaters, "Students per Teacher", "Repeaters"),
        "state": state,
        "Type": "New" if state in sa.NEW_OLD_STATES_MAPPING["New Federal States"] else "Old"
    }
    result.append(corr)

result = pd.DataFrame(result)

# Visualization using matplotlib and a custom heatmap library
import matplotlib.pyplot as plt
import school_analysis.plotting.germany_heatmap_lib as heatmaplib

plotter = heatmaplib.GermanStatesHeatmapPlot()

# Create a heatmap for correlation between Students per Teacher and Repeaters
heatmap_dictionary1 = dict(zip(result["state"], result["Repeaters"]))

heatmap_dictionary2 = dict(zip(result["state"], result["Budget"]))


def create_merged_plot_repeater_budget(plotter, data1, data2, default_state_color):
    fig, (ax1, ax2) = plt.subplots(1, 2)

    _, ax1,sm = plotter.create_plot(data1, default_state_color, ax=ax1)
    _, ax2,sm = plotter.create_plot(data2, default_state_color, ax=ax2)

    ax1.set_title("Repeaters")
    ax2.set_title("Budget")

    cbar = plt.colorbar(sm, ax=ax2, fraction=0.10, pad=0.2)    

    cbar.set_label("Pearson correlation coefficient")    

    return fig

fig_combined = create_merged_plot_repeater_budget(plotter, heatmap_dictionary1, heatmap_dictionary2, "gray")

fig_combined.suptitle("Correlation coefficients students per teacher")


if DEBUG:
    plt.show(block=True)

fig_combined.savefig(os.path.join(sa.PROJECT_PATH, "doc",
            "report", "fig", "{}.pdf".format(os.path.realpath(__file__).split(".")[0])), format="pdf")
