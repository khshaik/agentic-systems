#!/usr/bin/env python3
"""Preview the root-to-directory .goosehints chain for a repository path."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from hints_common import hint_chain_for_path, referenced_paths, repository_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=".", type=Path)
    parser.add_argument("--root", type=Path, help="repository root; auto-detected by default")
    parser.add_argument(
        "--content",
        action="store_true",
        help="print hint contents in addition to filenames",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        root = args.root.resolve() if args.root else repository_root()
        target = args.path if args.path.is_absolute() else root / args.path
        chain = hint_chain_for_path(root, target)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print("Documented hierarchy preview (helper output, not Goose runtime output)")
    print(f"repository: {root}")
    print(f"target:     {target.resolve()}")
    print("order:      project-wide to most-specific\n")

    if not chain:
        print("No applicable .goosehints files found.")
        return 1

    for index, hint_file in enumerate(chain, start=1):
        print(f"{index}. {hint_file.relative_to(root)}")
        references = referenced_paths(hint_file, root)
        for raw, resolved in references:
            display = resolved.relative_to(root) if resolved else "MISSING"
            print(f"   @ reference: {raw} -> {display}")
        if args.content:
            print("   ---")
            for line in hint_file.read_text(encoding="utf-8").splitlines():
                print(f"   {line}")
            print("   ---")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
