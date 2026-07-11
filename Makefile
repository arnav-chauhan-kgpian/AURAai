.DEFAULT_GOAL := help
.PHONY: help install backend frontend dev lint format test up down build clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install: ## Install backend and frontend dependencies
	cd backend && poetry install
	cd frontend && npm install

backend: ## Run the backend dev server
	cd backend && poetry run uvicorn app.main:app --reload

frontend: ## Run the frontend dev server
	cd frontend && npm run dev

dev: up ## Alias for `up` (full stack via docker compose)

lint: ## Lint backend and frontend
	cd backend && poetry run ruff check . && poetry run mypy app
	cd frontend && npm run lint && npm run typecheck

format: ## Auto-format the backend
	cd backend && poetry run ruff format .

test: ## Run the backend test suite
	cd backend && poetry run pytest

up: ## Start the full stack with docker compose
	docker compose up --build

down: ## Stop the stack
	docker compose down

build: ## Build all docker images
	docker compose build

clean: ## Remove build artifacts and caches
	docker compose down --volumes --remove-orphans
