include runtime.mk

.PHONY: generator-tests docs-install docs-build docs-serve docs-check docs-clean dev-env dev-shell dev-ci dev-check-tools dev-validate dev-fixtures dev-smoke act-check act-install docker-check ci-local ci-list ci-clean

# The template adds generator tests to the shared runtime CI target.
ci: generator-tests

generator-tests:
	uv run --no-sync python -m unittest tests.test_generate_starter tests.test_starter_static -v

# Documentation
###############
DOCS_PORT ?= 8000

ensure-uv:
	@which uv > /dev/null || (curl -LsSf https://astral.sh/uv/install.sh | sh)

docs-install: ensure-uv
	@echo "Installing documentation dependencies..."
	uv sync --group dev
	@echo "Documentation dependencies installed"

docs-build: docs-install
	@echo "Building documentation..."
	uv run mkdocs build --strict
	@echo "Documentation built successfully"
	@echo "📄 Site location: site/"
	@echo "🌐 Open site/index.html in your browser to view"

docs-serve: docs-install
	@echo "Starting documentation server with live reload..."
	@echo "📍 Documentation will be available at:"
	@echo "   - Local: http://localhost:$(DOCS_PORT)"
	@echo "🔄 Changes will auto-reload (press Ctrl+C to stop)"
	@echo ""
	@echo "💡 To use a different port: make docs-serve DOCS_PORT=9999"
	uv run mkdocs serve --dev-addr 0.0.0.0:$(DOCS_PORT)

docs-check: docs-build
	@echo "Checking documentation..."
	@echo "📊 Site size: $$(du -sh site/ | cut -f1)"
	@echo "📄 Pages built: $$(find site/ -name "*.html" | wc -l)"
	@echo "🔗 Checking for common issues..."
	@if grep -r "404" site/ >/dev/null 2>&1; then \
		echo "⚠️  Found potential 404 errors"; \
	else \
		echo "✅ No obvious 404 errors found"; \
	fi
	@if find site/ -name "*.html" -size 0 | grep -q .; then \
		echo "⚠️  Found empty HTML files"; \
		find site/ -name "*.html" -size 0; \
	else \
		echo "✅ No empty HTML files found"; \
	fi
	@echo "Documentation check complete"

docs-clean:
	@echo "Cleaning documentation build files..."
	rm -rf site/
	rm -rf .cache/
	@echo "Documentation cleaned"

# Container dev environment
############################
dev-env:
	docker compose -f docker/docker-compose.yml build
	docker compose -f docker/docker-compose.yml run --rm dev

dev-shell:
	docker compose -f docker/docker-compose.yml run --rm dev /bin/bash

dev-ci:
	docker compose -f docker/docker-compose.yml run --rm dev make ci

dev-check-tools:
	@echo "Checking container tool availability..."
	docker compose -f docker/docker-compose.yml run --rm dev bash -c '\
		echo "=== Rust ===" && rustc --version && cargo --version && \
		echo "=== Rust tools ===" && cargo fmt --version && cargo clippy --version && \
		echo "=== Godot ===" && godot --version && \
		echo "=== Python/uv ===" && python3 --version && uv --version && \
		echo "=== All tools OK ==="'

dev-validate: dev-check-tools dev-ci
	@echo "Dev environment fully validated"

dev-fixtures:
	docker compose -f docker/docker-compose.yml run --rm dev make fixtures

dev-smoke:
	docker compose -f docker/docker-compose.yml run --rm dev make smoke

# Local GitHub Actions Testing with act
#######################################

# Detect docker socket (Colima, Docker Desktop, Podman, or default)
define docker_socket
$(shell \
	if [ -S $$HOME/.colima/default/docker.sock ]; then \
		echo "$$HOME/.colima/default/docker.sock"; \
	elif [ -S /var/run/docker.sock ]; then \
		echo "/var/run/docker.sock"; \
	elif [ -S $$HOME/.docker/run/docker.sock ]; then \
		echo "$$HOME/.docker/run/docker.sock"; \
	elif [ -S /run/user/$$(id -u)/podman/podman.sock ]; then \
		echo "/run/user/$$(id -u)/podman/podman.sock"; \
	else \
		echo "/var/run/docker.sock"; \
	fi \
)
endef

DOCKER_SOCKET := $(docker_socket)
ACT_IMAGE := catthehacker/ubuntu:act-22.04
ACT_ARCH := linux/amd64

act-check:  ## Check if act is installed, install if missing
	@if ! which act > /dev/null 2>&1; then \
		echo "act is not installed. Installing automatically..."; \
		$(MAKE) act-install; \
	fi

docker-check:  ## Check if Docker/Podman/Colima is running
	@if ! DOCKER_HOST="unix://$(DOCKER_SOCKET)" docker ps >/dev/null 2>&1; then \
		echo "Cannot connect to Docker daemon"; \
		echo ""; \
		echo "Please start your container runtime first:"; \
		echo "  - Docker Desktop: Open Docker Desktop app"; \
		echo "  - Colima: run 'colima start'"; \
		echo "  - Podman: run 'podman machine start'"; \
		echo "  - Docker (Linux): run 'sudo systemctl start docker'"; \
		echo ""; \
		echo "Attempted socket: $(DOCKER_SOCKET)"; \
		exit 1; \
	fi
	@echo "Docker is running (socket: $(DOCKER_SOCKET))"

act-install:  ## Install act for local GitHub Actions testing
	@echo "Installing act (GitHub Actions local runner)..."
	@if which act > /dev/null 2>&1; then \
		echo "act is already installed: $$(which act)"; \
		act --version; \
	elif which brew > /dev/null 2>&1; then \
		echo "Installing act via Homebrew..."; \
		brew install act; \
	else \
		echo "Installing act via install script..."; \
		curl --proto '=https' --tlsv1.2 -sSf https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash; \
	fi
	@echo ""
	@echo "act installed successfully!"
	@echo "Run 'make ci-list' to see available workflows"
	@echo "Run 'make ci-local' to run CI locally"

ci-list: act-check docker-check  ## List available GitHub Actions workflows and jobs
	@echo "Available workflows and jobs:"
	@DOCKER_HOST="unix://$(DOCKER_SOCKET)" act -l

ci-local: act-check docker-check  ## Run GitHub Actions CI workflow locally
	@echo "Running GitHub Actions CI locally..."
	@echo "Using Docker socket: $(DOCKER_SOCKET)"
	@echo "Container architecture: $(ACT_ARCH)"
	@echo "Image: $(ACT_IMAGE)"
	@echo ""
	@DOCKER_HOST="unix://$(DOCKER_SOCKET)" act push \
		-W .github/workflows/ci.yml \
		-j web \
		--container-daemon-socket - \
		--container-architecture $(ACT_ARCH) \
		-P ubuntu-latest=$(ACT_IMAGE)
	@echo ""
	@echo "Local CI complete - matches GitHub Actions!"

ci-clean:  ## Clean up act cache and containers
	@echo "Cleaning up act cache and containers..."
	@-docker ps -a | grep "act-" | awk '{print $$1}' | xargs docker rm -f 2>/dev/null || true
	@-docker images | grep "act-" | awk '{print $$3}' | xargs docker rmi -f 2>/dev/null || true
	@echo "Cleanup complete!"
