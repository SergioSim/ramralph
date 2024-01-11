# -- General
SHELL := /bin/bash

# -- Docker
# Get the current user ID to use for docker run and docker exec commands
DOCKER_UID           = $(shell id -u)
DOCKER_GID           = $(shell id -g)
DOCKER_USER          = $(DOCKER_UID):$(DOCKER_GID)
COMPOSE              = DOCKER_USER=$(DOCKER_USER) docker compose
COMPOSE_RUN          = $(COMPOSE) run --rm
COMPOSE_TEST_RUN     = $(COMPOSE_RUN)
COMPOSE_TEST_RUN_APP = $(COMPOSE_TEST_RUN) app

RAMRALPH_IMAGE_NAME  ?= ramralph
RAMRALPH_IMAGE_TAG   ?= development

# ==============================================================================
# RULES

default: help

bootstrap: ## bootstrap the project for development
bootstrap: \
  build
.PHONY: bootstrap

build: ## build the app container
	RAMRALPH_IMAGE_NAME=$(RAMRALPH_IMAGE_NAME) \
	RAMRALPH_IMAGE_TAG=$(RAMRALPH_IMAGE_TAG) \
	  $(COMPOSE) build app
.PHONY: build

down: ## stop and remove backend containers
	@$(COMPOSE) down
.PHONY: down

lint: ## lint back-end python sources
lint: \
	lint-black \
	lint-ruff
.PHONY: lint

lint-mypy: ## lint back-end python sources with mypy
	@echo 'lint:mypy started…'
	@$(COMPOSE_TEST_RUN_APP) mypy
.PHONY: lint-mypy

lint-black: ## lint back-end python sources with black
	@echo 'lint:black started…'
	@$(COMPOSE_TEST_RUN_APP) black src/ralph tests
.PHONY: lint-black

lint-ruff: ## lint python sources with ruff
	@echo 'lint:ruff started…'
	@$(COMPOSE_TEST_RUN_APP) ruff check .
.PHONY: lint-ruff

lint-ruff-fix: ## lint python sources with ruff with fix option
	@echo 'lint:ruff-fix started…'
	@$(COMPOSE_TEST_RUN_APP) ruff check . --fix
.PHONY: lint-ruff-fix

logs: ## display app logs (follow mode)
	@$(COMPOSE) logs -f app
.PHONY: logs

status: ## an alias for "docker compose ps"
	@$(COMPOSE) ps
.PHONY: status

stop: ## stops backend servers
	@$(COMPOSE) stop
.PHONY: stop

test: ## run back-end tests
	bin/pytest
.PHONY: test
