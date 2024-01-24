import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import school_analysis as sa
import matplotlib.pyplot as plt
from tueplots import bundles
from tueplots.constants.color import rgb
from school_analysis.preprocessing.load import Loader

# Settings and definitions
plt.rcParams.update(bundles.icml2022(
    column="half", nrows=2, ncols=2, usetex=True))
REFERENCE_BEFORE = 2021
DEBUG = False
loader = Loader()
grades = loader.load("abi-grades")


def get_average_grades_by_year_and_state(flat_data: pd.DataFrame, states=["BW"]):
    plot_data: pd.DataFrame = pd.DataFrame()
    for state in states:
        state_data = flat_data[state].copy()
        average_grades_per_year = state_data.apply(lambda col: np.dot(
            col, state_data.index) / col.sum(), axis=0).sort_index()
        plot_data[state] = average_grades_per_year
    return plot_data.copy()


# Aggregate data by year and state
data = get_average_grades_by_year_and_state(
    grades, grades.columns.get_level_values(0))
overall_mean = data.mean(axis=1)
overall_mean = overall_mean.reset_index().rename(
    columns={'index': 'year', 0: 'grade'})
overall_mean["year"] = overall_mean["year"].astype(np.int32)

# Calculate linear regression
reg_data = overall_mean.copy()
reg_data = reg_data.drop(
    reg_data[reg_data["year"].astype(np.int32) >= REFERENCE_BEFORE].index)
X = np.array([[1, reg_data["year"].iloc[i]]
             for i in range(reg_data.shape[0])], dtype=np.int32)
y = np.array(reg_data["grade"])

w, res, _, _ = np.linalg.lstsq(X, y, rcond=None)
print(f"w={w}; res={res}")

# -- Plotting --
fig, ax = plt.subplots()

# Federal States in the background
label_set = False
for state in data.columns:
    ax.plot(
        data[state].index.astype(np.int32),
        data[state],
        "-",
        color=rgb.tue_gray,
        alpha=0.5,
        label="Single States" if not label_set else None,
        lw=0.3,
    )
    label_set = True

# Plot the data before Covid
ax.plot(
    reg_data["year"],
    reg_data["grade"],
    ".",
    label="Avg. Grade (reference)",
    lw=0.5,
)

# Plot the data after Covid
ax.plot(
    overall_mean.loc[overall_mean["year"] >= REFERENCE_BEFORE, "year"],
    overall_mean.loc[overall_mean["year"] >= REFERENCE_BEFORE, "grade"],
    ".",
    label="Avg. Grade (Covid)",
    color=rgb.tue_dark,
    lw=0.5,
)


# Linear fit
xp = overall_mean["year"].unique().astype(np.int32)
ax.plot(
    xp, w[0] + w[1] * (xp), label="Linear fit", color=rgb.tue_red, lw=0.5
)

# Regression uncertainty
# ax.fill_between(
#     xp,
#     w[0] + w[1] * (xp) - np.sqrt(res / len(y)),
#     w[0] + w[1] * (xp) + np.sqrt(res / len(y)),
#     alpha=0.4,
#     color=rgb.tue_dark,
# )

ax.invert_yaxis()
ax.grid(True)
ax.set_xlabel("Year")
ax.set_ylabel("Average Grade")
# Create the legend with the specified order
order = [1, 2, 3, 0]
handles, labels = ax.get_legend_handles_labels()
ax.legend([handles[idx] for idx in order], [labels[idx] for idx in order])
ax.set_title("Linear Regression on the data before Covid")

if DEBUG:
    plt.show(block=True)

fig.savefig(os.path.join(sa.PROJECT_PATH, "doc",
            "report", "fig", "{}.pdf".format(os.path.realpath(__file__).split(".")[0])), format="pdf")
