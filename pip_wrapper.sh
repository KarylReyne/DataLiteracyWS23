#!/bin/bash

# Script to add and install new dependencies to a virtual environment

VENV_DIR=".venv"

source "$VENV_DIR/bin/activate"

touch requirements.txt

# Check if there are packages to uninstall
if pip freeze | grep -q -vxF -f requirements.txt; then
    # Uninstall existing packages not in requirements.txt
    pip freeze | grep -vxF -f requirements.txt | xargs pip uninstall -y
fi

# Install complete reuqirements
pip install -r requirements.txt

pip $@

pip freeze > requirements.txt

# Check if there are packages to uninstall
if pip freeze | grep -q -vxF -f requirements.txt; then
    # Uninstall existing packages not in requirements.txt
    pip freeze | grep -vxF -f requirements.txt | xargs pip uninstall -y
fi

deactivate

echo "Dependencies updated succesfully."
