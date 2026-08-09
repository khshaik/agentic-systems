# Severity Rubric

## Critical

Immediate credential compromise or material that can directly enable unauthorized access, such as a private key or high-confidence access token.

Release decision: `BLOCKED`.

## High

A release-blocking control gap with a credible path to production failure or security exposure, such as a committed `.env`, missing primary documentation, no test evidence, no CI definition, or a container running as root.

Release decision: `BLOCKED`.

## Medium

An important governance, traceability, or reproducibility gap that should be corrected before a normal release, such as missing license/change history or missing dependency lock data.

Release decision: `READY_WITH_WARNINGS` unless organizational policy promotes it to a blocker.

## Low

Maintainability or process debt that does not normally block release, such as unresolved TODO/FIXME markers.

Release decision: `READY_WITH_WARNINGS`.

## Accepted risk

Only the user or an authorized decision-maker can accept risk. Record:

- finding identifier
- approver supplied by the user
- rationale
- expiry or follow-up date when supplied

Do not invent approvals.
