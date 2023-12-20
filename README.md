# Data Literacy COVID School

## Introduction

This project aims to analyze the influence of the COVID-19 pandemic on the German school system.

## Prerequisites

- Python (>=3.8)
- [Poetry](https://python-poetry.org/docs/#installation)

## Getting Started

### Clone the Repository

```bash
git clone https://github.com/your-username/data-lit-covid-school.git
cd data-lit-covid-school
```

### Install Dependencies

```bash
poetry install
```

### Activating venv

```bash
poetry shell
```

### Running python files

```bash
poetry run python path/to/file
```

### Updating Dependencies

```bash
poetry update
```

### Adding Dependencies

```bash
poetry add name-of-package
```

## Use the project

### Download Data

For downloading the data of <https://www.kmk.org/dokumentation-statistik/statistik/schulstatistik/abiturnoten.html> the script `download_grades.py` can be used. Just run:

```shell
python3 {project_dir}/src/helpers/download_grades.py
```

For downloading only one specific year run:

```shell
python3 {project_dir}/src/helpers/download_grades.py [year]
```

More options for specify directories and extensions fell free to run the script with the `-h` option to see all functionality.

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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
