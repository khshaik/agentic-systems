# Default Release Policy

This reference describes the human interpretation of the bundled default policy.

## Required repository evidence

- `README.md`: setup, test, and operational information
- `LICENSE`: distribution terms
- `.gitignore`: prevention of accidental generated-file commits
- `CHANGELOG.md`: user-visible release history
- a test directory or recognizable test files
- at least one recognized CI definition

## Security hygiene

A release is blocked by:

- private-key material
- high-confidence cloud or source-control tokens
- a committed `.env` file other than an example/template
- a likely hard-coded password, token, secret, or API key with a non-placeholder value

Never print a complete matched value. Redact it.

## Container hygiene

When a Dockerfile exists, it should define a non-root runtime user. A missing `USER` directive or `USER root` is a high-severity finding.

## Dependency reproducibility

Full mode looks for common dependency manifests and their corresponding lock files. Missing lock files are warnings because exact requirements vary by ecosystem.

## Scope boundaries

The bundled script performs static repository checks. It does not:

- install dependencies
- run tests
- build binaries or images
- query CI providers
- scan container images
- validate infrastructure credentials
- deploy anything

Goose may perform those actions only when the user explicitly requests them and the repository provides safe, documented commands.
