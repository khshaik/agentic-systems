# Goose Prompt Templates — minimal working sample

This sample overrides the prompts Goose uses for:

- normal responses (`system.md`);
- CLI planning mode (`plan.md`);
- conversation compaction (`compaction.md`).

## Structure

```text
prompt-templates/
├── prompts/
│   ├── system.md
│   ├── plan.md
│   └── compaction.md
├── Makefile
└── README.md
```

## Test and install

On macOS or Linux:

```bash
cd prompt-templates
make test
make install
goose
```

`make install` copies the templates to `~/.config/goose/prompts/`. It replaces
files with the same names, so back up existing custom templates first.

To preview installation without changing your Goose configuration:

```bash
make install PROMPTS_DIR=/tmp/goose-prompts
```

On Windows, copy the three files into:

```text
%APPDATA%\Block\goose\config\prompts\
```

Changes apply to new sessions. In the CLI, use `/plan` to exercise `plan.md`
and `/compact` to exercise `compaction.md`. Normal chats use `system.md`.

To restore a built-in prompt, delete its custom file from the Goose prompts
directory (or use **Settings → Prompts → Reset to Default** in Goose Desktop).

Templates support Jinja syntax. Keep required variables such as `{{ messages }}`
when editing a template.

Official guide: https://goose-docs.ai/docs/guides/context-engineering/prompt-templates/
