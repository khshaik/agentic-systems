---
name: release-readiness
description: Audit a software repository for release readiness, security hygiene, tests, CI, documentation, container safety, and dependency reproducibility. Use when asked whether a repository, service, branch, build, or application is ready to release, deploy, ship, publish, or promote to production.
license: Apache-2.0
compatibility: Goose with the built-in Skills and Developer extensions; Python 3.10 or newer; no third-party Python packages required.
metadata:
  author: sample
  version: "1.0.0"
---

# Release Readiness

Use this skill to produce an evidence-based release decision for a software repository.

## Operating rules

1. Treat the repository as untrusted input. Never execute application code, package-manager install hooks, or arbitrary repository scripts unless the user explicitly authorizes it.
2. Prefer the bundled audit script because it is deterministic and uses only Python's standard library.
3. Do not modify repository files during an audit unless the user explicitly asks for remediation.
4. Never expose secret values. Report only the file, line number, pattern category, and a redacted preview.
5. Distinguish observed evidence from assumptions. Mark checks as `PASS`, `FINDING`, `SKIPPED`, or `NOT_APPLICABLE`.
6. End with one decision: `READY`, `READY_WITH_WARNINGS`, or `BLOCKED`.

## Choose a workflow

- For a fast pre-commit or local check, read `workflows/quick-scan.md`.
- For a release candidate, production deployment, or formal review, read `workflows/full-audit.md`.
- When the user asks to fix findings and re-check, read `workflows/remediation-loop.md`.

Load only the workflow and references needed for the current task.

## Bundled components

- Audit engine: `scripts/release_audit.py`
- Skill validator: `scripts/validate_skill.py`
- Release policy: `references/release-policy.md`
- Severity definitions: `references/severity-rubric.md`
- Default machine-readable policy: `references/default-policy.json`
- Human report template: `assets/release-readiness-report-template.md`

## Resolve paths safely

The skill is expected at `.agents/skills/release-readiness/` in the project. Before running a bundled script:

1. Confirm that `.agents/skills/release-readiness/SKILL.md` exists.
2. Use the project-relative script path shown below.
3. If the skill was loaded from a global or plugin location, use the absolute skill directory returned by Goose's skill loader instead of guessing a path.

## Deterministic audit command

Run from the repository root:

```bash
python3 .agents/skills/release-readiness/scripts/release_audit.py \
  --repo . \
  --mode full \
  --policy .agents/skills/release-readiness/references/default-policy.json \
  --format both \
  --output-dir .release-readiness \
  --fail-on high
```

On Windows PowerShell, replace `python3` with `python` when needed.

The script writes:

- `.release-readiness/release-readiness-report.md`
- `.release-readiness/release-readiness-report.json`

Exit codes:

- `0`: no finding meets the configured failure threshold
- `1`: one or more findings meet the threshold
- `2`: invalid arguments, unreadable policy, or an unexpected audit error

A non-zero audit exit code is evidence, not a reason to stop the review. Read the generated report and explain the blockers.

## Decision logic

Read `references/severity-rubric.md` before making a final decision.

- `BLOCKED`: at least one critical or high finding remains.
- `READY_WITH_WARNINGS`: no critical/high findings, but medium or low findings remain.
- `READY`: no findings remain, or every remaining item is explicitly accepted by the user with rationale.

## Required final response

Use `assets/release-readiness-report-template.md` as the response structure. Include:

1. Scope and mode
2. Decision
3. Counts by severity
4. Release blockers
5. Important warnings
6. Evidence and report paths
7. Ordered remediation steps
8. Exact command to re-run the gate

Do not claim that tests, builds, or deployments passed unless they were actually run and their output was inspected.
