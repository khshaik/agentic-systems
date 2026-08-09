CLI Starter — Fetch and Summarize
================================

This example shows a minimal recipe that fetches a URL and returns a concise summary. It demonstrates a CLI-first flow using the `goose` command used in other samples in this repo.

Files
- `recipe.yaml` — top-level recipe that delegates to `subrecipes/fetch_and_summarize.yaml`
- `subrecipes/fetch_and_summarize.yaml` — subrecipe that retrieves and summarizes URL content

Run (example)

Set a workspace or temporary state root (optional) and run the recipe with a URL parameter. This uses the same `goose run` pattern used elsewhere in this repository.

```bash
# from this folder:
cd context-engineering/recipes/cli-starter

# example using a temporary GOOSE_PATH_ROOT; replace the URL below
GOOSE_PATH_ROOT=/tmp/goose-cli-starter goose run --recipe recipe.yaml --params url="https://example.com"
```

Notes
- The example subrecipe expects an HTTP fetch tool (MCP-backed) to be available. If your local Goose installation has a configured HTTP tool, the subrecipe will call it. If not, the subrecipe contains fallback instructions to explain what would have been done.
- You can validate the recipe similarly to other samples in this repo (if `goose` CLI is installed):

```bash
GOOSE_PATH_ROOT=/tmp/goose-cli-starter goose recipe validate recipe.yaml
```

Customization ideas
- Swap the subrecipe to call other tools (e.g., `code_search`, `git_diff`) to experiment with different tool patterns.
- Configure model choices in the subrecipe or via your Goose config to test dynamic model switching (local vs remote).
