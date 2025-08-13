.PHONY: check test typecheck lint format clean

# Run all quality checks
check: format lint typecheck test

# Run tests with coverage
test:
	.venv/bin/pytest --cov=cosmic_neighborhoods tests/ --cov-report=term-missing

# Run type checks
typecheck:
	.venv/bin/mypy cosmic_neighborhoods/ tests/

# Run linting
lint:
	.venv/bin/ruff check cosmic_neighborhoods/ tests/

# Format code
format:
	.venv/bin/ruff format cosmic_neighborhoods/ tests/

# Clean temporary files
clean:
	rm -rf .coverage
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +