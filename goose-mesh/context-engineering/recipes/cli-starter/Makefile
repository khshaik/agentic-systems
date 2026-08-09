PYTHON ?= python3
GOOSE_STATE ?= /tmp/goose-cli-starter

.PHONY: test run

test:
	@command -v goose >/dev/null 2>&1 && GOOSE_PATH_ROOT="$(GOOSE_STATE)" goose recipe validate recipe.yaml || echo "goose CLI not installed; skipped Goose validation"

run:
	GOOSE_PATH_ROOT="$(GOOSE_STATE)" goose run --recipe recipe.yaml --params url="https://example.com"
