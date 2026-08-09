#!/usr/bin/env python3
"""Validate a local Agent Skill without third-party dependencies."""

from __future__ import annotations

import argparse
import json
import py_compile
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REFERENCE_RE = re.compile(r"`((?:scripts|references|assets|workflows)/[^`\s]+)`")


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must begin with YAML frontmatter delimited by ---")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("SKILL.md frontmatter has no closing --- delimiter")
    raw = text[4:end]
    body = text[end + 5:]
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if not line or line[0].isspace() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip("\"'")
    return data, body


def validate(skill_dir: Path) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    skill_dir = skill_dir.resolve()
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        return {"valid": False, "errors": [f"Missing {skill_file}"], "warnings": []}
    try:
        text = skill_file.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(text)
    except (OSError, UnicodeError, ValueError) as exc:
        return {"valid": False, "errors": [str(exc)], "warnings": []}

    name = meta.get("name", "")
    description = meta.get("description", "")
    if not name:
        errors.append("Frontmatter field 'name' is required")
    elif not NAME_RE.fullmatch(name):
        errors.append("name must contain lowercase letters, numbers, and single hyphens only")
    elif len(name) > 64:
        errors.append("name must not exceed 64 characters")
    if name and name != skill_dir.name:
        errors.append(f"name '{name}' must match parent directory '{skill_dir.name}'")
    if not description:
        errors.append("Frontmatter field 'description' is required")
    elif len(description) > 1024:
        errors.append("description must not exceed 1024 characters")
    if not body.strip():
        errors.append("SKILL.md body is empty")
    if len(body.split()) > 5000:
        warnings.append("SKILL.md body exceeds the recommended 5000-token-scale size; split more content into resources")

    referenced = sorted(set(REFERENCE_RE.findall(body)))
    for rel in referenced:
        if not (skill_dir / rel).exists():
            errors.append(f"Referenced file does not exist: {rel}")

    for script in (skill_dir / "scripts").glob("*.py") if (skill_dir / "scripts").is_dir() else []:
        try:
            py_compile.compile(str(script), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"Python syntax error in {script.name}: {exc.msg}")

    expected_dirs = ["scripts", "references", "assets", "workflows"]
    for dirname in expected_dirs:
        path = skill_dir / dirname
        if not path.is_dir():
            warnings.append(f"Optional sample directory is absent: {dirname}/")

    return {
        "valid": not errors,
        "skill": name or skill_dir.name,
        "description": description,
        "references_checked": referenced,
        "errors": errors,
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", nargs="?", type=Path, default=Path(".agents/skills/release-readiness"))
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    result = validate(args.skill_dir)
    if args.as_json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Skill: {result.get('skill', args.skill_dir.name)}")
        print(f"Valid: {result['valid']}")
        for warning in result.get("warnings", []):
            print(f"WARNING: {warning}")
        for error in result.get("errors", []):
            print(f"ERROR: {error}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
