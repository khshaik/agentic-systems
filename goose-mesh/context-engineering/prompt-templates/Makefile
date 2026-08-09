PROMPTS_DIR ?= $(HOME)/.config/goose/prompts

.PHONY: test install

test:
	@test -s prompts/system.md
	@test -s prompts/plan.md
	@test -s prompts/compaction.md
	@grep -Fq '{{ messages }}' prompts/compaction.md
	@grep -Fq 'extensions' prompts/system.md
	@grep -Fq 'tools' prompts/plan.md
	@echo "Prompt templates: valid"

install: test
	@mkdir -p "$(PROMPTS_DIR)"
	@cp prompts/system.md prompts/plan.md prompts/compaction.md "$(PROMPTS_DIR)/"
	@echo "Installed in $(PROMPTS_DIR). Start a new goose session."
