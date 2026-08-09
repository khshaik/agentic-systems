.PHONY: test config

test:
	@python3 -m json.tool recipes/review.json >/dev/null
	@python3 -m json.tool recipes/explain.json >/dev/null
	@if command -v goose >/dev/null 2>&1; then \
		GOOSE_PATH_ROOT="$${TMPDIR:-/tmp}/goose-slash-commands-validation" goose recipe validate recipes/review.json; \
		GOOSE_PATH_ROOT="$${TMPDIR:-/tmp}/goose-slash-commands-validation" goose recipe validate recipes/explain.json; \
	else \
		echo "JSON valid (goose CLI not installed; skipped recipe validation)"; \
	fi

config:
	@sed 's|REPLACE_WITH_ABSOLUTE_PATH|$(CURDIR)|g' config.yaml.example
