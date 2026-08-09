PYTHON ?= python3
export PYTHONPATH := src:scripts

.PHONY: help preflight validate-hints test run show-root-context show-api-context verify clean

help:
	@printf '%s\n' \
	  'make verify             Validate hints and run all tests' \
	  'make run                Run the sample order calculation' \
	  'make validate-hints     Validate .goosehints files and @ references' \
	  'make show-api-context   Preview root-to-API nested hints' \
	  'make preflight          Check Python, repository, and optional Goose CLI'

preflight:
	$(PYTHON) scripts/preflight.py

validate-hints:
	$(PYTHON) scripts/validate_goosehints.py

test:
	$(PYTHON) -m unittest discover -s tests -v

run:
	$(PYTHON) -m order_service.cli

show-root-context:
	$(PYTHON) scripts/show_effective_hints.py README.md --content

show-api-context:
	$(PYTHON) scripts/show_effective_hints.py src/order_service/api/handlers.py

verify: preflight validate-hints test run

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
