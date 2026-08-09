PYTHON ?= python3
BRIEF ?= $(CURDIR)/sample/brief.md
GOOSE_STATE ?= /tmp/goose-recipes-validation

.PHONY: test run

test:
	$(PYTHON) scripts/check.py
	@if command -v goose >/dev/null 2>&1; then \
		GOOSE_PATH_ROOT="$(GOOSE_STATE)" goose recipe validate recipe.yaml; \
		GOOSE_PATH_ROOT="$(GOOSE_STATE)" goose recipe validate subrecipes/summarize.yaml; \
	else \
		echo "goose CLI not installed; skipped Goose validation"; \
	fi

run:
	goose run --recipe recipe.yaml --params brief_content="$$(tr '\n' ' ' < "$(BRIEF)")"
