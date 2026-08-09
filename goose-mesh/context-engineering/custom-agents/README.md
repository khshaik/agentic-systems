# Goose Custom Agents — complete working sample

This repository is a drop-in, project-scoped example of Goose **Custom Agents**. It includes reusable specialist prompts, metadata, agent-to-agent delegation guidance, a dependency-free lifecycle CLI for creating/editing/importing/exporting agents, tests, and a small Python module that gives the agents something concrete to review.

## What this sample covers

| Capability | Where it is demonstrated |
|---|---|
| Specialized reusable agents | `.agents/agents/*.md` |
| Reusable prompts | Markdown body of each agent file |
| Agent metadata | YAML frontmatter: `name`, `description`, optional `model` |
| Project-scoped discovery | `.agents/agents/` under this repository |
| Load into current conversation | Prompt examples below |
| Isolated delegation | `code-reviewer`, `test-planner`, and `docs-writer` examples |
| Agent-to-agent coordination | `delivery-lead.md` |
| Create an agent | `scripts/agentctl.py create` |
| Edit an agent | `scripts/agentctl.py edit` |
| Import an agent | `scripts/agentctl.py import` |
| Export an agent | `scripts/agentctl.py export` |
| Install into another repository or globally | `scripts/agentctl.py install` |
| Validate agent files | `scripts/agentctl.py validate` |
| Automated verification | `make verify` |

The lifecycle helper is supplied by this sample repository; it is not presented as a built-in Goose CLI command. Goose consumes the Markdown files it creates.

## Repository structure

```text
.
├── .agents/
│   └── agents/
│       ├── code-reviewer.md
│       ├── delivery-lead.md
│       ├── docs-writer.md
│       └── test-planner.md
├── docs/
│   └── custom-agent-anatomy.md
├── examples/
│   └── importable/
│       └── security-reviewer.md
├── sample-inputs/
│   └── feature-request.md
├── scripts/
│   ├── agentctl.py
│   └── demo_lifecycle.sh
├── src/
│   └── discounts.py
├── tests/
│   ├── test_agentctl.py
│   └── test_discounts.py
├── Makefile
└── README.md
```

## Prerequisites

- Goose Desktop or Goose CLI with an LLM provider configured
- Python 3.10 or newer for the included lifecycle helper and tests
- `make` is convenient but optional

Install Goose CLI using the official installer if it is not already installed:

```bash
curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh | bash
```

Then configure your preferred provider through Goose.

## Quick start

Run these commands from the repository root:

```bash
python3 scripts/agentctl.py validate
python3 -m unittest discover -s tests -v
```

Or run both through `make`:

```bash
make verify
```

List the installed project agents:

```bash
python3 scripts/agentctl.py list
```

Start Goose from this repository so it can discover `.agents/agents/`:

```bash
goose
```

Inside the Goose chat, ask it to show discoverable sources:

```text
list available sources
```

## Use the custom agents

### Mention an agent

```text
@code-reviewer review src/discounts.py and tests/test_discounts.py. Do not edit files.
```

### Load an agent into the current conversation

```text
Load the test-planner agent, then create a risk-based test plan for sample-inputs/feature-request.md.
```

Loading adds the agent's instructions to the current conversation.

### Delegate to an isolated agent

```text
Delegate to docs-writer: inspect this repository and identify any README instructions that are inaccurate or unverified. Do not edit files.
```

Delegation runs the specialist separately and returns its result to the current conversation.

### Coordinate multiple specialists

```text
Use the delivery-lead agent. Evaluate sample-inputs/feature-request.md against the current code. Delegate code review, test planning, and documentation analysis to the appropriate custom agents. Do not change files. Return one READY, READY WITH CONDITIONS, or NOT READY decision with evidence.
```

Whether actual parallel delegation is available depends on the tools enabled in the current Goose session. The delivery lead is instructed to fall back to doing the necessary inspection itself rather than fabricate delegated results.

## Included agents

### `code-reviewer`

Finds correctness, security, maintainability, compatibility, and test-coverage risks. It defaults to review-only behavior.

### `test-planner`

Creates risk-based, prioritized test plans and can implement focused tests when explicitly asked.

### `docs-writer`

Creates task-oriented documentation using commands and behavior verified from the repository.

### `delivery-lead`

Coordinates the other specialists, reconciles their findings, verifies important claims, and returns one delivery decision.

## Agent file format

A Goose custom agent is a Markdown file with YAML frontmatter:

```markdown
---
name: example-agent
description: Explains when to select this specialist
model: optional-model-preference
---
You are a specialist. These are your reusable instructions...
```

- `name` is required.
- `description` is optional but strongly recommended for discovery.
- `model` is optional.
- The Markdown body contains the reusable prompt/instructions.

The checked-in agents intentionally omit `model`, so they use the provider/model already configured for the Goose session. This is the most portable default. To pin a model, add the frontmatter field manually or use the lifecycle CLI shown below.

## Create an agent

Create the prompt body in a normal text file:

```bash
cat > /tmp/api-reviewer-instructions.md <<'EOF_PROMPT'
You are a senior API compatibility reviewer.
Inspect public interfaces and identify breaking changes.
For each finding, provide evidence, impact, and a compatible alternative.
Do not modify files unless explicitly asked.
EOF_PROMPT
```

Create the project agent:

```bash
python3 scripts/agentctl.py create api-reviewer \
  --description "Reviews API compatibility and breaking-change risk" \
  --instructions-file /tmp/api-reviewer-instructions.md
```

Create one with an optional model preference:

```bash
python3 scripts/agentctl.py create api-reviewer \
  --description "Reviews API compatibility and breaking-change risk" \
  --model "YOUR_CONFIGURED_MODEL_NAME" \
  --instructions-file /tmp/api-reviewer-instructions.md \
  --force
```

Use an actual model identifier supported by your configured provider. An invalid or unavailable preference can prevent delegated use of that agent.

## Edit an agent

Edit metadata non-interactively:

```bash
python3 scripts/agentctl.py edit api-reviewer \
  --description "Reviews public APIs, schemas, and compatibility risk"
```

Replace its reusable instructions:

```bash
python3 scripts/agentctl.py edit api-reviewer \
  --instructions-file /tmp/api-reviewer-instructions.md
```

Open it in `$VISUAL` or `$EDITOR`, then validate the result automatically:

```bash
export EDITOR=vim
python3 scripts/agentctl.py edit api-reviewer --open-editor
```

Remove a model preference by passing an empty value:

```bash
python3 scripts/agentctl.py edit api-reviewer --model ""
```

## Export an agent

A custom agent is portable as its Markdown file. Export a validated copy:

```bash
mkdir -p exports
python3 scripts/agentctl.py export code-reviewer --output exports/
```

This creates:

```text
exports/code-reviewer.md
```

You can send that file to another user or commit it to another repository.

## Import an agent

This repository includes an importable security specialist:

```bash
python3 scripts/agentctl.py import examples/importable/security-reviewer.md
python3 scripts/agentctl.py validate
python3 scripts/agentctl.py list
```

It will be copied to:

```text
.agents/agents/security-reviewer.md
```

Use `--force` only when you intentionally want to replace an existing agent with the same name.

## Demonstrate the complete lifecycle safely

The demonstration creates, edits, validates, exports, and imports an agent entirely inside temporary directories:

```bash
make demo-lifecycle
```

No checked-in agent is changed.

## Install these agents into another repository

From this sample repository:

```bash
python3 scripts/agentctl.py install --target /path/to/your/repository
```

This copies all checked-in agents to:

```text
/path/to/your/repository/.agents/agents/
```

Or copy the directory yourself:

```bash
mkdir -p /path/to/your/repository/.agents
cp -R .agents/agents /path/to/your/repository/.agents/
```

Then start Goose from the target repository.

## Install globally

Global agents are available across Goose sessions:

```bash
python3 scripts/agentctl.py install --global
```

This installs them under:

```text
~/.agents/agents/
```

The sample does not overwrite existing files unless `--force` is supplied.

## Use a different agent directory

Every lifecycle command accepts `--agents-dir` before the subcommand:

```bash
python3 scripts/agentctl.py \
  --agents-dir /tmp/example/.agents/agents \
  list
```

## Validation rules in this sample

The helper checks that:

- the file starts and ends YAML frontmatter with `---`
- `name` exists
- names use lowercase letters, digits, and hyphens
- the filename matches `<name>.md`
- only documented fields `name`, `description`, and `model` are used
- the instruction body is not empty
- two files do not declare the same name during bulk validation

This validator intentionally supports the documented simple frontmatter shape rather than implementing the entire YAML specification.

## Tests

Run everything:

```bash
make verify
```

Run only the management CLI lifecycle tests:

```bash
python3 -m unittest tests.test_agentctl -v
```

Run only the sample application's tests:

```bash
python3 -m unittest tests.test_discounts -v
```

## Troubleshooting

### Agent does not appear

**Likely cause:** Goose was started outside the repository, or the file is not under `.agents/agents/`.

```bash
pwd
find .agents/agents -maxdepth 1 -type f -name '*.md' -print
python3 scripts/agentctl.py validate
```

Start Goose from the repository root afterward.

### Goose treats `@agent-name` as ordinary text

The exact mention picker and source-loading UX can vary by interface/version. Use explicit wording:

```text
Use the code-reviewer agent to review the current repository.
```

Or:

```text
Load the code-reviewer agent, then review the current repository.
```

### Delegation is unavailable

Delegated agents require delegation tools in the session. Loading the agent into the current conversation remains useful:

```text
Load the test-planner agent, then analyze sample-inputs/feature-request.md.
```

### Preferred model is unavailable

Remove the model field so the agent uses the session's configured model:

```bash
python3 scripts/agentctl.py edit AGENT_NAME --model ""
```

### Import reports an existing file

Inspect the difference before replacing it:

```bash
diff -u .agents/agents/security-reviewer.md examples/importable/security-reviewer.md
```

Then import with `--force` only when replacement is intended.

## Custom agents versus skills and recipes

- Use a **custom agent** to define *who Goose should be*: role, behavior, reusable prompt, and optional model preference.
- Use a **skill** to teach reusable domain knowledge or procedures that Goose loads on demand.
- Use a **recipe** for repeatable steps, parameters, extension configuration, or scheduling.
- Use **delegation/subagents** when work should run in an isolated specialist session.

## Official references

- Custom Agents: https://goose-docs.ai/docs/guides/context-engineering/custom-agents/
- Context Engineering: https://goose-docs.ai/docs/guides/context-engineering/
- Goose repository: https://github.com/aaif-goose/goose
