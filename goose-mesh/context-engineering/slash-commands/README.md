# Goose Slash Commands — minimal working sample

This sample adds two custom commands:

- `/review` loads reusable code-review instructions;
- `/explain <topic>` launches a parameterized recipe.

Both commands work by mapping a command name to a Goose recipe.

## Structure

```text
slash-commands/
├── recipes/
│   ├── review.json
│   └── explain.json
├── config.yaml.example
├── Makefile
└── README.md
```

## Validate

```bash
cd slash-commands
make test
```

If Goose is installed, this also runs its recipe validator.

## Configure Goose

Print configuration containing the correct absolute recipe paths:

```bash
make config
```

Copy the printed `slash_commands` section into:

```text
~/.config/goose/config.yaml
```

If that file already contains `slash_commands`, add the two list entries beneath the existing key instead of adding a second key.

## Run

Start an interactive session from the repository you want to inspect:

```bash
cd /path/to/your/repository
goose session
```

Then enter either command at the start of a message:

```text
/review
/explain authentication flow
```

Goose loads the mapped recipe's instructions and prompt into the current chat. A custom slash command accepts at most one parameter; quote it only if you want to.

Command names are case-insensitive, must be unique, cannot contain spaces, and cannot conflict with built-in commands such as `/help`, `/recipe`, or `/compact`.

Official guide: https://goose-docs.ai/docs/guides/context-engineering/slash-commands/
