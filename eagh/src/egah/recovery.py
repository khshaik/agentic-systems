"""
EGAH PoC — Recovery Controller

Implements two recovery modes to demonstrate the EGAH value proposition:

1. Traditional Recovery:
   - Restores execution state only (which step we were on)
   - Resumes blindly — no evidence validity check
   - Risk: evidence may be stale, unverified, or missing

2. EGAH Recovery (Evidence-Governed):
   - Restores execution state
   - Restores evidence state (all envelopes up to crash point)
   - Restores verification history
   - Analyses evidence freshness and validity
   - Determines: RESUME / REFRESH / ESCALATE / ABORT
   - Only resumes when evidence supports safe continuation

This is the critical demo differentiator:
  "State survived. But did the evidence survive?"
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from egah.evidence_store import EvidenceStore
from egah.models import (
    EvidenceEnvelope,
    EvidenceValidityResult,
    PolicyDecision,
    RecoveryPlan,
    RunStatus,
    VerificationRecord,
    VerificationStatus,
    WorkflowRun,
)


class RecoveryController:
    """
    Manages crash recovery for EGAH workflows.

    The key insight: traditional checkpoint recovery restores WHERE the agent was.
    EGAH recovery also restores WHAT the agent knew, verified, and accomplished.
    """

    def __init__(self, store: EvidenceStore):
        self.store = store

    # ------------------------------------------------------------------
    # Traditional Recovery — state only, no evidence analysis
    # ------------------------------------------------------------------

    def traditional_recovery(self, run_id: str) -> dict:
        """
        Traditional recovery: restore execution state and continue.
        No evidence validity check. No verification history analysis.
        This is what most agent frameworks do today.
        """
        run = self.store.get_run(run_id)
        if not run or run.status != RunStatus.CRASHED:
            return {"error": "Run not found or not in crashed state"}

        crash_step = run.current_step + 1  # the step that crashed

        return {
            "recovery_type": "traditional",
            "run_id": run_id,
            "crash_step": crash_step,
            "execution_state_restored": True,
            "evidence_state_restored": False,
            "verification_history_checked": False,
            "resume_from_step": crash_step,
            "warnings": [
                f"⚠️ Resuming from step {crash_step} without evidence validation.",
                "⚠️ No check whether prior evidence is still fresh or valid.",
                "⚠️ No verification history analysis.",
                "⚠️ Agent will continue as if nothing happened.",
            ],
            "safe_to_resume": True,  # traditional always says yes
            "recommendation": (
                f"Traditional recovery resumes at step {crash_step}. "
                f"Execution state restored. Evidence state: NOT CHECKED. "
                f"The agent will proceed without knowing whether its prior "
                f"observations, verifications and decisions remain valid."
            ),
        }

    # ------------------------------------------------------------------
    # EGAH Recovery — full evidence-governed recovery
    # ------------------------------------------------------------------

    def egah_recovery(
        self,
        run_id: str,
        simulate_stale: bool = True,
        stale_age_seconds: int = 300,
    ) -> RecoveryPlan:
        """
        EGAH evidence-governed recovery:
        1. Restore execution state
        2. Restore evidence state (all envelopes)
        3. Restore verification history
        4. Analyse evidence freshness & validity
        5. Generate recovery plan with recommendations
        """
        run = self.store.get_run(run_id)
        if not run or run.status != RunStatus.CRASHED:
            return RecoveryPlan(
                run_id=run_id,
                crash_step=0,
                recommendation="Run not found or not in crashed state",
            )

        crash_step = run.current_step + 1

        # 1. Restore evidence state
        evidence_envelopes = self.store.get_evidence_up_to_step(run_id, crash_step)

        # 2. Restore verification history
        verifications = self.store.get_verifications_for_run(run_id)

        # 3. Analyse each evidence envelope
        analysis = []
        revalidation_needed = []

        for envelope in evidence_envelopes:
            # Check freshness
            if simulate_stale:
                # For demo: artificially age the earliest evidence
                is_fresh = envelope.step_number > (crash_step - 3)
            else:
                is_fresh = envelope.is_fresh()

            # Check validity
            is_valid = envelope.verification_status == VerificationStatus.VERIFIED
            needs_revalidation = not is_fresh or not is_valid

            if needs_revalidation:
                recommendation = PolicyDecision.REFRESH
                revalidation_needed.append(envelope.evidence_id)
            else:
                recommendation = PolicyDecision.ACT

            validity_result = EvidenceValidityResult(
                evidence_id=envelope.evidence_id,
                step_number=envelope.step_number,
                summary=envelope.summary,
                original_status=envelope.verification_status,
                current_freshness=is_fresh,
                current_validity=is_valid,
                needs_revalidation=needs_revalidation,
                recommendation=recommendation,
            )
            analysis.append(validity_result)

        # 4. Determine overall recovery strategy
        all_valid = all(not a.needs_revalidation for a in analysis)
        any_critical_stale = any(
            a.needs_revalidation and a.step_number <= 3 for a in analysis
        )

        if all_valid:
            safe_to_resume = True
            resume_step = crash_step
            recommendation = (
                f"✅ All evidence is fresh and verified. "
                f"Safe to resume from step {crash_step}."
            )
        elif any_critical_stale:
            safe_to_resume = False
            resume_step = None
            recommendation = (
                f"🔴 Critical evidence from early steps is stale. "
                f"{len(revalidation_needed)} evidence envelope(s) need revalidation. "
                f"Recommend refreshing evidence before continuing."
            )
        else:
            safe_to_resume = True
            resume_step = crash_step
            recommendation = (
                f"🟡 Some evidence is stale ({len(revalidation_needed)} envelope(s)). "
                f"Can resume from step {crash_step} with revalidation of flagged evidence."
            )

        plan = RecoveryPlan(
            run_id=run_id,
            crash_step=crash_step,
            execution_state_restored=True,
            evidence_state_restored=True,
            verification_history_restored=True,
            evidence_analysis=analysis,
            safe_to_resume=safe_to_resume,
            resume_from_step=resume_step,
            revalidation_required=revalidation_needed,
            recommendation=recommendation,
        )

        return plan

    # ------------------------------------------------------------------
    # Resume execution after EGAH recovery
    # ------------------------------------------------------------------

    def resume_after_egah_recovery(self, run_id: str) -> WorkflowRun:
        """Mark the run as recovered so execution can continue."""
        run = self.store.get_run(run_id)
        if run and run.status == RunStatus.CRASHED:
            run.status = RunStatus.RECOVERED
            run.updated_at = datetime.now(timezone.utc)
            # Remove the crashed step record so it can be retried
            run.steps = [s for s in run.steps if s.status != "crashed"]
            self.store.save_run(run)
        return run

    def resume_after_traditional_recovery(self, run_id: str) -> WorkflowRun:
        """Mark the run as running (traditional — no evidence check)."""
        run = self.store.get_run(run_id)
        if run and run.status == RunStatus.CRASHED:
            run.status = RunStatus.RUNNING
            run.updated_at = datetime.now(timezone.utc)
            run.steps = [s for s in run.steps if s.status != "crashed"]
            self.store.save_run(run)
        return run
