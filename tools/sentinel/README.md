# DevPath Sentinel

DevPath Sentinel is a lightweight developer utility for validating repository integrity.

It currently provides a dataset validator that checks the project dataset for common issues before changes are submitted.

## Features

The current validator detects:

- Duplicate project IDs
- Duplicate project titles
- Missing required fields
- Empty required fields
- Missing starter code references

## Usage

Run the validator from the project root:

```bash
python -m tools.sentinel.cli
```

The validator prints a summary of all checks, including any warnings or errors found in the dataset.

## Project Structure

```
tools/
└── sentinel/
    ├── cli.py
    ├── models.py
    ├── report.py
    └── validators/
        └── dataset_validator.py
```