SHELL := /bin/bash

.DEFAULT_GOAL := up

# ENV selects which env file to use, e.g. `make up ENV=prod` -> .env.prod
ENV_FILE := $(if $(ENV),.env.$(ENV),.env)

COMPOSE = docker compose --env-file=$(ENV_FILE) -f compose.yml -f compose.dev.yml

up: ## Start all services with hot reload
	$(COMPOSE) up --watch --build --renew-anon-volumes

down: ## Stop all services

	$(COMPOSE) down

sync: ## Sync Python dependencies with uv
	uv sync

test: ## Run the test suite
	uv run pytest

seed: ## Add the default providers to the database
	uv run python -m scripts.seed_providers
