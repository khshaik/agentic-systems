.PHONY: help list-agents validate test verify demo-lifecycle

PYTHON ?= python3

help:
	@printf '%s\n' \
	  'make list-agents     List project custom agents' \
	  'make validate        Validate all agent files' \
	  'make test            Run application and management CLI tests' \
	  'make verify          Run validation and all tests' \
	  'make demo-lifecycle  Demonstrate create/edit/export/import safely in a temp directory'

list-agents:
	$(PYTHON) scripts/agentctl.py list

validate:
	$(PYTHON) scripts/agentctl.py validate

test:
	$(PYTHON) -m unittest discover -s tests -v

verify: validate test

demo-lifecycle:
	bash scripts/demo_lifecycle.sh
