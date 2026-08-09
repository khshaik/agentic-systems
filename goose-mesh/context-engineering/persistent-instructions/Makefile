.PHONY: test demo

test:
	@test -s guardrails.md
	@test "$$(wc -c < guardrails.md)" -le 65536
	@grep -q '^# Project guardrails' guardrails.md
	@echo "Persistent instructions: valid"

demo: test
	@GOOSE_MOIM_MESSAGE_FILE="$$PWD/guardrails.md"; \
	printf 'GOOSE_MOIM_MESSAGE_FILE=%s\n\n' "$$GOOSE_MOIM_MESSAGE_FILE"; \
	cat "$$GOOSE_MOIM_MESSAGE_FILE"
