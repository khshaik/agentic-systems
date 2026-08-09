#!/usr/bin/env python3
"""Handle repository-companion Goose hooks using only the standard library."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BLOCKED_SHELL_PATTERNS = (
    (re.compile(r"(?:^|[;&|]\s*)sudo(?:\s|$)"), "sudo requires explicit user approval"),
    (re.compile(r"\brm\s+(?:-[A-Za-z]*r[A-Za-z]*f|-[A-Za-z]*f[A-Za-z]*r)\s+/(?:\s|$)"), "refusing recursive deletion of the filesystem root"),
    (re.compile(r"\bgit\s+reset\s+--hard(?:\s|$)"), "git reset --hard can discard uncommitted work"),
)


def read_payload(stream: Any = sys.stdin) -> dict[str, Any]:
    """Read and validate one Goose hook payload from stdin."""

    try:
        payload = json.load(stream)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid hook JSON: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError("hook payload must be a JSON object")
    return payload


def strings(value: Any) -> list[str]:
    """Return all string values nested in a JSON-compatible value."""

    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        result: list[str] = []
        for child in value.values():
            result.extend(strings(child))
        return result
    if isinstance(value, list):
        result = []
        for child in value:
            result.extend(strings(child))
        return result
    return []


def blocked_reason(payload: dict[str, Any]) -> str | None:
    """Return a reason for an obviously destructive shell request, if present."""

    command_text = "\n".join(strings(payload.get("tool_input", {})))
    for pattern, reason in BLOCKED_SHELL_PATTERNS:
        if pattern.search(command_text):
            return reason
    return None


def guard_shell(payload: dict[str, Any]) -> int:
    reason = blocked_reason(payload)
    if reason:
        print(json.dumps({"decision": "block", "reason": reason}))
    return 0


def record_event(payload: dict[str, Any]) -> int:
    """Append a redacted event only when REPOSITORY_COMPANION_LOG is configured."""

    configured = os.environ.get("REPOSITORY_COMPANION_LOG")
    if not configured:
        return 0
    destination = Path(configured).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": payload.get("event"),
        "session_id": payload.get("session_id"),
        "matcher_context": payload.get("matcher_context"),
    }
    with destination.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("guard-shell", "record-event"))
    args = parser.parse_args(argv)
    try:
        payload = read_payload()
    except ValueError as exc:
        print(f"repository-companion hook: {exc}", file=sys.stderr)
        return 1
    if args.action == "guard-shell":
        return guard_shell(payload)
    return record_event(payload)


if __name__ == "__main__":
    raise SystemExit(main())
