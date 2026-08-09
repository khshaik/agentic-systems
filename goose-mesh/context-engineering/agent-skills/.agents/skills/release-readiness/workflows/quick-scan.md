# Quick Scan Workflow

Use for local checks, pull-request preparation, and fast feedback.

## Steps

1. Confirm the repository path and state that this workflow does not run the project's tests or build.
2. Run the audit engine in quick mode:

```bash
python3 .agents/skills/release-readiness/scripts/release_audit.py \
  --repo <repo-path> \
  --mode quick \
  --policy .agents/skills/release-readiness/references/default-policy.json \
  --format both \
  --output-dir <repo-path>/.release-readiness \
  --fail-on high
```

3. Read both generated reports.
4. Prioritize exposed secrets, missing release documentation, absent tests, absent CI, and unsafe Docker defaults.
5. Return a concise decision and the three most important next actions.

## Quick-mode boundaries

Quick mode limits content scanning and skips deeper dependency reproducibility checks. It is not a substitute for the full workflow before production deployment.
