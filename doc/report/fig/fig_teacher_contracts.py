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
plt.rcParams.update(bundles.icml2022(column="full", nrows=1, ncols=2))
DEBUG = False
loader = Loader()


def get_relative(df):
    df["Number of Teachers"] = df["Number of Teachers"] / \
        df["Number of Teachers"].sum()

    return df


teachers = loader.load("teachers-per-schooltype")
teachers = teachers[teachers["Gender"] == "z"]
group = teachers.groupby(["Year", "Federal State"])
teachers = group.apply(get_relative).reset_index(drop=True)
teachers = teachers.groupby(
    ["Year", "Federal State", "Contract Type"])["Number of Teachers"].sum().reset_index()
teachers = teachers[teachers["Contract Type"]
                    != "Stundenweise beschäftigte Lehrkräfte"]

# Plot
fig, axs = plt.subplots(1, 2, sharey=True, sharex=True)

# Display detailed lines
# for state in teachers["Federal State"].unique():
#     ax = axs[0] if state in sa.NEW_OLD_STATES_MAPPING["Old Federal States"] else axs[1]
#     data = teachers[teachers["Federal State"] == state]

#     for contract_type in data["Contract Type"].unique():
#         color = rgb.tue_darkblue if contract_type == "Vollzeitbeschäftigte Lehrkräfte" else rgb.tue_gray
#         alpha = 0.6 if contract_type == "Vollzeitbeschäftigte Lehrkräfte" else 1
#         d = data[data["Contract Type"] == contract_type]
#         ax.plot(d["Year"], d["Number of Teachers"], color=color, alpha=alpha)

for states in sa.NEW_OLD_STATES_MAPPING.keys():
    for contract in ["Vollzeitbeschäftigte Lehrkräfte", "Teilzeitbeschäftigte Lehrkräfte"]:

        # Get data
        data = teachers[
            (teachers["Federal State"].isin(sa.NEW_OLD_STATES_MAPPING[states]))
            & (teachers["Contract Type"] == contract)
        ]

        # Aggregate
        average = data.groupby(
            "Year")["Number of Teachers"].mean().reset_index()
        minimal = data.groupby(
            "Year")["Number of Teachers"].min().reset_index()
        maximal = data.groupby(
            "Year")["Number of Teachers"].max().reset_index()

        # Get axis
        ax = axs[0] if states == "Old Federal States" else axs[1]
        color = rgb.tue_blue if contract == "Vollzeitbeschäftigte Lehrkräfte" else rgb.tue_red

        # Plot
        ax.plot(average["Year"], average["Number of Teachers"],
                color=color, linestyle="--")
        ax.fill_between(minimal["Year"], minimal["Number of Teachers"],
                        maximal["Number of Teachers"], color=color, alpha=0.3)

# Set axis labels
axs[0].set_title("Old Federal States")
axs[1].set_title("New Federal States")
axs[0].set_ylabel("Relative Number of Teachers")
axs[0].set_xlabel("Year")
axs[1].set_xlabel("Year")
axs[1].legend(["Full-time", "Min/Max",
              "Part-time", "Min/Max"], title="Contract Type", loc="center right", bbox_to_anchor=(1.3, 0.5))
fig.suptitle("Relative Number of Teachers per Contract Type")

for ax in axs.flatten():
    ax.grid(True)

if DEBUG:
    plt.show(block=True)

fig.savefig(os.path.join(sa.PROJECT_PATH, "doc",
            "report", "fig", "{}.pdf".format(os.path.realpath(__file__).split(".")[0])), format="pdf")
