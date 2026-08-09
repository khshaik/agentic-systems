# Goose Hooks — minimal working sample

This sample runs one Python script when Goose receives these events:

- session start;
- prompt submission;
- successful tool call;
- successful file edit;
- successful shell execution.

## Structure

```text
hooks/
├── plugin.json
├── hooks/
│   └── hooks.json
├── scripts/
│   └── log_event.py
├── Makefile
└── README.md
```

Goose hooks live inside a plugin directory. `hooks/hooks.json` selects events, and `${PLUGIN_ROOT}` resolves to this directory.

## Test locally

```bash
cd hooks
make test
make demo
```

The demo creates `.goose-hook-events.jsonl` with one event.

## Use in a repository

Copy the complete directory into a project:

```bash
mkdir -p /path/to/project/.agents/plugins
cp -R hooks /path/to/project/.agents/plugins/event-logger
```

Start a new Goose session from that project:

```bash
cd /path/to/project
goose
```

Events are written to:

```text
.goose-hook-events.jsonl
```

Use a different location by setting this before starting Goose:

```bash
export GOOSE_HOOK_LOG=/tmp/goose-events.jsonl
goose
```

Inspect the log:

```bash
tail -n 20 .goose-hook-events.jsonl
```

The script records only the timestamp, event name, session ID, and matcher context. It does not log prompt bodies or full tool inputs.

## Customize

Supported events include `SessionStart`, `SessionEnd`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `AfterFileEdit`, and `AfterShellExecution`.

Matchers are regular expressions. Omit `matcher` to handle every event, or use `.*`. A bare `*` is invalid.

Hooks execute local commands, so install only hooks you trust.

Official guide: https://goose-docs.ai/docs/guides/context-engineering/hooks/
