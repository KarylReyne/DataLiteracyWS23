import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import school_analysis as sa
import matplotlib.pyplot as plt
from tueplots.constants.color import rgb
from tueplots import bundles
from school_analysis.preprocessing import SCHOOL_TYPE_MAPPING
from school_analysis.preprocessing.helpers import students_teachers
from school_analysis.preprocessing.load import Loader

# Settings and definitions
plt.rcParams.update(bundles.icml2022(
    column="full", nrows=1, ncols=2, usetex=True))
DEBUG = False
loader = Loader()

# Settings
MCS = 5
TEACHER_CONTRACT = [
    "Vollzeitbeschäftigte Lehrkräfte",
    "Teilzeitbeschäftigte Lehrkräfte"
]

# Students per teachers avg
fig, ax = plt.subplots()


# Get the number of students for the most common school types
plot_data = loader.load("students-per-teacher-by-type",
                        contract_types=TEACHER_CONTRACT)
swapped = {value: key for key, value in SCHOOL_TYPE_MAPPING.items()}
plot_data["School Type"] = plot_data["School Type"].map(swapped)
plot_data = plot_data[
    (plot_data["Gender_students"] == "all")
    & (plot_data["Gender_teachers"] == "all")
]
plot_data = plot_data[plot_data["Contract Type"].isin(TEACHER_CONTRACT)]
most_common_school_types = students_teachers.get_most_common_school_types(
    plot_data, MCS, school_type_col="School Type", value_col="Students")

# Recalculate students per teacher
grouped = plot_data.groupby(["Year", "School Type"])
plot_data = grouped["Students"].sum().reset_index()
plot_data.loc[:, "Teachers"] = grouped["Number of Teachers"].sum().reset_index()[
    "Number of Teachers"]
plot_data["Students per Teacher"] = plot_data["Students"] / \
    plot_data["Teachers"]

# Select data to plot (aggregation)
grouped = plot_data[plot_data["School Type"].isin(
    most_common_school_types)].dropna().groupby("Year")
plot_data_mean = grouped["Students per Teacher"].mean().reset_index()
# plot_data_std = grouped["Students per Teacher"].std().reset_index()

# Plot
# ax.fill_between(plot_data_mean["Year"], plot_data_mean["Students per Teacher"] - plot_data_std["Students per Teacher"],
#                 plot_data_mean["Students per Teacher"] + plot_data_std["Students per Teacher"], alpha=0.25, label="Std-Deviation(Top {})".format(MCS),  color=rgb.tue_gray)
for idx, st in enumerate(most_common_school_types):
    st_group = plot_data[plot_data["School Type"] == st].groupby("Year")
    st_group_mean = st_group["Students per Teacher"].mean().reset_index()
    ax.plot(st_group_mean["Year"],
            st_group_mean["Students per Teacher"], label=st)
ax.plot(plot_data_mean["Year"], plot_data_mean["Students per Teacher"],
        label="Average (Top {} school types)".format(MCS), color=rgb.tue_gold, linestyle='--')

# Other settings
ax.set_xlabel("Year")
ax.set_ylabel("Student-to-teacher ratio")
ax.set_xticks(np.arange(plot_data["Year"].min(),
              plot_data["Year"].max() + 1, 2))
ax.grid(True)
ax.legend(bbox_to_anchor=(1.05, 0.5), loc='center left', title="School Type")

# Other settings
fig.suptitle("Student-to-teacher ratio in Germany")

if DEBUG:
    plt.show(block=True)

fig.savefig(os.path.join(sa.PROJECT_PATH, "doc",
            "report", "fig", "{}.pdf".format(os.path.realpath(__file__).split(".")[0])), format="pdf")
