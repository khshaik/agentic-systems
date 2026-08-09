#!/usr/bin/env python3
"""Perform dependency-free structural checks for the recipe sample."""

from pathlib import Path


ROOT = Path(__file__).parents[1]


def main() -> int:
    required = (
        ROOT / "recipe.yaml",
        ROOT / "subrecipes" / "summarize.yaml",
        ROOT / "sample" / "brief.md",
    )
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        print("Missing: " + ", ".join(missing))
        return 1

    parent = (ROOT / "recipe.yaml").read_text(encoding="utf-8")
    expected = (
        "sub_recipes:",
        "./subrecipes/summarize.yaml",
        "{{ brief_content }}",
    )
    if any(value not in parent for value in expected):
        print("recipe.yaml is missing required subrecipe configuration")
        return 1

    print("Recipe sample: valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
