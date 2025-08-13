.PHONY: help install install-dev test test-unit test-integration test-e2e test-multiagent test-coverage lint format type-check security-check run run-dev cli docker-up docker-down docker-build clean migrate db-upgrade db-downgrade celery celery-flower monitoring-up monitoring-down docs serve-docs

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3.11
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
BLACK := $(PYTHON) -m black
RUFF := $(PYTHON) -m ruff
MYPY := $(PYTHON) -m mypy
UVICORN := $(PYTHON) -m uvicorn
DOCKER_COMPOSE := docker-compose

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo '$(BLUE)Cidadão.AI - Development Commands$(NC)'
	@echo ''
	@echo 'Usage:'
	@echo '  $(GREEN)make$(NC) $(YELLOW)<target>$(NC)'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(NC)"
	$(PIP) install -e .
	@echo "$(GREEN)Installation complete!$(NC)"

install-dev: ## Install all dependencies including dev tools
	@echo "$(BLUE)Installing all dependencies...$(NC)"
	$(PIP) install -e ".[dev,prod]"
	pre-commit install
	@echo "$(GREEN)Development installation complete!$(NC)"

test: ## Run all tests
	@echo "$(BLUE)Running all tests...$(NC)"
	$(PYTEST) tests/ -v

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	$(PYTEST) tests/unit/ -v -m unit

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	$(PYTEST) tests/integration/ -v -m integration

test-e2e: ## Run end-to-end tests only
	@echo "$(BLUE)Running e2e tests...$(NC)"
	$(PYTEST) tests/e2e/ -v -m e2e

test-multiagent: ## Run multi-agent simulation tests
	@echo "$(BLUE)Running multi-agent tests...$(NC)"
	$(PYTEST) tests/multiagent/ -v -s

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	$(PYTEST) tests/ -v --cov=src --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)Coverage report generated in htmlcov/index.html$(NC)"

lint: ## Run linters (ruff)
	@echo "$(BLUE)Running linters...$(NC)"
	$(RUFF) check src/ tests/
	@echo "$(GREEN)Linting complete!$(NC)"

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	$(BLACK) src/ tests/
	$(PYTHON) -m isort src/ tests/
	$(RUFF) check src/ tests/ --fix
	@echo "$(GREEN)Formatting complete!$(NC)"

type-check: ## Run type checking with mypy
	@echo "$(BLUE)Running type checks...$(NC)"
	$(MYPY) src/ --strict
	@echo "$(GREEN)Type checking complete!$(NC)"

security-check: ## Run security checks
	@echo "$(BLUE)Running security checks...$(NC)"
	$(PYTHON) -m safety check
	$(PYTHON) -m bandit -r src/
	@echo "$(GREEN)Security checks complete!$(NC)"

run: ## Run the FastAPI application
	@echo "$(BLUE)Starting Cidadão.AI API...$(NC)"
	$(UVICORN) src.api.main:app --host 0.0.0.0 --port 8000

run-dev: ## Run the application in development mode with hot reload
	@echo "$(BLUE)Starting Cidadão.AI API in development mode...$(NC)"
	$(UVICORN) src.api.main:app --reload --host 0.0.0.0 --port 8000

cli: ## Install and test CLI tool
	@echo "$(BLUE)Installing CLI tool...$(NC)"
	$(PIP) install -e .
	cidadao --help
	@echo "$(GREEN)CLI installation complete!$(NC)"

docker-up: ## Start all services with docker-compose
	@echo "$(BLUE)Starting Docker services...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)Services started!$(NC)"

docker-down: ## Stop all docker services
	@echo "$(BLUE)Stopping Docker services...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)Services stopped!$(NC)"

docker-build: ## Build docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	$(DOCKER_COMPOSE) build
	@echo "$(GREEN)Build complete!$(NC)"

clean: ## Clean up generated files
	@echo "$(BLUE)Cleaning up...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +
	@echo "$(GREEN)Cleanup complete!$(NC)"

migrate: ## Create a new database migration
	@echo "$(BLUE)Creating database migration...$(NC)"
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

db-upgrade: ## Apply database migrations
	@echo "$(BLUE)Applying database migrations...$(NC)"
	alembic upgrade head
	@echo "$(GREEN)Database upgraded!$(NC)"

db-downgrade: ## Rollback database migration
	@echo "$(BLUE)Rolling back database migration...$(NC)"
	alembic downgrade -1
	@echo "$(YELLOW)Database rolled back!$(NC)"

celery: ## Start Celery worker
	@echo "$(BLUE)Starting Celery worker...$(NC)"
	celery -A src.core.celery_app worker --loglevel=info

celery-flower: ## Start Celery Flower monitoring
	@echo "$(BLUE)Starting Celery Flower...$(NC)"
	celery -A src.core.celery_app flower

monitoring-up: ## Start monitoring stack (Prometheus + Grafana)
	@echo "$(BLUE)Starting monitoring services...$(NC)"
	$(DOCKER_COMPOSE) -f docker-compose.monitoring.yml up -d
	@echo "$(GREEN)Monitoring services started!$(NC)"
	@echo "Prometheus: http://localhost:9090"
	@echo "Grafana: http://localhost:3000"

monitoring-down: ## Stop monitoring stack
	@echo "$(BLUE)Stopping monitoring services...$(NC)"
	$(DOCKER_COMPOSE) -f docker-compose.monitoring.yml down
	@echo "$(GREEN)Monitoring services stopped!$(NC)"

docs: ## Build documentation
	@echo "$(BLUE)Building documentation...$(NC)"
	mkdocs build
	@echo "$(GREEN)Documentation built in site/$(NC)"

serve-docs: ## Serve documentation locally
	@echo "$(BLUE)Serving documentation...$(NC)"
	mkdocs serve

# Development workflow shortcuts
dev: install-dev ## Full development setup
	@echo "$(GREEN)Development environment ready!$(NC)"

check: lint type-check test ## Run all checks (lint, type-check, test)
	@echo "$(GREEN)All checks passed!$(NC)"

ci: check security-check ## Run all CI checks
	@echo "$(GREEN)CI checks passed!$(NC)"

# Git hooks
pre-commit: format lint type-check test-unit ## Run pre-commit checks
	@echo "$(GREEN)Pre-commit checks passed!$(NC)"

# Database shortcuts
db-reset: ## Reset database (drop and recreate)
	@echo "$(RED)WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		alembic downgrade base && alembic upgrade head; \
		echo "$(GREEN)Database reset complete!$(NC)"; \
	fi

# Utility commands
shell: ## Start IPython shell with app context
	@echo "$(BLUE)Starting IPython shell...$(NC)"
	ipython -i scripts/shell_context.py

logs: ## Tail application logs
	@echo "$(BLUE)Tailing logs...$(NC)"
	tail -f logs/*.log

# Performance
profile: ## Run performance profiling
	@echo "$(BLUE)Running performance profiling...$(NC)"
	$(PYTHON) -m cProfile -o profile.stats src/api/main.py
	@echo "$(GREEN)Profile saved to profile.stats$(NC)"

benchmark: ## Run performance benchmarks
	@echo "$(BLUE)Running benchmarks...$(NC)"
	$(PYTEST) tests/benchmarks/ -v
	@echo "$(GREEN)Benchmarks complete!$(NC)"

# Setup commands
setup-llm: ## Setup LLM providers
	@echo "$(BLUE)Setting up LLM providers...$(NC)"
	$(PYTHON) scripts/setup_llm_providers.py

setup-db: ## Initialize database with seed data
	@echo "$(BLUE)Setting up database...$(NC)"
	$(PYTHON) scripts/seed_data.py
	@echo "$(GREEN)Database setup complete!$(NC)"

# Fine-tuning
fine-tune: ## Start fine-tuning process
	@echo "$(BLUE)Starting fine-tuning...$(NC)"
	$(PYTHON) scripts/fine_tune_model.py
	@echo "$(GREEN)Fine-tuning complete!$(NC)"

# Version
version: ## Show version
	@echo "$(BLUE)Cidadão.AI$(NC) version $(GREEN)1.0.0$(NC)"