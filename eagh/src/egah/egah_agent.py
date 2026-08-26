"""
EGAH PoC — Evidence-Governed Agent (LangGraph Workflow)

Implements the EGAH evidence-enhanced execution graph:

    Plan → Evidence Checkpoint → Tool Call → Result Verification → Evidence Update → Next

The workflow simulates a 10-step document-analysis pipeline where evidence
checkpoints fire at steps 3, 6 and 9.  A crash can be injected at any step
to demonstrate evidence-governed recovery vs traditional state-only recovery.

Core EGAH Principle:
  Observability tells us what happened.
  EGAH determines whether what happened is still sufficient evidence
  for what the agent is about to do.
"""

from __future__ import annotations

import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from openai import OpenAI

from egah.evidence_store import EvidenceStore
from egah.models import (
    EvidenceEnvelope,
    EvidenceType,
    PolicyDecision,
    ResourceRecord,
    RunStatus,
    StepRecord,
    VerificationRecord,
    VerificationStatus,
    WorkflowRun,
)

# ---------------------------------------------------------------------------
# Workflow step definitions — a 10-step document analysis pipeline
# ---------------------------------------------------------------------------

WORKFLOW_STEPS = [
    {"step": 1, "name": "Receive Document", "description": "Ingest and validate the input document"},
    {"step": 2, "name": "Parse Structure", "description": "Extract sections, headings, metadata"},
    {"step": 3, "name": "Extract Entities", "description": "Identify key entities, dates, amounts"},
    {"step": 4, "name": "Classify Content", "description": "Determine document type and risk level"},
    {"step": 5, "name": "Cross-Reference", "description": "Check entities against external data sources"},
    {"step": 6, "name": "Assess Risk", "description": "Evaluate compliance and risk indicators"},
    {"step": 7, "name": "Generate Findings", "description": "Produce structured findings from analysis"},
    {"step": 8, "name": "Validate Findings", "description": "Verify findings against source evidence"},
    {"step": 9, "name": "Create Report", "description": "Generate final analysis report"},
    {"step": 10, "name": "Finalize & Sign-off", "description": "Complete workflow with audit trail"},
]

CHECKPOINT_STEPS = [3, 6, 9]


class EGAHAgent:
    """
    Evidence-Governed Agent Harness.

    Orchestrates a multi-step workflow with:
    - Durable execution state (step progress)
    - Durable evidence state (evidence envelopes)
    - Verification history
    - Resource accounting
    - Crash simulation
    - Evidence-aware recovery
    """

    def __init__(
        self,
        store: EvidenceStore,
        openai_api_key: Optional[str] = None,
        use_llm: bool = True,
    ):
        self.store = store
        self.use_llm = use_llm and openai_api_key is not None
        if self.use_llm:
            self.client = OpenAI(api_key=openai_api_key)
        else:
            self.client = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_run(self, task_description: str) -> WorkflowRun:
        """Create a new workflow run."""
        run = WorkflowRun(
            task_description=task_description,
            total_steps=len(WORKFLOW_STEPS),
            checkpoint_steps=CHECKPOINT_STEPS,
        )
        self.store.save_run(run)
        return run

    def execute_step(
        self,
        run_id: str,
        crash_at_step: Optional[int] = None,
        callback: Any = None,
    ) -> dict:
        """
        Execute the *next* pending step in the workflow.

        Returns a dict with:
          step_number, step_name, status, output,
          evidence (if checkpoint), verification (if checkpoint),
          resource, crashed (bool)
        """
        run = self.store.get_run(run_id)
        if run is None:
            return {"error": "Run not found"}
        if run.status in (RunStatus.COMPLETED, RunStatus.CRASHED):
            return {"error": f"Run is {run.status.value}"}

        next_step_num = run.current_step + 1
        if next_step_num > run.total_steps:
            return {"error": "All steps completed"}

        step_def = WORKFLOW_STEPS[next_step_num - 1]

        # --- Crash injection ---
        if crash_at_step and next_step_num == crash_at_step:
            return self._simulate_crash(run, next_step_num, step_def)

        # --- Execute step ---
        result = self._execute_single_step(run, next_step_num, step_def)

        # --- Save updated run ---
        run.current_step = next_step_num
        run.updated_at = datetime.now(timezone.utc)
        if next_step_num == run.total_steps:
            run.status = RunStatus.COMPLETED
        self.store.save_run(run)

        return result

    def run_all(
        self,
        run_id: str,
        crash_at_step: Optional[int] = None,
        step_callback: Any = None,
    ) -> list[dict]:
        """Execute all remaining steps, with optional crash injection."""
        results = []
        run = self.store.get_run(run_id)
        if not run:
            return [{"error": "Run not found"}]

        remaining = run.total_steps - run.current_step
        for _ in range(remaining):
            result = self.execute_step(run_id, crash_at_step=crash_at_step, callback=step_callback)
            results.append(result)
            if step_callback:
                step_callback(result)
            if result.get("crashed") or result.get("error"):
                break
        return results

    # ------------------------------------------------------------------
    # Internal: single step execution
    # ------------------------------------------------------------------

    def _execute_single_step(self, run: WorkflowRun, step_num: int, step_def: dict) -> dict:
        """Execute one step with evidence checkpoint logic."""
        is_checkpoint = step_num in run.checkpoint_steps
        started = datetime.now(timezone.utc)
        t0 = time.time()

        # --- Call LLM (or simulate) ---
        llm_output, resource = self._call_llm(run, step_num, step_def)
        latency = int((time.time() - t0) * 1000)

        # --- Build step record ---
        step_record = StepRecord(
            step_number=step_num,
            step_name=step_def["name"],
            status="completed",
            started_at=started,
            completed_at=datetime.now(timezone.utc),
            output=llm_output,
            has_checkpoint=is_checkpoint,
        )

        result = {
            "step_number": step_num,
            "step_name": step_def["name"],
            "status": "completed",
            "output": llm_output,
            "is_checkpoint": is_checkpoint,
            "latency_ms": latency,
            "crashed": False,
        }

        # --- Evidence checkpoint ---
        evidence = None
        verification = None
        if is_checkpoint:
            evidence, verification = self._evidence_checkpoint(
                run, step_num, step_def, llm_output, resource
            )
            step_record.evidence_id = evidence.evidence_id
            result["evidence"] = evidence.dict()
            result["verification"] = verification.dict()

        # --- Save resource record ---
        if resource:
            self.store.save_resource(resource)
            result["resource"] = resource.dict()

        # --- Update run's step list ---
        run.steps.append(step_record)

        return result

    # ------------------------------------------------------------------
    # Evidence Checkpoint — the core EGAH mechanism
    # ------------------------------------------------------------------

    def _evidence_checkpoint(
        self,
        run: WorkflowRun,
        step_num: int,
        step_def: dict,
        llm_output: str,
        resource: Optional[ResourceRecord],
    ) -> tuple[EvidenceEnvelope, VerificationRecord]:
        """
        EGAH Evidence Checkpoint:
        1. Capture current state
        2. Create evidence envelope
        3. Verify evidence (policy evaluation)
        4. Persist both evidence + verification
        """

        # 1. Create evidence envelope
        envelope = EvidenceEnvelope(
            run_id=run.run_id,
            step_number=step_num,
            evidence_type=EvidenceType.LLM_OUTPUT,
            source=f"llm:gpt-4o-mini",
            content={
                "step_name": step_def["name"],
                "step_description": step_def["description"],
                "output": llm_output,
                "task": run.task_description,
            },
            summary=f"Evidence from step {step_num} ({step_def['name']}): {llm_output[:120]}",
            provenance=f"EGAH agent / run {run.run_id} / step {step_num}",
            verification_status=VerificationStatus.PENDING,
            freshness_seconds=300,  # 5-minute freshness for demo
            tokens_used=resource.total_tokens if resource else 0,
            cost_usd=resource.cost_usd if resource else 0.0,
            latency_ms=resource.latency_ms if resource else 0,
        )

        # 2. Verify evidence (simplified policy: check content is non-empty)
        is_verified = bool(llm_output and len(llm_output) > 10)
        envelope.verification_status = (
            VerificationStatus.VERIFIED if is_verified else VerificationStatus.FAILED
        )

        # 3. Create verification record
        policy_decision = PolicyDecision.ACT if is_verified else PolicyDecision.ASK
        verification = VerificationRecord(
            run_id=run.run_id,
            step_number=step_num,
            evidence_id=envelope.evidence_id,
            verification_status=envelope.verification_status,
            policy_decision=policy_decision,
            reason=(
                f"Evidence verified: output length={len(llm_output)}, "
                f"content valid={'yes' if is_verified else 'no'}"
            ),
            verifier="system",
        )

        # 4. Persist
        self.store.save_evidence(envelope)
        self.store.save_verification(verification)

        return envelope, verification

    # ------------------------------------------------------------------
    # Crash simulation
    # ------------------------------------------------------------------

    def _simulate_crash(self, run: WorkflowRun, step_num: int, step_def: dict) -> dict:
        """Simulate a crash at the given step — execution state saved, but step incomplete."""
        run.status = RunStatus.CRASHED
        run.current_step = step_num - 1  # crashed BEFORE completing this step
        run.updated_at = datetime.now(timezone.utc)

        crash_step = StepRecord(
            step_number=step_num,
            step_name=step_def["name"],
            status="crashed",
            started_at=datetime.now(timezone.utc),
            has_checkpoint=step_num in run.checkpoint_steps,
        )
        run.steps.append(crash_step)
        self.store.save_run(run)

        return {
            "step_number": step_num,
            "step_name": step_def["name"],
            "status": "crashed",
            "output": None,
            "crashed": True,
            "message": (
                f"💥 CRASH at step {step_num}/{run.total_steps} ({step_def['name']}). "
                f"Execution state saved. Evidence state: "
                f"{'preserved up to last checkpoint' if any(s.has_checkpoint for s in run.steps[:-1]) else 'NONE'}."
            ),
        }

    # ------------------------------------------------------------------
    # LLM interaction (or simulation)
    # ------------------------------------------------------------------

    def _call_llm(
        self, run: WorkflowRun, step_num: int, step_def: dict
    ) -> tuple[str, Optional[ResourceRecord]]:
        """Call GPT-4o-mini or generate simulated output."""

        prompt = (
            f"You are an AI document analysis agent performing step {step_num} of a "
            f"{run.total_steps}-step workflow.\n\n"
            f"Task: {run.task_description}\n"
            f"Current Step: {step_def['name']}\n"
            f"Step Description: {step_def['description']}\n\n"
            f"Provide a concise (2-3 sentence) result for this step. "
            f"Be specific and factual."
        )

        if self.use_llm and self.client:
            try:
                t0 = time.time()
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.3,
                )
                latency = int((time.time() - t0) * 1000)
                output = response.choices[0].message.content.strip()
                usage = response.usage

                resource = ResourceRecord(
                    run_id=run.run_id,
                    step_number=step_num,
                    model="gpt-4o-mini",
                    prompt_tokens=usage.prompt_tokens,
                    completion_tokens=usage.completion_tokens,
                    total_tokens=usage.total_tokens,
                    cost_usd=round(
                        (usage.prompt_tokens * 0.15 + usage.completion_tokens * 0.60)
                        / 1_000_000,
                        6,
                    ),
                    latency_ms=latency,
                )
                return output, resource

            except Exception as e:
                return self._simulated_output(step_num, step_def, run), None
        else:
            return self._simulated_output(step_num, step_def, run), self._simulated_resource(
                run.run_id, step_num
            )

    def _simulated_output(self, step_num: int, step_def: dict, run: WorkflowRun) -> str:
        """Generate realistic simulated output when no LLM is available."""
        outputs = {
            1: f"Document received and validated. Format: PDF, 12 pages. Title: '{run.task_description}'. Checksum verified.",
            2: "Parsed document structure: 5 sections, 3 tables, 2 appendices. Metadata extracted: author, date, classification level.",
            3: "Extracted 14 entities: 3 organizations, 4 persons, 2 monetary amounts ($45,000 and $120,000), 3 dates, 2 regulatory references.",
            4: "Document classified as: Financial Compliance Report. Risk level: Medium. Contains regulatory references requiring cross-check.",
            5: "Cross-referenced 14 entities against 3 external databases. 12/14 confirmed. 2 entities flagged for manual verification: 'Acme Holdings' and 'Q3 filing date'.",
            6: "Risk assessment complete. Overall risk: MEDIUM. 2 compliance gaps identified: (1) Missing signatory on appendix B, (2) Outdated regulatory reference in Section 4.",
            7: "Generated 6 findings: 2 critical (compliance gaps), 2 informational (entity confirmations), 2 recommendations (update references, obtain signature).",
            8: "Validated all 6 findings against source evidence. 5/6 fully supported. Finding #4 has partial support — source entity 'Acme Holdings' requires external confirmation.",
            9: "Final report generated: 4-page summary with executive overview, detailed findings, risk matrix, and recommended actions. All findings traceable to source evidence.",
            10: "Workflow finalized. Audit trail complete: 10 steps executed, 3 evidence checkpoints verified, 6 findings documented, 2 actions recommended. Ready for sign-off.",
        }
        return outputs.get(step_num, f"Step {step_num} ({step_def['name']}) completed successfully.")

    def _simulated_resource(self, run_id: str, step_num: int) -> ResourceRecord:
        """Generate simulated resource consumption."""
        import random

        prompt_tokens = random.randint(80, 150)
        completion_tokens = random.randint(40, 100)
        return ResourceRecord(
            run_id=run_id,
            step_number=step_num,
            model="gpt-4o-mini (simulated)",
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            cost_usd=round(
                (prompt_tokens * 0.15 + completion_tokens * 0.60) / 1_000_000, 6
            ),
            latency_ms=random.randint(200, 800),
        )
