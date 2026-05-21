.PHONY: help install run test lint

# Self-Documenting Help (Default target)
help:
	@echo "Available commands:"
	@echo "  make install   Install all dependencies"
	@echo "  make run       Start the development server"
	@echo "  make test      Run the full test suite"
	@echo "  make lint      Run flake8 code style checks"

install:
	pip install -r requirements.txt

run:
	python app.py

test:
	pytest tests/ -v

lint:
	flake8 . --max-line-length=120