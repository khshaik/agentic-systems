# Goose Subagents — minimal working sample

This recipe keeps a review out of the main conversation by delegating it to
temporary, isolated Goose instances. Two independent reviews run in parallel;
after they finish, a third subagent combines their results sequentially.

## Structure

```text
subagents/
├── recipe.yaml
├── sample/
│   └── brief.md
├── scripts/
│   └── check.py
├── Makefile
└── README.md
```

## Check and run

You need a configured [Goose CLI](https://goose-docs.ai/docs/getting-started/installation/).
Subagents work in autonomous permission mode; they are disabled in manual,
smart-approval, and chat-only modes.

```bash
cd subagents
make test       # dependency-free local check
make validate   # validate with the Goose CLI
make run        # run the recipe
```

The run reads `sample/brief.md` and prints one recommendation. It does not edit
files. In the Goose UI or CLI, subagent tool calls are visible while the main
conversation receives the compact result.

## What the recipe demonstrates

- **Isolation:** each subagent has its own context; only its returned result is
  passed back.
- **Parallel work:** the requirements and risk reviews run at the same time.
- **Sequential work:** synthesis starts only after both reviews return, and the
  parent explicitly passes those results to it.
- **Focused access:** `summon` provides delegation and `developer` lets the
  read-only reviewers inspect the sample file.

For a one-off task instead of a recipe, ask Goose directly:

```text
Use two read-only subagents in parallel to review sample/brief.md: one for
requirements and one for risks. Then use a third subagent to combine their
results. Return only the final summary and do not edit files.
```

Keep parallel tasks independent. If tasks modify the same files or depend on
earlier output, run them sequentially.

Official guide: https://goose-docs.ai/docs/guides/context-engineering/subagents/
