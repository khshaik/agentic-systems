"""Shared, dependency-free helpers for this repository's hints tooling."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

REFERENCE_PATTERN = re.compile(r"(?<![\w/])@([A-Za-z0-9_.\-/]+)")


def repository_root(start: Path | None = None) -> Path:
    """Find the Git root, falling back to the sample root containing .goosehints."""

    current = (start or Path.cwd()).resolve()
    try:
        result = subprocess.run(
            ["git", "-C", str(current), "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        )
        return Path(result.stdout.strip()).resolve()
    except (FileNotFoundError, subprocess.CalledProcessError):
        for candidate in (current, *current.parents):
            if (candidate / ".goosehints").is_file():
                return candidate
        raise FileNotFoundError("could not find a Git root or parent .goosehints file")


def iter_hint_files(root: Path) -> list[Path]:
    """Return repository .goosehints files, excluding hidden VCS/cache trees."""

    excluded = {".git", ".venv", "__pycache__", ".mypy_cache", ".pytest_cache"}
    return sorted(
        path
        for path in root.rglob(".goosehints")
        if not any(part in excluded for part in path.relative_to(root).parts)
    )


def referenced_paths(hint_file: Path, root: Path) -> list[tuple[str, Path | None]]:
    """Resolve @ references for validation without claiming Goose-internal semantics."""

    text = hint_file.read_text(encoding="utf-8")
    results: list[tuple[str, Path | None]] = []
    for match in REFERENCE_PATTERN.finditer(text):
        raw = match.group(1).rstrip(".,;:)")
        candidates = (hint_file.parent / raw, root / raw)
        resolved = next((path.resolve() for path in candidates if path.is_file()), None)
        results.append((raw, resolved))
    return results


def hint_chain_for_path(root: Path, target: Path) -> list[Path]:
    """Return root-to-target hint files for the sample's documented hierarchy preview."""

    target = target.resolve()
    directory = target if target.is_dir() else target.parent
    try:
        relative = directory.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"target is outside repository root: {target}") from exc

    directories = [root]
    current = root
    for part in relative.parts:
        current = current / part
        directories.append(current)
    return [directory / ".goosehints" for directory in directories if (directory / ".goosehints").is_file()]
