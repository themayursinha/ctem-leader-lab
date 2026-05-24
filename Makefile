.PHONY: up down build test backend-test frontend-build

up:
	docker compose up --build -d
	@echo "Open http://localhost:8080"

down:
	docker compose down

build:
	docker compose build

test: backend-test frontend-build

backend-test:
	cd backend && .venv/bin/python -m pytest

frontend-build:
	cd frontend && npm ci && npm run build

logs:
	docker compose logs -f
