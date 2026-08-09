# Anatomy of a Goose custom agent

A project-scoped custom agent is a Markdown file in:

```text
.agents/agents/<agent-name>.md
```

The file has YAML frontmatter followed by the reusable instructions:

```markdown
---
name: example-agent
description: Explains when this specialist should be selected
model: optional-model-preference
---
You are a specialist...
```

`name` is required. `description` and `model` are optional. This sample omits `model` from installed agents so it works with the provider and model already configured in Goose. The included management CLI supports adding a model preference when a team intentionally standardizes on one.

Loading and delegation are different:

- **Load** adds the specialist instructions to the current conversation.
- **Delegate** starts an isolated specialist session and returns its result.

Custom agents define a role and behavior. They do not package a deterministic workflow, extension set, parameters, or schedule; use Goose Recipes for those needs.
