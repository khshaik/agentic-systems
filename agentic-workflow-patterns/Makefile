.PHONY: help setup setup-nvidia test check run-router run-learning

help:
	@echo "Agentic Workflow Patterns"
	@echo "  make setup          Install both examples"
	@echo "  make setup-nvidia   Add NVIDIA support to the router"
	@echo "  make test           Run deterministic tests"
	@echo "  make check          Compile all project Python files"
	@echo "  make run-router     Run the conditional router"
	@echo "  make run-learning   Run the multi-agent learning assistant"

setup:
	uv sync --project conditional-routing
	uv sync --project multi-agent-workflow

setup-nvidia:
	uv sync --project conditional-routing --extra nvidia

test:
	cd conditional-routing && uv run python -m unittest discover -s tests -v

check:
	cd conditional-routing && uv run python -m compileall -q app.py tests
	cd multi-agent-workflow && uv run python -m compileall -q .

run-router:
	cd conditional-routing && uv run python app.py

run-learning:
	cd multi-agent-workflow && uv run python main.py
