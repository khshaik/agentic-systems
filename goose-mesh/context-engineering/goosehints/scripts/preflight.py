#!/usr/bin/env python3
"""Check local prerequisites for running the sample with or without Goose."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from hints_common import repository_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-goose",
        action="store_true",
        help="fail rather than warn when the goose executable is unavailable",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    failures: list[str] = []

    if sys.version_info < (3, 11):
        failures.append("Python 3.11 or newer is required")
    else:
        print(f"OK: Python {sys.version.split()[0]}")

    try:
        root = repository_root(Path.cwd())
        print(f"OK: repository root {root}")
        if not (root / ".goosehints").is_file():
            failures.append("root .goosehints is missing")
        else:
            print("OK: root .goosehints exists")
    except FileNotFoundError as exc:
        failures.append(str(exc))

    goose = shutil.which("goose")
    if goose:
        result = subprocess.run(
            [goose, "--version"], capture_output=True, text=True, check=False
        )
        version = (result.stdout or result.stderr).strip() or "version unavailable"
        print(f"OK: Goose executable {goose} ({version})")
    elif args.require_goose:
        failures.append("Goose executable not found in PATH")
    else:
        print("WARNING: Goose executable not found; repository validation still works")

    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
