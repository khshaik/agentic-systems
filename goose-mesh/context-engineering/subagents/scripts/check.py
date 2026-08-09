#!/usr/bin/env python3
"""Small dependency-free check for the sample files."""

from pathlib import Path


root = Path(__file__).resolve().parents[1]
recipe = (root / "recipe.yaml").read_text(encoding="utf-8")
brief = (root / "sample" / "brief.md").read_text(encoding="utf-8")

required = [
    'version: "1.0.0"',
    "name: summon",
    "name: developer",
    "In parallel",
    "sequentially",
    "Do not edit any files",
]
missing = [value for value in required if value not in recipe]
if missing:
    raise SystemExit(f"recipe.yaml is missing: {', '.join(missing)}")
if not brief.strip():
    raise SystemExit("sample/brief.md is empty")

print("Subagent sample check: passed")
