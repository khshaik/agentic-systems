# Goose Recipes and Subrecipes — minimal working sample

This sample turns a project brief into an action checklist:

1. the parent recipe calls `summarize_brief`;
2. that subrecipe summarizes the brief in an isolated session;
3. its concise result returns to the parent;
4. the parent converts it into the final checklist.

## Structure

```text
recipes/
├── recipe.yaml
├── subrecipes/
│   ├── summarize.yaml
├── sample/
│   └── brief.md
├── scripts/
│   └── check.py
├── Makefile
└── README.md
```

## Validate

```bash
cd recipes
make test
```

This performs local structural checks and, when Goose is installed, validates both recipe files with `goose recipe validate`.

## Run

Configure a Goose provider, then run:

```bash
cd recipes
make run
```

Or provide another brief:

```bash
make run BRIEF=/absolute/path/to/brief.md
```

Direct Goose command:

```bash
goose run --recipe recipe.yaml \
  --params brief_content="Add CSV export for filtered rows with a header and tests"
```

## Key concepts

- `parameters` makes a recipe reusable.
- `{{ brief_content }}` inserts supplied brief text.
- The parent passes supplied content to the subrecipe as a tool parameter.
- `sub_recipes` registers isolated recipes as tools for the parent.
- Results return to the parent, but subrecipe conversation history does not.
- Subrecipes cannot define their own nested subrecipes.
- Different subrecipes run sequentially by default. Ask for them "in parallel" only when they are independent.
- `settings.max_turns` limits each subrecipe's work.

Recipes with `sub_recipes` automatically receive Goose's `summon` platform extension, so it does not need to be listed manually.

Subrecipes are currently experimental and their behavior may change.

Official documentation:

- https://goose-docs.ai/docs/guides/recipes/
- https://goose-docs.ai/docs/guides/recipes/recipe-reference/
- https://goose-docs.ai/docs/guides/recipes/subrecipes/
