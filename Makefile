.PHONY: help venv install test run clean lint commit bump activate

help:
	@echo "Available commands:"
	@echo "  venv       - Create virtual environment"
	@echo "  install    - Install dependencies in virtual environment"
	@echo "  test       - Run tests"
	@echo "  run        - Start the FastAPI server"
	@echo "  clean      - Clean cache files"
	@echo "  commit     - Create a conventional commit using commitizen"
	@echo "  bump       - Bump version using commitizen"
	@echo "  activate   - Show command to activate virtual environment"

venv:
	python3 -m venv venv
	@echo "Virtual environment created. Activate with: source venv/bin/activate"

install: venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install -r requirements.txt

test:
	venv/bin/pytest -v

run:
	venv/bin/python run.py

clean:
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache

commit:
	venv/bin/cz commit

bump:
	venv/bin/cz bump

activate:
	source venv/bin/activate