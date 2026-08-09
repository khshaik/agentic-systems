# The Agentic Systems Lifecycle

[← Project README](../README.md) · [Architecture and frameworks →](agent-architectures-and-frameworks.md)

```text
Topics
1. When to use Multi Agents?
2. Agent to Agent (A2A) Communication
3. Planning & Coordination
4. Environment & Memory Architecture
5. Safety, Permissions & Governance
6. Observability & Evaluation
7. Scaling & Reliability
8. Frameworks & Build Options
9. Anti-Patterns & Design Checklists
```

This page translates the AILaunchPad session agenda into an end-to-end engineering guide. The nine topics are intentionally sequential: decide whether agents are justified before designing their communication; design coordination before state; secure state and tools before scaling; make the system observable before claiming reliability.

## Lifecycle at a glance

| # | Stage | Core question | Primary artifact | Exit criterion |
|---:|---|---|---|---|
| 1 | Multi-agent suitability | Is decomposition worth the coordination cost? | Decision record and baseline | Multi-agent benefit is measurable |
| 2 | Agent-to-agent communication | How do agents exchange work unambiguously? | Message and hand-off protocol | Ownership and termination are explicit |
| 3 | Planning and coordination | Who plans, delegates, verifies, and stops? | Orchestration topology | Every task has owner, budget, and completion rule |
| 4 | Environment and memory | What is shared, private, durable, and fresh? | State/memory architecture | State has schema, lifecycle, and provenance |
| 5 | Safety, permissions, governance | What may each agent see and do? | Capability and policy matrix | Least privilege and action approval are enforced |
| 6 | Observability and evaluation | Can we explain behavior and measure quality? | Trace model, KPIs, eval suite | Regressions and incidents are detectable |
| 7 | Scaling and reliability | How does the system survive load and failure? | SLO and recovery design | Recovery, isolation, and budgets are tested |
| 8 | Framework and build options | Which abstraction fits the required control? | Architecture decision record | Framework choice follows requirements |
| 9 | Anti-pattern and design review | What commonly fails, and what remains unsafe? | Launch checklist and risk register | Blocking risks have owners and mitigations |

## 1. When should you use multiple agents?

| Lens | Guidance |
|---|---|
| **What** | Multiple agents are separately configured decision-makers that cooperate through messages, shared state, delegated tasks, or tools. |
| **Why** | Use specialization to isolate responsibilities, parallelize independent work, cross-check important outputs, or enforce different permissions. |
| **How** | Begin with a single-agent baseline. Decompose only where stages have distinct inputs, tools, evaluation rubrics, owners, or security boundaries. |
| **When** | Prefer multiple agents for heterogeneous expertise, independently testable stages, dynamic routing, large-context separation, or explicit maker/checker workflows. Stay single-agent for short, linear, tightly coupled tasks. |

### Decision test

Use a multi-agent design when at least one benefit can be measured:

- **quality:** specialization or independent verification improves task success;
- **latency:** independent branches can execute concurrently;
- **governance:** different roles need different data/tool permissions;
- **maintainability:** components require separate prompts, owners, versions, or tests;
- **resilience:** one failed specialist can be retried or replaced without restarting everything.

Account for the costs: additional model calls, context serialization, routing errors, duplicated work, harder debugging, and wider attack surface. A “crew” that merely asks three agents the same question is usually an expensive ensemble, not a designed system.

## 2. Agent-to-agent communication

<p align="center">
  <img src="../AILaunchPad/2.png" alt="Turn-taking and hand-off protocols" width="46%" />
  <img src="../AILaunchPad/3.png" alt="Arbitration and conflict resolution" width="46%" />
</p>

| Lens | Guidance |
|---|---|
| **What** | A2A communication is the protocol for requests, responses, task transfer, results, errors, and control between agents. |
| **Why** | Natural-language chat alone leaves ownership, status, ordering, and failure semantics ambiguous. |
| **How** | Use typed envelopes, correlation IDs, bounded payloads, role identity, status, timestamps, provenance, and explicit hand-off/acknowledgement. |
| **When** | Required whenever agents execute asynchronously, use different runtimes, share a conversation, negotiate ownership, or can disagree. |

### Minimal message contract

```json
{
  "message_id": "uuid",
  "trace_id": "uuid",
  "sender": "researcher",
  "recipient": "writer",
  "type": "task_result",
  "schema_version": "1.0",
  "payload": {},
  "provenance": [],
  "status": "complete",
  "created_at": "ISO-8601",
  "expires_at": "ISO-8601"
}
```

### Protocol choices

| Pattern | How it works | Use when | Main risk |
|---|---|---|---|
| Round-robin | Fixed speaker order | Structured review or ideation | Wasted turns |
| Leader-directed | Supervisor selects next agent | Hierarchical work | Bottleneck or supervisor bias |
| Event-driven | Agents subscribe to typed events | Long-running/asynchronous flows | Causality and duplicate delivery |
| Direct hand-off | Current owner transfers task and context | Sequential specialist chain | Context loss |
| Blackboard | Agents read/write shared state | Shared-world problem solving | Races and stale state |
| Voting/judging | Candidates are scored or arbitrated | High-value conflicting answers | Correlated model errors |

Define timeout, retry, rejection, cancellation, escalation, and duplicate-message semantics. The AILaunchPad error guidance recommends backoff, dead-letter handling, timeouts, and fallback agents:

<p align="center">
  <img src="../AILaunchPad/4.png" alt="Error channels and retries" width="850" />
</p>

## 3. Planning and coordination

<p align="center">
  <img src="../AILaunchPad/6.png" alt="Global planner and hierarchical workflows" width="46%" />
  <img src="../AILaunchPad/7.png" alt="Delegation and negotiation" width="46%" />
</p>

| Lens | Guidance |
|---|---|
| **What** | Planning decomposes goals into work; coordination assigns, orders, synchronizes, verifies, and terminates that work. |
| **Why** | Without a single coordination model, agents can duplicate tasks, issue conflicting plans, wait cyclically, or optimize local goals at the expense of the system objective. |
| **How** | Choose a topology—deterministic workflow, supervisor/worker, planner/executor, router/specialists, or decentralized negotiation—and define budgets plus completion criteria. |
| **When** | Use deterministic workflows for known business processes; dynamic planners when task structure is genuinely unknown; hierarchical delegation when specialists and consolidation are clear. |

### Planning topology matrix

| Topology | Control | Adaptability | Best fit |
|---|---:|---:|---|
| Fixed sequential DAG | High | Low | Regulated/repeatable processes |
| Conditional graph | High | Medium | Known branches and recovery paths |
| Router + specialists | Medium–high | Medium | Intent/domain classification |
| Planner + workers | Medium | High | Open-ended task decomposition |
| Peer negotiation | Low | High | Research/simulation experiments |

Use **one authoritative plan** unless the design explicitly compares candidate plans. A worker may plan its own steps, but it should not silently redefine the global objective.

### Stop conditions and human pauses

<p align="center">
  <img src="../AILaunchPad/8.png" alt="Stop conditions and budgets" width="46%" />
  <img src="../AILaunchPad/9.png" alt="Planned pauses and human approval" width="46%" />
</p>

Every run needs:

- maximum agent turns, tool calls, tokens, cost, and elapsed time;
- explicit success and partial-success states;
- no-progress and repeated-output detection;
- a kill switch and cancellation propagation;
- review gates before irreversible or high-impact actions; and
- escalation after a bounded number of failures.

## 4. Environment and memory architecture

<p align="center">
  <img src="../AILaunchPad/10.png" alt="Shared world state introduction" width="46%" />
  <img src="../AILaunchPad/11.png" alt="Agentic retrieval, provenance, and caching" width="46%" />
</p>

| Lens | Guidance |
|---|---|
| **What** | The environment is the external world agents observe and change. Memory is retained context: task state, conversation, facts, preferences, and learned summaries. |
| **Why** | Agents need a consistent world model without placing all history into every prompt. Bad memory creates stale decisions, privacy exposure, and hidden coupling. |
| **How** | Separate shared state, per-agent scratchpads, immutable events, retrieval indices, caches, and durable checkpoints. Attach scope, provenance, owner, timestamp, confidence, and TTL. |
| **When** | Shared state is needed for coordination; private scratchpads for local calculations; retrieval for large knowledge; durable state for resumable/long-running workflows. |

### Memory taxonomy

| Memory | Scope | Persistence | Example | Rule |
|---|---|---|---|---|
| Working context | One model call/task | Ephemeral | Current instructions and evidence | Keep minimal and relevant |
| Agent scratchpad | One agent/run | Short-lived | Intermediate calculations | Do not treat as verified fact |
| Shared task state | Whole workflow | Run lifetime/durable | Task status and artifacts | Version writes and control concurrency |
| Episodic memory | Across runs | Durable | Prior interaction summaries | Consent, retention, and deletion required |
| Semantic memory | Across agents/runs | Durable | Retrieved enterprise knowledge | Preserve source and freshness metadata |
| Cache | Reusable operation | TTL-based | Expensive API result | Key on all behavior-changing inputs |

### Reliability semantics

<p align="center">
  <img src="../AILaunchPad/12.png" alt="Determinism, checkpointing, and exactly-once actions" width="850" />
</p>

Model generation is not deterministic in the database sense. Make the surrounding workflow replayable through immutable inputs, versioned prompts/models/tools, checkpoints, and idempotency keys. “Exactly once” usually means **effectively once**: record an action identifier and make retries return the prior result instead of repeating the side effect.

## 5. Safety, permissions, and governance

<p align="center">
  <img src="../AILaunchPad/14.png" alt="Capability scoping and least privilege" width="46%" />
  <img src="../AILaunchPad/15.png" alt="Guardrails and policy enforcement" width="46%" />
</p>

| Lens | Guidance |
|---|---|
| **What** | Governance defines allowed data, tools, actions, models, destinations, retention, and accountability for every role and environment. |
| **Why** | Prompt instructions alone cannot safely constrain credentials, code execution, external actions, or sensitive-data movement. |
| **How** | Enforce least privilege outside the model with scoped credentials, sandboxing, policy checks, allowlists, approval gates, content controls, and auditable identity. |
| **When** | Always; controls become stricter for personal data, money movement, communications, code execution, regulated decisions, or irreversible actions. |

### Capability matrix example

| Role | Read knowledge | Internet | Execute code | Write records | Publish externally |
|---|---:|---:|---:|---:|---:|
| Researcher | Scoped read | Approved domains | No | Artifact only | No |
| Writer | Research artifact | No | No | Draft only | No |
| Reviewer | Draft + evidence | Optional read | No | Review decision | No |
| Publisher | Approved draft | Destination only | No | Audit record | Human-approved only |
| Orchestrator | Metadata/state | No | No | Workflow state | No |

Guardrails should exist at input, context retrieval, model output, tool invocation, and final action—not only at the user-facing boundary. Log actions without leaking secrets or unnecessarily retaining sensitive prompts.

<p align="center">
  <img src="../AILaunchPad/16.png" alt="Audit trails, monitoring, and kill switches" width="850" />
</p>

## 6. Observability and evaluation

<p align="center">
  <img src="../AILaunchPad/20.png" alt="Trace IDs, spans, and causality trees" width="46%" />
  <img src="../AILaunchPad/22.png" alt="Evaluation harness and testing" width="46%" />
</p>

| Lens | Guidance |
|---|---|
| **What** | Observability explains what happened; evaluation determines whether the behavior and outcome were good. |
| **Why** | A successful HTTP response can still contain an unsupported claim, wrong tool choice, policy violation, excessive cost, or hidden retry loop. |
| **How** | Use trace/session IDs, parent-child spans, structured events, model/tool metadata, state transitions, redaction, scenario tests, rubrics, golden sets, and adversarial probes. |
| **When** | Add before pilot deployment. Establish a baseline before changing prompts, models, tools, memory, or orchestration. |

### Four evaluation layers

| Layer | Questions | Metrics |
|---|---|---|
| Component | Did this agent/tool satisfy its contract? | schema validity, task score, tool accuracy |
| Coordination | Did work reach the right role in the right order? | hand-off accuracy, steps, loops, retries |
| End-to-end product | Did the user receive a useful, correct result? | task success, groundedness, human rating |
| Operations/safety | Was it efficient, secure, and policy-compliant? | latency, cost, intervention, policy incidents |

Avoid comparing frameworks or prompts on a single pleasant demo. Maintain representative normal, edge, adversarial, and failure-recovery scenarios in CI.

## 7. Scaling and reliability

<p align="center">
  <img src="../AILaunchPad/24.png" alt="Concurrency, isolation, and load shedding" width="46%" />
  <img src="../AILaunchPad/25.png" alt="Failure recovery strategies" width="46%" />
</p>

| Lens | Guidance |
|---|---|
| **What** | Reliability keeps outcomes within defined SLOs despite model variability, transient dependencies, process crashes, and load. Scaling increases throughput without losing isolation or cost control. |
| **Why** | Multi-agent fan-out multiplies calls, shared-state contention, partial failure, and spend. |
| **How** | Queue work, isolate tenants/runs, checkpoint state, classify errors, retry transient failures, compensate side effects, shed load, cache safely, and degrade gracefully. |
| **When** | Design recovery before external side effects; add concurrency after correctness; distribute components only when measured capacity or isolation requires it. |

### Failure policy

| Failure type | Example | Preferred response |
|---|---|---|
| Transient | timeout, 429, temporary service failure | bounded exponential backoff with jitter |
| Permanent input | invalid schema, forbidden request | fail fast and explain |
| Model-quality | malformed or weak output | constrained retry, alternate model, or human review |
| Tool side effect uncertain | response lost after POST | query idempotency record before retry |
| Agent crash | worker process exits | resume from durable checkpoint |
| Partial workflow | specialist unavailable | return partial result with explicit limitations |

### Cost control

<p align="center">
  <img src="../AILaunchPad/26.png" alt="Multi-model routing, caching, batching, and budgets" width="850" />
</p>

Budget at run, task, agent, model, and tool levels. Route routine extraction/classification to smaller models, reserve stronger models for hard synthesis, cache deterministic/retrieval work, and stop low-value branches when marginal benefit falls below cost.

## 8. Frameworks and build options

<p align="center">
  <img src="../AILaunchPad/28.png" alt="No-code workflow frameworks" width="46%" />
  <img src="../AILaunchPad/30.png" alt="Code-based agent frameworks" width="46%" />
</p>

| Lens | Guidance |
|---|---|
| **What** | Build options range from visual automation to role-based crews, state graphs, SDKs, and custom event-driven runtimes. Supporting systems provide retrieval, observability, queues, and policy enforcement. |
| **Why** | The chosen abstraction determines how precisely you can model state, recovery, concurrency, human review, deployment, and testing. |
| **How** | Start from requirements and operational constraints; prototype the riskiest behavior; compare failure semantics and maintainability, not only demo speed. |
| **When** | Use no/low-code for bounded integrations; role frameworks for specialist collaboration; graphs for explicit state/control; custom runtimes for unusual scale, protocol, or isolation needs. |

The AILaunchPad material contrasts the graph/state model of LangGraph with CrewAI's agent/task/crew abstractions:

<p align="center">
  <img src="../AILaunchPad/32.png" alt="LangGraph state graph example" width="46%" />
  <img src="../AILaunchPad/35.png" alt="CrewAI key concepts" width="46%" />
</p>

See the [framework comparison](agent-architectures-and-frameworks.md#framework-landscape) for current positioning and adoption signals.

## 9. Anti-patterns and design checklist

| Anti-pattern | Why it fails | Better design |
|---|---|---|
| Agent for every function | Adds LLM cost and ambiguity to deterministic logic | Keep validation/transformation as code |
| Multiple uncoordinated planners | Conflicting global plans and duplicated work | One authoritative plan or explicit plan competition |
| Everyone sees everything | Token waste, data leakage, prompt contamination | Minimum necessary context by role |
| Tool access via prompt policy only | The model can still attempt dangerous calls | Enforce permissions in the tool/runtime layer |
| Unbounded group chat | Loops, drift, and runaway cost | Step/token/time budgets plus progress checks |
| Retry everything | Repeats permanent failures and side effects | Classify errors and use idempotency |
| “The LLM cited it” | Plausible URLs/claims may be false or unsupported | Resolve sources and validate claim-evidence links |
| Shared mutable state without versioning | Lost updates and inconsistent decisions | Events, optimistic concurrency, locks/queues where needed |
| Logs without trace relationships | Cannot reconstruct causality | Trace IDs and parent-child spans |
| Framework-first architecture | Demo abstractions dictate product behavior | Requirements and failure model first |
| Evaluation only at final answer | Hidden weak stages remain undiagnosed | Component, coordination, E2E, and safety evaluations |
| Autonomous high-impact action | Model uncertainty becomes real-world harm | Human approval and compensating controls |

### Pre-launch checklist

- [ ] A single-agent/non-agent baseline was measured.
- [ ] Every agent has one bounded responsibility and owner.
- [ ] Every task has typed inputs, outputs, and completion criteria.
- [ ] Context and memory have scope, provenance, freshness, and retention rules.
- [ ] Tools use scoped credentials and enforce authorization outside prompts.
- [ ] External actions have idempotency and approval appropriate to impact.
- [ ] Loops, tokens, time, cost, retries, and concurrency are bounded.
- [ ] Checkpoints and recovery paths have been exercised.
- [ ] Trace IDs connect agents, model calls, tools, state, and humans.
- [ ] Evaluation covers happy paths, edge cases, adversarial inputs, and failures.
- [ ] Partial and degraded outcomes are explicit to users.
- [ ] Kill-switch, rollback, incident ownership, and audit retention are defined.

## Applying the lifecycle to this repository

<p align="center">
  <img src="../AILaunchPad/38.png" alt="CrewAI demo notebook workflow map" width="900" />
</p>

| Lifecycle stage | Notebook implementation | Next maturity step |
|---|---|---|
| Suitability | Three distinct content responsibilities | Compare quality/cost to a one-agent baseline |
| Communication | CrewAI task context | Add structured task outputs and provenance |
| Coordination | Sequential crew | Add explicit time/token budgets and review gate |
| Memory | In-run task context only | Add approved retrieval and scoped durable state if needed |
| Governance | Live and publish flags; no publisher tool attached | External policy service and scoped credentials |
| Observability | Verbose CrewAI trace | Durable spans, redaction, cost/quality dashboard |
| Reliability | Safe key-free preview | Checkpointing, retries, idempotency, partial results |
| Framework | CrewAI role/task abstraction | Re-evaluate if graph-level state control becomes necessary |
| Review | Documented limitations and checks | Automated evaluation suite in CI |

---

### Core principle

An agentic system is not “several prompts connected together.” It is a distributed decision system whose state, authority, communication, cost, failure, evidence, and human accountability must be designed as carefully as its intelligence.
