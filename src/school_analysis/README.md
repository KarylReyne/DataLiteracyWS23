# School Analysis Framework

This package aims to hold all framework like tasks, formulas, preprocessing for analyzing the german schools.

## Structure

The package is structured in the following way:

```
school_analysis
├── README.md
├── __init__.py
├── main.py # Dummy main file for importing the package
├── analysis
│   ├── __init__.py
│   ├── ... # All analysis algorithms
├── download
│   ├── __init__.py
│   ├── ... # All download algorithms
├── plotting
│   ├── __init__.py
│   ├── ... # All plotting algorithms
├── preprocessing
│   ├── __init__.py
│   ├── ... # All preprocessing algorithms
```

## Usage

The package can be used by importing it in your python script:

```import school_analysis as sa```