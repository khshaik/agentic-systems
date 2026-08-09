# Building with open-source AI agents

Workshop materials for a hands-on session on [goose](https://github.com/aaif-goose/goose),
the open-source AI agent governed by the Agentic AI Foundation under the Linux Foundation.
Covers the ground from "what is an agent?" to the goose Development Kit: sessions, context
engineering, recipes, tool permissions, MCP and ACP.

Presented by Azeez Syed (AIYatra).

## Contents

| Path | What it is |
| --- | --- |
| `export/goose-workshop.pdf` | The deck as a 35-page PDF, one page per slide. |
| `export/goose-workshop.pptx` | The deck as PowerPoint. 39 slides, because click-steps become separate slides. |
| `slides.md` | Slidev source for the deck. |
| `components/`, `styles/`, `global-bottom.vue` | Vue components and CSS the deck depends on. |
| `DESIGN.md` | Design system for the deck: type scale, colour, layout rules. |
| `context-engineering/` | Runnable samples for each goose context-engineering feature. |

## Context engineering samples

Each directory under `context-engineering/` is a self-contained, runnable sample with
its own `README.md` and a `Makefile`. Run `make` inside one to get its targets or run
its checks; most default to `test`, `agent-skills` to `verify`.

| Sample | Feature |
| --- | --- |
| `goosehints` | `.goosehints` files that load project context and conventions at session start, including nested per-directory hints. |
| `gooseignore` | `.gooseignore` patterns that stop the Developer extension reading or writing matching files. |
| `persistent-instructions` | Guardrails placed in working memory on every turn. |
| `memory-extension` | Facts goose stores and recalls across sessions. |
| `prompt-templates` | Overrides for the system, plan, and compaction prompts. |
| `planning-mode` | Plan-then-execute flow with a review step before any change. |
| `recipes` | A parent recipe calling a subrecipe to turn a brief into a checklist. |
| `subagents` | Parallel reviews delegated to isolated goose instances. |
| `slash-commands` | Custom `/review` and `/explain` commands backed by recipes. |
| `custom-agents` | Project-scoped specialist agents plus a lifecycle CLI and tests. |
| `agent-skills` | A complete Agent Skill (`release-readiness`) with scripts, workflows, and tests. |
| `plugins` | The `repository-companion` plugin, bundling a skill and hooks. |
| `hooks` | A Python script wired to goose session and tool events. |

There is also a `.commandcode/taste/taste.md` placeholder, left empty during the session.

`context-engineering/goose-agent-workshop.pptx` is the original slide deck the Slidev
version was rebuilt from. It is kept for reference; `export/goose-workshop.pptx` is the
current deck.

## Working on the deck

```bash
npm install
npm run dev          # live preview at localhost:3030
npm run build        # static site into dist/
```

Re-export after editing `slides.md`:

```bash
npx slidev export --output export/goose-workshop.pdf slides.md
npx slidev export --format pptx --output export/goose-workshop.pptx slides.md
```

Export needs `playwright-chromium`, which `npm install` pulls in as a dev dependency.

## Goose in the multi-agent landscape

Goose can be used as a multi-agent system, but it is better understood as a general-purpose open-source agent runtime and platform with strong support for subagents, tools, skills, recipes and MCP-based orchestration. It is not best described simply as a multi-agent framework in the same way as CrewAI.

The official Goose documentation presents it primarily as a local AI agent with desktop, CLI and API interfaces. It supports tools through MCP and explicitly supports subagents that can be spawned independently and run tasks in parallel. That makes Goose especially relevant for studies of agentic systems, because it sits at a slightly different layer from frameworks focused purely on agent teams or workflow state machines.

A useful way to think about it is:

- Goose: open-source agent runtime/platform + MCP + tools/skills + subagents + workflow/recipe orchestration
- CrewAI: a framework for building teams of agents
- LangGraph: a framework for precise workflow and state management

In practice, Goose is most useful when you want one extensible agent to coordinate work across tools, skills, recipes and subagents. A simple mental model is a main manager agent delegating tasks to specialist subagents such as research, coding and review, and then combining their outputs into a final result.

The architecture also aligns with Goose's public roadmap, which emphasizes "Meta-Agent Orchestration (Many Agents, One Workflow)" and highlights parallel subagents, recipes/subrecipes, task tracking and execution models. For that reason, Goose fits naturally into a study map of multi-agent and agentic AI systems, especially when the focus is on runtime design, MCP integration, local LLM use and observability rather than only on agent-team construction.

One additional point is that Goose is now part of the Agentic AI Foundation under the Linux Foundation, and its official documentation emphasizes open standards such as MCP and ACP. That makes it especially interesting as an agent runtime/platform in the broader ecosystem of agentic AI tools.

## Architecture diagrams

Below are workshop diagrams illustrating Goose's architecture and subagent patterns. Save the supplied images into the `images/` directory using the filenames shown below so they render correctly in this README.

### Diagrams

- **Core architecture** — `images/goose-core-architecture.png`

	![Goose core architecture](images/goose-core-architecture.png)

- **Main agent → subagents flow** — `images/goose-subagents-flow.png`

	![Main agent delegating to subagents](images/goose-subagents-flow.png)

- **Sub-agent architecture** — `images/goose-subagent-architecture.png`

	![Sub-agent architecture and token usage](images/goose-subagent-architecture.png)

Each image is accompanied by a short caption describing the component illustrated. If you prefer different filenames, update the `images/README.md` file with the names you used and adjust the references here accordingly.

## Detailed overview — purpose, capabilities and getting started

This section adds practical and conceptual detail about Goose for beginners and practitioners who want to evaluate or adopt it. The existing content above remains unchanged; the material below supplements that content with actionable context, feature highlights, implementation guidance and a brief comparison to related frameworks.

**Purpose and positioning**

- Goose is an open-source agent runtime and platform designed to run extensible AI agents locally (desktop, CLI and API). Its primary purpose is to combine an agent execution runtime, a tools/skills ecosystem and MCP-based integrations so that a single manager agent can orchestrate work and spawn subagents to run tasks in parallel.
- Think of Goose as an agent runtime/platform first (agent + tools + skills + subagents + recipes) rather than a pure multi-agent framework where the team-of-agents is the primary design abstraction.

**Key capabilities**

- Subagents: Spawn independent subagents that run tasks in parallel (research, code, review, data extraction).
- Recipes and workflows: Compose recipes and subrecipes to represent multi-step tasks and reusable workflows.
- MCP & tool integrations: Native focus on MCP (Model/Tool Communication Protocol) makes integrating external tools, APIs and runtime services straightforward.
- Local LLMs and model management: Supports local LLMs and remote providers; enables dynamic selection and switching of models depending on task requirements or cost/performance tradeoffs.
- Observability & task tracking: Execution models and task-tracking primitives make it easier to follow what subagents are doing and why.
- Extensibility: Skills, plugins and hooks allow project-scoped specialist agents and deep integrations with developer workflows.

**Why use Goose**

- If you want a single extensible agent that can coordinate tools, spawn subagents, and integrate with local or hosted LLMs, Goose is a strong fit.
- If your focus is on runtime/platform features (observability, MCP-based tool use, recipes, local LLMs), Goose provides a pragmatic foundation.
- If you need to author complex automation that mixes human prompts, tool calls and parallel subagent work, Goose's recipes+subagents model is convenient.

**Comparative overview**

The following table highlights high-level differences useful for quick comparisons. It is illustrative and intended to orient beginners — consult each project's official docs for definitive details.

| Aspect | Goose | CrewAI | LangGraph |
| --- | ---: | :---: | :---: |
| Primary identity | Agent runtime / platform | Multi-agent framework | Agent/workflow orchestration framework |
| Single agent | ✅ | ✅ | ✅ |
| Multiple agents | ✅ Subagents | ✅ Core capability | ✅ |
| Parallel subagents | ✅ | ✅ | ✅ |
| Agent roles | Possible / flexible | Core concept | Flexible |
| Workflow / state control | Good (recipes & execution models) | Good | Very high (workflow-first) |
| MCP / tool focus | Strong / native | Supported | Supported |
| Local LLMs | ✅ | ✅ | ✅ |
| Coding agent focus | Strong | Not primary | Not primary |
| Best mental model | Agent + tools + subagents | AI team | Programmable workflow |

**Dynamic model switching**

Goose supports selecting different models for different tasks and can be configured to prefer local LLMs for private or cost-sensitive work and remote providers for high-capability needs. This dynamic switching enables workflows like:

- Use a high-capacity hosted model for research or plan generation.
- Spawn subagents that use smaller local models for chunked processing or summarization to save cost and latency.
- Re-run a specific step with a different model to improve fidelity or verify results.

**Quick start (beginner-friendly)**

1. Clone the Goose repository or explore the official documentation to find the recommended install path for your platform.
2. Try the simplest interface first: the desktop or CLI, depending on your environment and preferences.
3. Explore `recipes/`, `subagents/` and `context-engineering/` samples (this repository includes runnable examples).
4. Create a small recipe that spawns a single subagent (e.g., research task) and returns a summary — use that as a growth point for more complex orchestration.

Helpful example workflow (conceptual):

- Create a `brief` describing the problem you want solved.
- Write a `recipe` that splits the brief into research/coding/review steps.
- Configure subagents and skills for each step (assign models, tools, and hints).
- Run the recipe from the CLI or desktop and review subagent outputs.

Example local commands (conceptual; check official docs for exact CLI names):

```bash
# clone the project
git clone https://github.com/aaif-goose/goose.git
cd goose

# run the desktop or CLI according to the project's README
# e.g. `goose run` or open the Electron desktop app
```

**Implementation notes**

- Start with small experiments: a single recipe and one subagent that calls a simple tool (e.g., a web fetcher or a code formatter).
- Use `.goosehints` and prompt templates to keep agent behaviour consistent across runs.
- Leverage MCP integrations for tool-heavy workflows and to keep tool interfaces decoupled from agent logic.
- Use local models for private data and quick turn-around tasks; switch to hosted models for tasks needing higher reasoning capacity.

**Resources and next steps**

- Read the official Goose docs and the roadmap for the latest recommended patterns and supported interfaces.
- Explore `context-engineering/` and `recipes/` in this repository for runnable samples.
- If you'd like, I can add one or two concrete starter recipes and a minimal walkthrough in this repo (including exact CLI commands and a tiny example recipe) — tell me whether you prefer a CLI-first or desktop-first walkthrough.

