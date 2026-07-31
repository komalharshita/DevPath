# DevPath Sentinel

DevPath Sentinel is a lightweight developer utility for validating repository integrity.

It provides modular validators that help contributors identify repository and dataset issues before submitting changes.

## Features

DevPath Sentinel currently includes the following validators.

### Dataset Validator

Detects:

- Duplicate project IDs
- Duplicate project titles
- Missing required fields
- Empty required fields
- Missing starter code references

### Starter Code Integrity Validator

Detects:

- Orphan starter code files
- Empty starter code files
- Unsupported starter code file types
- Hidden files inside the `starter_code/` directory

## Usage

Run the validator from the project root:

```bash
python -m tools.sentinel.cli
```

The CLI executes all available validators sequentially and prints a consolidated validation report, including any warnings or errors detected.

Example output:

```text
DevPath Sentinel

Running Dataset Validator...

Running Starter Code Integrity Validator...
```

## Project Structure

```text
tools/
└── sentinel/
    ├── cli.py
    ├── models.py
    ├── report.py
    └── validators/
        ├── dataset_validator.py
        └── starter_code_validator.py
```