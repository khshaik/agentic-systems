#!/usr/bin/env python3
"""Dependency-free static repository health check."""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


EXCLUDED = {".git", ".venv", "venv", "node_modules", "dist", "build", "__pycache__"}
TEST_PATTERNS = ("test_*.py", "*_test.py", "*.test.js", "*.test.ts", "*.spec.js", "*.spec.ts")
SECRET_RE = re.compile(
    r"(?i)\b(api[_-]?key|access[_-]?token|auth[_-]?token|password|passwd|secret)\b\s*[:=]\s*[\"']?([^\s\"'#,;]{8,})"
)
PLACEHOLDERS = ("example", "sample", "placeholder", "change-me", "your_", "your-")


@dataclass(frozen=True)
class Finding:
    severity: str
    category: str
    message: str
    path: str | None = None
    line: int | None = None


def candidate_files(repo: Path) -> list[Path]:
    return sorted(
        path
        for path in repo.rglob("*")
        if path.is_file() and not any(part in EXCLUDED for part in path.relative_to(repo).parts)
    )


def has_tests(repo: Path, files: list[Path]) -> bool:
    return (repo / "tests").is_dir() or any(
        any(fnmatch.fnmatch(path.name, pattern) for pattern in TEST_PATTERNS) for path in files
    )


def has_ci(repo: Path) -> bool:
    candidates = (repo / ".github" / "workflows", repo / ".gitlab-ci.yml", repo / "Jenkinsfile")
    return any(path.is_file() or (path.is_dir() and any(path.iterdir())) for path in candidates)


def secret_findings(repo: Path, files: list[Path]) -> list[Finding]:
    findings: list[Finding] = []
    for path in files:
        relative = path.relative_to(repo).as_posix()
        lower_name = path.name.lower()
        if lower_name == ".env":
            findings.append(Finding("high", "secret", "committed .env file may contain credentials", relative))
        if path.stat().st_size > 1_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        for number, line in enumerate(text.splitlines(), start=1):
            match = SECRET_RE.search(line)
            if not match:
                continue
            value = match.group(2).lower()
            if any(word in value or word in lower_name for word in PLACEHOLDERS):
                continue
            findings.append(Finding("high", "secret", "potential hard-coded secret; value redacted", relative, number))
    return findings


def assess(repo: Path) -> dict[str, object]:
    repo = repo.resolve()
    if not repo.is_dir():
        raise ValueError(f"repository path is not a directory: {repo}")
    files = candidate_files(repo)
    findings: list[Finding] = []
    if not (repo / "README.md").is_file():
        findings.append(Finding("high", "documentation", "README.md is missing", "README.md"))
    if not (repo / "LICENSE").is_file():
        findings.append(Finding("medium", "governance", "LICENSE is missing", "LICENSE"))
    if not has_tests(repo, files):
        findings.append(Finding("high", "tests", "no recognizable tests were found"))
    if not has_ci(repo):
        findings.append(Finding("medium", "ci", "no recognized CI definition was found"))
    findings.extend(secret_findings(repo, files))
    decision = "BLOCKED" if any(item.severity == "high" for item in findings) else "NEEDS_ATTENTION" if findings else "HEALTHY"
    return {
        "repository": str(repo),
        "decision": decision,
        "files_scanned": len(files),
        "findings": [asdict(item) for item in findings],
        "not_performed": ["tests", "build", "CI status", "deployment"],
    }


def text_report(result: dict[str, object]) -> str:
    lines = [f"Decision: {result['decision']}", f"Repository: {result['repository']}", f"Files scanned: {result['files_scanned']}"]
    findings = result["findings"]
    if not findings:
        lines.append("Findings: none")
    else:
        lines.append("Findings:")
        for item in findings:  # type: ignore[union-attr]
            location = item.get("path") or "repository"
            if item.get("line"):
                location += f":{item['line']}"
            lines.append(f"- {item['severity'].upper()} {item['category']} at {location}: {item['message']}")
    lines.append("Not performed: tests, build, CI status, deployment")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        result = assess(args.repo)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2) if args.format == "json" else text_report(result))
    return 1 if result["decision"] == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
