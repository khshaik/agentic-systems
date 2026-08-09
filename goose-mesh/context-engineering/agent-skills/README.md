# Goose Agent Skills: Complete Working Sample

This repository is a complete, dependency-free example of a Goose **Agent Skill**. It demonstrates:

- reusable instructions in `SKILL.md`
- on-demand workflow files
- executable scripts
- reference material and machine-readable policy
- a report asset/template
- automatic discovery from a project repository
- explicit loading from Goose CLI
- deterministic local tests

The sample skill is named **`release-readiness`**. It audits a repository for release documentation, tests, CI, likely secrets, Docker non-root execution, dependency locks, and maintainability markers.

## Repository layout

```text
.
├── .agents/skills/release-readiness/
│   ├── SKILL.md
│   ├── workflows/
│   │   ├── quick-scan.md
│   │   ├── full-audit.md
│   │   └── remediation-loop.md
│   ├── scripts/
│   │   ├── release_audit.py
│   │   └── validate_skill.py
│   ├── references/
│   │   ├── release-policy.md
│   │   ├── severity-rubric.md
│   │   └── default-policy.json
│   └── assets/
│       └── release-readiness-report-template.md
├── sample-service/          # Small healthy repository used by the demo
├── tests/                   # Tests for the skill scripts
├── Makefile
└── README.md
```

## Prerequisites

- Python 3.10 or newer
- Goose CLI or Goose Desktop
- A configured Goose model provider for agent-driven use
- `make` is optional; every command also has a direct Python equivalent

The scripts use only the Python standard library. They do not install packages, execute the target application's code, or access the network.

## 1. Put the skill in a repository

Copy the `.agents` directory into the root of your repository:

```text
YOUR-REPOSITORY/
└── .agents/
    └── skills/
        └── release-readiness/
            └── SKILL.md
```

Run Goose from `YOUR-REPOSITORY`. Project-level skills are discovered from `.agents/skills/`.

## 2. Verify the sample locally

From this repository root:

```bash
make verify
```

Without `make`:

```bash
python3 .agents/skills/release-readiness/scripts/validate_skill.py \
  .agents/skills/release-readiness

python3 -m unittest discover -s tests -v

cd sample-service
python3 -m unittest discover -s tests -v
cd ..

python3 .agents/skills/release-readiness/scripts/release_audit.py \
  --repo sample-service \
  --mode full \
  --policy .agents/skills/release-readiness/references/default-policy.json \
  --format both \
  --output-dir out/demo \
  --fail-on none
```

Expected audit decision for `sample-service`: `READY`.

Generated files:

```text
out/demo/release-readiness-report.md
out/demo/release-readiness-report.json
```

## 3. Confirm Goose discovers the skill

Start in this repository root, then run:

```bash
goose --version
goose skills list
```

You should see `release-readiness` in the list. In an interactive Goose CLI session, you can also run:

```text
/skills
```

To explicitly load it:

```text
/skills release-readiness
```

If the skill does not appear, confirm:

1. the current directory is this repository root
2. the file is exactly `.agents/skills/release-readiness/SKILL.md`
3. the frontmatter name is `release-readiness`
4. the built-in Skills extension is enabled
5. you started a new Goose session after adding the skill

## 4. Run through Goose

### Explicit activation

Start Goose from this repository root:

```bash
goose
```

Then enter:

```text
Use the release-readiness skill. Run a full release audit of ./sample-service. Do not change any files. Save the reports under ./out/goose-full and give me a go/no-go decision with evidence.
```

### Automatic activation

The description is written with release-related trigger terms. This request should cause Goose to load the skill on demand:

```text
Is ./sample-service ready to release to production? Perform an evidence-based audit, do not modify files, and save the report under ./out/goose-auto.
```

### Quick workflow

```text
Use the release-readiness skill to do a quick pre-commit scan of this repository. Do not run project code and do not modify files.
```

### Remediation workflow

Use this on a repository that has findings:

```text
Use the release-readiness skill. Audit this repository, fix only the critical and high findings that can be corrected without credentials or organizational decisions, run relevant validation after each change, and show the before/after results. Do not commit or push.
```

## 5. Run the audit script directly on your repository

From your repository root after copying `.agents/`:

```bash
python3 .agents/skills/release-readiness/scripts/release_audit.py \
  --repo . \
  --mode full \
  --policy .agents/skills/release-readiness/references/default-policy.json \
  --format both \
  --output-dir .release-readiness \
  --fail-on high
```

The command returns:

- exit `0`: no finding at or above the selected threshold
- exit `1`: the threshold was reached; inspect the report
- exit `2`: invalid input or an audit error

Available thresholds:

```text
critical | high | medium | low | none
```

For a non-blocking exploratory run:

```bash
python3 .agents/skills/release-readiness/scripts/release_audit.py \
  --repo . --mode quick --format both \
  --output-dir .release-readiness --fail-on none
```

## 6. Customize the policy

Edit a copy of:

```text
.agents/skills/release-readiness/references/default-policy.json
```

Supported settings include:

- required files and their severity
- recognized CI paths
- recognized test directories
- excluded paths
- maximum scanned file size
- quick/full scan file limits

Example organization policy:

```json
{
  "required_files": [
    {
      "path": "README.md",
      "severity": "high",
      "message": "README.md is mandatory."
    },
    {
      "path": "SECURITY.md",
      "severity": "high",
      "message": "SECURITY.md is mandatory for production services."
    }
  ],
  "exclude_paths": [
    ".git",
    "node_modules",
    "vendor",
    "generated"
  ]
}
```

Run with the custom file:

```bash
python3 .agents/skills/release-readiness/scripts/release_audit.py \
  --repo . --policy ./release-policy.json \
  --mode full --format both \
  --output-dir .release-readiness --fail-on high
```

## 7. What “loaded on demand” means in this sample

At session startup, Goose needs only the skill's frontmatter `name` and `description` to know the skill exists. When a release-readiness request matches the description, Goose loads `SKILL.md`. The skill then directs Goose to load only the applicable workflow, policy/rubric, and report template. The audit script is executed only when the workflow requires it.

This creates three layers:

1. **Discovery:** `name` and `description`
2. **Activation:** the full `SKILL.md`
3. **Execution:** selected workflow/reference files and scripts

## Safety characteristics

- no third-party Python packages
- no network calls
- no dependency installation
- no target application execution
- conservative secret detection with redacted output
- excluded build/dependency directories
- configurable scan limits
- no file modification outside the chosen output directory

The static audit does not prove that tests, builds, CI runs, images, infrastructure, or deployments are healthy. The skill explicitly prevents Goose from claiming those checks passed unless they were actually performed.

## Official references

- Goose Agent Skills documentation: `https://block.github.io/goose/docs/guides/context-engineering/using-skills`
- Goose repository: `https://github.com/aaif-goose/goose`
- Agent Skills specification: `https://agentskills.io/specification`
