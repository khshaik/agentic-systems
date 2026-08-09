# Goose Planning Mode — minimal working sample

Planning Mode lets Goose clarify a complex task and produce a step-by-step plan
for review before it changes anything. After you accept the plan, Goose returns
to normal mode and implements it.

## Structure

```text
planning-mode/
├── config.yaml.example
├── scripts/
│   └── check.py
├── Makefile
└── README.md
```

## Check and run

You need a configured [Goose CLI](https://goose-docs.ai/docs/getting-started/installation/).

```bash
cd planning-mode
make test
make run
```

In the interactive session, enter:

```text
/plan Add a health endpoint to a small HTTP service and test it. Do not change files until I accept the plan.
```

Answer any clarifying questions. When Goose presents the plan:

1. Review it and request changes if needed.
2. Accept it only when it is correct; Goose can then implement it.
3. Use `/endplan` to leave early without proceeding.

The CLI keeps planning separate from implementation and asks whether you want
to act on the completed plan. Goose Desktop has no `/plan` command; instead ask
it to create a plan and explicitly say not to start implementation.

## Optional separate planner model

By default, Planning Mode uses the normal provider and model. To use a different
planner, copy the two keys from `config.yaml.example` into your Goose config and
replace the example values:

```text
~/.config/goose/config.yaml
```

Restart Goose, then verify the active planner and execution settings:

```bash
make info
```

You can also set them for one shell instead:

```bash
export GOOSE_PLANNER_PROVIDER="openai"
export GOOSE_PLANNER_MODEL="your-planner-model"
make run
```

Keep your existing default provider/model for execution. Provider credentials
belong in the keyring or provider environment variable, not this sample config.

Official guides:

- https://goose-docs.ai/docs/guides/creating-plans/
- https://goose-docs.ai/docs/guides/config-files/
