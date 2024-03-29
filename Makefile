.PHONY: help
help:  ## Print this help menu
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: setup
setup:  ## Set up the local development environment
	poetry install -E docs
	poetry run pre-commit install

.PHONY: publish
publish:  ## Build & publish the new version
	poetry build
	poetry publish

.PHONY: build-docs
build-docs:
	poetry run sphinx-build -M html docs docs/_build

.PHONY: serve-docs
serve-docs: build-docs  ## Simple development server for Sphinx docs
	@echo "Serving documentation locally."
	@echo "Open browser with 'make open-docs'"
	@find docs serdelicacy | entr -ps "$(MAKE) build-docs"

.PHONY: open-docs
open-docs:  ## Open Sphinx docs index in a browser
	gio open docs/_build/html/index.html

.PHONY: fix
fix:  ## Fix all files in-place
	poetry run nox -s $@

.PHONY: lint
lint:  ## Run linters on all files
	poetry run nox -s $@

.PHONY: typecheck
typecheck:  ## Run static type checks
	poetry run nox -s $@

.PHONY: pytest
pytest:  ## Run unit tests
	poetry run nox -s $@
