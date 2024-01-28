# Data Literacy Project: Grade Inflation in the German School System - Causes and Effects

[![Build LaTeX document](https://github.com/KarylReyne/DataLiteracyWS23/actions/workflows/build-pdf.yml/badge.svg)](https://github.com/KarylReyne/DataLiteracyWS23/actions/workflows/build-pdf.yml) [![Tests](https://github.com/KarylReyne/DataLiteracyWS23/actions/workflows/python-app.yml/badge.svg)](https://github.com/KarylReyne/DataLiteracyWS23/actions/workflows/python-app.yml) [![PDF](https://img.shields.io/badge/PDF-Download-blue)](https://github.com/KarylReyne/DataLiteracyWS23/blob/main/report.pdf)

## Introduction

This project aims to analyze different factors that could influence the grades of students in Germany. The data is collected from the [Kultusministerkonferenz](https://www.kmk.org/dokumentation-statistik/statistik/schulstatistik/abiturnoten.html) and the [Statistisches Bundesamt](https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Bildung-Forschung-Kultur/Schulen/Publikationen/Downloads-Schulen/schueler-schularten-2180320197004.pdf?__blob=publicationFile). The project is part of the Data Literacy course at the University of Tübingen.

## Prerequisites

- Python (>=3.8)
- Destatis Genesis account (for downloading the data) - [Destatis](https://www-genesis.destatis.de/genesis/online)
- [Poetry](https://python-poetry.org/docs/#installation)

## Getting Started

For running the project, you need to install the dependencies and activate the virtual environment. For the installation of Poetry please refer to the [Poetry documentation](https://python-poetry.org/docs/#installation).

If you have Poetry installed, you can run the following commands to install the dependencies and activate the virtual environment:

```bash
poetry install
```

### Downloading the Data

If you want to download all the data, including the data from the Destatis Genesis database, you need to create an credentials.yml file in the config directory. To make this process easier, you can use the [credentials.example.yml](config/credentials.example.yml) file as a template.

In order to download the data, you need to run the following command:

```bash
poetry run python src/school_analysis/download_all.py
```

If you want to download only the data of a specific data source, you can run the following command:

```bash
poetry run python src/school_analysis/download_all.py <genesis|default|abi>
```

For keeping the raw data you may add the `--keep-raw` flag.

### Reproducing the Results

If you want to reproduce the results, you can run the following command (only works on Unix systems):

```bash
poetry run doc/report/build_figures.sh # Unix command
```

Else you can run each python file in the [doc/report/fig/](doc/report/fig) directory individually. They create the figures used in the report.

Furthermore, you can run the notebooks in the [exp](exp) directory to reproduce the results of the experiments and analysis.

##### Important Note

Make sure that you have downloaded the data before running the notebooks. Otherwise, the notebooks will not work.

### Folder Structure

The project is structured as follows:

```bash
|-- config
|   |-- credentials.example.yml # Example credentials file
|   |-- credentials.yml # Credentials files (ignored by git)
|   |-- download.yml # Configuration of all data sources
|-- data # ignored by git
|   |-- abi # Data from the Kultusministerkonferenz regarding the Abitur
|   |-- genesis # Data from the Destatis Genesis database
|   |-- raw # Raw data from other sources
|-- doc
|   |-- LICENSES # Licenses of the data used in this project
|   |-- report # The latex files used to generate the final report
|   |   |-- fig # Figures used in the report
|   |   |-- ... # LaTeX files for the report
|-- exp 
|   |-- ... # Experiments
|-- src/school_analysis # Source code
|   |-- README.md # Further information about the project
|   |-- download_all.py # Script for downloading all data
|   |... # Python files and framework please refer to the README.md in the src directory
|-- .gitignore
|-- LICENSE
|-- pyproject.toml
|-- README.md
|-- report.pdf # Final report
```

## Additional Notes

- **Python Version:** This project requires Python 3.11 or higher.
- **Virtual Environment:** Ensure that you activate the Poetry virtual environment before running the project.

## Contributing

If you would like to contribute to the project, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes.
4. Test thoroughly.
5. Submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. It makes use of and is distributed with the following components:
 - a modified version of [genesisclient](https://github.com/marians/genesisclient) which is licensed under the MIT License
 - the file `doc/report/icml2023.bst` which is licensed under the LaTeX Project Public License and redistributed as a complete, unmodified copy
 
Please refer to the [LICENSES](doc/LICENSES) directory for the individual licenses as well as the licenses of the data used in this project.
