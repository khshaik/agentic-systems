# Remediation Loop Workflow

Use only when the user explicitly asks Goose to fix findings.

## Loop

1. Start from the latest JSON report or run a full audit if no current report exists.
2. Work in severity order: critical, high, medium, low.
3. Before each change:
   - identify the exact finding
   - explain the intended change
   - preserve existing project conventions
4. Make the smallest safe change.
5. Run the narrowest relevant validation for that change.
6. Re-run the deterministic audit after each critical/high fix, or after a small related batch.
7. Never fabricate secrets, production credentials, approvals, CI results, release notes, or legal text.
8. Stop and request user-supplied information when a valid fix requires organization-specific facts.
9. Finish with a full audit and compare before/after counts.

## Changes that require explicit confirmation

- deleting files or history
- rotating or revoking credentials
- changing CI/CD deployment behavior
- changing licensing
- publishing artifacts
- pushing commits or tags
- deploying to any environment
