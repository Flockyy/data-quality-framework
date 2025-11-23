# Makefile for Data Quality Framework

.PHONY: help install test lint format clean docker-up docker-down run-dashboard

# Default target
help:
	@echo "Data Quality Framework - Available Commands:"
	@echo "  make install       - Install dependencies and package"
	@echo "  make test          - Run tests"
	@echo "  make test-cov      - Run tests with coverage"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code"
	@echo "  make clean         - Clean generated files"
	@echo "  make docker-up     - Start Docker containers"
	@echo "  make docker-down   - Stop Docker containers"
	@echo "  make run-dashboard - Run Streamlit dashboard"
	@echo "  make docs          - Generate documentation"

# Installation
install:
	uv pip install -e .

install-dev:
	uv pip install -e ".[dev]"

setup-hooks:
	pre-commit install
	pre-commit install --hook-type commit-msg

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=dqf --cov-report=html --cov-report=term-missing --cov-report=xml
	@echo "Coverage report generated in htmlcov/index.html"

test-parallel:
	pytest tests/ -n auto -v

# Code quality
lint:
	ruff check dqf tests examples

lint-fix:
	ruff check --fix dqf tests examples

format:
	ruff format dqf examples tests

format-check:
	ruff format --check dqf examples tests

typecheck:
	mypy dqf/ --ignore-missing-imports

security:
	bandit -c pyproject.toml -r dqf

check: lint format-check typecheck test

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/
	rm -rf reports/*.html reports/*.json reports/*.pdf

# Docker
docker-up:
	docker-compose -f docker/docker-compose.yml up -d
	@echo "Services started. Dashboard: http://localhost:8501"
	@echo "Grafana: http://localhost:3000 (admin/admin)"

docker-down:
	docker-compose -f docker/docker-compose.yml down

docker-logs:
	docker-compose -f docker/docker-compose.yml logs -f

# Run dashboard locally
run-dashboard:
	streamlit run dashboard/app.py

# Examples
run-example-profile:
	python examples/basic_profiling.py

run-example-validate:
	python examples/custom_validators.py

# Documentation
docs:
	mkdocs build
	@echo "Documentation generated in site/"

docs-serve:
	mkdocs serve

# Database operations
db-init:
	docker-compose -f docker/docker-compose.yml exec postgres psql -U dqf_user -d data_quality -f /docker-entrypoint-initdb.d/init.sql

# Development
dev-setup: install-dev setup-hooks
	@echo "Development environment ready!"

# CI/CD
ci: check
	@echo "All CI checks passed!"

# Release
build:
	python setup.py sdist bdist_wheel

publish: build
	twine upload dist/*
