# Full Audit Workflow

Use for release candidates, production promotion, formal engineering reviews, and go/no-go decisions.

## Steps

1. Establish scope:
   - repository path
   - intended environment
   - release identifier when supplied
   - whether remediation is allowed
2. Read `references/release-policy.md` and `references/severity-rubric.md`.
3. Run the deterministic audit in full mode:

```bash
python3 .agents/skills/release-readiness/scripts/release_audit.py \
  --repo <repo-path> \
  --mode full \
  --policy .agents/skills/release-readiness/references/default-policy.json \
  --format both \
  --output-dir <repo-path>/.release-readiness \
  --fail-on high
```

4. Inspect the generated Markdown and JSON reports.
5. Inspect relevant evidence files for every critical/high finding. Do not reveal secret values.
6. When safe and authorized, run the repository's documented tests and build commands. Do not infer commands solely from filenames when the repository documentation gives explicit commands.
7. Record commands, exit codes, and any skipped checks.
8. Classify the release using the decision logic in `SKILL.md`.
9. Produce the response using `assets/release-readiness-report-template.md`.

## Evidence rules

- A file's existence is evidence only for existence, not correctness.
- A CI workflow's existence is not evidence that the latest run passed.
- Test files are not evidence that tests pass.
- A Docker `USER` directive is evidence of a non-root default only when its value is not `root` or `0`.
- A redacted secret-pattern match is a suspected exposure until manually confirmed, but it remains a blocker because false negatives are more dangerous than false positives.
