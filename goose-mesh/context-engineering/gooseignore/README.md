# Goose `.gooseignore` — minimal working sample

`.gooseignore` prevents Goose's Developer extension from reading or changing matching files and directories. Its patterns use `.gitignore` syntax.

## Structure

```text
gooseignore/
├── .gooseignore                 # project-wide rules
├── global.gooseignore.example   # global rules to install
├── app.txt                      # safe example file
├── scripts/validate.py
├── Makefile
└── README.md
```

The project file blocks:

```gitignore
.env
secrets/
*.pem
```

## Test

```bash
cd gooseignore
make test
```

## Use project rules

Copy `.gooseignore` to the root of any repository, edit its patterns, then start a new Goose session there:

```bash
cp gooseignore/.gooseignore /path/to/project/.gooseignore
cd /path/to/project
goose
```

Ask Goose to read `app.txt` and then `.env`. The first path is available; the ignored path is denied.

## Use global rules

Global rules apply across projects. Install the example as Goose's global `.gooseignore`:

```bash
mkdir -p ~/.config/goose
cp global.gooseignore.example ~/.config/goose/.gooseignore
```

Restart Goose after changing ignore rules. Keep project-specific paths in the repository file and personal, machine-wide rules in the global file. Both files are applied when present.

Negation is supported when a broad rule needs an exception:

```gitignore
logs/
!logs/example.log
```

Do not use `.gooseignore` as the only secret-management control: keep secrets out of the repository and use appropriate file permissions as well.

Official reference: https://goose-docs.ai/docs/mcp/developer-mcp/#configuring-access-controls
