PYTHON ?= python3

.PHONY: test validate run

test:
	$(PYTHON) scripts/check.py

validate: test
	goose recipe validate recipe.yaml

run:
	goose run --recipe recipe.yaml
