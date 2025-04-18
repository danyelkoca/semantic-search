# Makefile for semantic-search project

.PHONY: install lint format sort test

# Install dev dependencies
install:
	pip install -r requirements-dev.txt

# Run all linters and formatters
lint:
	flake8 backend/
	isort --check-only backend/
	black --check backend/

# Auto-format code
format:
	black backend/
	isort backend/

# Run tests
test:
	PYTHONPATH=backend pytest backend/tests/
	
# Full local check before push
check: lint test