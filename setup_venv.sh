#!/bin/bash

# Script to set up or activate a virtual environment

# Define the virtual environment directory
VENV_DIR=".venv"

# Check if the virtual environment directory exists
if [ ! -d "$VENV_DIR" ]; then
    # Create a virtual environment if it doesn't exist
    python3 -m venv "$VENV_DIR"
fi

# Activate the virtual environment
source "$VENV_DIR/bin/activate"

# Install dependencies from requirements.txt if it exists
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

