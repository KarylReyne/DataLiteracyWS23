#!/bin/bash

# Script to add and install new dependencies to a virtual environment

VENV_DIR=".venv"

source "$VENV_DIR/bin/activate"

touch requirements.txt

pip install -r requirements.txt

pip $@

pip freeze > requirements.txt

deactivate

echo "Dependencies updated succesfully."
