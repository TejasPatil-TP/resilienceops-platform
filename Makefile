.PHONY: help up down test test-backend test-demo-service build-frontend

help:
	@echo "Available commands:"
	@echo "  up                  - Start all services using Docker Compose"
	@echo "  down                - Stop all services"
	@echo "  test                - Run all tests"
	@echo "  test-backend        - Run backend tests"
	@echo "  test-demo-service   - Run demo-service tests"
	@echo "  build-frontend      - Build frontend"

up:
	docker-compose up -d

down:
	docker-compose down

test-backend:
	cd backend && pytest

test-demo-service:
	cd demo-service && pytest

test: test-backend test-demo-service

build-frontend:
	cd frontend && npm run build
