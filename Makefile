export PYTHONDONTWRITEBYTECODE=1

.PHONY=help

help:  ## This help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

clean:  ## Remove cache files
	@find . -name "*.pyc" | xargs rm -rf
	@find . -name "*.pyo" | xargs rm -rf
	@find . -name "__pycache__" -type d | xargs rm -rf

###
# Dependencies section
###
_base-pip:
	@pip install -U pip wheel

system-dependencies:
	@sudo apt-get update -y && sudo apt-get install -y libpq-dev

export-requirements: _base-pip
	@pip freeze > requirements.txt

dependencies: _base-pip  ## Install dependencies
	@pip install -r requirements.txt --upgrade pip

###
# Run local section
###
copy-envs:  ## Copy `.env.example` to `.env`
	@cp -n .env.example .env

init: dependencies copy-envs ## Initialize project

run-local:  ## Run server
	@python -m app --reload

###
# Tests section
###
test: clean  ## Run tests
	@pytest tests/

test-coverage: clean  ## Run tests with coverage output
	@pytest tests/ --cov app/ --cov-report term-missing --cov-report xml

test-matching: clean  ## Run tests by match ex: make test-matching k=name_of_test
	@pytest -k $(k) tests/

###
# Lint section
###
_flake8:
	@flake8 --show-source app/

_isort:
	@isort --check-only app/

_black:
	@black --diff --check app/

_isort-fix:
	@isort app/ tests/

_black-fix:
	@black app/ tests/

_dead-fixtures:
	@pytest app/ --dead-fixtures

_mypy:
	@mypy app/

lint: _flake8 _isort _black _dead-fixtures  ## Check code lint
format-code: _isort-fix _black-fix  ## Format code

###
# Docker section
###
build:  ## Docker: Initialize project
	docker-compose build && docker-compose up -d

run-docker:  ## Docker: Run server
	docker-compose run --service-ports --rm api bash -c "make run-local"

run-bash:  ## Docker: Get bash from container
	docker-compose run --service-ports --rm api bash

run-pytest:  ## Docker: Run tests
	docker-compose run --service-ports --no-deps --rm api bash -c "make test"

run-coverage:  ## Docker: Run tests with coverage output
	docker-compose run --service-ports --rm api bash -c "make test-coverage"

run-format-code:  ## Docker: Format code
	docker-compose run --service-ports --no-deps --rm api bash -c "make format-code"

run-code-convention:  ## Docker: Check code lint
	docker-compose run --service-ports --no-deps --rm api bash -c "make lint"

###
# Git section
###
_push : # push on github
	git push
linted-push: format-code lint _push
