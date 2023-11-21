# DataLiteracyWS23

## .venv setup (Linux)

For managing the packages installed in our project we use a virtual python environment. If you want to setup the env just run:

```shell
./setup_venv.sh
```

For adding, uninstalling new packages run, this ensures that the requirements.txt file is always up to date:

```shell
./pip_wrapper.sh [normal pip arguments]
```

*HINT:* If you face an error of executing the file run `chmod +x {file}`.

## Download Data

For downloading the data of <https://www.kmk.org/dokumentation-statistik/statistik/schulstatistik/abiturnoten.html> the script `download_grades.py` can be used. Just run:

```shell
python3 {project_dir}/src/helpers/download_grades.py
```

For downloading only one specific year run:

```shell
python3 {project_dir}/src/helpers/download_grades.py [year]
```

More options for specify directories and extensions fell free to run the script with the `-h` option to see all functionality.