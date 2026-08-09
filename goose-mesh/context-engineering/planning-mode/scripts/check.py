#!/usr/bin/env python3
"""Dependency-free check for the Planning Mode sample."""

from pathlib import Path

root = Path(__file__).resolve().parents[1]
readme = (root / "README.md").read_text()
config = (root / "config.yaml.example").read_text()

for text in ("/plan", "/endplan", "review", "accept"):
    assert text in readme, f"README.md is missing {text!r}"

for key in ("GOOSE_PLANNER_PROVIDER", "GOOSE_PLANNER_MODEL"):
    assert key in config, f"config.yaml.example is missing {key}"

print("Planning Mode sample: valid")
