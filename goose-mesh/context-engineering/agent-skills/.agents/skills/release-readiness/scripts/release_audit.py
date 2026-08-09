#!/usr/bin/env python3
"""Dependency-free static release-readiness audit for software repositories."""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3, "critical": 4}
TEXT_SUFFIXES = {
    ".c", ".cc", ".conf", ".cpp", ".cs", ".env", ".go", ".h", ".hpp",
    ".ini", ".java", ".js", ".json", ".jsx", ".kt", ".kts", ".php",
    ".properties", ".py", ".rb", ".rs", ".sh", ".sql", ".toml", ".ts",
    ".tsx", ".txt", ".xml", ".yaml", ".yml",
}

DEFAULT_POLICY: dict[str, Any] = {
    "required_files": [
        {"path": "README.md", "severity": "high", "message": "Primary repository documentation is missing."},
        {"path": "LICENSE", "severity": "medium", "message": "No LICENSE file was found."},
        {"path": ".gitignore", "severity": "low", "message": "No .gitignore file was found."},
        {"path": "CHANGELOG.md", "severity": "medium", "message": "No CHANGELOG.md file was found."},
    ],
    "ci_candidates": [
        ".github/workflows", ".gitlab-ci.yml", "Jenkinsfile",
        "azure-pipelines.yml", ".circleci/config.yml",
    ],
    "test_directories": ["tests", "test", "spec"],
    "exclude_paths": [
        ".git", ".release-readiness", ".venv", "venv", "node_modules",
        "dist", "build", "target", "vendor", "__pycache__",
    ],
    "max_file_bytes": 1_048_576,
    "quick_scan_file_limit": 500,
    "full_scan_file_limit": 5_000,
}

SECRET_PATTERNS = [
    ("private-key", "critical", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("aws-access-key", "critical", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("github-token", "critical", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b")),
    ("generic-secret", "high", re.compile(
        r"(?i)\b(api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|password|passwd|secret)\b"
        r"\s*[:=]\s*[\"']?([^\s\"'#,;]{8,})"
    )),
]
PLACEHOLDER_WORDS = {
    "change-me", "changeme", "dummy", "example", "placeholder", "replace-me",
    "replace_me", "sample", "test", "your-api-key", "your_api_key", "your-secret",
    "your_secret", "xxxxx", "xxxxxxxx",
}

LOCKFILE_GROUPS = {
    "package.json": ["package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lock", "bun.lockb"],
    "pyproject.toml": ["poetry.lock", "uv.lock", "Pipfile.lock"],
    "Pipfile": ["Pipfile.lock"],
    "Gemfile": ["Gemfile.lock"],
    "Cargo.toml": ["Cargo.lock"],
    "composer.json": ["composer.lock"],
}

TEST_FILE_PATTERNS = [
    "test_*.py", "*_test.py", "*_test.go", "*.test.js", "*.test.ts",
    "*.spec.js", "*.spec.ts", "*Test.java", "*Tests.cs",
]


@dataclass(frozen=True)
class Finding:
    id: str
    severity: str
    category: str
    message: str
    path: str | None = None
    line: int | None = None
    evidence: str | None = None
    recommendation: str | None = None


@dataclass
class AuditResult:
    repository: str
    mode: str
    generated_at: str
    scanned_files: int
    truncated: bool
    findings: list[Finding]
    checks: dict[str, str]

    def counts(self) -> dict[str, int]:
        counts = {key: 0 for key in ("critical", "high", "medium", "low")}
        for finding in self.findings:
            counts[finding.severity] += 1
        return counts

    def decision(self) -> str:
        counts = self.counts()
        if counts["critical"] or counts["high"]:
            return "BLOCKED"
        if counts["medium"] or counts["low"]:
            return "READY_WITH_WARNINGS"
        return "READY"

    def to_dict(self) -> dict[str, Any]:
        return {
            "repository": self.repository,
            "mode": self.mode,
            "generated_at": self.generated_at,
            "scanned_files": self.scanned_files,
            "truncated": self.truncated,
            "decision": self.decision(),
            "counts": self.counts(),
            "checks": self.checks,
            "findings": [asdict(finding) for finding in self.findings],
        }


def merge_policy(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        merged[key] = value
    return merged


def load_policy(path: Path | None) -> dict[str, Any]:
    if path is None:
        return dict(DEFAULT_POLICY)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Unable to read policy {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Policy root must be a JSON object")
    return merge_policy(DEFAULT_POLICY, data)


def normalize_rel(path: Path) -> str:
    return path.as_posix().lstrip("./")


def is_excluded(rel_path: str, exclude_paths: Iterable[str]) -> bool:
    parts = Path(rel_path).parts
    for excluded in exclude_paths:
        excluded = excluded.strip("/")
        if not excluded:
            continue
        if excluded in parts or rel_path == excluded or rel_path.startswith(excluded + "/"):
            return True
        if fnmatch.fnmatch(rel_path, excluded):
            return True
    return False


def iter_candidate_files(repo: Path, policy: dict[str, Any], mode: str) -> tuple[list[Path], bool]:
    limit_key = "quick_scan_file_limit" if mode == "quick" else "full_scan_file_limit"
    limit = int(policy.get(limit_key, 500 if mode == "quick" else 5000))
    exclude_paths = policy.get("exclude_paths", [])
    files: list[Path] = []
    truncated = False
    for current_root, dirnames, filenames in os.walk(repo):
        current = Path(current_root)
        rel_dir = normalize_rel(current.relative_to(repo)) if current != repo else ""
        dirnames[:] = sorted(
            d for d in dirnames
            if not is_excluded(normalize_rel(Path(rel_dir) / d), exclude_paths)
        )
        for filename in sorted(filenames):
            path = current / filename
            rel = normalize_rel(path.relative_to(repo))
            if is_excluded(rel, exclude_paths):
                continue
            files.append(path)
            if len(files) >= limit:
                truncated = True
                return files, truncated
    return files, truncated


def finding_id(category: str, number: int) -> str:
    prefix = {
        "secret": "SEC", "required-file": "DOC", "tests": "TST", "ci": "CIC",
        "container": "CTR", "dependency": "DEP", "maintainability": "MNT",
        "scan": "SCN",
    }.get(category, "FND")
    return f"{prefix}-{number:03d}"


def is_placeholder(value: str) -> bool:
    normalized = value.strip().strip("\"'").lower()
    if normalized in PLACEHOLDER_WORDS:
        return True
    if any(word in normalized for word in ("placeholder", "example", "your_", "your-", "change_me", "change-me")):
        return True
    if len(set(normalized)) <= 2:
        return True
    return False


def redact(value: str) -> str:
    value = value.strip().strip("\"'")
    if len(value) <= 6:
        return "<redacted>"
    return f"{value[:3]}…{value[-2:]} ({len(value)} chars)"


def check_required_files(repo: Path, policy: dict[str, Any], findings: list[Finding]) -> str:
    missing = 0
    for rule in policy.get("required_files", []):
        rel = str(rule.get("path", "")).strip()
        if not rel:
            continue
        if not (repo / rel).exists():
            missing += 1
            findings.append(Finding(
                id=finding_id("required-file", len(findings) + 1),
                severity=str(rule.get("severity", "medium")).lower(),
                category="required-file",
                message=str(rule.get("message", f"Required path {rel} is missing.")),
                path=rel,
                recommendation=f"Add and maintain {rel} before release.",
            ))
    return "PASS" if missing == 0 else "FINDING"


def check_tests(repo: Path, files: list[Path], policy: dict[str, Any], findings: list[Finding]) -> str:
    has_test_dir = any((repo / d).is_dir() for d in policy.get("test_directories", []))
    has_test_file = any(
        any(fnmatch.fnmatch(path.name, pattern) for pattern in TEST_FILE_PATTERNS)
        for path in files
    )
    if has_test_dir or has_test_file:
        return "PASS"
    findings.append(Finding(
        id=finding_id("tests", len(findings) + 1),
        severity="high",
        category="tests",
        message="No recognizable test directory or test files were found.",
        recommendation="Add automated tests and document how to run them.",
    ))
    return "FINDING"


def check_ci(repo: Path, policy: dict[str, Any], findings: list[Finding]) -> str:
    for candidate in policy.get("ci_candidates", []):
        path = repo / candidate
        if path.is_file():
            return "PASS"
        if path.is_dir() and any(child.is_file() for child in path.rglob("*")):
            return "PASS"
    findings.append(Finding(
        id=finding_id("ci", len(findings) + 1),
        severity="high",
        category="ci",
        message="No recognized CI workflow definition was found.",
        recommendation="Add a CI workflow that runs the documented validation and test commands.",
    ))
    return "FINDING"


def is_text_candidate(path: Path, max_bytes: int) -> bool:
    try:
        if path.stat().st_size > max_bytes:
            return False
    except OSError:
        return False
    if path.name in {"Dockerfile", "Jenkinsfile", "Makefile", "Gemfile", "Pipfile"}:
        return True
    return path.suffix.lower() in TEXT_SUFFIXES


def check_secrets(repo: Path, files: list[Path], policy: dict[str, Any], findings: list[Finding]) -> str:
    initial = len(findings)
    max_bytes = int(policy.get("max_file_bytes", 1_048_576))
    for path in files:
        rel = normalize_rel(path.relative_to(repo))
        lower_name = path.name.lower()
        if lower_name == ".env" or (lower_name.startswith(".env.") and not any(x in lower_name for x in ("example", "sample", "template"))):
            findings.append(Finding(
                id=finding_id("secret", len(findings) + 1),
                severity="high",
                category="secret",
                message="A committed environment file may contain credentials.",
                path=rel,
                recommendation="Remove it from version control, rotate exposed credentials, and keep only a sanitized example file.",
            ))
        if not is_text_candidate(path, max_bytes):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            for pattern_name, severity, regex in SECRET_PATTERNS:
                match = regex.search(line)
                if not match:
                    continue
                matched_value = match.group(2) if pattern_name == "generic-secret" and match.lastindex and match.lastindex >= 2 else match.group(0)
                if pattern_name == "generic-secret" and (is_placeholder(matched_value) or any(x in lower_name for x in ("example", "sample", "template"))):
                    continue
                findings.append(Finding(
                    id=finding_id("secret", len(findings) + 1),
                    severity=severity,
                    category="secret",
                    message=f"Potential {pattern_name.replace('-', ' ')} detected.",
                    path=rel,
                    line=line_number,
                    evidence=redact(matched_value),
                    recommendation="Confirm the match, remove the secret from history, and rotate/revoke it if real.",
                ))
                break
    return "PASS" if len(findings) == initial else "FINDING"


def dockerfiles(files: list[Path]) -> list[Path]:
    return [path for path in files if path.name == "Dockerfile" or path.name.startswith("Dockerfile.")]


def check_containers(repo: Path, files: list[Path], findings: list[Finding]) -> str:
    candidates = dockerfiles(files)
    if not candidates:
        return "NOT_APPLICABLE"
    found_issue = False
    user_re = re.compile(r"^\s*USER\s+(.+?)\s*$", re.IGNORECASE)
    for path in candidates:
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        users = [m.group(1).strip() for line in lines if (m := user_re.match(line))]
        safe = bool(users) and users[-1].lower() not in {"root", "0", "0:0"}
        if not safe:
            found_issue = True
            rel = normalize_rel(path.relative_to(repo))
            findings.append(Finding(
                id=finding_id("container", len(findings) + 1),
                severity="high",
                category="container",
                message="Docker image has no confirmed non-root final USER.",
                path=rel,
                recommendation="Create an unprivileged runtime user and make it the final USER in the Dockerfile.",
            ))
    return "FINDING" if found_issue else "PASS"


def check_dependencies(repo: Path, findings: list[Finding], mode: str) -> str:
    if mode == "quick":
        return "SKIPPED"
    found_issue = False
    for manifest, locks in LOCKFILE_GROUPS.items():
        if not (repo / manifest).exists():
            continue
        if not any((repo / lock).exists() for lock in locks):
            found_issue = True
            findings.append(Finding(
                id=finding_id("dependency", len(findings) + 1),
                severity="medium",
                category="dependency",
                message=f"Dependency manifest {manifest} has no recognized lock file.",
                path=manifest,
                recommendation=f"Commit an ecosystem-appropriate lock file when reproducible application builds require it ({', '.join(locks)}).",
            ))
    return "FINDING" if found_issue else "PASS"


def check_todos(repo: Path, files: list[Path], policy: dict[str, Any], findings: list[Finding], mode: str) -> str:
    if mode == "quick":
        return "SKIPPED"
    max_bytes = int(policy.get("max_file_bytes", 1_048_576))
    matches: list[tuple[str, int, str]] = []
    todo_re = re.compile(r"\b(TODO|FIXME)\b", re.IGNORECASE)
    for path in files:
        if not is_text_candidate(path, max_bytes):
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for line_number, line in enumerate(lines, start=1):
            if todo_re.search(line):
                matches.append((normalize_rel(path.relative_to(repo)), line_number, line.strip()[:120]))
                if len(matches) >= 25:
                    break
        if len(matches) >= 25:
            break
    if not matches:
        return "PASS"
    preview = "; ".join(f"{p}:{line}" for p, line, _ in matches[:5])
    findings.append(Finding(
        id=finding_id("maintainability", len(findings) + 1),
        severity="low",
        category="maintainability",
        message=f"Found {len(matches)} TODO/FIXME marker(s) in scanned files.",
        evidence=preview,
        recommendation="Review unresolved markers and convert release-relevant work into tracked issues.",
    ))
    return "FINDING"


def audit(repo: Path, policy: dict[str, Any], mode: str) -> AuditResult:
    repo = repo.resolve()
    if not repo.is_dir():
        raise ValueError(f"Repository path is not a directory: {repo}")
    files, truncated = iter_candidate_files(repo, policy, mode)
    findings: list[Finding] = []
    checks: dict[str, str] = {}
    checks["required_files"] = check_required_files(repo, policy, findings)
    checks["tests_present"] = check_tests(repo, files, policy, findings)
    checks["ci_present"] = check_ci(repo, policy, findings)
    checks["secret_hygiene"] = check_secrets(repo, files, policy, findings)
    checks["container_user"] = check_containers(repo, files, findings)
    checks["dependency_locking"] = check_dependencies(repo, findings, mode)
    checks["todo_markers"] = check_todos(repo, files, policy, findings, mode)
    if truncated:
        findings.append(Finding(
            id=finding_id("scan", len(findings) + 1),
            severity="medium",
            category="scan",
            message="File scan reached the configured limit; results may be incomplete.",
            evidence=f"Scanned {len(files)} files.",
            recommendation="Increase the policy file limit and re-run the audit.",
        ))
    findings.sort(key=lambda item: (-SEVERITY_RANK[item.severity], item.category, item.path or "", item.line or 0))
    return AuditResult(
        repository=str(repo),
        mode=mode,
        generated_at=datetime.now(timezone.utc).isoformat(),
        scanned_files=len(files),
        truncated=truncated,
        findings=findings,
        checks=checks,
    )


def markdown_report(result: AuditResult) -> str:
    counts = result.counts()
    lines = [
        "# Release Readiness Audit",
        "",
        f"- **Repository:** `{result.repository}`",
        f"- **Mode:** `{result.mode}`",
        f"- **Generated:** `{result.generated_at}`",
        f"- **Files scanned:** `{result.scanned_files}`",
        f"- **Decision:** **{result.decision()}**",
        "",
        "## Summary",
        "",
        "| Severity | Count |",
        "|---|---:|",
        f"| Critical | {counts['critical']} |",
        f"| High | {counts['high']} |",
        f"| Medium | {counts['medium']} |",
        f"| Low | {counts['low']} |",
        "",
        "## Checks",
        "",
        "| Check | Status |",
        "|---|---|",
    ]
    for name, status in result.checks.items():
        lines.append(f"| `{name}` | {status} |")
    lines.extend(["", "## Findings", ""])
    if not result.findings:
        lines.append("No findings.")
    else:
        lines.extend([
            "| ID | Severity | Category | Location | Finding | Evidence | Recommendation |",
            "|---|---|---|---|---|---|---|",
        ])
        for item in result.findings:
            location = item.path or "—"
            if item.line is not None:
                location += f":{item.line}"
            values = [
                item.id, item.severity.upper(), item.category, location, item.message,
                item.evidence or "—", item.recommendation or "—",
            ]
            escaped = [value.replace("|", "\\|").replace("\n", " ") for value in values]
            lines.append("| " + " | ".join(escaped) + " |")
    lines.extend([
        "",
        "## Scope note",
        "",
        "This is a static repository audit. It does not install dependencies, run tests, build artifacts, query CI, scan images, or deploy software.",
        "",
    ])
    return "\n".join(lines)


def should_fail(result: AuditResult, threshold: str) -> bool:
    if threshold == "none":
        return False
    minimum = SEVERITY_RANK[threshold]
    return any(SEVERITY_RANK[item.severity] >= minimum for item in result.findings)


def write_reports(result: AuditResult, fmt: str, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    if fmt in {"markdown", "both"}:
        path = output_dir / "release-readiness-report.md"
        path.write_text(markdown_report(result), encoding="utf-8")
        written.append(path)
    if fmt in {"json", "both"}:
        path = output_dir / "release-readiness-report.json"
        path.write_text(json.dumps(result.to_dict(), indent=2) + "\n", encoding="utf-8")
        written.append(path)
    return written


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("."), help="Repository directory to audit")
    parser.add_argument("--mode", choices=("quick", "full"), default="full")
    parser.add_argument("--policy", type=Path, help="Optional JSON policy overlay")
    parser.add_argument("--format", choices=("markdown", "json", "both"), default="both")
    parser.add_argument("--output-dir", type=Path, default=Path(".release-readiness"))
    parser.add_argument("--fail-on", choices=("critical", "high", "medium", "low", "none"), default="high")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        policy = load_policy(args.policy)
        result = audit(args.repo, policy, args.mode)
        written = write_reports(result, args.format, args.output_dir)
    except (ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"Decision: {result.decision()}")
    print("Findings: " + ", ".join(f"{k}={v}" for k, v in result.counts().items()))
    for path in written:
        print(f"Wrote: {path}")
    return 1 if should_fail(result, args.fail_on) else 0


if __name__ == "__main__":
    raise SystemExit(main())
