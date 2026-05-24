.PHONY: up down build test backend-test frontend-test frontend-build logs lint clean

up:
	docker compose up --build -d
	@echo "Open http://localhost:8080"

down:
	docker compose down

build:
	docker compose build

test: backend-test frontend-test

backend-test:
	cd backend && .venv/bin/python -m pytest tests/test_api.py tests/test_auth.py tests/test_scoring.py -v

backend-test-integration:
	cd backend && .venv/bin/python -m pytest tests/test_integration.py -v

frontend-test:
	cd frontend && npx vitest run

frontend-build:
	cd frontend && npm ci && npm run build

frontend-e2e:
	cd frontend && npm run build && npm run test:e2e

lint:
	cd backend && .venv/bin/python -m ruff check app/ tests/
	cd frontend && npx eslint src/

logs:
	docker compose logs -f

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf frontend/dist
