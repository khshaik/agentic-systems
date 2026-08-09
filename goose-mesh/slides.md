---
theme: default
title: Building with open-source AI agents
info: |
  Hands-on workshop on goose. From "what is an agent?" to the goose Development
  Kit: sessions, context engineering, recipes, tool permissions, MCP and ACP.

  Azeez Syed, AIYatra.
author: Azeez Syed
colorSchema: light
transition: slide-left
mdc: true
fonts:
  sans: 'Geist'
  mono: 'Geist Mono'
  weights: '400,500,600'
class: cover vcenter
---

<div class="grid grid-cols-[1.1fr_0.9fr] gap-14 items-center">

<div>

<div class="eyebrow">Hands-on workshop</div>

# Building with open-source AI agents

<div class="lead">From “what is an agent?” to the goose Development Kit: sessions, context engineering, recipes, tool permissions, MCP and ACP.</div>

<div class="caption mt-10">
  <div>Azeez Syed &nbsp;·&nbsp; AIYatra</div>
  <div class="mt-2">Khaja Moinuddin Mohammad &nbsp;·&nbsp; Organiser and founder, AIYatra</div>
</div>

</div>

<div>

<div class="term">
  <div><span class="dim">$</span> brew install block-goose-cli</div>
  <div><span class="dim">$</span> goose configure</div>
  <div>  <span class="accent">◇</span> Configure Providers</div>
  <div>  <span class="accent">◇</span> Anthropic</div>
  <div>  <span class="ok">└</span> Saved</div>
  <div>&nbsp;</div>
  <div><span class="dim">$</span> goose session</div>
  <div>  goose <span class="accent">›</span> _</div>
</div>

<p class="caption mt-6">Deconstruct the abstraction.<br/>Expose the kernel truth.</p>

</div>

</div>

<!--
Welcome. Full-day, terminal-first workshop on goose. We go bottom-up: agent
fundamentals, then goose itself, then every major feature, then architecture,
then where the project is heading with GDK. Everything we cover maps to
goose-docs.ai/docs/category/guides.
-->

---
class: cover vcenter
---

<div class="grid grid-cols-[1fr_auto] gap-16 items-center">

<div>

<div class="eyebrow">Community</div>

# Join AIYatra

<div class="lead mt-4">An AI learning journey out of Manikonda, Hyderabad. Talks, workshops and hands-on sessions.</div>

<div class="mt-8">
  <span class="badge badge-accent">meetup.com/aiyatra</span>
</div>

</div>

<div>

<MeetupQr :size="200" />

<div class="caption mt-3" style="text-align: center">Scan to join</div>

</div>

</div>

<!--
Put this up while the room settles. Scanning takes ten seconds and people can do
it before we start rather than at the end when they are packing up.
-->

---
class: vcenter
---

<div class="eyebrow">The day, end to end</div>

## Fourteen sections

<div class="grid grid-cols-2 gap-x-14 gap-y-0 mt-4">

<div>
  <div class="agenda-item"><span class="agenda-num">01</span> What is an agent?</div>
  <div class="agenda-item"><span class="agenda-num">02</span> Introduction to goose</div>
  <div class="agenda-item"><span class="agenda-num">03</span> goose vs Claude Code, Cursor &amp; Codex</div>
  <div class="agenda-item"><span class="agenda-num">04</span> Installation &amp; configuration</div>
  <div class="agenda-item"><span class="agenda-num">05</span> The goose folder structure</div>
  <div class="agenda-item"><span class="agenda-num">06</span> Session management</div>
  <div class="agenda-item" style="border-bottom: 0"><span class="agenda-num">07</span> Context engineering</div>
</div>

<div>
  <div class="agenda-item"><span class="agenda-num">08</span> Recipes &amp; subrecipes</div>
  <div class="agenda-item"><span class="agenda-num">09</span> Managing tools &amp; permissions</div>
  <div class="agenda-item"><span class="agenda-num">10</span> Security &amp; safe autonomy</div>
  <div class="agenda-item"><span class="agenda-num">11</span> MCP surface &amp; platform operations</div>
  <div class="agenda-item"><span class="agenda-num">12</span> The Agent Client Protocol</div>
  <div class="agenda-item"><span class="agenda-num">13</span> goose architecture</div>
  <div class="agenda-item" style="border-bottom: 0"><span class="agenda-num">14</span> The goose Development Kit</div>
</div>

</div>

<div class="ref">Reference: goose-docs.ai/docs/category/guides</div>

---
class: vcenter
---

<div class="eyebrow">01 &nbsp;·&nbsp; What is an agent?</div>

## Prompt, context, agent

<div class="lead">Three layers, each larger than the last.</div>

<div class="grid grid-cols-3 gap-6 mt-8">

<div class="card">
<h3><span class="accent" style="font-family: var(--font-mono); font-size: 13px">01</span><br/>Prompt</h3>
<p>The instruction, in natural language. On its own a model only produces text. No side effects, no state.</p>
</div>

<div class="card">
<h3><span class="accent" style="font-family: var(--font-mono); font-size: 13px">02</span><br/>Context</h3>
<p>Everything the model can see this turn: conversation history, file contents, tool schemas, project rules. Context quality sets the ceiling on output quality.</p>
</div>

<div class="card is-key">
<h3><span style="font-family: var(--font-mono); font-size: 13px">03</span><br/>Agent</h3>
<p>All three in a loop. The model proposes a tool call, the harness runs it, the result goes back. Repeat until the goal is met or a limit stops it.</p>
</div>

</div>

<div class="ref">Reference: goose-docs.ai/docs/goose-architecture</div>

<!--
Land the point that the model is only one of four layers. Ask the room: who has
written a for-loop around an LLM call? That is an agent in embryo. Everything
else in goose is hardening that loop.
-->

---
class: vcenter
---

<div class="eyebrow">01 &nbsp;·&nbsp; What is an agent?</div>

## The harness decides what the agent can do

<v-clicks>

- The model is stateless and executes nothing. It emits a JSON tool call, and something else runs it.
- That something else decides what the model can touch, what happens when a call fails, and what stays in context.
- Swap the model and you change quality. Swap the harness and you change what the agent can do at all.
- goose, Claude Code, Cursor and Codex are all harnesses. They compete on loop design, tooling and safety.

</v-clicks>

<div class="ref">Reference: goose-docs.ai/docs/goose-architecture</div>

---
class: vcenter
---

<div class="eyebrow">02 &nbsp;·&nbsp; Introduction to goose</div>

## What it actually is

<p style="max-width: 80ch">
goose is a local agent runtime. It pairs an LLM with real tools and runs the loop on your machine: it reads and writes your files, runs shell commands, calls APIs, and keeps working until the task is done. It is not a chat window that suggests snippets.
</p>

<p style="max-width: 80ch">
It ships as a Desktop app and a CLI. Both share one configuration, and you can resume a session in either.
</p>

<div class="grid grid-cols-4 gap-4 mt-6">

<div class="card-sm">
<h4>Open source</h4>
<p>github.com/aaif-goose/goose · AAIF, under the Linux Foundation</p>
</div>

<div class="card-sm">
<h4>Written in Rust</h4>
<p>Local-first runtime; Desktop and CLI share ~/.config/goose</p>
</div>

<div class="card-sm">
<h4>Provider-agnostic</h4>
<p>Anthropic, OpenAI, Gemini, Ollama, OpenRouter, Tetrate and more</p>
</div>

<div class="card-sm">
<h4>MCP-native</h4>
<p>Extensions are Model Context Protocol servers</p>
</div>

</div>

<div class="ref">Reference: goose-docs.ai/docs/quickstart</div>

<!--
Emphasise: local-first and open source. The agent runs on your laptop, your keys
stay in your keyring, and nothing forces you onto one model vendor. Mention the
AAIF move (April 2026). This is now foundation-governed, not a single-company
project.
-->

---
class: vcenter dense
---

<div class="eyebrow">02 &nbsp;·&nbsp; Introduction to goose</div>

## What ships with it

<div class="grid grid-cols-[1fr_1fr] gap-10 mt-2">

<div>

- **Developer extension:** shell, file edit, and the analyze tool
- Memory, Computer Controller, Chat Recall and other bundled MCPs
- Persistent sessions in SQLite, resumable across CLI and Desktop
- Recipes: shareable, parameterised, one-click workflows
- Skills, subagents, hooks, plugins and custom slash commands
- Four permission modes, from full autonomy to read-only chat

</div>

<div>

<div class="term">
  <div><span class="dim">$</span> goose session          <span class="dim"># interactive</span></div>
  <div><span class="dim">$</span> goose run -i plan.md   <span class="dim"># headless</span></div>
  <div><span class="dim">$</span> goose configure        <span class="dim"># providers</span></div>
  <div><span class="dim">$</span> goose info -v          <span class="dim"># all settings</span></div>
  <div><span class="dim">$</span> goose acp              <span class="dim"># ACP server</span></div>
  <div><span class="dim">$</span> goose update           <span class="dim"># upgrade</span></div>
  <div>&nbsp;</div>
  <div>goose <span class="accent">›</span> analyze the auth flow in src/</div>
  <div>        and tell me what calls</div>
  <div>        authenticate()</div>
</div>

</div>

</div>

<div class="ref">Reference: goose-docs.ai/docs/quickstart</div>

---
class: vcenter dense
---

<div class="eyebrow">03 &nbsp;·&nbsp; goose vs Claude Code, Cursor &amp; Codex</div>

## They are all harnesses

<p class="caption" style="margin-bottom: 14px">They differ in openness, form factor and who owns the runtime.</p>

<div class="matrix">

| | goose | Claude Code | Cursor | Codex |
| --- | --- | --- | --- | --- |
| Steward | AAIF / open source | Anthropic | Anysphere | OpenAI |
| Form factor | Desktop app + CLI + ACP server | CLI + IDE + desktop | Full IDE (VS Code fork) + CLI agent | CLI + cloud + IDE extension |
| Openness | Fully open source, Rust | Proprietary client | Proprietary | CLI open source, service is not |
| Model choice | Any provider; swap freely | Anthropic models | Mixed / routed models | OpenAI GPT-5 series |
| Extensibility | MCP extensions, recipes, skills, hooks, subagents | MCP servers, skills, subagents | IDE-centric rules and tooling | Skills, sandboxed execution |
| Where it wins | You own the runtime: embed or fork it | Deep Anthropic model integration | Best in-editor UX | Cloud-delegated long tasks |

</div>

<div class="ref">Reference: goose-docs.ai/docs/guides/acp-providers · /guides/cli-providers</div>

<!--
Be fair here. This is not a takedown. The honest differentiator for goose is that
it is open source, model-agnostic and embeddable. Note the deprecation: CLI
providers are backward-compat only, ACP providers are the supported path and they
preserve MCP extensions.
-->

---
class: vcenter
---

<div class="eyebrow">03 &nbsp;·&nbsp; goose vs Claude Code, Cursor &amp; Codex</div>

## goose can drive the others

<div class="mt-2">
  <span class="badge badge-accent">claude-acp</span>
  <span class="badge badge-accent">codex-acp</span>
</div>

<div class="mt-1">
  <span class="badge">claude-code</span>
  <span class="badge">codex</span>
  <span class="badge">cursor-agent</span>
  <span class="badge">gemini-cli</span>
</div>

<p class="mt-8" style="max-width: 82ch">
Configure <code>claude-acp</code> or <code>codex-acp</code> as ACP providers and goose delegates execution to Claude Code or Codex, while keeping its own sessions, recipes and scheduling.
</p>

<p style="max-width: 82ch">
The older pass-through CLI providers (<code>claude-code</code>, <code>codex</code>, <code>cursor-agent</code>, <code>gemini-cli</code>) still work but are deprecated, and they drop goose’s extension ecosystem.
</p>

<div class="ref">Reference: goose-docs.ai/docs/guides/acp-providers · /guides/cli-providers</div>

---
class: vcenter dense
---

<div class="eyebrow">04 &nbsp;·&nbsp; Installation &amp; configuration</div>

## Desktop, CLI, or both

<p>They share one configuration store.</p>

<div class="grid grid-cols-2 gap-10 mt-2">

<div>

<div class="colhead">1 · Install</div>

```bash
# macOS / Linux - CLI
curl -fsSL https://github.com/aaif-goose/goose/\
  releases/download/stable/download_cli.sh | bash

# macOS via Homebrew
brew install block-goose-cli      # CLI
brew install --cask block-goose   # Desktop

# Windows (PowerShell)
.\download_cli.ps1

goose update                      # upgrade later
```

</div>

<div>

<div class="colhead">2 · Set an LLM provider</div>

<div class="term">
  <div><span class="dim">$</span> goose configure</div>
  <div>&nbsp;</div>
  <div><span class="dim">┌</span>  goose-configure</div>
  <div><span class="accent">◇</span>  What would you like to configure?</div>
  <div><span class="dim">│</span>  Configure Providers</div>
  <div><span class="accent">◇</span>  Which model provider should we use?</div>
  <div><span class="dim">│</span>  Anthropic</div>
  <div><span class="accent">◇</span>  Provider requires ANTHROPIC_API_KEY</div>
  <div><span class="dim">│</span>  ▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪</div>
  <div><span class="ok">└</span>  Configuration saved successfully</div>
</div>

</div>

</div>

<div class="ref">Reference: goose-docs.ai/docs/getting-started/installation</div>

<!--
Checkpoint: everyone should have goose running and a provider configured before
we move on. Free options: Google Gemini free tier, or Ollama for fully local.
Windows users, decline the keyring prompt and use environment variables if you
hit keyring errors.
-->

---
class: vcenter
---

<div class="eyebrow">04 &nbsp;·&nbsp; Installation &amp; configuration</div>

## Four things to know before you start

<div class="grid grid-cols-2 gap-5 mt-4">

<div class="card is-key">
<h3>Keys live in the keyring</h3>
<p>Never in <code>config.yaml</code>; goose ignores keys there. Use the keyring, <code>secrets.yaml</code>, or an env var.</p>
</div>

<div class="card">
<h3>Desktop first-run options</h3>
<p>Quick setup with an API key, ChatGPT subscription, Tetrate Agent Router, or OpenRouter.</p>
</div>

<div class="card">
<h3>Tool calling matters</h3>
<p>goose leans on tool calling, and the docs say it works best with Claude 4 models.</p>
</div>

<div class="card">
<h3>Pin versions in CI</h3>
<p>Set <code>GOOSE_VERSION</code> for reproducible, non-interactive installs in pipelines.</p>
</div>

</div>

<p class="mt-7">
Run <code>goose info -v</code>. It prints every active setting and where it came from.
</p>

<div class="ref">Reference: goose-docs.ai/docs/getting-started/installation</div>

---
class: vcenter dense
---

<div class="eyebrow">05 &nbsp;·&nbsp; The goose folder structure</div>

## Where state lives

<div class="grid grid-cols-2 gap-10 mt-2">

<div>

```text
~/.config/goose/              # macOS + Linux
├─ config.yaml                provider, model,
│                             extensions, GOOSE_*
├─ permission.yaml            tool permission levels
├─ secrets.yaml               keys, if no keyring
├─ permissions/
│  └─ tool_permissions.json   runtime decisions
└─ prompts/                   custom templates

~/.local/share/goose/
├─ sessions/sessions.db       SQLite (v1.10.0+)
└─ recipes/                   saved recipes
```

</div>

<div>

```text
<your-repo>/
├─ AGENTS.md | .goosehints    project context
└─ .gooseignore               paths goose must
                              not touch
```

<div class="colhead mt-7">Precedence: highest wins</div>

1. Environment variables
2. `config.yaml` settings
3. Built-in defaults

</div>

</div>

<p class="caption mt-4">
Windows: <code>%APPDATA%\Block\goose\config\config.yaml</code>
</p>

<div class="ref">Reference: goose-docs.ai/docs/guides/config-files · /guides/environment-variables</div>

<!--
Open the config file live and walk it. Point out that extensions are just YAML
entries with a type: builtin, platform, stdio, streamable_http, frontend,
inline_python. Show available_tools as a token-saving filter.
-->

---
class: vcenter
---

<div class="eyebrow">05 &nbsp;·&nbsp; The goose folder structure</div>

## Settings worth knowing on day one

<div class="grid grid-cols-2 gap-5 mt-4">

<div class="card-sm">
<h4><code>GOOSE_MODE</code></h4>
<p>auto | approve | smart_approve | chat</p>
</div>

<div class="card-sm">
<h4><code>GOOSE_MAX_TURNS</code></h4>
<p>Turns without input (default 1000)</p>
</div>

<div class="card-sm">
<h4><code>GOOSE_AUTO_COMPACT_THRESHOLD</code></h4>
<p>Default 0.8</p>
</div>

<div class="card-sm">
<h4><code>GOOSE_TEMPERATURE</code>, <code>GOOSE_MAX_TOKENS</code></h4>
<p>Sampling and output ceilings</p>
</div>

<div class="card-sm">
<h4><code>GOOSE_ALLOWLIST</code></h4>
<p>Restrict installable extensions</p>
</div>

<div class="card-sm">
<h4><code>SECURITY_PROMPT_ENABLED</code></h4>
<p>Injection detection</p>
</div>

</div>

<div class="ref">Reference: goose-docs.ai/docs/guides/environment-variables</div>

---
class: vcenter
---

<div class="eyebrow">05 &nbsp;·&nbsp; The goose folder structure</div>

## API keys in config.yaml are ignored

<div class="warn mt-4">
<div class="warn-label">silent failure</div>
<p style="margin: 0">
goose does not read provider API keys from <code>config.yaml</code>. A key there is ignored, and fails later with “No api key passed in.” Store it in the system keyring with <code>goose configure</code>, or in <code>secrets.yaml</code> when there is no keyring, such as on headless servers, in containers and in CI. You can also export the provider’s environment variable, which wins over stored secrets.
</p>
</div>

<p class="mt-8">
Editing these files directly needs a restart before existing sessions see the change.
</p>

<div class="ref">Reference: goose-docs.ai/docs/guides/config-files</div>

---
class: vcenter dense
---

<div class="eyebrow">06 &nbsp;·&nbsp; Session management</div>

## A session is one continuous interaction

<p>goose stores it and lets you resume it.</p>

<div class="grid grid-cols-3 gap-4 mt-4">

<div class="card-sm">
<h4>Start and name</h4>
<p>goose names the session from your first prompt. IDs use YYYYMMDD_&lt;count&gt;. Set GOOSE_DISABLE_SESSION_NAMING in CI.</p>
</div>

<div class="card-sm">
<h4>Resume</h4>
<p>goose session -r --name &lt;name&gt;. The 10 most recent sit in the Desktop sidebar; older ones come from Session History.</p>
</div>

<div class="card-sm">
<h4>Search</h4>
<p>Cmd+F within a session, or across sessions from history. Or ask goose: the Chat Recall extension searches your history.</p>
</div>

<div class="card-sm">
<h4>Duplicate vs fork</h4>
<p>Duplicate copies a whole session to reuse its setup. Fork branches from a specific edited message to explore a different path.</p>
</div>

<div class="card-sm">
<h4>Import and export</h4>
<p>Export any session to JSON for backup, sharing or migration. Import creates a new session rather than overwriting.</p>
</div>

<div class="card-sm">
<h4>Smart context</h4>
<p>Automatic compaction at 80% of the window by default, plus a max-turns ceiling so a runaway loop stops on its own.</p>
</div>

</div>

<div class="ref">Reference: goose-docs.ai/docs/guides/sessions</div>

<!--
The stale-session point is the practical one. Long sessions accumulate
contradictory context and the model starts fighting its own history. New task,
new session. Treat it like a clean branch.
-->

---
class: vcenter dense
---

<div class="eyebrow">06 &nbsp;·&nbsp; Session management</div>

## Practitioner rules

<div class="grid grid-cols-[1.05fr_0.95fr] gap-10 mt-2">

<div>

- Sessions save on exit. Nothing to commit.
- Start in Desktop, resume in the CLI. One database, both interfaces.
- New task, new session. A stale one fills with contradictory context and the model starts fighting its own history.
- Delete in Desktop and it goes from the CLI too. No undo.

</div>

<div>

<div class="term">
  <div><span class="dim">$</span> goose session</div>
  <div><span class="dim">$</span> goose session list -l 1</div>
  <div>  20260213_9 - react-migration</div>
  <div>  2026-02-13 16:20 UTC</div>
  <div>&nbsp;</div>
  <div><span class="dim">$</span> goose session -r --name react-migration</div>
  <div>&nbsp;</div>
  <div><span class="dim">$</span> sqlite3 ~/.local/share/goose/\</div>
  <div>    sessions/sessions.db \</div>
  <div>    "SELECT id, description FROM sessions"</div>
</div>

</div>

</div>

<div class="ref">Reference: goose-docs.ai/docs/guides/sessions</div>

---
class: vcenter dense
---

<div class="eyebrow">07 &nbsp;·&nbsp; Context engineering</div>

## Define how you work once

<p class="caption" style="margin-bottom: 0">Instead of re-explaining it every session. Twelve guides cover this area.</p>

<div class="grid grid-cols-4 gap-2 mt-3.5">

<div class="card-sm">
<h4>.goosehints</h4>
<p>Project context, conventions and preferences. goose loads it at session start.</p>
</div>

<div class="card-sm">
<h4>Agent Skills</h4>
<p>Reusable instruction sets: workflows, scripts, resources. Loaded on demand, not always on.</p>
</div>

<div class="card-sm">
<h4>Custom Agents</h4>
<p>Create, edit, import and export specialised agents with reusable prompts and metadata.</p>
</div>

<div class="card-sm">
<h4>Plugins</h4>
<p>Installable packages that bundle skills, hooks and other reusable components.</p>
</div>

<div class="card-sm">
<h4>Hooks</h4>
<p>Run your own scripts on session start, prompt submit, tool call, file edit or shell execution.</p>
</div>

<div class="card-sm">
<h4>Slash Commands</h4>
<p>Custom /shortcuts that fire reusable instructions or launch a recipe in any chat.</p>
</div>

<div class="card-sm">
<h4>Prompt Templates</h4>
<p>Override the built-in prompts that govern how goose responds, plans and compacts.</p>
</div>

<div class="card-sm">
<h4>Subagents</h4>
<p>Delegate focused work to isolated instances, in sequence or in parallel, without polluting your context.</p>
</div>

<div class="card-sm">
<h4>.gooseignore</h4>
<p>Global or per-project rules for files and directories goose must never read or touch.</p>
</div>

<div class="card-sm">
<h4>Planning Mode</h4>
<p>Break complex work into reviewed steps before implementation starts. Supports a separate planner model.</p>
</div>

<div class="card-sm">
<h4>Persistent Instructions</h4>
<p>Goes into working memory every turn. For guardrails that must not drift.</p>
</div>

<div class="card-sm">
<h4>Memory Extension</h4>
<p>Durable knowledge across sessions: commands, snippets, preferences goose can recall later.</p>
</div>

</div>

<div class="ref">Reference: goose-docs.ai/docs/guides/context-engineering (12 guides)</div>

<!--
This is the slide to slow down on. Context engineering is where practitioners get
the biggest wins. Demo: add a .goosehints file with build commands and coding
conventions, then show the difference in a fresh session.
-->

---
class: vcenter
---

<div class="eyebrow">07 &nbsp;·&nbsp; Context engineering</div>

## Pick the right tool

<div class="grid grid-cols-4 gap-4 mt-4">

<div class="card">
<h3>Hint</h3>
<p><code>.goosehints</code> always loads. Keep it small and stable.</p>
</div>

<div class="card">
<h3>Skill</h3>
<p>Skills load on demand. Put long procedures there.</p>
</div>

<div class="card">
<h3>Memory</h3>
<p>Memory persists across sessions. Use it for facts you will need again.</p>
</div>

<div class="card">
<h3>Persistent instruction</h3>
<p>Re-injects every turn. Reserve it for hard guardrails.</p>
</div>

</div>

<p class="mt-8" style="max-width: 82ch">
Persistent instructions cost tokens on every call. Everything competes for the same context window, so <em>budget it</em>.
</p>

<div class="ref">Reference: goose-docs.ai/docs/guides/context-engineering</div>

---
class: vcenter dense
---

<div class="eyebrow">08 &nbsp;·&nbsp; Recipes &amp; subrecipes</div>

## Package a working session

<p class="caption" style="margin-bottom: 14px">Tools, prompt, parameters and settings, in one file a teammate launches in one click.</p>

<div class="grid grid-cols-[1.15fr_0.85fr] gap-10">

<div>

<div class="colhead">What a recipe carries</div>

- The instructions and goal for the session
- Which extensions must be enabled
- Parameters the runner fills in at launch
- Provider, model and behaviour settings
- Optional subrecipes for delegated sub-tasks

</div>

<div>

<div class="colhead">Subrecipes</div>

<p>
A recipe can call other recipes, in sequence or several in parallel. This is how you fan out repetitive work, such as auditing twenty services or migrating thirty files, without one context window holding all of it.
</p>

</div>

</div>

<div class="ref">Reference: goose-docs.ai/docs/guides/recipes · goose-docs.ai/recipes</div>

<!--
Frame recipes as the unit of team scale. One engineer works out a workflow; a
recipe turns that into something the rest of the team runs without rediscovering
it. Show the Recipe Cookbook and the deeplink generator on the docs site.
-->

---
class: vcenter dense
---

<div class="eyebrow">08 &nbsp;·&nbsp; Recipes &amp; subrecipes</div>

## Bind one to a slash command

<div class="grid grid-cols-[1fr_1fr] gap-10 mt-2">

<div>

```yaml
# config.yaml
slash_commands:
  - command: "run-tests"
    recipe_path: "/path/to/recipe.yaml"
  - command: "daily-standup"
    recipe_path: "~/.local/share/goose/\
                  recipes/standup.yaml"

# point goose at a shared team recipe repo
GOOSE_RECIPE_GITHUB_REPO:
  "aaif-goose/goose-recipes"
```

<div class="term mt-4">
  <div>goose <span class="accent">›</span> /run-tests</div>
</div>

</div>

<div>

<div class="colhead">In the docs</div>

<div class="row-item">
<h4>Reusable Recipes</h4>
<p>Share a session setup others launch with one click, including via deeplink.</p>
</div>

<div class="row-item">
<h4>Recipe Reference</h4>
<p>The full technical schema for authoring recipes from the CLI.</p>
</div>

<div class="row-item">
<h4>Saving Recipes</h4>
<p>Save, organise and discover recipes; back them with a GitHub repo.</p>
</div>

<div class="row-item">
<h4>Recipe Cookbook</h4>
<p>Ready-made recipes for common development scenarios, ready to adapt.</p>
</div>

</div>

</div>

<div class="ref">Reference: goose-docs.ai/docs/guides/recipes</div>

---
class: vcenter
---

<div class="eyebrow">09 &nbsp;·&nbsp; Managing tools &amp; permissions</div>

## GOOSE_MODE sets four levels of autonomy

<div class="grid grid-cols-4 gap-4 mt-4">

<div class="card">
<h3>auto</h3>
<p>goose runs tools without asking. Fast, and only for a sandbox or a throwaway branch.</p>
</div>

<div class="card is-key">
<h3>smart_approve</h3>
<p>goose judges risk and prompts only for consequential actions. The everyday default.</p>
</div>

<div class="card">
<h3>approve</h3>
<p>Every tool call waits for your yes. Slow, but right when the target is production.</p>
</div>

<div class="card">
<h3>chat</h3>
<p>No tools run. Conversation only, for design discussion and code review.</p>
</div>

</div>

<div class="ref">Reference: goose-docs.ai/docs/guides/managing-tools</div>

<!--
Guidance: start everyone in smart_approve. Let them feel the prompts, then explain
why auto mode belongs in a container or a disposable branch, never on a machine
with production credentials loaded.
-->

---
class: vcenter dense
---

<div class="eyebrow">09 &nbsp;·&nbsp; Managing tools &amp; permissions</div>

## Underneath the global mode

<div class="grid grid-cols-3 gap-4 mt-4">

<div class="card-sm">
<h4>Tool Permissions</h4>
<p>Per-tool control layered under the global mode, stored in permission.yaml.</p>
</div>

<div class="card-sm">
<h4>Code Mode</h4>
<p>Rather than pre-loading every tool schema, goose discovers and calls MCP tools on demand.</p>
</div>

<div class="card-sm">
<h4>Adjust Tool Output</h4>
<p>Dial verbosity from full transcripts to clean summaries with GOOSE_CLI_MIN_PRIORITY.</p>
</div>

<div class="card-sm">
<h4>Tool Filtering</h4>
<p>available_tools in config.yaml loads only the tools you need. Fewer schemas, fewer tokens.</p>
</div>

<div class="card-sm">
<h4>Ollama Tool Shim</h4>
<p>Experimental interpreter layer that adds tool calling to local models without native support.</p>
</div>

<div class="card-sm">
<h4>Extension Allowlist</h4>
<p>GOOSE_ALLOWLIST restricts which MCP servers install. Needed in corporate estates.</p>
</div>

</div>

<div class="ref">Reference: goose-docs.ai/docs/guides/managing-tools</div>

---
class: vcenter
---

<div class="eyebrow">10 &nbsp;·&nbsp; Security &amp; safe autonomy</div>

## An agent with shell access is a supply-chain surface

<div class="grid grid-cols-2 gap-6 mt-4">

<div class="card is-key">
<h3>Adversary Mode</h3>
<p>A second agent watches tool calls as they run, so there is another opinion if the first agent goes somewhere it should not.</p>
<p class="mt-3">It is a runtime guard, not a policy file. It reads what runs, not what was declared up front.</p>
</div>

<div class="card">
<h3>Prompt Injection Detection</h3>
<p>Screens for hijacking instructions before they run. The file you read, the issue you fetched and the web page you scraped are all untrusted input.</p>
<p class="mt-3"><code>SECURITY_PROMPT_ENABLED</code> turns it on; <code>SECURITY_PROMPT_THRESHOLD</code> (default 0.8) tunes strictness. You can self-host an ML classifier endpoint against a published API spec.</p>
</div>

</div>

<div class="ref">Reference: goose-docs.ai/docs/guides/security · /guides/sandbox · /guides/allowlist</div>

<!--
Make the supply-chain point concretely: an MCP server runs on your machine with
your credentials. The threat model is not the model going rogue, it is a poisoned
tool description or a malicious README instructing your agent.
-->

---
class: vcenter
---

<div class="eyebrow">10 &nbsp;·&nbsp; Security &amp; safe autonomy</div>

## Four more controls

<div class="grid grid-cols-4 gap-4 mt-4">

<div class="card-sm">
<h4>macOS Sandbox</h4>
<p>Apple sandbox controls over file access, network connections and process restrictions for goose Desktop.</p>
</div>

<div class="card-sm">
<h4>Extension Allowlist</h4>
<p>Point GOOSE_ALLOWLIST at a URL of approved MCP servers so only vetted extensions install.</p>
</div>

<div class="card-sm">
<h4>.gooseignore</h4>
<p>Keep secrets, key material and vendored directories out of the agent’s reach.</p>
</div>

<div class="card-sm">
<h4>Secrets handling</h4>
<p>Keyring by default. secrets.yaml is a plaintext fallback, so treat it as one in CI and containers.</p>
</div>

</div>

<div class="warn mt-8">
<div class="warn-label">before you connect any mcp server</div>
<p style="margin: 0">
Read what it does. An extension is code, and you are giving it your agent’s privileges. The docs have a guide on judging whether an MCP server is safe.
</p>
</div>

<div class="ref">Reference: goose-docs.ai/docs/guides/security</div>

---
class: vcenter dense
---

<div class="eyebrow">11 &nbsp;·&nbsp; MCP surface &amp; platform operations</div>

## Protocol capabilities, and running at scale

<div class="grid grid-cols-2 gap-10 mt-2">

<div>

<div class="colhead">MCP protocol capabilities</div>

<div class="row-item">
<h4>MCP Sampling</h4>
<p>An MCP server can ask goose’s model to think, which turns a passive tool into one that reasons.</p>
</div>

<div class="row-item">
<h4>MCP Elicitation</h4>
<p>Extensions ask you for structured input mid-task rather than guessing or failing.</p>
</div>

<div class="row-item">
<h4>MCP Roots</h4>
<p>How goose shares your working directory with roots-aware extensions.</p>
</div>

<div class="row-item">
<h4>MCP Apps / MCP-UI</h4>
<p>An extension can render an interactive UI surface inside the chat.</p>
</div>

</div>

<div>

<div class="colhead">Running goose at scale</div>

<div class="row-item">
<h4>Multi-Model Config</h4>
<p>Cheap model for routine turns, strong model for planning. Trades cost against results.</p>
</div>

<div class="row-item">
<h4>LLM Rate Limits</h4>
<p>How to work within provider request ceilings without stalling a run.</p>
</div>

<div class="row-item">
<h4>Remote Server</h4>
<p>Run goose serve on a VM and point Desktop at it. Heavy work leaves your laptop.</p>
</div>

<div class="row-item">
<h4>Run Tasks</h4>
<p>goose run with a file or one-liner: headless execution for CI and cron.</p>
</div>

</div>

</div>

<div class="ref">Reference: goose-docs.ai/docs/category/guides · full index</div>

<!--
Do not read this slide line by line. Point at it, say these exist, and flag the
three that matter most for this audience: multi-model config for cost, remote
server for heavy runs, and run tasks for CI integration.
-->

---
class: vcenter
---

<div class="eyebrow">11 &nbsp;·&nbsp; MCP surface &amp; platform operations</div>

## And the rest of the index

<div class="grid grid-cols-2 gap-6 mt-4">

<div class="card">
<h3>Custom Distributions</h3>
<p>Fork goose into your own branded distro with preconfigured providers and bundled extensions.</p>
</div>

<div class="card">
<h3>Logging &amp; Usage Data</h3>
<p>Unified local storage of conversations; OTLP export; telemetry is opt-in.</p>
</div>

</div>

<div class="colhead mt-8">Also in the guides</div>

<div>
  <span class="badge">Enhanced Code Editing</span>
  <span class="badge">File Management</span>
  <span class="badge">Terminal Integration</span>
  <span class="badge">Desktop Sidebar</span>
  <span class="badge">Offline Docs</span>
  <span class="badge">CLI Commands</span>
  <span class="badge">Quick Tips</span>
  <span class="badge">VMware Tanzu</span>
</div>

<div class="ref">Reference: goose-docs.ai/docs/category/guides · full index</div>

---
class: vcenter
---

<div class="eyebrow">12 &nbsp;·&nbsp; The Agent Client Protocol</div>

## ACP is to agents what LSP was to language tooling

<p>One interface, many clients, many agents.</p>

<div class="acp mt-8">

<div class="acp-box">
  <span class="tag">Client</span>
  Zed · JetBrains · goose Desktop · your own app
</div>

<div class="acp-link">
  <span class="wire">← &nbsp;ACP&nbsp; →</span>
  stdio / JSON-RPC
</div>

<div class="acp-box is-agent">
  <span class="tag">Agent</span>
  goose acp, the runtime, running as its own process or daemon
</div>

</div>

<p class="caption mt-6">
The agent then reaches its tools over <strong>MCP</strong>: extensions and tools, one layer further down.
</p>

<div class="ref">Reference: agentclientprotocol.com · goose-docs.ai/docs/guides/acp-clients · /guides/acp-providers</div>

<!--
The LSP analogy lands well with engineers. Before LSP, every editor implemented
every language. ACP is the same bet for agents: implement the protocol once and
any compliant client can drive any compliant agent.
-->

---
class: vcenter
---

<div class="eyebrow">12 &nbsp;·&nbsp; The Agent Client Protocol</div>

## It runs in both directions

<div class="grid grid-cols-2 gap-6 mt-4">

<div class="card">
<h3>1 · goose as an ACP server</h3>
<p><code>goose acp</code> starts goose as an ACP server over stdio. Editors that speak ACP, such as Zed and JetBrains, connect to it and drive the agent from inside the editor.</p>
<p class="mt-3">The interface and the runtime stay separate processes.</p>
</div>

<div class="card">
<h3>2 · ACP agents as goose providers</h3>
<p>goose can also delegate to an external ACP agent such as Claude Code (<code>claude-acp</code>) or Codex (<code>codex-acp</code>). That agent runs the tools, while goose passes its configured extensions through as MCP servers.</p>
<p class="mt-3">You keep goose’s sessions, recipes and scheduling on top of someone else’s model subscription.</p>
</div>

</div>

<p class="mt-7" style="max-width: 86ch">
ACP separates the interface from the runtime. One protocol means an agent is not <em>trapped inside the client that shipped it</em>, and it is the protocol the goose Development Kit builds on.
</p>

<div class="ref">Reference: agentclientprotocol.com · goose-docs.ai/docs/guides/acp-clients</div>

---
class: vcenter
---

<div class="eyebrow">13 &nbsp;·&nbsp; goose architecture</div>

## Three components, one interactive loop

<p>This is the whole system.</p>

<div class="grid grid-cols-3 gap-6 mt-6">

<div class="card">
<h3>Interface</h3>
<p>Desktop app or CLI. Collects your input, renders output, and starts agents, more than one at a time if needed.</p>
</div>

<div class="card is-key">
<h3>Agent</h3>
<p>The core logic that runs the interactive loop: calls the provider, executes tool calls, revises context, handles errors.</p>
</div>

<div class="card">
<h3>Extensions</h3>
<p>MCP servers exposing tools. Built in, external, or ones you write. Capability comes from here.</p>
</div>

</div>

<div class="ref">Reference: goose-docs.ai/docs/goose-architecture · /goose-architecture/extensions-design</div>

<!--
Draw the loop on the whiteboard as you talk. Step 5 is the one people miss.
Context revision is why goose stays usable on long tasks where a naive loop would
blow the window in twenty turns.
-->

---
class: vcenter dense
---

<div class="eyebrow">13 &nbsp;·&nbsp; goose architecture</div>

## The interactive loop

<div class="loop-steps mt-6">

<div class="loop-step">
<div class="n">1</div>
<h4>Human request</h4>
<p>You state a goal.</p>
</div>

<div class="loop-step">
<div class="n">2</div>
<h4>Provider chat</h4>
<p>Request plus available tool schemas go to the LLM.</p>
</div>

<div class="loop-step">
<div class="n">3</div>
<h4>Tool call</h4>
<p>Model emits JSON; goose runs it and collects results.</p>
</div>

<div class="loop-step">
<div class="n">4</div>
<h4>Response to model</h4>
<p>Results return. More tools needed? Repeat 2 to 4.</p>
</div>

<div class="loop-step">
<div class="n">5</div>
<h4>Context revision</h4>
<p>goose prunes old or irrelevant content to manage tokens.</p>
</div>

<div class="loop-step">
<div class="n">6</div>
<h4>Model response</h4>
<p>Final answer to you. The loop restarts on your reply.</p>
</div>

</div>

<div class="loop-back mt-6"></div>

<div class="ref">Reference: goose-docs.ai/docs/goose-architecture</div>

---
class: vcenter
---

<div class="eyebrow">13 &nbsp;·&nbsp; goose architecture</div>

## Two properties that make it survivable

<div class="grid grid-cols-2 gap-6 mt-4">

<div class="card">
<h3>Errors do not break the flow</h3>
<p>Invalid JSON, a missing tool, a failed command: goose catches these and returns them to the model as tool responses. The model then has what it needs to correct itself and carry on, instead of the run dying.</p>
</div>

<div class="card">
<h3>Context revision keeps the bill down</h3>
<p>Summarise with smaller, faster models · drop stale content algorithmically · find-and-replace rather than rewriting whole files · ripgrep to skip system files · compress verbose command output.</p>
</div>

</div>

<div class="ref">Reference: goose-docs.ai/docs/goose-architecture/extensions-design</div>

---
class: vcenter
---

<div class="eyebrow">14 &nbsp;·&nbsp; The goose Development Kit</div>

## Not one agent app, but the infrastructure

<div class="grid grid-cols-[1.1fr_0.9fr] gap-10 mt-4">

<div>

<div class="colhead">The thesis</div>

<p>
GDK is an open-source SDK in Rust for building agent applications that are model-agnostic, run locally, and do not depend on one provider. Instead of every team rebuilding the agent loop, tool calling and context management, they share the parts.
</p>

</div>

<div>

<div class="colhead">Two ways to integrate</div>

<div class="card-sm">
<h4>ACP</h4>
<p>Talk to goose as a separate process or daemon, keeping the runtime independent of your interface.</p>
</div>

<div class="card-sm mt-3">
<h4>Rust API</h4>
<p>Embed the agent in your application. goose Desktop and the goose CLI are built this way.</p>
</div>

</div>

</div>

<div class="ref">Governed by the Agentic AI Foundation, under the Linux Foundation</div>

<!--
Close on the platform story: goose today is a good agent; GDK is the bet that the
agent loop becomes shared infrastructure the way the Lightning Development Kit
did for payments. Invite the room to contribute. It is foundation-governed and
open to outside contributors.
-->

---
class: vcenter
---

<div class="eyebrow">14 &nbsp;·&nbsp; The goose Development Kit</div>

## Building blocks on offer

<div class="mt-4">
  <span class="badge badge-accent">Agent orchestration</span>
  <span class="badge badge-accent">Flexible agent loop</span>
  <span class="badge">In-process local models</span>
  <span class="badge">50+ model providers</span>
  <span class="badge">Routing &amp; model selection</span>
  <span class="badge">Context management</span>
  <span class="badge">Tools &amp; MCP</span>
  <span class="badge">Memory</span>
  <span class="badge">Remote execution</span>
  <span class="badge">Automations &amp; scheduling</span>
  <span class="badge">Skills</span>
  <span class="badge">Subagents</span>
  <span class="badge">Code mode</span>
  <span class="badge">Slash command infra</span>
</div>

<div class="linkrow mt-10">
  <div><div class="k">Docs</div><div class="v">goose-docs.ai</div></div>
  <div><div class="k">Source</div><div class="v">github.com/aaif-goose/goose</div></div>
  <div><div class="k">Community</div><div class="v">discord.gg/goose-oss</div></div>
  <div><div class="k">Recipes</div><div class="v">goose-docs.ai/recipes</div></div>
  <div><div class="k">Skills</div><div class="v">goose-docs.ai/skills</div></div>
</div>

---
class: cover vcenter
---

<div class="eyebrow">Thank you</div>

# Open standards over closed platforms.

<div class="lead mt-6">Governed by the Agentic AI Foundation, under the Linux Foundation.</div>

<div class="mt-10">
  <span class="badge badge-accent">goose-docs.ai</span>
  <span class="badge badge-accent">github.com/aaif-goose/goose</span>
  <span class="badge badge-accent">discord.gg/goose-oss</span>
</div>

<div class="caption mt-10">
  <div>Azeez Syed &nbsp;·&nbsp; AIYatra</div>
  <div class="mt-2">Khaja Moinuddin Mohammad &nbsp;·&nbsp; Organiser and founder, AIYatra</div>
  <div class="mt-4 accent">Kubernetes over Koffee &nbsp;·&nbsp; AIYatra</div>
</div>

---
class: cover vcenter
---

<div class="grid grid-cols-[1fr_auto] gap-16 items-center">

<div>

<div class="eyebrow">Community</div>

# Join AIYatra

<div class="lead mt-4">An AI learning journey out of Manikonda, Hyderabad. Talks, workshops and hands-on sessions.</div>

<div class="mt-8">
  <span class="badge badge-accent">meetup.com/aiyatra</span>
</div>

</div>

<div>

<MeetupQr :size="200" />

<div class="caption mt-3" style="text-align: center">Scan to join</div>

</div>

</div>
