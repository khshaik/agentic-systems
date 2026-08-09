PYTHON ?= python3

.PHONY: test info run

test:
	$(PYTHON) scripts/check.py

info:
	goose info -v

run:
	goose session -n planning-mode-demo
