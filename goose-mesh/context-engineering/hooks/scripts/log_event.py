#!/usr/bin/env python3
"""Append a small Goose hook event record to a JSON Lines file."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(f"invalid hook payload: {exc.msg}", file=sys.stderr)
        return 1

    if not isinstance(payload, dict):
        print("invalid hook payload: expected a JSON object", file=sys.stderr)
        return 1

    destination = Path(
        os.environ.get("GOOSE_HOOK_LOG", ".goose-hook-events.jsonl")
    ).expanduser()
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": payload.get("event"),
        "session_id": payload.get("session_id"),
        "context": payload.get("matcher_context"),
    }
    with destination.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
