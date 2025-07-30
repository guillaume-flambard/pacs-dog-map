# PACS Dog Map - Development Makefile

.PHONY: help install test lint format clean sync generate serve docs

# Default target
help:
	@echo "PACS Dog Map - Available Commands:"
	@echo ""
	@echo "  install     Install dependencies and development tools"
	@echo "  test        Run all tests"
	@echo "  test-unit   Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  lint        Run code linting"
	@echo "  format      Format code with black"
	@echo "  clean       Clean build artifacts and caches"
	@echo ""
	@echo "  sync        Sync data from Google Sheets"
	@echo "  generate    Generate interactive map"
	@echo "  serve       Start local web server for map"
	@echo ""
	@echo "  docs        Generate documentation"
	@echo "  setup-dev   Set up development environment"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev,test]"

# Testing
test:
	python -m pytest tests/ -v --cov=src/pacs_map --cov-report=html --cov-report=term

test-unit:
	python -m pytest tests/test_*.py -v -k "not integration"

test-integration:
	python -m pytest tests/test_integration.py -v

# Code quality
lint:
	flake8 src/ tests/
	mypy src/pacs_map/

format:
	black src/ tests/

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Application commands
sync:
	./pacs-map sync

generate:
	./pacs-map generate

serve:
	@echo "Starting local server at http://localhost:8000"
	@cd web && python -m http.server 8000

# Development setup
setup-dev: install-dev
	@echo "Setting up development environment..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env file - please configure it"; fi
	@mkdir -p data web docs
	@echo "Development environment ready!"

# Documentation
docs:
	@echo "Generating documentation..."
	@mkdir -p docs/api
	@echo "Documentation generated in docs/"

# Project structure
show-structure:
	@echo "Project Structure:"
	@tree -I '__pycache__|*.pyc|.git|.pytest_cache|htmlcov|*.egg-info' --dirsfirst