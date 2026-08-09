#!/usr/bin/env python3
"""Validate this Goose Open Plugins sample without third-party dependencies."""

from __future__ import annotations

import argparse
import json
import py_compile
import re
import sys
from pathlib import Path


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
EVENTS = {
    "SessionStart", "SessionEnd", "Stop", "UserPromptSubmit", "PreToolUse",
    "PostToolUse", "PostToolUseFailure", "BeforeReadFile", "AfterFileEdit",
    "BeforeShellExecution", "AfterShellExecution",
}


def load_object(path: Path) -> tuple[dict[str, object] | None, list[str]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"{path}: cannot read JSON: {exc}"]
    if not isinstance(value, dict):
        return None, [f"{path}: root must be a JSON object"]
    return value, []


def parse_skill(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing opening YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("missing closing YAML frontmatter")
    metadata: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()
    return metadata, text[end + 5 :]


def validate(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    manifest_path = root / "plugin.json"
    manifest, manifest_errors = load_object(manifest_path)
    errors.extend(manifest_errors)
    if manifest:
        for field in ("name", "version", "description"):
            if not isinstance(manifest.get(field), str) or not str(manifest[field]).strip():
                errors.append(f"plugin.json: non-empty string field {field!r} is required")
        name = manifest.get("name")
        if isinstance(name, str) and not NAME_RE.fullmatch(name):
            errors.append("plugin.json: name must use lowercase letters, digits, and single hyphens")

    skill_files = sorted((root / "skills").glob("*/SKILL.md"))
    if not skill_files:
        errors.append("no skills/*/SKILL.md files found")
    for path in skill_files:
        try:
            metadata, body = parse_skill(path)
        except (OSError, ValueError) as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")
            continue
        name = metadata.get("name", "")
        if not NAME_RE.fullmatch(name):
            errors.append(f"{path.relative_to(root)}: invalid or missing name")
        if name and name != path.parent.name:
            errors.append(f"{path.relative_to(root)}: name must match its directory")
        if not metadata.get("description"):
            errors.append(f"{path.relative_to(root)}: description is required")
        if not body.strip():
            errors.append(f"{path.relative_to(root)}: instructions are empty")

    hooks_path = root / "hooks" / "hooks.json"
    hooks, hook_errors = load_object(hooks_path)
    errors.extend(hook_errors)
    if hooks:
        event_map = hooks.get("hooks")
        if not isinstance(event_map, dict) or not event_map:
            errors.append("hooks/hooks.json: non-empty hooks object is required")
        else:
            for event, rules in event_map.items():
                if event not in EVENTS:
                    errors.append(f"hooks/hooks.json: unsupported event {event!r}")
                if not isinstance(rules, list) or not rules:
                    errors.append(f"hooks/hooks.json: {event} must contain rules")
                    continue
                for rule in rules:
                    if not isinstance(rule, dict) or not isinstance(rule.get("hooks"), list):
                        errors.append(f"hooks/hooks.json: {event} rule must contain hooks array")
                        continue
                    matcher = rule.get("matcher")
                    if matcher is not None:
                        try:
                            re.compile(str(matcher))
                        except re.error as exc:
                            errors.append(f"hooks/hooks.json: invalid matcher for {event}: {exc}")
                    for action in rule["hooks"]:
                        if not isinstance(action, dict) or not action.get("command"):
                            errors.append(f"hooks/hooks.json: {event} action requires command")
                        elif action.get("type", "command") != "command":
                            errors.append(f"hooks/hooks.json: {event} action type must be command")

    for script in root.rglob("*.py"):
        if "__pycache__" in script.parts:
            continue
        try:
            py_compile.compile(str(script), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"{script.relative_to(root)}: {exc.msg}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path("."))
    args = parser.parse_args(argv)
    errors = validate(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("OK: plugin manifest, skills, hooks, and Python scripts are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
