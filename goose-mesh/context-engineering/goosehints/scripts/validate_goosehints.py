#!/usr/bin/env python3
"""Validate the structure and references of this .goosehints sample."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from hints_common import iter_hint_files, referenced_paths, repository_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, help="repository root; auto-detected by default")
    parser.add_argument(
        "--max-lines",
        type=int,
        default=160,
        help="warn when a hints file exceeds this line count",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        root = (args.root.resolve() if args.root else repository_root())
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    errors: list[str] = []
    warnings: list[str] = []
    root_hint = root / ".goosehints"
    if not root_hint.is_file():
        errors.append("missing root .goosehints")

    hint_files = iter_hint_files(root)
    if not hint_files:
        errors.append("no .goosehints files found")

    for hint_file in hint_files:
        relative = hint_file.relative_to(root)
        text = hint_file.read_text(encoding="utf-8")
        if not text.strip():
            errors.append(f"{relative}: file is empty")
        if "\x00" in text:
            errors.append(f"{relative}: contains a NUL byte")
        line_count = len(text.splitlines())
        if line_count > args.max_lines:
            warnings.append(
                f"{relative}: {line_count} lines; concise hints consume less context"
            )

        for raw_reference, resolved in referenced_paths(hint_file, root):
            if resolved is None:
                errors.append(f"{relative}: missing @ reference {raw_reference!r}")

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)

    if errors:
        print(
            f"FAILED: {len(errors)} error(s), {len(warnings)} warning(s), "
            f"{len(hint_files)} hint file(s) checked"
        )
        return 1

    print(
        f"OK: {len(hint_files)} .goosehints file(s), all @ references resolve, "
        f"{len(warnings)} warning(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
