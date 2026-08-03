.PHONY: install dev test coverage lint format run run-prod docker-build docker-up

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements-dev.txt
	pre-commit install

test:
	pytest -v

coverage:
	pytest --cov=src --cov-report=term-missing --cov-report=html

lint:
	ruff check src tests
	mypy src

format:
	ruff format src tests

run:
	uvicorn src.api.main:app --reload

run-prod:
	uvicorn src.api.main:app --host 0.0.0.0 --port $${PORT:-8000}

docker-build:
	docker compose build

docker-up:
	docker compose up
