# Makefile for ClinicalBERT API Docker operations

.PHONY: help build run stop clean logs test deploy

# Default target
help:
	@echo "Available commands:"
	@echo "  build       - Build Docker images"
	@echo "  run         - Run development environment"
	@echo "  run-prod    - Run production environment"
	@echo "  run-gpu     - Run GPU-enabled environment"
	@echo "  stop        - Stop all services"
	@echo "  clean       - Clean up containers and images"
	@echo "  logs        - Show logs"
	@echo "  test        - Run tests"
	@echo "  deploy      - Deploy to production"

# Build Docker images
build:
	docker-compose build

build-prod:
	docker-compose -f docker-compose.prod.yml build

build-gpu:
	docker-compose -f docker-compose.gpu.yml build

# Run environments
run:
	docker-compose up -d
	@echo "Development environment started at http://localhost:8000"

run-prod:
	docker-compose -f docker-compose.prod.yml up -d
	@echo "Production environment started"

run-gpu:
	docker-compose -f docker-compose.gpu.yml up -d
	@echo "GPU environment started"

# Stop services
stop:
	docker-compose down

stop-prod:
	docker-compose -f docker-compose.prod.yml down

stop-gpu:
	docker-compose -f docker-compose.gpu.yml down

# Clean up
clean:
	docker-compose down -v --rmi all
	docker system prune -f

# Show logs
logs:
	docker-compose logs -f

logs-api:
	docker-compose logs -f clinicalbert-api

# Run tests
test:
	docker-compose exec clinicalbert-api python -m pytest

# Health check
health:
	curl -f http://localhost:8000/health

# Deploy to production
deploy:
	@echo "Deploying to production..."
	docker-compose -f docker-compose.prod.yml pull
	docker-compose -f docker-compose.prod.yml up -d --remove-orphans
	@echo "Production deployment complete"

# Database operations
db-migrate:
	docker-compose exec clinicalbert-api alembic upgrade head

db-reset:
	docker-compose exec postgres psql -U clinicalbert -d clinicalbert -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	$(MAKE) db-migrate

# Backup operations
backup-db:
	docker-compose exec postgres pg_dump -U clinicalbert clinicalbert > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore-db:
	@read -p "Enter backup file path: " backup_file; \
	docker-compose exec -T postgres psql -U clinicalbert clinicalbert < $$backup_file

# Monitoring
monitor:
	@echo "Opening monitoring dashboards..."
	@echo "Prometheus: http://localhost:9090"
	@echo "Grafana: http://localhost:3000 (admin/admin)"

# Security scan
security-scan:
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
		-v $(PWD):/src aquasec/trivy image clinicalbert-api:latest
