import pandas as pd
import os
import school_analysis as sa
from school_analysis.preprocessing import SCHOOL_TYPE_MAPPING
import school_analysis.preprocessing.helpers.budgets as budgets
import school_analysis.preprocessing.helpers.students_teachers as students_teachers

class Loader():
    
    STD_CONFIG = {
        "sep": ",",
        "encoding": "utf-8",
        "header": [0],
        "index_col": 0
    }
    
    def __init__(self):
        super().__init__()
        
        self._download_config = sa.load_download_config()
        self._mapping = {
            # Grades performance related
            'abi-fails': lambda **kwargs: self._load_abi('fails'),
            'abi-grades': lambda **kwargs: self._load_abi('grades'),
            'pisa-germany': lambda **kwargs: self._default_loader("DEFAULT", "Pisa study data for Germany"),
            
            # Number of students / teachers related
            'school-children-by-state': lambda **kwargs: self._default_loader("GENESIS", "# of school children by federal state (ger)"),
            'school-children-by-type': lambda **kwargs: self._default_loader("GENESIS", "# of school children by school type (ger)"),
            'graduates-by-type': lambda **kwargs: self._default_loader("GENESIS", "# of graduates by school type (ger)"),
            'school-children-by-state-percents': self._load_students_by_federal_state_percents,
            'teachers-per-schooltype': lambda **kwargs: self._default_loader("DEFAULT", "Overview destatis german schools 2020/21"),
            'zensus': lambda **kwargs: self._default_loader("GENESIS", "Zensus"),
            'zensus-age': lambda **kwargs: self._load_age_group("GENESIS", "zensus-"),
            'students-per-teacher-by-state': self._load_students_per_teacher_by_state,
            'students-per-teacher-by-type': self._load_students_per_teacher_by_type,
            
            # Budgets related
            'budgets-by-state': lambda **kwargs: self._default_loader("GENESIS", "Budgets of schools by federal state (ger)"),
            'budgets-corrected': self._load_corrected_budgets,
            'budgets-per-child-by-state': lambda **kwargs: self._default_loader("GENESIS", "Budgets per public schools by children by federal state (ger)"),
            'verbraucherpreisindex-state': lambda **kwargs: self._default_loader("GENESIS", "Verbraucherpreisindex by state"),
            
            # Other Performance related
            'students_with_special_educational_support': lambda **kwargs: self._default_loader("GENESIS", "# students with special educational support"),
            'students_with_special_educational_support_no_gender': lambda **kwargs: self._default_loader("GENESIS", "# special educational needs no gender"),
            'number_of_repeaters': lambda **kwargs: self._load_age_group("GENESIS", "number_of_repeaters_"),
            'no_hauptschulabschluss': lambda **kwargs: self._load_age_group("GENESIS", "no_hauptschulabschluss"),
            'children_wo_degree': self._load_children_wo_degree,
        }

    def load(self, name: str, **kwargs):
        if name not in self._mapping:
            raise ValueError(f"Unknown loader {name}")
        
        return self._mapping[name](**kwargs)
    
    def contains(self, name: str):
        return name in self._mapping
    
    # --- Loader ---
    
    def _load_abi(self, data_set: str):
        # Check if file exists
        if data_set not in self._download_config["ABI"]:
            raise ValueError(f"Unknown data set {data_set}")
        
        path = os.path.join(sa.PROJECT_PATH, "data", self._download_config["ABI"]["dir"], self._download_config["ABI"][data_set]["target"])
        return pd.read_csv(path, **self._download_config["ABI"][data_set]["read_args"])
    
    def _default_loader(self, key: str, dataset: str):
        # Check if file exists
        if key not in self._download_config:
            raise ValueError(f"Unknown key {key}")
        if dataset not in [n["name"] for n in self._download_config[key]]:
            raise ValueError(f"Unknown dataset {dataset}")
        
        i = [n["name"] for n in self._download_config[key]].index(dataset)
        path = os.path.join(sa.PROJECT_PATH, "data", self._download_config[key][i]["folder"], self._download_config[key][i]["filename"].split(".")[0] + ".csv")
        return pd.read_csv(path, **self.STD_CONFIG)
    
    def _load_age_group(self, key: str, filename_prefix: str):
        # Check if file exists
        if key not in self._download_config:
            raise ValueError(f"Unknown key {key}")
        
        # Find file
        dfs = []
        for entry in self._download_config[key]:
            if entry["filename"].startswith(filename_prefix):
                path = os.path.join(sa.PROJECT_PATH, "data", entry["folder"], entry["filename"].split(".")[0] + ".csv")
                dfs.append(pd.read_csv(path, **self.STD_CONFIG))
        
        if len(dfs) == 0:
            raise ValueError(f"Unknown dataset {filename_prefix}")
            
        return pd.concat(dfs, ignore_index=True).reset_index(drop=True)

    def _load_students_per_teacher_by_type(self, **kwargs):
        students_per_type = self.load("school-children-by-type")
        teachers = self.load("teachers-per-schooltype")
        contract_types = kwargs.get("contract_types", sa.CONTRACT_TYPES)
        
        # Preprocess Students
        students_per_type.loc[:, "School Type"] = students_per_type["School Type"].map(
            SCHOOL_TYPE_MAPPING)
        # 1. Combine Gymnasien (G8) and Gymnasien (G9) into Gymnasien
        combined_students = students_teachers.combine_school_type(
            students_per_type, "School Type", "Students", new_type="Gymnasien")
        # 2. Ignore certificate Grade
        combined_students = combined_students.groupby(list(set(combined_students.columns.tolist(
        )) - set(["Students", "Grade"])))["Students"].sum().reset_index()
        # 3. Map gender to defined values
        combined_students = students_teachers.map_gender(
            combined_students, "Gender")

        # Preprocess Teachers
        teachers = teachers[teachers["Contract Type"].isin(contract_types)]
        # 1. Combine Gymnasien (G8) and Gymnasien (G9) into Gymnasien
        combined_teachers = students_teachers.combine_school_type(
            teachers, "School Type", "Number of Teachers", new_type="Gymnasien")
        # 2. Map gender to defined values
        combined_teachers = students_teachers.map_gender(
            combined_teachers, "Gender")
        # 3. Ignore federal State
        combined_teachers = combined_teachers[(combined_teachers["School Type"] != "Zusammen") & (
            combined_teachers["Federal State"] == "Deutschland")].drop(columns=["Federal State"])

        # Merge with teachers
        merged = pd.merge(
            combined_students,
            combined_teachers,
            how="left",
            on=["Year", "School Type"],
            suffixes=("_students", "_teachers")
        )

        merged = students_teachers.aggregate_students_per_teacher(
            merged, students_col="Students", teachers_col="Number of Teachers", new_col="Students per Teacher")
        return merged
    
    def _load_students_per_teacher_by_state(self, **kwargs):
        students_per_state = self.load("school-children-by-state", **kwargs)
        teachers = self.load("teachers-per-schooltype")
        contract_types = kwargs.get("contract_types", sa.CONTRACT_TYPES)
        
        # Merge with teachers
        temp_students = students_per_state[students_per_state["Type"] == "Pupils"].rename(
            columns={"Value": "Students"}).drop_duplicates()
        temp_teacher = teachers[(teachers["School Type"] == "Zusammen")]
        temp_teacher = temp_teacher.drop(
            "School Type", axis=1).drop_duplicates()
        temp_teacher = temp_teacher[temp_teacher["Contract Type"].isin(
            contract_types)]
        temp_teacher = students_teachers.map_gender(temp_teacher, "Gender")
        students_per_techear_by_federal_state = pd.merge(
            temp_students, temp_teacher, how="left", on=["Federal State", "Year"], suffixes=("_students", "_teachers"))
        return students_teachers.aggregate_students_per_teacher(students_per_techear_by_federal_state, students_col="Students", teachers_col="Number of Teachers", new_col="Students per Teacher")
    
    def _load_students_by_federal_state_percents(self, **kwargs):
        """Loads the students by federal state and calculates the percentage of the children between 6-18 years old."""
        # Load other data
        students_per_state = self.load("school-children-by-state", **kwargs)
        zensus_age = self.load("zensus-age", **kwargs)
        
        # Calculate percentage
        zensus_children = zensus_age[(zensus_age["Age"] >= 6) & (zensus_age["Age"] <= 18)]
        merged = pd.merge(students_per_state, zensus_children, how="inner", on=["Federal State", "Gender", "Year"], suffixes=("_students", "_zensus"))
        merged["Percentage"] = merged.groupby(["Federal State", "Gender", "Year", "Type"]).apply(lambda x: x["Value_students"] / x["Value_zensus"].sum()).reset_index(drop=True)
        students_per_state = merged.drop(columns=["Value_zensus", "Age"]).drop_duplicates().reset_index(drop=True).rename(columns={"Value_students": "Students"})

        return students_per_state
    
    def _load_corrected_budgets(self, **kwargs):
        """Loads the budgets and corrects them by the verbraucherpreisindex."""
        budgets_per_child = self.load("budgets-per-child-by-state", **kwargs)
        verbraucherpreisindex = self.load("verbraucherpreisindex-state", **kwargs)
        return budgets.correct_by_verbraucherpreisindex(budgets_per_child[budgets_per_child["Federal State"] != "Total"], verbraucherpreisindex)

    def _load_children_wo_degree(self, **kwargs):
        """Loads the number of children without a degree."""
        df_melted = self.load('no_hauptschulabschluss')
        # df_melted['year'] = df_melted["year"].astype(int)
        df_melted['total'] = pd.to_numeric(df_melted['total'], errors='coerce')
        total_students_by_year = df_melted.groupby('year')['total'].sum()

        children_state = self.load('school-children-by-state')
        children_state = children_state.rename(columns={'Year': 'year'})
        # children_state['year'] = children_state["year"].astype(int)
        child_amount_per_year = children_state.groupby('year')['Value'].sum()

        merged_df = pd.merge(total_students_by_year,
                             child_amount_per_year, on='year').reset_index()
        merged_df["year"] = merged_df["year"].astype(int)
        merged_df['relative'] = merged_df['total']/merged_df['Value']
        merged_df = merged_df.rename(columns={
                                     'total': 'Without degree', 'Value': 'Total students', "relative": "Without degree (rel.)"})
        return merged_df.reset_index(drop=True)
