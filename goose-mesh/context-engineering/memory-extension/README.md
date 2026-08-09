# Goose Memory Extension — minimal working sample

This sample teaches Goose three facts it can recall in later sessions:

- a project command;
- a reusable code snippet;
- a response preference.

The built-in Memory extension stores local project memories under
`.goose/memory/` and loads them when a new session starts.

## Structure

```text
memory-extension/
├── prompts.md
├── scripts/
│   └── check.py
├── .gitignore
├── Makefile
└── README.md
```

## Check and run

You need a configured [Goose CLI](https://goose-docs.ai/docs/getting-started/installation/).

```bash
cd memory-extension
make test
make run
```

`make run` starts Goose with its built-in Memory extension enabled. In that
session, paste the **Store** prompt from `prompts.md`, wait for confirmation,
and exit.

Start a separate session:

```bash
make run
```

Paste the **Recall** prompt. Goose should return the saved command, snippet,
and preference without you teaching them again.

## Local and global memory

The sample explicitly asks for **local** memory, stored in:

```text
.goose/memory/
```

It is ignored by Git because memories can contain personal or project-specific
information. Use global memory only for facts that should apply everywhere;
Goose stores it under `~/.config/goose/memory/`.

Ask Goose to manage saved knowledge naturally:

```text
Search local memory for sample_project.
Forget the sample_project memory in local scope.
```

Do not store passwords, tokens, or other secrets in memory.

Official guide: https://goose-docs.ai/docs/mcp/memory-mcp/
