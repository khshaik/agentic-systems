"""
EGAH PoC — Streamlit Demo Application

Evidence-Governed Agent Harnesses:
  What Should Survive When an Agent Crashes at Step 40 of 60?

This demo shows:
1. Normal execution with evidence checkpoints
2. Crash simulation at any step
3. Side-by-side comparison: Traditional vs EGAH recovery
4. Evidence envelope inspector
5. Verification history timeline
6. Resource accounting dashboard
"""

from __future__ import annotations

import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Ensure src/ is on the path when Streamlit runs this file directly
_SRC_DIR = str(Path(__file__).resolve().parent.parent)
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

import streamlit as st
from dotenv import load_dotenv

from egah.egah_agent import CHECKPOINT_STEPS, WORKFLOW_STEPS, EGAHAgent
from egah.evidence_store import EvidenceStore
from egah.models import PolicyDecision, RunStatus, VerificationStatus
from egah.recovery import RecoveryController

# Load .env from project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="EGAH — Evidence-Governed Agent Harness",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    .main-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #555;
        margin-bottom: 1.5rem;
    }
    .step-card {
        padding: 0.8rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 4px solid #ddd;
    }
    .step-completed {
        background: #f0fdf4;
        border-left-color: #22c55e;
    }
    .step-checkpoint {
        background: #eff6ff;
        border-left-color: #3b82f6;
    }
    .step-crashed {
        background: #fef2f2;
        border-left-color: #ef4444;
    }
    .step-pending {
        background: #f9fafb;
        border-left-color: #d1d5db;
    }
    .evidence-card {
        padding: 1rem;
        border-radius: 8px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        margin-bottom: 0.8rem;
    }
    .metric-card {
        padding: 1rem;
        border-radius: 8px;
        background: #fff;
        border: 1px solid #e5e7eb;
        text-align: center;
    }
    .recovery-traditional {
        background: #fef3c7;
        border: 1px solid #f59e0b;
        padding: 1rem;
        border-radius: 8px;
    }
    .recovery-egah {
        background: #ecfdf5;
        border: 1px solid #10b981;
        padding: 1rem;
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Initialize services
# ---------------------------------------------------------------------------


@st.cache_resource
def get_store():
    return EvidenceStore()


@st.cache_resource
def get_agent():
    api_key = os.getenv("OPENAI_API_KEY")
    store = get_store()
    use_llm = bool(api_key and api_key.startswith("sk-"))
    return EGAHAgent(store=store, openai_api_key=api_key, use_llm=use_llm)


@st.cache_resource
def get_recovery():
    return RecoveryController(store=get_store())


store = get_store()
agent = get_agent()
recovery_ctrl = get_recovery()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## 🛡️ EGAH PoC")

    st.markdown("### Configuration")
    llm_mode = "🟢 Live LLM (GPT-4o-mini)" if agent.use_llm else "🟡 Simulated (no API key)"
    st.info(llm_mode)

    crash_step = st.slider(
        "💥 Crash at step",
        min_value=2,
        max_value=10,
        value=7,
        help="The step at which to simulate a crash",
    )

    st.divider()

    st.markdown("### Actions")

    if st.button("🔄 Reset Database", use_container_width=True):
        store.reset()
        for key in list(st.session_state.keys()):
            if key.startswith("run_") or key.startswith("results_") or key.startswith("recovery_"):
                del st.session_state[key]
        st.rerun()

# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------

st.markdown(
    '<p class="main-header">Evidence-Governed Agent Harnesses</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-header">'
    "What should survive when an agent crashes at step 7 of 10?"
    "</p>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Tab layout
# ---------------------------------------------------------------------------

tab_demo, tab_evidence, tab_recovery, tab_audit, tab_about = st.tabs(
    ["🚀 Demo", "📋 Evidence Inspector", "🔧 Recovery", "📊 Audit Trail", "ℹ️ About"]
)

# ============================= TAB: DEMO ==================================
with tab_demo:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📄 Document Analysis Workflow")
        st.markdown(
            "A 10-step document analysis pipeline with "
            f"evidence checkpoints at steps **{CHECKPOINT_STEPS}**."
        )

        task = st.text_input(
            "Task description",
            value="Analyze Q3 2026 Financial Compliance Report for regulatory gaps",
            key="task_input",
        )

        btn_col1, btn_col2, btn_col3 = st.columns(3)

        with btn_col1:
            run_normal = st.button("▶️ Run Normal (no crash)", use_container_width=True)
        with btn_col2:
            run_crash = st.button(
                f"💥 Run with Crash at Step {crash_step}", use_container_width=True
            )
        with btn_col3:
            run_step = st.button("⏭️ Run Next Step", use_container_width=True)

    # --- Handle button actions ---
    if run_normal:
        run = agent.create_run(task)
        st.session_state["run_id"] = run.run_id
        st.session_state[f"results_{run.run_id}"] = []
        results = agent.run_all(run.run_id, crash_at_step=None)
        st.session_state[f"results_{run.run_id}"] = results

    if run_crash:
        run = agent.create_run(task)
        st.session_state["run_id"] = run.run_id
        st.session_state[f"results_{run.run_id}"] = []
        results = agent.run_all(run.run_id, crash_at_step=crash_step)
        st.session_state[f"results_{run.run_id}"] = results

    if run_step:
        run_id = st.session_state.get("run_id")
        if not run_id:
            run = agent.create_run(task)
            st.session_state["run_id"] = run.run_id
            run_id = run.run_id
            st.session_state[f"results_{run_id}"] = []
        result = agent.execute_step(run_id)
        if f"results_{run_id}" not in st.session_state:
            st.session_state[f"results_{run_id}"] = []
        st.session_state[f"results_{run_id}"].append(result)

    # --- Display execution results ---
    run_id = st.session_state.get("run_id")
    if run_id:
        results = st.session_state.get(f"results_{run_id}", [])
        run = store.get_run(run_id)

        if run:
            with col2:
                st.markdown("### Status")
                status_color = {
                    RunStatus.RUNNING: "🔵",
                    RunStatus.COMPLETED: "🟢",
                    RunStatus.CRASHED: "🔴",
                    RunStatus.RECOVERED: "🟡",
                    RunStatus.PAUSED: "⚪",
                }
                st.markdown(
                    f"**Status:** {status_color.get(run.status, '⚪')} {run.status.value.upper()}"
                )
                st.markdown(f"**Progress:** {run.current_step}/{run.total_steps}")
                st.markdown(f"**Run ID:** `{run.run_id[:8]}...`")

                total_cost = store.get_total_cost(run_id)
                total_tokens = store.get_total_tokens(run_id)
                evidence_count = len(store.get_evidence_for_run(run_id))

                st.metric("Total Tokens", f"{total_tokens:,}")
                st.metric("Total Cost", f"${total_cost:.6f}")
                st.metric("Evidence Envelopes", evidence_count)

        # --- Step-by-step execution timeline ---
        st.markdown("---")
        st.markdown("### Execution Timeline")

        for result in results:
            step_num = result.get("step_number", "?")
            step_name = result.get("step_name", "Unknown")
            status = result.get("status", "unknown")
            is_cp = result.get("is_checkpoint", False)
            crashed = result.get("crashed", False)

            if crashed:
                css_class = "step-crashed"
                icon = "💥"
            elif is_cp:
                css_class = "step-checkpoint"
                icon = "🔒"
            else:
                css_class = "step-completed"
                icon = "✅"

            with st.container():
                st.markdown(
                    f'<div class="step-card {css_class}">'
                    f"<strong>{icon} Step {step_num}: {step_name}</strong>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

                if crashed:
                    st.error(result.get("message", "Crash occurred"))
                else:
                    output = result.get("output", "")
                    if output:
                        st.markdown(f"📝 {output[:200]}")

                    if is_cp and "evidence" in result:
                        ev = result["evidence"]
                        vr = result["verification"]
                        st.info(
                            f"🔒 **Evidence Checkpoint** — "
                            f"Status: `{ev.get('verification_status', 'unknown')}` | "
                            f"Decision: `{vr.get('policy_decision', 'unknown')}` | "
                            f"Evidence ID: `{ev.get('evidence_id', '')[:8]}...`"
                        )

                    latency = result.get("latency_ms", 0)
                    if latency:
                        st.caption(f"⏱️ {latency}ms")


# ========================= TAB: EVIDENCE INSPECTOR ========================
with tab_evidence:
    st.markdown("### 📋 Evidence Envelope Inspector")
    st.markdown(
        "Browse all evidence envelopes created during execution. "
        "Each envelope captures *what was known, when it was verified, "
        "and whether it remains valid.*"
    )

    run_id = st.session_state.get("run_id")
    if not run_id:
        st.info("Run a workflow first to see evidence envelopes.")
    else:
        envelopes = store.get_evidence_for_run(run_id)
        if not envelopes:
            st.warning("No evidence envelopes found for this run.")
        else:
            for env in envelopes:
                status_icon = {
                    VerificationStatus.VERIFIED: "✅",
                    VerificationStatus.PENDING: "⏳",
                    VerificationStatus.FAILED: "❌",
                    VerificationStatus.STALE: "⚠️",
                }.get(env.verification_status, "❓")

                fresh = env.is_fresh()

                with st.expander(
                    f"{status_icon} Step {env.step_number} — {env.content.get('step_name', 'Unknown')} "
                    f"({'🟢 Fresh' if fresh else '🔴 Stale'})",
                    expanded=True,
                ):
                    col_a, col_b = st.columns(2)

                    with col_a:
                        st.markdown("**Evidence Identity**")
                        st.code(f"ID: {env.evidence_id}\nRun: {env.run_id[:8]}...\nStep: {env.step_number}")

                        st.markdown("**Provenance**")
                        st.code(
                            f"Source: {env.source}\n"
                            f"Type: {env.evidence_type.value}\n"
                            f"Provenance: {env.provenance}"
                        )

                    with col_b:
                        st.markdown("**Verification & Validity**")
                        st.code(
                            f"Status: {env.verification_status.value}\n"
                            f"Fresh: {'Yes' if fresh else 'No'}\n"
                            f"Freshness window: {env.freshness_seconds}s\n"
                            f"Created: {env.timestamp.strftime('%H:%M:%S UTC')}"
                        )

                        st.markdown("**Resource Consumption**")
                        st.code(
                            f"Tokens: {env.tokens_used}\n"
                            f"Cost: ${env.cost_usd:.6f}\n"
                            f"Latency: {env.latency_ms}ms"
                        )

                    st.markdown("**Summary**")
                    st.markdown(f"> {env.summary}")


# ============================= TAB: RECOVERY ==============================
with tab_recovery:
    st.markdown("### 🔧 Crash Recovery Comparison")
    st.markdown(
        "**The core EGAH question:** "
        "_State survived. But did the evidence survive?_"
    )

    run_id = st.session_state.get("run_id")
    if not run_id:
        st.info("Run a workflow with a crash first.")
    else:
        run = store.get_run(run_id)
        if not run or run.status != RunStatus.CRASHED:
            st.info(
                "No crashed workflow found. Use the Demo tab to run with a crash."
            )
        else:
            crash_step_actual = run.current_step + 1
            st.error(
                f"💥 **Workflow crashed at step {crash_step_actual}/{run.total_steps}** "
                f"({WORKFLOW_STEPS[crash_step_actual - 1]['name']})"
            )

            col_trad, col_egah = st.columns(2)

            # --- Traditional Recovery ---
            with col_trad:
                st.markdown("#### 🔶 Traditional Recovery")
                st.markdown("*Restores execution state only*")

                if st.button("Run Traditional Recovery", key="trad_recovery"):
                    trad_result = recovery_ctrl.traditional_recovery(run_id)
                    st.session_state[f"recovery_trad_{run_id}"] = trad_result

                trad = st.session_state.get(f"recovery_trad_{run_id}")
                if trad:
                    st.markdown(
                        f'<div class="recovery-traditional">',
                        unsafe_allow_html=True,
                    )

                    st.markdown(f"**Resume from:** Step {trad['resume_from_step']}")
                    st.markdown(f"**Execution state:** ✅ Restored")
                    st.markdown(f"**Evidence state:** ❌ Not checked")
                    st.markdown(f"**Verification history:** ❌ Not analysed")

                    for w in trad.get("warnings", []):
                        st.warning(w)

                    st.markdown(f"**Recommendation:** {trad['recommendation']}")
                    st.markdown("</div>", unsafe_allow_html=True)

                    if st.button("▶️ Resume (Traditional)", key="resume_trad"):
                        recovery_ctrl.resume_after_traditional_recovery(run_id)
                        remaining = agent.run_all(run_id)
                        st.session_state[f"results_{run_id}"].extend(remaining)
                        st.rerun()

            # --- EGAH Recovery ---
            with col_egah:
                st.markdown("#### 🟢 EGAH Recovery")
                st.markdown("*Restores execution + evidence + verification*")

                if st.button("Run EGAH Recovery", key="egah_recovery"):
                    plan = recovery_ctrl.egah_recovery(run_id, simulate_stale=True)
                    st.session_state[f"recovery_egah_{run_id}"] = plan

                plan = st.session_state.get(f"recovery_egah_{run_id}")
                if plan:
                    st.markdown(
                        f'<div class="recovery-egah">', unsafe_allow_html=True
                    )

                    st.markdown(f"**Execution state:** ✅ Restored")
                    st.markdown(f"**Evidence state:** ✅ Restored")
                    st.markdown(f"**Verification history:** ✅ Analysed")

                    # Evidence analysis
                    st.markdown("---")
                    st.markdown("**Evidence Validity Analysis:**")

                    for ev_result in plan.evidence_analysis:
                        fresh_icon = "🟢" if ev_result.current_freshness else "🔴"
                        valid_icon = "✅" if ev_result.current_validity else "❌"
                        reval_icon = "🔄" if ev_result.needs_revalidation else "✓"

                        st.markdown(
                            f"- Step {ev_result.step_number}: "
                            f"Fresh {fresh_icon} | Valid {valid_icon} | "
                            f"Revalidation {reval_icon} → "
                            f"`{ev_result.recommendation.value}`"
                        )

                    st.markdown("---")

                    safe_icon = "✅" if plan.safe_to_resume else "🔴"
                    st.markdown(f"**Safe to resume:** {safe_icon}")

                    if plan.resume_from_step:
                        st.markdown(f"**Resume from:** Step {plan.resume_from_step}")

                    if plan.revalidation_required:
                        st.markdown(
                            f"**Revalidation needed:** {len(plan.revalidation_required)} envelope(s)"
                        )

                    st.markdown(f"**Recommendation:** {plan.recommendation}")
                    st.markdown("</div>", unsafe_allow_html=True)

                    if plan.safe_to_resume:
                        if st.button("▶️ Resume (EGAH)", key="resume_egah"):
                            recovery_ctrl.resume_after_egah_recovery(run_id)
                            remaining = agent.run_all(run_id)
                            st.session_state[f"results_{run_id}"].extend(remaining)
                            st.rerun()


# ============================= TAB: AUDIT TRAIL ===========================
with tab_audit:
    st.markdown("### 📊 Audit Trail & Resource Accounting")

    run_id = st.session_state.get("run_id")
    if not run_id:
        st.info("Run a workflow first.")
    else:
        run = store.get_run(run_id)
        if not run:
            st.warning("Run not found.")
        else:
            # --- Summary metrics ---
            col1, col2, col3, col4 = st.columns(4)

            envelopes = store.get_evidence_for_run(run_id)
            verifications = store.get_verifications_for_run(run_id)
            resources = store.get_resources_for_run(run_id)

            total_tokens = sum(r.total_tokens for r in resources)
            total_cost = sum(r.cost_usd for r in resources)

            with col1:
                st.metric("Steps Completed", len([s for s in run.steps if s.status == "completed"]))
            with col2:
                st.metric("Evidence Envelopes", len(envelopes))
            with col3:
                st.metric("Verifications", len(verifications))
            with col4:
                st.metric("Total Cost", f"${total_cost:.6f}")

            st.divider()

            # --- Verification History ---
            st.markdown("#### Verification History")
            if verifications:
                for v in verifications:
                    decision_icon = {
                        PolicyDecision.ACT: "🟢",
                        PolicyDecision.REFRESH: "🟡",
                        PolicyDecision.ASK: "🟠",
                        PolicyDecision.ABSTAIN: "🔴",
                    }.get(v.policy_decision, "❓")

                    st.markdown(
                        f"**{decision_icon} Step {v.step_number}** — "
                        f"Decision: `{v.policy_decision.value}` | "
                        f"Status: `{v.verification_status.value}` | "
                        f"Verifier: `{v.verifier}` | "
                        f"Time: `{v.timestamp.strftime('%H:%M:%S')}`"
                    )
                    st.caption(f"↳ {v.reason}")
            else:
                st.info("No verification records yet.")

            st.divider()

            # --- Resource Accounting ---
            st.markdown("#### Resource Accounting")
            if resources:
                for r in resources:
                    st.markdown(
                        f"**Step {r.step_number}** — "
                        f"Model: `{r.model}` | "
                        f"Tokens: {r.total_tokens} "
                        f"(↑{r.prompt_tokens} ↓{r.completion_tokens}) | "
                        f"Cost: ${r.cost_usd:.6f} | "
                        f"Latency: {r.latency_ms}ms"
                    )
            else:
                st.info("No resource records yet.")

            st.divider()

            # --- Step execution details ---
            st.markdown("#### Step Execution Log")
            if run.steps:
                for s in run.steps:
                    status_icon = {"completed": "✅", "crashed": "💥", "pending": "⏳"}.get(
                        s.status, "❓"
                    )
                    cp_tag = " 🔒CHECKPOINT" if s.has_checkpoint else ""
                    ev_tag = f" | Evidence: `{s.evidence_id[:8]}...`" if s.evidence_id else ""

                    st.markdown(
                        f"{status_icon} **Step {s.step_number}: {s.step_name}**{cp_tag}{ev_tag}"
                    )
                    if s.output:
                        st.caption(f"↳ {s.output[:150]}")


# ============================= TAB: ABOUT =================================
with tab_about:
    st.markdown(
        """
        ### About EGAH

        **Evidence-Governed Agent Harnesses** explore treating evidence as
        first-class runtime state in agent systems.

        #### The Problem

        Long-running agents don't just need to remember *where they were*.
        They need to know:
        - What they had already verified
        - Which evidence is still valid
        - What was accomplished
        - What can safely happen next

        #### The EGAH Approach

        The execution pattern evolves from:

        `Plan → Tool Call → Result → Next Step`

        to:

        `Plan → Evidence Checkpoint → Tool Call → Verification → Evidence Update → Next`

        #### Key Distinction

        | Observability | EGAH |
        |---|---|
        | Records execution | Governs continuation |
        | Primarily diagnostic | Decision-bearing |
        | Logs events | Maintains evidence state |
        | Shows what happened | Determines what remains valid |
        | Retrospective | Prospective |
        | "What happened?" | "What can happen next?" |

        #### Architecture

        ```
        ┌────────────────────────────────────────────┐
        │              EGAH RUNTIME                   │
        │                                             │
        │  DURABLE EXECUTION STATE                    │
        │  Graph • Checkpoints • Memory               │
        │                                             │
        │  DURABLE EVIDENCE STATE                     │
        │  Provenance • Validity • Verification       │
        │                                             │
        │  POLICY / DECISION CONTROL                  │
        │  Continue • Refresh • Escalate • Abstain    │
        └────────────────────────────────────────────┘
                        │ telemetry
                        ▼
        ┌────────────────────────────────────────────┐
        │          OBSERVABILITY PLANE                │
        │  OpenTelemetry / Langfuse / Datadog / etc. │
        └────────────────────────────────────────────┘
        ```

        #### Core Principle

        > *Observability tells us what happened.*
        > *EGAH asks whether what happened is still sufficient evidence*
        > *for what the agent is about to do.*

        ---
        **Research:** Shaik Khaja Nayab Rasool
        """
    )
