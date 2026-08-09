.PHONY: verify test validate-skill demo gate clean

PYTHON ?= python3
SKILL_DIR := .agents/skills/release-readiness
AUDIT := $(SKILL_DIR)/scripts/release_audit.py
POLICY := $(SKILL_DIR)/references/default-policy.json

verify: validate-skill test demo

validate-skill:
	$(PYTHON) $(SKILL_DIR)/scripts/validate_skill.py $(SKILL_DIR)

test:
	$(PYTHON) -m unittest discover -s tests -v
	cd sample-service && $(PYTHON) -m unittest discover -s tests -v

demo:
	$(PYTHON) $(AUDIT) --repo sample-service --mode full --policy $(POLICY) --format both --output-dir out/demo --fail-on none

gate:
	$(PYTHON) $(AUDIT) --repo sample-service --mode full --policy $(POLICY) --format both --output-dir out/gate --fail-on high

clean:
	rm -rf out .release-readiness sample-service/.release-readiness
