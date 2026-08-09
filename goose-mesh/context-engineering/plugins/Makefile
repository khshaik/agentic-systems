PYTHON ?= python3

.PHONY: help validate test demo verify

help:
	@printf '%s\n' \
	  'make validate  Validate the plugin manifest, skill, hooks, and scripts' \
	  'make test      Run all unit tests' \
	  'make demo      Run the repository-health checker against this sample' \
	  'make verify    Run validation, tests, and the deterministic demo'

validate:
	$(PYTHON) scripts/validate_plugin.py .

test:
	$(PYTHON) -m unittest discover -s tests -v

demo:
	$(PYTHON) skills/repository-health/scripts/repository_health.py --repo .

verify: validate test demo
