.PHONY: help venv install run test lint

# Self-Documenting Help (Default target)
help:
	@echo "Available commands:"
	@echo "  make venv      Create a local python virtual environment"
	@echo "  make install   Install all dependencies from requirements.txt"
	@echo "  make run       Start the development server"
	@echo "  make test      Run the full test suite"
	@echo "  make lint      Run flake8 code style checks"

venv:
	python -m venv venv
	@echo "Virtual environment created! Activate it using:"
	@echo "  Windows: venv\\Scripts\\activate"
	@echo "  Mac/Linux: source venv/bin/activate"

install:
	pip install -r requirements.txt

run:
	python app.py

test:
	pytest tests/ -v

lint:
	flake8 . --max-line-length=120