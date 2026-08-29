# EGAH presentation review guide

## Recommendation in one sentence

Present EGAH as a **working proof of concept for evidence-governed recovery**: observability reconstructs an execution, while EGAH persists and evaluates the decision basis required to continue safely.

**Opening thesis:** “A checkpoint tells an agent where to restart. It does not prove that the evidence collected before the crash still justifies the next action.”

**Reviewer outcome:** They should see a relevant production problem, a distinct control-layer abstraction, working code, an honest feasibility boundary, and a clear experiment worth putting before practitioners.

## What the local implementation actually does

The PoC runs a sequential ten-step document-analysis workflow. It saves workflow progress, step outputs, evidence envelopes at steps 3/6/9, verification decisions, and per-step resource records in SQLite. A controlled crash before step 7 leaves steps 1–6 and two evidence envelopes durable. Recovery reloads the run, envelopes, and verification history; evaluates freshness and verification status; then returns a `RecoveryPlan` containing `safe_to_resume`, evidence requiring revalidation, and a resume recommendation.

Local verification on 28 August 2026: **35 tests passed**. The test run also reports Pydantic v2 deprecation warnings; these are maintenance issues, not proof of incorrect recovery behavior.

### Claim discipline

| Status | Safe claim |
|---|---|
| Implemented and tested | SQLite persistence; steps 3/6/9 checkpoints; crash before step 7; evidence and verification restoration; freshness/validity analysis; recovery plan; UI comparison; audit/resource views |
| Simplified for the demo | Verification means non-empty output longer than ten characters; freshness is five minutes; demo recovery deliberately treats early evidence as stale |
| Representative production scenario | Loan decision, pod eviction, credit/employment/fraud revalidation, 3.5-hour interruption |
| Proposed extension, not implemented | Real tool-specific refresh; live authorization checks; model capability routing; outcome-value attribution; OpenTelemetry/Langfuse integration; LangGraph graph execution; production HA database |

Do not say “EGAH automatically recovers safely.” Say: **“EGAH produces and enforces, through the UI path, a recovery decision; production adapters would execute refresh, authorization, or escalation.”**

## 1. What EGAH captures beyond ordinary observability

Observability and EGAH overlap in raw events, but have different semantics.

| Question | Trace/log/metric | EGAH durable record |
|---|---|---|
| What ran? | Spans, tool calls, errors, sequence | Run and step identity |
| How did it perform? | Latency, tokens, cost | Resource record tied to run/step; copied into checkpoint envelope |
| What fact supports the next action? | May exist inside span payload | Evidence `content` and human-readable `summary` |
| Where did that fact come from? | Event metadata may contain source | Explicit `source` and `provenance` |
| When was it observed? | Event timestamp | Evidence timestamp plus `valid_from`, `valid_until`, and freshness window |
| Was it checked? | An evaluation event may exist | Durable verification status, verifier, reason, and policy decision |
| Is it still usable now? | Requires application interpretation | Runtime freshness/validity assessment |
| What may the agent do next? | Usually not a trace responsibility | `ACT`, `REFRESH`, `ASK`, or `ABSTAIN` decision |

The difference is not “telemetry versus more telemetry.” It is **descriptive record versus executable decision state**. EGAH can consume observability signals; it should not replace OpenTelemetry, Langfuse, Phoenix, or Datadog.

Current implementation caveat: authorization and explicit outcome attribution are described in the research materials but are not fields or live checks in the present data model. Present them as the next production schema/policy extension.

## 2. Essence and business value

### Essence

EGAH adds two primitives at consequential boundaries:

1. **Evidence envelope:** content + provenance + time/validity + verification + run/step/resource linkage.
2. **Policy gate:** decide whether the next action may proceed, requires refreshed evidence, needs intervention, or must stop.

### Why use it

- Prevent a technically successful restart from becoming a semantically unsafe continuation.
- Avoid repeating an entire expensive workflow when only one stale dependency must be refreshed.
- Make recovery decisions explainable to operators, auditors, and incident reviewers.
- Attach compute cost to steps and evidence-bearing outcomes rather than only to model calls.
- Provide a future control point for model routing: use a smaller model inside a validated task boundary; verify or escalate near/outside it.

### Where it earns its complexity

Use it for long-running, interruptible workflows with time-sensitive evidence or consequential actions: credit, fraud, claims, compliance, healthcare workflow coordination, legal review, or privileged infrastructure changes. Do not checkpoint every token or harmless transformation. Place an evidence checkpoint immediately before a decision whose correctness depends on earlier external facts.

## 3. Representative loan process: steps 1–10

This is the production analogue; the code demo uses generic document-analysis step names.

1. **Receive application** — capture request, consent, declared data, and document references.  
   ↓
2. **Validate identity/KYC** — establish applicant identity and screening result.  
   ↓
3. **Retrieve credit report — CHECKPOINT A** — store bureau/source, report ID or hash, score, observed time, freshness policy, verification result, and the decision it can support.  
   ↓
4. **Verify income** — validate stated income against submitted or authoritative evidence.  
   ↓
5. **Verify employment** — record employer source, employment state, verification time, and confidence.  
   ↓
6. **Screen fraud and assess risk — CHECKPOINT B** — store fraud-rule/model version, triggered signals, risk band, policy version, upstream evidence references, verification status, and permitted next action.  
   ↓
7. **Generate eligibility decision — CRASH** — pod is evicted before the decision completes; durable `current_step` remains 6.  
   ↓
8. **Price loan and terms** — pending; must not run until required evidence is current and authorization is confirmed.  
   ↓
9. **Revalidate and construct offer — CHECKPOINT C** — refresh expired dependencies, rerun affected risk rules, record policy/authorization, and persist offer evidence.  
   ↓
10. **Issue offer/sign-off** — produce the governed outcome and complete the audit chain.

### What is stored at checkpoints 3 and 6

**Checkpoint 3, credit evidence**

- Identity: evidence ID, run ID, step 3.
- Payload: score/report summary; production version should reference or hash sensitive source data rather than duplicate it blindly.
- Provenance: bureau/tool and request/report identifier.
- Time semantics: observed timestamp, valid-from/until, freshness rule.
- Verification: status, verifier, reason, decision (`ACT` initially).
- Accounting: tokens, cost, latency for the producing step.

**Checkpoint 6, risk evidence**

- Payload: fraud signals, risk result, policy/model version, and upstream evidence references.
- Provenance: risk service/rule engine/model.
- Verification: whether inputs were complete and policy checks passed.
- Decision: whether the next consequential action—eligibility/offer generation—is allowed.

**Database explanation:** the PoC uses four SQLite tables: `workflow_runs`, `evidence_envelopes`, `verification_records`, and `resource_records`. Each object is serialized as JSON; run ID and step number provide correlation. For production, use transactional writes/outbox semantics and a durable multi-writer store so run state, evidence, and verification cannot diverge during a crash.

## 4. How recovery works—exactly

1. The crash is recorded before step 7 completes; the run is `CRASHED`, `current_step=6`, and the failed step record remains visible.
2. Recovery loads the workflow run by `run_id`; therefore it knows the failed step is `current_step + 1`.
3. It queries evidence envelopes with the same run ID up to the crash step: checkpoint records from steps 3 and 6.
4. It loads verification history for the run: original status, decision, reason, verifier, and time.
5. For each envelope it evaluates freshness and verification status. The demo deliberately marks the older step-3 envelope stale; step 6 remains fresh.
6. It builds a recovery plan: stale evidence ID → `REFRESH`; fresh verified evidence → `ACT`; critical stale evidence makes `safe_to_resume=False`.
7. The UI hides the EGAH Resume button while the plan is unsafe. After required revalidation in a production implementation, execution would retry step 7, not redo steps 1–6 indiscriminately.
8. On resume, the crash record is removed, the run becomes recovered, and the loop continues from step 7. Step 9 creates the third envelope; step 10 completes the run.

### The four recovery questions

- **What was done?** `WorkflowRun.steps`, `current_step`, and step outputs.
- **How does it know?** Durable SQLite records correlated by run ID, step, evidence ID, and timestamps.
- **What happens next?** `RecoveryPlan.resume_from_step` plus policy recommendations.
- **What is required first?** Revalidate every evidence ID in `revalidation_required`; also check domain authorization/policy in the production version.

### Honest technical limits

- Crash injection is controlled, not an operating-system kill or Kubernetes restart test.
- Staleness in the comparison is simulated by step position; real mode can use envelope timestamps, but external invalidation events are not wired.
- Verification currently checks output length, not factual correctness.
- The PoC creates a refresh recommendation; it does not call a bureau/employment/fraud service to refresh evidence.
- SQLite calls are separate commits, not one atomic transaction across run/evidence/verification/resource state.
- LangGraph is a dependency/design direction, but the present execution engine is a Python sequential loop.
- The backend recovery marker does not itself accept a `RecoveryPlan`; the Streamlit UI supplies the current safety guard.

These limits make a credible validation roadmap, not a reason to hide the work.

## 5. Slide-by-slide review talk track

Target: **20 minutes slides + 5 minutes demo + 5 minutes Q&A**. Do not read bullets. Use one claim, one example, and one transition per slide.

### Slide 1 — Evidence-Governed Agent Harnesses (0:00–0:40)

**Say:** “Suppose a 60-step agent crashes at step 40. Most systems can restore its position. My question is harder: what evidence still justifies step 41?”

**Purpose:** State the problem, not your biography or a framework definition.

**Transition:** “A familiar loan workflow makes the missing decision obvious.”

### Slide 2 — Observability cannot validate a safe resume (0:40–3:10)

**Say:** “A pod fails after credit, employment, fraud, and risk evidence were collected. Three and a half hours later, the trace tells us the calls, latency, failure, and restart point. It does not decide whether those facts remain applicable to an offer generated now.”

Point left-to-right:

1. Observability answers **what happened**.
2. The production gap is **whether the prior evidence still supports the next decision**.
3. EGAH supplies the recovery gate: `ACT`, `REFRESH`, `ASK`, or `ABSTAIN`.

**Avoid:** “Observability cannot store evidence.” It can store payloads and evaluations. Your claim is that telemetry is not automatically durable, policy-evaluated continuation state.

**Transition:** “The PoC reduces this to a reproducible crash at step 7.”

### Slide 3 — A crash preserves state—not evidence (3:10–5:30)

**Say:** “The implemented demo has ten document-analysis steps, checkpoints at 3, 6, and 9, and a crash before 7. After the crash, two envelopes survive. I deliberately age step 3 for the demonstration: step 3 becomes `REFRESH`, step 6 remains `ACT`, and step 7 must wait.”

Be explicit: **preservation and plan generation are implemented; staleness is simulated.** The loan case is an analogue, not the literal code workflow.

**Transition:** “What makes an envelope different from a trace payload?”

### Slide 4 — Evidence is first-class runtime state (5:30–7:35)

**Say:** “A value is not enough. To reuse it safely I need its origin, observation time, validity rule, verification history, content, and run/step/resource linkage.”

Use one concrete object: “credit score 742” is unsafe alone; “bureau report X, observed 13:58, verified under policy P, valid for Y, supporting eligibility decision Z” is decision-bearing evidence.

Correct the slide verbally: outcome linkage and authorization are production extensions, while the PoC currently persists run/step linkage and resources.

**Transition:** “The envelope matters only if it changes execution.”

### Slide 5 — The harness adds a policy gate (7:35–10:00)

**Say:** “EGAH is not an audit database bolted on afterwards. At a consequential boundary, the harness captures evidence, applies a policy, persists the decision, and chooses the next edge.”

Explain decisions precisely:

- `ACT`: evidence is usable; continue.
- `REFRESH`: reacquire an expired or invalid dependency.
- `ASK`: missing or uncertain evidence requires intervention.
- `ABSTAIN`: capability/authorization boundary forbids action.

**Avoid:** claiming the current PoC implements every edge; `ACT`, `REFRESH` analysis, and unsafe blocking are demonstrated, while live escalation/authorization adapters remain work.

**Transition:** “Here is where that control plane sits.”

### Slide 6 — Architecture (10:00–13:45)

Walk it in five passes; do not trace every arrow:

1. **Inputs:** request + context enter; model and tools perform work against the world.
2. **Runtime state:** separate execution state, evidence state, and telemetry. State answers where; evidence answers why; telemetry answers how the run behaved.
3. **Control path:** plan → checkpoint → policy gate → sufficiency decision.
4. **Outcomes:** act, refresh, ask, or abstain; failure enters recovery and only then safe resume.
5. **Durable record:** actions and decisions should form the verified audit chain.

**Architecture truth:** the diagram is the target architecture. The current PoC implements its core evidence store, policy analysis, recovery plan, and UI using Python + SQLite; it does not yet implement the pictured production integrations or a LangGraph state graph.

**Transition:** “The practical proof is that recovery reaches a different decision.”

### Slide 7 — Recovery restores the decision basis (13:45–16:45)

**Say:** “Both approaches know to retry step 7. Traditional recovery says go. EGAH restores two evidence envelopes, finds step 3 stale and step 6 fresh, and says refresh before going. The value is the changed decision, not a prettier recovery screen.”

Emphasize targeted recomputation and audit continuity. Do not imply every existing framework is incapable of this; say existing checkpointing does not provide these domain semantics by default.

**Transition:** “The demo will show this exact divergence.”

### Slide 8 — Demo contract (16:45–17:20)

**Say:** “I will show one deterministic path: crash at 7, inspect two envelopes, compare recovery plans, and show why the EGAH path blocks.”

Do not spend time reading six steps.

### Slide 9 — Production test and close (17:20–20:00)

**Say:** “This mechanism belongs in production only if reliability gain exceeds checkpoint, storage, and revalidation overhead. The correct checkpoint is not every step; it is the boundary before a consequential action.”

Close with: **“After a crash, remember not only where the agent was, but why it may continue. Which action in your system deserves that gate?”**

Then switch to the application.

## Five-minute demo script (20:00–25:00)

Prepare the app before joining: start it, reset the database, verify the crash selector is 7, and keep the screenshots in `resources/images/demo/` open as fallback.

1. **0:00–0:50:** Run with crash at step 7. Say: “Six steps committed; step 7 did not.”
2. **0:50–1:40:** Evidence Inspector. Show exactly two envelopes, at steps 3 and 6; point to provenance, timestamp, freshness, and verification.
3. **1:40–3:20:** Recovery tab. Run traditional recovery, then EGAH recovery. Pause on the changed answer: traditional says resume; EGAH says unsafe and identifies the stale envelope.
4. **3:20–4:10:** Audit Trail. Show verification reason and step-level tokens/cost/latency. Do not dwell on synthetic numbers.
5. **4:10–5:00:** Return to the recovery decision. Say: “The PoC stops here intentionally: a production adapter refreshes the flagged source, creates a new verification, and only then enables step 7.”

Do not click EGAH resume while the demo plan is unsafe—the UI correctly hides it. If reviewers want completion, rerun without simulated staleness or explain the required refresh adapter; do not pretend that refresh already occurred.

## Likely reviewer questions and crisp answers

**Is this just metadata in a trace?**  
The fields can originate in traces, but EGAH makes selected evidence durable, applies domain validity policy at runtime, and uses the result to control continuation. The distinction is behavioral, not merely storage format.

**Why not put everything in the graph checkpoint?**  
You can share a database, but evidence needs its own schema, lifecycle, provenance, validity, and policy semantics. Separating the concepts also enables selective refresh without replaying the whole graph.

**How is validity known?**  
By a domain policy: time window, source version, invalidation event, verification result, or authorization state. The PoC implements time/status analysis; real source invalidation is future work.

**Does it recover itself?**  
It reconstructs state and computes the safe recovery plan. The current PoC blocks unsafe UI continuation; real-world refresh/escalation actions require adapters and idempotent workflow edges.

**Why checkpoints 3, 6, and 9?**  
They represent semantic boundaries: extracted evidence, risk decision, and report/offer. They are illustrative; production placement follows consequential action dependencies, not a fixed interval.

**What about small models?**  
EGAH provides the control point for evidence-backed routing, but this PoC does not benchmark or route an 8B model. Keep this as a research extension unless you add data and evaluation.

**What proves feasibility?**  
Working local UI, SQLite persistence, crash/recovery comparison, and 35 passing tests prove the core state-and-policy path. They do not yet prove distributed crash consistency, domain verification accuracy, or acceptable production overhead.

**What is the measurable business case?**  
Measure unsafe-continuation prevention, percentage of targeted versus full replay, recovery time, human escalations, false blocks, checkpoint latency/storage overhead, and cost per verified outcome.

## Professor-level critique: what could prevent selection

1. **Overclaiming observability.** Sophisticated observability/evaluation systems can store payloads and scores. Frame EGAH as continuation semantics and a policy gate, not as information no other system can physically record.
2. **Scenario mismatch.** Slide 2 is a loan workflow; the implementation is generic document analysis. Label one “production analogue” and the other “minimal executable PoC.” Never blur them.
3. **Architecture outruns code.** The diagram suggests LangGraph, tool/world integrations, authorization, and a verified-record pipeline. State which subset exists today.
4. **Recovery is not yet closed-loop.** The PoC identifies stale evidence but does not refresh it. Reviewers will notice if you say “self-healing.” Say “evidence-governed recovery planning and gating.”
5. **Verification is weak.** Output length demonstrates the plumbing, not epistemic correctness. Make policy adapters the next engineering experiment.
6. **Crash consistency is unproven.** Separate SQLite commits can leave partial durable state. A production design needs atomic transaction boundaries, idempotency keys, and recovery from actual process/container failure.
7. **Small-model claim lacks evidence.** Do not spend core talk time on 8B routing unless you bring an eval set, boundary definition, routing policy, and quality/cost results.
8. **No measured overhead yet.** A harness abstraction earns its place only with latency, storage, revalidation, false-block, and reliability measurements.

## Selection-ready framing

Use this description in the review:

> “This is a practitioner talk about a narrow gap in long-running agent recovery. I have a local, deterministic PoC that crashes a ten-step workflow, preserves evidence and verification records, and demonstrates that evidence-aware recovery reaches a different continuation decision from state-only recovery. I will show the implementation honestly, including the simplified policy, then invite practitioners to debate where the added checkpoint semantics earn their operational cost.”

That framing is aligned with the meetup: it tests whether a harness abstraction earns its keep, addresses state surviving a late crash, provides a working demo, and exposes trade-offs rather than selling a framework.

## Final preparation checklist

- Add an email address to the Hasgeek profile.
- Calendar text says “tomorrow, Friday, 28 August,” while the local date is Friday, 28 August 2026; verify the invite time rather than relying on the prose.
- Open the deck, app, terminal, and fallback screenshots before the call.
- Rehearse once to 20 + 5 minutes; stop even if a slide has unused content.
- Keep terminal proof ready: `PYTHONPATH=src python3 -m pytest -q`.
- Be ready to open `models.py`, `egah_agent.py`, `recovery.py`, and `evidence_store.py` if asked for implementation depth.
- Never claim real loan data, a real bureau integration, Kubernetes failure recovery, LangGraph execution, live authorization, or automatic evidence refresh.
- Ask reviewers one useful question: “Is the evidence-policy boundary sufficiently distinct from observability for this audience, and which production integration would make the demo most credible?”

## Local evidence used

- `src/egah/models.py`: evidence, verification, resource, workflow, and recovery-plan models.
- `src/egah/egah_agent.py`: ten steps, checkpoints 3/6/9, persistence flow, crash injection, simplified verification.
- `src/egah/evidence_store.py`: four SQLite-backed durable record types.
- `src/egah/recovery.py`: traditional comparison, envelope analysis, and recovery-plan generation.
- `src/egah/app.py`: five demo tabs and UI safety gating.
- `tests/test_egah.py`: normal, crash, recovery, evidence, audit, and step-7 scenario tests.
- `resources/documents/cfp/egah_fifth_elephant_cfp_v3_minimal.pptx`: nine-slide narrative reviewed above.

