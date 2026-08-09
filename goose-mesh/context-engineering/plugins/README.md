# Goose Plugins — complete working sample

This repository is a drop-in, runnable example of a Goose **Plugin**. The plugin is named `repository-companion` and bundles both component types currently supported by Goose Open Plugins:

- a reusable `repository-health` skill;
- lifecycle hooks backed by local Python scripts.

It also includes dependency-free validation, tests, CI, a deterministic demo, manual project/user installation instructions, and Git-backed install/update instructions.

## What this sample covers

| Capability | Where it is demonstrated |
|---|---|
| Plugin identity and version | `plugin.json` |
| Skill packaged by a plugin | `skills/repository-health/SKILL.md` |
| Skill supporting script | `skills/repository-health/scripts/repository_health.py` |
| Hook event configuration | `hooks/hooks.json` |
| `${PLUGIN_ROOT}` command paths | `hooks/hooks.json` |
| Matcher regular expressions | `PreToolUse` and `AfterShellExecution` rules |
| Hook JSON received on stdin | `scripts/hook_handler.py` |
| `PreToolUse` policy denial | `guard-shell` action |
| Safe, opt-in event logging | `record-event` action |
| Project and user discovery | Installation examples below |
| Git-backed installation | `goose plugin install` |
| Automatic and manual updates | `--auto-update` and `goose plugin update` |
| Plugin disabling | `disabledPlugins` examples below |
| Local validation and tests | `make verify` |

## Repository structure

```text
plugins/
├── plugin.json
├── README.md
├── CHANGELOG.md
├── LICENSE
├── Makefile
├── hooks/
│   └── hooks.json
├── scripts/
│   ├── hook_handler.py
│   └── validate_plugin.py
├── skills/
│   └── repository-health/
│       ├── SKILL.md
│       └── scripts/
│           └── repository_health.py
└── tests/
    ├── test_hook_handler.py
    ├── test_repository_health.py
    └── test_validation.py
```

The directory itself is the plugin. Keep `plugin.json`, `skills/`, `hooks/`, and `scripts/` together when copying or publishing it.

## Prerequisites

- Python 3.11 or newer for the bundled scripts and tests
- GNU Make, or run the Python commands directly
- A current Goose CLI or Goose Desktop build with a configured model provider for live use
- The built-in Developer extension for the shell hook demonstration
- Git when using `goose plugin install` and plugin updates

Install the current Goose CLI using the command published by the Goose project:

```bash
curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh | bash
```

## Verify the package locally

Enter this directory and run all deterministic checks:

```bash
cd plugins
make verify
```

This performs:

1. plugin manifest, skill frontmatter, hook JSON, matcher, and Python syntax validation;
2. unit tests for the validator, health checker, denial policy, and redacted event logger;
3. a read-only repository-health scan of this sample.

Run checks individually:

```bash
make validate
make test
make demo
```

Without Make:

```bash
python3 scripts/validate_plugin.py .
python3 -m unittest discover -s tests -v
python3 skills/repository-health/scripts/repository_health.py --repo .
```

Expected demo decision:

```text
Decision: HEALTHY
```

## Fastest live test: project plugin

From the parent workspace, copy the complete plugin into a target repository:

```bash
mkdir -p /path/to/target-repository/.agents/plugins
cp -R plugins /path/to/target-repository/.agents/plugins/repository-companion
```

Start a **new** Goose session from the target repository:

```bash
cd /path/to/target-repository
goose
```

List discoverable skills:

```text
/skills
```

The plugin-provided skill is namespaced by Goose and appears as:

```text
repository-companion:repository-health
```

Explicitly load and use it:

```text
/skills repository-companion:repository-health
```

Then ask:

```text
Run the repository health workflow against this repository. Do not modify files or execute application code. Give me the decision, evidence, and three next actions.
```

Goose may also load the skill automatically for a matching request:

```text
Give this repository a quick pre-commit health assessment. Check documentation, tests, CI, and secret hygiene without changing anything.
```

## Install for your user account manually

User plugins are available across projects:

```bash
mkdir -p ~/.agents/plugins
cp -R plugins ~/.agents/plugins/repository-companion
```

Review all hooks before installing a plugin into the user directory because they can run in every project where the plugin is active.

## Install from Git

For `goose plugin install`, publish the contents of this directory as the root of its own Git repository. The remote repository must have `plugin.json` at its root.

```bash
goose plugin install https://github.com/YOUR-ACCOUNT/repository-companion.git
```

Goose clones the repository, detects the Open Plugins format, and installs it under:

```text
~/.agents/plugins/repository-companion/
```

Enable rate-limited update checks before plugin skills are loaded:

```bash
goose plugin install --auto-update https://github.com/YOUR-ACCOUNT/repository-companion.git
```

Only Git-backed plugins installed through `goose plugin install` are managed by the update command. Manually copied project and user plugins are discovered but not update-managed.

## Update a Git-backed installation

After publishing a new commit and increasing the version in `plugin.json` and `CHANGELOG.md`, run:

```bash
goose plugin update repository-companion
```

Start a new session after updating so discovery and startup hooks use the current package.

## How the skill works

`repository-health` performs a conservative, static check for:

- `README.md`;
- `LICENSE`;
- recognizable tests;
- a recognizable CI definition;
- a committed `.env` file;
- likely hard-coded secret assignments.

It excludes common VCS, dependency, cache, and build directories. Potential secret values are never returned in the report. It does not install dependencies, run application code, access the network, or change the target repository.

Run its script directly:

```bash
python3 skills/repository-health/scripts/repository_health.py \
  --repo /path/to/repository \
  --format text
```

Machine-readable output:

```bash
python3 skills/repository-health/scripts/repository_health.py \
  --repo /path/to/repository \
  --format json
```

Exit status is `1` for `BLOCKED`, `0` for `HEALTHY` or `NEEDS_ATTENTION`, and `2` for invalid command usage.

## How the hooks work

Goose loads hook rules from `hooks/hooks.json`. It supplies the event payload as JSON on standard input and expands `${PLUGIN_ROOT}` to this plugin directory.

### Shell safety hook

Before a `developer__shell` tool call, the `PreToolUse` rule invokes:

```text
python3 "${PLUGIN_ROOT}/scripts/hook_handler.py" guard-shell
```

The sample blocks only a deliberately small set of commands:

- `sudo` shell commands;
- recursive forced deletion of filesystem root;
- `git reset --hard`.

When a match is found, the hook prints Goose's structured denial response:

```json
{"decision":"block","reason":"..."}
```

The hook is an additional guardrail, not a complete shell security policy. Goose permission controls and human review remain necessary.

### Verification event hook

After selected successful test commands, `AfterShellExecution` invokes the `record-event` action. Logging is disabled by default to avoid silently creating files.

Enable it before starting Goose:

```bash
export REPOSITORY_COMPANION_LOG="$PWD/.plugin-demo-events.jsonl"
goose
```

Then ask Goose to run `make test`, `make verify`, or a supported Python test command. Each matching successful event appends one JSON line containing only timestamp, event, session ID, and matcher context. The logger intentionally excludes `tool_input` and tool output to reduce the chance of recording secrets.

Inspect it:

```bash
sed -n '1,20p' .plugin-demo-events.jsonl
```

Unset logging when finished:

```bash
unset REPOSITORY_COMPANION_LOG
```

## Test a hook script without Goose

Allowed shell command (no output, exit `0`):

```bash
printf '%s' '{"event":"PreToolUse","session_id":"demo","tool_input":{"command":"make test"}}' \
  | python3 scripts/hook_handler.py guard-shell
```

Blocked shell command (structured JSON denial, exit `0`):

```bash
printf '%s' '{"event":"PreToolUse","session_id":"demo","tool_input":{"command":"git reset --hard HEAD"}}' \
  | python3 scripts/hook_handler.py guard-shell
```

Opt-in logger:

```bash
REPOSITORY_COMPANION_LOG=/tmp/repository-companion-events.jsonl \
  python3 scripts/hook_handler.py record-event <<'JSON'
{"event":"AfterShellExecution","session_id":"demo","matcher_context":"make test"}
JSON
```

## Disable the plugin

Disable it globally by adding its name to the Goose user settings:

```json
{
  "disabledPlugins": ["repository-companion"]
}
```

User settings path:

```text
~/.config/goose/settings.json
```

For a shared project setting, use:

```text
<project>/.config/goose/settings.json
```

For a project-local setting that should not be committed, use:

```text
<project>/.config/goose/settings.local.json
```

A disabled plugin is skipped completely: its skill is unavailable and its hooks do not run.

## Customize the sample

To create your own plugin from this one:

1. Rename the directory and change `name`, `version`, and `description` in `plugin.json`.
2. Rename or add directories under `skills/`; each must contain a matching `SKILL.md` name.
3. Add supported hook event rules to `hooks/hooks.json`.
4. Reference bundled commands using `${PLUGIN_ROOT}` rather than machine-specific absolute paths.
5. Keep hooks fast, deterministic, and conservative about logged data.
6. Update tests and run `make verify`.
7. Review every hook before publishing because installed hooks execute local commands.

## Troubleshooting

### Plugin or skill does not appear

Confirm the structure and start a new session from the repository:

```bash
pwd
find .agents/plugins/repository-companion -maxdepth 4 -type f -print
python3 .agents/plugins/repository-companion/scripts/validate_plugin.py \
  .agents/plugins/repository-companion
goose skills list
```

The skill name is `repository-companion:repository-health`, not only `repository-health`.

### Hook does not run

Check that:

- the plugin is not listed in `disabledPlugins`;
- `hooks/hooks.json` exists inside the plugin;
- the event name is supported;
- the matcher is a valid regular expression;
- the Developer extension's shell tool name matches `developer__shell`;
- `python3` is on the `PATH` used to start Goose.

Matchers are regular expressions, not globs. Use `.*` to match everything; a bare `*` is invalid.

### Event log is missing

The logger is intentionally opt-in. Set `REPOSITORY_COMPANION_LOG` before starting Goose, use one of the commands matched in `hooks/hooks.json`, and ensure the parent directory is writable.

### Git install fails

Ensure the URL is cloneable and `plugin.json` is at the root of that Git repository. Running `goose plugin install` against the larger parent monorepo will not select this nested directory automatically; publish this `plugins/` directory as its own plugin repository or copy it manually.

## Security notes

- Install plugins only from sources you trust.
- Read skills before allowing them to influence agent behavior.
- Read hook commands before installation; they execute on your machine.
- Do not store credentials in plugin manifests, skills, scripts, or hook configuration.
- Treat the bundled secret scan as a teaching example, not a replacement for a dedicated secret scanner.
- Plugin hooks supplement Goose permission controls; they do not replace them.

## Official references

- Plugins: https://goose-docs.ai/docs/guides/context-engineering/plugins/
- Hooks: https://goose-docs.ai/docs/guides/context-engineering/hooks/
- Agent Skills: https://goose-docs.ai/docs/guides/context-engineering/using-skills/
- Goose CLI commands: https://goose-docs.ai/docs/guides/goose-cli-commands/
- Goose repository: https://github.com/aaif-goose/goose

The official documentation was checked on **31 July 2026**. Goose evolves quickly, so verify current installation and hook behavior before distributing a long-lived production plugin.

## License

MIT. See `LICENSE`.
