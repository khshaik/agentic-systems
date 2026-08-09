# Complete working Goose `.goosehints` sample

This repository is a drop-in, runnable demonstration of Goose project hints:

> **`.goosehints`: project context, conventions, and preferences loaded automatically at session start.**

The sample uses a dependency-free Python order-pricing service so the instructions in the hints are concrete and verifiable rather than decorative.

## What the sample covers

| Capability | Where it is demonstrated |
|---|---|
| Project context loaded at session start | Root `.goosehints` |
| Coding conventions | Root and `src/order_service/.goosehints` |
| Collaboration preferences | Root `.goosehints` |
| Immediate context using an `@` file reference | `@docs/domain-rules.md` in the root file |
| Optional documents Goose should inspect when needed | Plain references to `README.md` and `docs/*.md` |
| Hierarchical/nested hints | Package, API, tests, scripts, and docs directories |
| More-specific rules supplementing project rules | `src/order_service/api/.goosehints` |
| Hints validation | `scripts/validate_goosehints.py` |
| Hierarchy preview | `scripts/show_effective_hints.py` |
| Runnable application and tests | `src/` and `tests/` |
| Reusable templates | `templates/` |

## Official Goose behavior represented here

According to the current Goose documentation:

- `.goosehints` is a plain text file containing natural-language project context and instructions.
- The Developer extension is required for hints; it is enabled by default in current Goose builds.
- A local `.goosehints` can live at the project root and in nested directories.
- At session start, Goose loads applicable context files from the working-directory hierarchy up to the Git repository root.
- When Goose later accesses a nested directory, it can discover that directory's additional hints.
- Global hints at `~/.config/goose/.goosehints` and local hints can be used together; local instructions take priority when they conflict.
- `@path/to/file` places that file's content in immediate context. A plain file reference tells Goose to inspect it when needed.
- Hints are added to the system prompt, so concise files reduce token use.
- Restart the session after editing `.goosehints` so the updated startup context is loaded.
- Goose currently looks for `.goosehints` and `AGENTS.md` by default; `CONTEXT_FILE_NAMES` can configure other filenames.

Official guide: <https://goose-docs.ai/docs/guides/context-engineering/using-goosehints/>

Official extensions guide: <https://goose-docs.ai/docs/getting-started/using-extensions/>

The documentation was checked on **31 July 2026**. Goose evolves quickly, so verify the official guide when adopting the sample in a long-lived repository.

## Repository layout

```text
.
├── .goosehints                         # Project-wide startup context
├── README.md
├── Makefile
├── docs/
│   ├── .goosehints                     # Documentation-specific conventions
│   ├── architecture.md
│   ├── domain-rules.md                  # Loaded immediately by root @ reference
│   └── engineering-standards.md
├── examples/
│   └── prompts.md                       # Goose verification prompts
├── scripts/
│   ├── .goosehints                     # Script-specific conventions
│   ├── hints_common.py
│   ├── preflight.py
│   ├── show_effective_hints.py
│   └── validate_goosehints.py
├── src/order_service/
│   ├── .goosehints                     # Domain-package conventions
│   ├── domain.py
│   ├── service.py
│   ├── cli.py
│   └── api/
│       ├── .goosehints                 # Most-specific API conventions
│       └── handlers.py
├── tests/
│   ├── .goosehints                     # Test conventions
│   ├── test_hint_tools.py
│   └── test_service.py
└── templates/
    ├── root.goosehints.example
    └── nested.goosehints.example
```

## Prerequisites

For repository validation and the runnable sample:

- Python 3.11 or newer
- GNU Make, or run the underlying Python commands directly
- Git is recommended because Goose's nested-hints behavior is repository-aware

For an actual Goose session:

- Goose CLI or Goose Desktop
- A configured LLM provider
- The built-in Developer extension enabled

Install the current Goose CLI using the command published by the Goose project:

```bash
curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh | bash
```

Configure a provider using the official quickstart, then confirm the CLI is available:

```bash
goose --version
```

## Run the sample

Extract the archive and enter the repository:

```bash
unzip goose-goosehints-complete-sample.zip
cd goose-goosehints-complete-sample
```

If the directory is not already inside a Git repository, initialize one. This is recommended for demonstrating the documented repository hierarchy:

```bash
git init
```

Run every local check:

```bash
make verify
```

The command performs these steps:

1. Checks Python, the repository root, the root `.goosehints`, and optionally the Goose executable.
2. Validates all `.goosehints` files and every `@` reference.
3. Runs the application and hint-tooling tests.
4. Runs the sample CLI calculation.

Expected final application output:

```json
{
  "discount_cents": 1250,
  "ok": true,
  "subtotal_cents": 12500,
  "total_cents": 11250
}
```

Commands can also be run individually:

```bash
make validate-hints
make test
make run
make show-api-context
```

Without Make:

```bash
PYTHONPATH=src:scripts python3 scripts/preflight.py
PYTHONPATH=src:scripts python3 scripts/validate_goosehints.py
PYTHONPATH=src:scripts python3 -m unittest discover -s tests -v
PYTHONPATH=src:scripts python3 -m order_service.cli
```

## Start Goose correctly

The working directory matters. Start a **new** Goose session from this repository root:

```bash
cd goose-goosehints-complete-sample
goose
```

The Developer extension is enabled by default in current Goose builds. To request it explicitly for the session, use:

```bash
goose session --with-builtin developer
```

For Goose Desktop, open this repository as the active directory, confirm the Developer extension is enabled under Extensions, and start a new session.

## Verify automatic root context

Paste this as the first request in the new session:

```text
Before changing anything, summarize this project's purpose, canonical
verification command, money representation, collaboration preferences, and
definition of done. Cite the project files that establish each answer.
```

The answer should be consistent with the root `.goosehints`. It should also know the discount rule from `docs/domain-rules.md`, because that file is pulled into immediate context by this line:

```text
@docs/domain-rules.md
```

A useful follow-up is:

```text
What is the maximum allowed discount, and how are fractional discount cents rounded?
Do not inspect source code unless the answer is absent from startup context.
```

The expected answer is a maximum of 50%, with discount cents rounded down by integer division.

## Verify nested hints

Goose loads the root hints first. More-specific nested hints become relevant when it accesses files in their directory.

Ask:

```text
Inspect src/order_service/api/handlers.py. Before proposing changes, list the
project-wide, order-service, and API-specific instructions that apply. Do not
edit files.
```

The applicable hierarchy is:

```text
.goosehints
src/order_service/.goosehints
src/order_service/api/.goosehints
```

Preview the same file chain locally with the sample helper:

```bash
python3 scripts/show_effective_hints.py src/order_service/api/handlers.py
```

To print the hint text too:

```bash
python3 scripts/show_effective_hints.py src/order_service/api/handlers.py --content
```

**Important:** this helper is not part of Goose and does not emulate Goose's complete prompt construction. It provides a deterministic repository-level preview of the documented root-to-directory hierarchy.

## Use Goose on a working implementation task

A safe exercise is:

```text
Add a new test proving that a 50% discount is accepted and a 51% discount is
rejected. Follow all automatically loaded project and test-directory
instructions. Make only the required change, run the required verification,
and report the exact commands and results.
```

The hints should guide Goose to:

- inspect the domain implementation and tests first;
- use `unittest` rather than adding a dependency;
- preserve integer-cent arithmetic;
- make a narrow change;
- run `make test` and `make validate-hints`;
- report evidence rather than merely claiming success.

More ready-to-paste prompts are in [`examples/prompts.md`](examples/prompts.md).

## Understand the root `.goosehints`

The file deliberately contains five categories.

### 1. Project context

It tells Goose what the repository is, the runtime, and the business purpose. This prevents the user from repeating basic context in every session.

### 2. Canonical commands

It gives one authoritative build/test/validation path. This helps prevent invented commands and inconsistent verification.

### 3. Engineering conventions

It states rules such as integer cents for money, no unapproved dependencies, type hints, pure domain logic, and required tests.

### 4. Collaboration preferences

It defines how Goose should work with the user: inspect before editing, state the likely scope, avoid unrelated refactors, ask before risky changes, and provide evidence afterward.

### 5. Definition of done

It explains what must be true before Goose calls work complete.

## `@` references versus plain references

The root file demonstrates both official patterns.

Immediate inclusion:

```text
@docs/domain-rules.md
```

Use this for small, essential context that Goose should receive immediately. It consumes context tokens every turn.

On-demand instruction:

```text
Read docs/architecture.md when a task changes module boundaries or data flow.
```

Use this for larger or less frequently needed material. Goose is instructed to inspect it when the task requires it, rather than automatically injecting all content.

Keep `@` references small and stable. Do not use them to include entire codebases, large logs, generated files, or secrets.

## Copy this into an existing repository

The minimum installation is one file:

```bash
cp .goosehints /path/to/your/repository/.goosehints
```

For the complete pattern:

1. Copy `templates/root.goosehints.example` to the target repository as `.goosehints`.
2. Replace every placeholder with real project facts and executable commands.
3. Add small reference documents under `docs/` only where useful.
4. Add nested `.goosehints` files to modules whose conventions genuinely differ.
5. Copy `scripts/hints_common.py` and `scripts/validate_goosehints.py` if CI validation is desired.
6. Run the validator.
7. Start a new Goose session from the repository root.

Example:

```bash
cp templates/root.goosehints.example /path/to/repo/.goosehints
cp templates/nested.goosehints.example /path/to/repo/src/payments/.goosehints
```

Do not copy the sample's Python-specific rules unchanged into a non-Python repository. The value comes from precise, true, repository-specific instructions.

## Optional global hints

Global hints apply across projects and live here:

```text
~/.config/goose/.goosehints
```

Good global preferences are personal and broadly applicable, for example:

```text
Prefer concise explanations followed by executable examples.
Never claim a command passed unless it was run successfully.
Ask before deleting files or adding a paid external service.
```

Keep project architecture, project commands, and domain rules local to the repository. When global and local instructions conflict, the official documentation states that local hints take priority.

## Optional custom context filenames

Current Goose supports the `CONTEXT_FILE_NAMES` environment variable as a JSON array. For example:

```bash
export CONTEXT_FILE_NAMES='["AGENTS.md", ".goosehints", "CLAUDE.md"]'
goose
```

Do not accidentally remove `.goosehints` from this array when expecting this sample to load.

## Validation in CI

The included validator uses only the standard library. It checks:

- a root `.goosehints` exists;
- every hints file is non-empty;
- every `@` reference points to an existing file;
- hints do not contain NUL bytes;
- very long hints generate a token-usage warning.

Run it in any CI system:

```bash
PYTHONPATH=scripts python3 scripts/validate_goosehints.py
```

The validator does **not** decide whether natural-language instructions are good, nor does it reproduce Goose internals. Human review is still required.

## Troubleshooting

### Goose does not appear to know the root hints

- Confirm the file is named exactly `.goosehints`.
- Confirm Goose was started from this repository or a directory inside the same Git hierarchy.
- Start a new session after changing the file.
- Confirm the Developer extension is enabled.
- Check whether `CONTEXT_FILE_NAMES` has been customized and excludes `.goosehints`.
- Run `make validate-hints` to catch missing files or broken references.

### Nested instructions are not reflected immediately

Nested hints are discovered as Goose accesses files in those nested directories. Ask Goose to inspect a file in the target directory, or start the session from that directory when appropriate.

### An `@` reference is missing

Run:

```bash
make validate-hints
```

Use repository-relative, version-controlled files and avoid machine-specific absolute paths.

### Goose wants to perform risky changes

Hints guide model behavior; they are not a security boundary. Configure Goose permission modes and tool permissions for actual enforcement. Keep secrets outside accessible project files.

### The sample works without Goose but a live session does not

`make verify` validates the repository sample, not your model provider or Goose configuration. Run:

```bash
goose --version
goose configure
```

Then confirm a provider and the Developer extension are enabled.

## Security guidance

- Never store API keys, passwords, tokens, customer data, private endpoints, or production credentials in `.goosehints`.
- Treat every `@` reference as content added to the model context.
- Keep generated and sensitive directories outside the context references.
- Use Goose permissions for enforcement; do not rely only on natural-language prohibitions.
- Review changes and command output before committing.

## Scope of verification

This repository's Python application, validator, hierarchy-preview tool, and automated tests can be run without a model provider. A true end-to-end Goose check additionally requires your local Goose installation and configured provider. The repository therefore separates deterministic local verification from the prompts used to exercise Goose itself.

## License

MIT. See [`LICENSE`](LICENSE).
