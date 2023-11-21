# DataLiteracyWS23

## Environment setup (Linux)

For managing the packages installed in our project we use a virtual python environment. If you want to setup the env just run:

```shell
./setup_venv.sh
```

From now on the environment can be used after executing the following command in every new terminal:
```shell
. {path/to/dir}/.venv/bin/activate
```

For adding, uninstalling new packages run, this ensures that the requirements.txt file is always up to date:

```shell
./pip_wrapper.sh [normal pip arguments]
```

*HINT:* If you face an error of executing the file run `chmod +x {file}`.

### Add activate script to .bashrc (Optional, only Linux)

If you don't want to activate your venv manually you can add the following alias to your `.bashrc`. In the next terminal session you can the use the `activate_venv` command to automatically fetch dependencies and activate the `.venv`.

```shell
# Add the following function to your shell profile file (e.g., .bashrc or .zshrc)

activate_venv() {
    VENV_DIR=".venv"

    # Check if the virtual environment directory exists
    if [ ! -d "$VENV_DIR" ]; then
        # Create a virtual environment if it doesn't exist
        python3 -m venv "$VENV_DIR"
    fi

    # Activate the virtual environment
    source "$VENV_DIR/bin/activate"

    # Install dependencies and uninstall not needed requirements from requirements.txt if it exists
    if [ -f "requirements.txt" ]; then
        # Check if there are packages to uninstall
        if pip freeze | grep -q -vxF -f requirements.txt; then
            # Uninstall existing packages not in requirements.txt
            pip freeze | grep -vxF -f requirements.txt | xargs pip uninstall -y
        fi
        pip install -r requirements.txt
    fi

    # Additional setup commands can be added here
}
```

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