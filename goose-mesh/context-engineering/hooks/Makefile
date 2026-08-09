PYTHON ?= python3

.PHONY: test demo

test:
	$(PYTHON) -m py_compile scripts/log_event.py
	$(PYTHON) -c 'import json; json.load(open("plugin.json")); json.load(open("hooks/hooks.json"))'

demo: test
	@rm -f .goose-hook-events.jsonl
	@printf '%s' '{"event":"SessionStart","session_id":"demo"}' | $(PYTHON) scripts/log_event.py
	@cat .goose-hook-events.jsonl
