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
    column="half", nrows=1, ncols=1, usetex=True))
CONTRACT_TYPE = [
    "Vollzeitbeschäftigte Lehrkräfte",
    "Teilzeitbeschäftigte Lehrkräfte",
    # "Stundenweise beschäftigte Lehrkräfte"
]
# DEBUG = True
DEBUG = False
loader = Loader()
grades = loader.load("abi-grades")

# Load students per teacher
teachers_students_type = loader.load("students-per-teacher-by-type")
teachers_students_type = teachers_students_type[
    (teachers_students_type["Gender_students"] == "all")
    & (teachers_students_type["Gender_teachers"] == "all")
]

# Filter the data to only required cols
teachers_students_type = teachers_students_type[
    (teachers_students_type["Gender_students"] == "all")
    & (teachers_students_type["Gender_teachers"] == "all")
    & (teachers_students_type["Contract Type"].isin(CONTRACT_TYPE))
]
teachers_students_type = teachers_students_type.groupby(["School Type", "Year"])[
    "Students per Teacher"].mean().reset_index()
teachers_students_type = teachers_students_type[teachers_students_type["School Type"].isin(
    ["Gymnasien"])]

# Load grades
grades = loader.load("abi-grades")
grades_temp = grades.T.reset_index().rename(
    columns={"level_0": "Federal State", "level_1": "Year"})
grades = pd.melt(grades_temp, id_vars=[
                 "Federal State", "Year"], value_vars=grades_temp.columns[2:], value_name="Value")
grades["Federal State"] = grades["Federal State"].map(sa.STATE_MAPPING)
grades["Year"] = grades["Year"].astype(int)
grades["Grade"] = grades["Grade"].astype(float)
avg_grade = grades.groupby(["Year"]).apply(lambda x: (
    x["Grade"] * x["Value"]).sum() / x["Value"].sum(), include_groups=False).reset_index().rename(columns={0: "Average Grade"})

# Combine data
merged = pd.merge(
    teachers_students_type,
    avg_grade,
    on="Year"
).dropna()

x_col = "Average Grade"
y_col = "Students per Teacher"

# -- Plotting --
fig, ax = plt.subplots(sharex=True, sharey=True)

school_data = merged[merged["School Type"] == "Gymnasien"]
ax.scatter(school_data[x_col], school_data[y_col], label="Gymnasien", s=10)

# Linear regression
corr = np.corrcoef(school_data[x_col], school_data[y_col])[0][1]
X = np.vstack([np.ones(len(school_data[x_col])), school_data[x_col]]).T
y = school_data[y_col]
w, res, _, _ = np.linalg.lstsq(X, y, rcond=None)
print("Grades students to teacher: w={}, res={}".format(w, res))
minimum = school_data[x_col].min()
maximum = school_data[x_col].max()
minimum = 0 if np.isnan(minimum) else minimum
maximum = 0 if np.isnan(maximum) else maximum
xp = np.linspace(minimum, maximum, int(abs(maximum - minimum) * 100))
ax.plot(xp, w[0] + w[1] * xp, "--",
        label="Linear Regression (r={:.2f})".format(corr), color=rgb.tue_red)

# Settings
ax.set_ylabel("Students-per-teacher")
ax.set_xlabel("Average Grade")
ax.grid()
ax.legend()

fig.suptitle("Correlation between Grades and Students per Teacher")

if DEBUG:
    plt.show(block=True)

fig.savefig(os.path.join(sa.PROJECT_PATH, "doc",
            "report", "fig", "{}.pdf".format(os.path.realpath(__file__).split(".")[0])), format="pdf")
