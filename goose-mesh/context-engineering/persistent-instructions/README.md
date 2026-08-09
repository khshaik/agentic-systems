# Goose Persistent Instructions — minimal working sample

Persistent instructions place critical reminders in Goose's working memory on every turn. This sample uses one file for three project guardrails.

## Structure

```text
persistent-instructions/
├── guardrails.md
├── Makefile
└── README.md
```

## Test locally

```bash
cd persistent-instructions
make test
make demo
```

## Use with Goose

From this directory, point Goose to the instructions before starting it:

```bash
export GOOSE_MOIM_MESSAGE_FILE="$PWD/guardrails.md"
goose
```

The built-in Top of Mind extension reads the file on every turn. Edit `guardrails.md` during the session and its new contents apply on the next interaction without restarting Goose.

Test it by asking Goose to upload the repository to a public service. It should follow the guardrail and refuse or ask for an appropriate safe alternative.

For a short reminder without a file, use:

```bash
export GOOSE_MOIM_MESSAGE_TEXT="Always run tests after changing code."
goose
```

If both variables are set, Goose concatenates their contents. Clear them with:

```bash
unset GOOSE_MOIM_MESSAGE_FILE GOOSE_MOIM_MESSAGE_TEXT
```

Keep instructions concise because they consume context on every turn. Goose caps persistent instruction content at 64 KB.

Official guide: https://goose-docs.ai/docs/guides/using-persistent-instructions/
