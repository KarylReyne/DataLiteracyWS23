#!/bin/bash

# Get the directory of the shell script
dir="$(dirname "$0")"

# Iterate over all Python files in the directory
for file in "$dir"/fig/*.py
do
  # Run the Python script
  python "$file"
done