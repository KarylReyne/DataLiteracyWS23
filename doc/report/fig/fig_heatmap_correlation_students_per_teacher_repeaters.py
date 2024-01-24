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

# Load and preprocess data for students per teacher by state and type
teachers_students_state = loader.load("students-per-teacher-by-state")
teachers_students_type = loader.load("students-per-teacher-by-type")

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
ts_state_avg = teachers_students_state.groupby(["Year"])["Students per Teacher"].mean().reset_index()

# Process repeaters data
repeaters_state = repeaters.groupby(["Federal State", "Year"])["Repeaters"].mean().reset_index()
repeaters_avg = repeaters.groupby(["Year"])["Repeaters"].mean().reset_index()

# Merge datasets and calculate average
ts_repeaters_state = pd.merge(teachers_students_state, repeaters_state, on=["Federal State", "Year"]).dropna().drop_duplicates()
ts_repeaters_state_avg = pd.merge(ts_state_avg, repeaters_avg, on=["Year"]).dropna().drop_duplicates()

# Analyze and compile results
result = []
for state in teachers_students_state["Federal State"].unique():   
    state_data_repeaters = ts_repeaters_state[ts_repeaters_state["Federal State"] == state]
    corr = {    
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
heatmap_dictionary = dict(zip(result["state"], result["Repeaters"]))
fig, ax, cbar = plotter.create_plot(heatmap_dictionary, default_state_color="gray")
ax.set_title("Correlation between Students per Teacher and Repeaters")
cbar.set_label("Coefficient of correlation")
plt.show()

if DEBUG:
    plt.show(block=True)

fig.savefig(os.path.join(sa.PROJECT_PATH, "doc",
            "report", "fig", "{}.pdf".format(os.path.realpath(__file__).split(".")[0])), format="pdf")
