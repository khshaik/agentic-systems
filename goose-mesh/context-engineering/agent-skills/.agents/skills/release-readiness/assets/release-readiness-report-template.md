# Release Readiness Report

## Scope

- Repository: `<path>`
- Audit mode: `<quick|full>`
- Release/environment: `<value or not supplied>`

## Decision: `<READY|READY_WITH_WARNINGS|BLOCKED>`

**Reason:** `<one-sentence evidence-based reason>`

## Findings summary

| Severity | Count |
|---|---:|
| Critical | `<n>` |
| High | `<n>` |
| Medium | `<n>` |
| Low | `<n>` |

## Release blockers

`<Critical and high findings, or "None">`

## Important warnings

`<Medium and low findings, or "None">`

## Verification performed

| Check or command | Result | Evidence |
|---|---|---|
| Static audit | `<exit code>` | `<report path>` |
| Tests | `<pass/fail/skipped>` | `<command/output>` |
| Build | `<pass/fail/skipped>` | `<command/output>` |

## Remediation order

1. `<highest-risk action>`
2. `<next action>`
3. `<next action>`

## Re-run command

```bash
<exact command>
```
