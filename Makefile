.PHONY: check test lint format typecheck clean

check: format lint typecheck test

test:
	pytest tests/ -v --cov=cosmiccli

lint:
	ruff check cosmiccli tests
	
format:
	ruff format cosmiccli tests
	black cosmiccli tests

typecheck:
	mypy cosmiccli tests

clean:
	rm -rf .pytest_cache .coverage .mypy_cache .ruff_cache __pycache__ cosmiccli/__pycache__ tests/__pycache__
	rm -rf dist build *.egg-info

