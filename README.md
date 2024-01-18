# Data Literacy COVID School
[![Build LaTeX document](https://github.com/KarylReyne/DataLiteracyWS23/actions/workflows/build-pdf.yml/badge.svg)](https://github.com/<username>/<repository>/actions/workflows/build-pdf.yml)
[![Tests](https://github.com/KarylReyne/DataLiteracyWS23/actions/workflows/tests.yml/badge.svg)](https://github.com/<username>/<repository>/actions/workflows/tests.yml)

## Introduction

This project aims to analyze different factors that could influence the grades of students in Germany. The data is collected from the [Kultusministerkonferenz](https://www.kmk.org/dokumentation-statistik/statistik/schulstatistik/abiturnoten.html) and the [Statistisches Bundesamt](https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Bildung-Forschung-Kultur/Schulen/Publikationen/Downloads-Schulen/schueler-schularten-2180320197004.pdf?__blob=publicationFile). The project is part of the Data Literacy course at the University of Tübingen.ß

[Report](doc/report.pdf)

## Prerequisites

- Python (>=3.8)
- Destatis Genesis account (for downloading the data) - [Destatis](https://www-genesis.destatis.de/genesis/online)
- [Poetry](https://python-poetry.org/docs/#installation)

## Getting Started

For running the project, you need to install the dependencies and activate the virtual environment. The following commands are for Linux and MacOS. For Windows, please refer to the [Poetry documentation](https://python-poetry.org/docs/#installation).

### Downloading the Data

If you want to download all the data, including the data from the Destatis Genesis database, you need to create an credentials.yml file in the config directory. To make this process easier, you can use the [credentials.example.yml](config/credentials.example.yml) file as a template.

In order to download the data, you need to run the following command:

```bash
poetry run python src/school_analysis/download_all.py
```

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
```

## Additional Notes

- **Python Version:** This project requires Python 3.8 or higher.
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
