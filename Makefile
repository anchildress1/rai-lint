# Package paths
NODE_PKG := packages/node-commitlint
PYTHON_PKG := packages/python-gitlint
PYTHON_SOURCES := gitlint_rai/ tests/

.PHONY: help install install-locked update-locks clean ai-checks
.PHONY: test test-node test-python
.PHONY: lint lint-node lint-python lint-format
.PHONY: format format-node format-python
.PHONY: build build-node build-python

help:
	@echo "Main targets:"
	@echo "  ai-checks      - Full env refresh + all checks (clean, install, lint, test, build)"
	@echo "  test           - Run all tests (Node + Python)"
	@echo "  lint           - Run all linters (Node + Python)"
	@echo "  format         - Format all code (Node + Python)"
	@echo "  build          - Build all packages"
	@echo "  install        - Install dependencies (updates locks if needed)"
	@echo "  install-locked - Install from existing lock files (CI mode)"
	@echo "  update-locks   - Explicitly update all lock files"
	@echo "  clean          - Clean build artifacts"

# ============================================================================
# Install & Clean
# ============================================================================

# Default install: updates lock files if they need resolution (e.g., missing or invalid)
# This is the recommended mode for local development.
# For reproducible builds in CI, use 'install-locked' instead.
install:
	npm install
	cd $(PYTHON_PKG) && uv sync --group dev

# CI install: uses existing lock files (fails if out of sync)
install-locked:
	npm ci
	cd $(PYTHON_PKG) && uv sync --locked --group dev

# Explicitly update lock files
update-locks:
	npm install
	cd $(PYTHON_PKG) && uv lock

clean:
	rm -rf .venv node_modules
	rm -rf $(NODE_PKG)/dist $(NODE_PKG)/node_modules
	rm -rf $(PYTHON_PKG)/build $(PYTHON_PKG)/dist $(PYTHON_PKG)/*.egg-info
	rm -rf $(PYTHON_PKG)/htmlcov $(PYTHON_PKG)/.venv
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true

# ============================================================================
# Test
# ============================================================================

test: test-node test-python

test-node:
	cd $(NODE_PKG) && mkdir -p reports && npm test

test-python:
	cd $(PYTHON_PKG) && mkdir -p reports && \
		uv run pytest \
			--cov \
			--cov-report=xml \
			--cov-report=term-missing

# ============================================================================
# Lint
# ============================================================================

lint: lint-format lint-node lint-python

lint-format:
	npm run format

lint-node:
	cd $(NODE_PKG) && npm run lint

lint-python:
	cd $(PYTHON_PKG) && uv run black --check $(PYTHON_SOURCES)
	cd $(PYTHON_PKG) && uv run isort --check-only $(PYTHON_SOURCES)

# ============================================================================
# Format
# ============================================================================

format: format-node format-python

format-node:
	npm run format

format-python:
	cd $(PYTHON_PKG) && uv run black $(PYTHON_SOURCES)
	cd $(PYTHON_PKG) && uv run isort $(PYTHON_SOURCES)

# ============================================================================
# Build
# ============================================================================

build: build-node build-python

build-node:
	cd $(NODE_PKG) && npm run build

build-python:
	cd $(PYTHON_PKG) && uv build

# ============================================================================
# AI Checks
# ============================================================================

ai-checks: clean install format lint test build
