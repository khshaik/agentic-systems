"""
EGAH PoC — End-to-end tests

Tests the core EGAH workflow:
1. Normal execution with evidence checkpoints
2. Crash simulation and evidence preservation
3. Traditional vs EGAH recovery comparison
4. Evidence freshness and validity checking
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from egah.evidence_store import EvidenceStore
from egah.egah_agent import EGAHAgent
from egah.models import PolicyDecision, RunStatus, VerificationStatus
from egah.recovery import RecoveryController


@pytest.fixture
def store(tmp_path):
    """Create a fresh store with a temp DB for each test."""
    return EvidenceStore(db_path=tmp_path / "test.db")


@pytest.fixture
def agent(store):
    return EGAHAgent(store=store, use_llm=False)


@pytest.fixture
def recovery(store):
    return RecoveryController(store=store)


class TestNormalExecution:
    """Test normal workflow execution without crashes."""

    def test_create_run(self, agent):
        run = agent.create_run("Test task")
        assert run.run_id
        assert run.status == RunStatus.RUNNING
        assert run.total_steps == 10

    def test_full_execution(self, agent, store):
        run = agent.create_run("Full run test")
        results = agent.run_all(run.run_id)

        assert len(results) == 10
        assert all(not r.get("crashed") for r in results)

        updated_run = store.get_run(run.run_id)
        assert updated_run.status == RunStatus.COMPLETED
        assert updated_run.current_step == 10

    def test_evidence_checkpoints_created(self, agent, store):
        run = agent.create_run("Checkpoint test")
        agent.run_all(run.run_id)

        envelopes = store.get_evidence_for_run(run.run_id)
        assert len(envelopes) == 3  # checkpoints at steps 3, 6, 9
        assert [e.step_number for e in envelopes] == [3, 6, 9]

    def test_evidence_verified(self, agent, store):
        run = agent.create_run("Verify test")
        agent.run_all(run.run_id)

        envelopes = store.get_evidence_for_run(run.run_id)
        for env in envelopes:
            assert env.verification_status == VerificationStatus.VERIFIED

    def test_verification_history(self, agent, store):
        run = agent.create_run("History test")
        agent.run_all(run.run_id)

        verifications = store.get_verifications_for_run(run.run_id)
        assert len(verifications) == 3  # one per checkpoint


class TestCrashSimulation:
    """Test crash simulation and state preservation."""

    def test_crash_at_step_7(self, agent, store):
        run = agent.create_run("Crash test")
        results = agent.run_all(run.run_id, crash_at_step=7)

        assert len(results) == 7  # steps 1-6 complete, step 7 crashes
        assert results[-1]["crashed"] is True

        updated_run = store.get_run(run.run_id)
        assert updated_run.status == RunStatus.CRASHED
        assert updated_run.current_step == 6  # completed up to step 6

    def test_evidence_preserved_before_crash(self, agent, store):
        run = agent.create_run("Evidence preservation test")
        agent.run_all(run.run_id, crash_at_step=7)

        envelopes = store.get_evidence_for_run(run.run_id)
        assert len(envelopes) == 2  # checkpoints at steps 3 and 6
        assert envelopes[0].step_number == 3
        assert envelopes[1].step_number == 6

    def test_crash_at_checkpoint_step(self, agent, store):
        run = agent.create_run("Crash at checkpoint test")
        agent.run_all(run.run_id, crash_at_step=6)

        envelopes = store.get_evidence_for_run(run.run_id)
        assert len(envelopes) == 1  # only step 3 checkpoint completed


class TestRecovery:
    """Test traditional vs EGAH recovery."""

    def test_traditional_recovery(self, agent, store, recovery):
        run = agent.create_run("Traditional recovery test")
        agent.run_all(run.run_id, crash_at_step=7)

        result = recovery.traditional_recovery(run.run_id)

        assert result["execution_state_restored"] is True
        assert result["evidence_state_restored"] is False
        assert result["verification_history_checked"] is False
        assert result["resume_from_step"] == 7
        assert len(result["warnings"]) > 0

    def test_egah_recovery(self, agent, store, recovery):
        run = agent.create_run("EGAH recovery test")
        agent.run_all(run.run_id, crash_at_step=7)

        plan = recovery.egah_recovery(run.run_id, simulate_stale=True)

        assert plan.execution_state_restored is True
        assert plan.evidence_state_restored is True
        assert plan.verification_history_restored is True
        assert len(plan.evidence_analysis) > 0

    def test_egah_detects_stale_evidence(self, agent, store, recovery):
        run = agent.create_run("Stale detection test")
        agent.run_all(run.run_id, crash_at_step=7)

        plan = recovery.egah_recovery(run.run_id, simulate_stale=True)

        stale = [a for a in plan.evidence_analysis if a.needs_revalidation]
        assert len(stale) > 0  # at least one stale envelope

    def test_resume_after_egah_recovery(self, agent, store, recovery):
        run = agent.create_run("Resume test")
        agent.run_all(run.run_id, crash_at_step=7)

        recovery.resume_after_egah_recovery(run.run_id)
        updated = store.get_run(run.run_id)
        assert updated.status == RunStatus.RECOVERED

        remaining = agent.run_all(run.run_id)
        final = store.get_run(run.run_id)
        assert final.status == RunStatus.COMPLETED
        assert final.current_step == 10


class TestResourceAccounting:
    """Test resource/cost tracking."""

    def test_resources_recorded(self, agent, store):
        run = agent.create_run("Resource test")
        agent.run_all(run.run_id)

        resources = store.get_resources_for_run(run.run_id)
        assert len(resources) == 10  # one per step

    def test_total_cost(self, agent, store):
        run = agent.create_run("Cost test")
        agent.run_all(run.run_id)

        total_cost = store.get_total_cost(run.run_id)
        assert total_cost > 0

    def test_total_tokens(self, agent, store):
        run = agent.create_run("Token test")
        agent.run_all(run.run_id)

        total_tokens = store.get_total_tokens(run.run_id)
        assert total_tokens > 0


class TestCrashAtStep7Scenario:
    """
    Full end-to-end crash-at-step-7 scenario — mirrors the Streamlit demo.

    Simulates the exact flow a user sees in the UI:
      1. Run 10-step workflow with crash at step 7
      2. Inspect execution state after crash
      3. Inspect evidence envelopes preserved before crash
      4. Inspect verification history
      5. Inspect resource accounting up to crash
      6. Run traditional recovery — blind resume
      7. Run EGAH recovery — evidence-governed analysis
      8. Compare traditional vs EGAH recovery decisions
      9. Resume after EGAH recovery
     10. Complete remaining steps and verify full audit trail
    """

    # -- Phase 1: Execute with crash at step 7 ---------------------------

    def test_step7_crash_executes_6_steps_then_crashes(self, agent, store):
        """Steps 1-6 complete successfully, step 7 crashes."""
        run = agent.create_run("Loan application analysis")
        results = agent.run_all(run.run_id, crash_at_step=7)

        # Steps 1-6 should succeed
        for i, r in enumerate(results[:6]):
            assert r["crashed"] is False, f"Step {i+1} should not have crashed"
            assert r["step_number"] == i + 1

        # Step 7 should crash
        assert results[6]["crashed"] is True
        assert results[6]["step_number"] == 7
        assert results[6]["step_name"] == "Generate Findings"

    def test_step7_crash_run_status(self, agent, store):
        """Run status should be CRASHED with current_step=6."""
        run = agent.create_run("Status check")
        agent.run_all(run.run_id, crash_at_step=7)

        run = store.get_run(run.run_id)
        assert run.status == RunStatus.CRASHED
        assert run.current_step == 6
        assert run.total_steps == 10

    # -- Phase 2: Inspect evidence after crash ----------------------------

    def test_step7_crash_preserves_two_evidence_envelopes(self, agent, store):
        """Checkpoints at steps 3 and 6 should produce 2 evidence envelopes."""
        run = agent.create_run("Evidence inspection")
        agent.run_all(run.run_id, crash_at_step=7)

        envelopes = store.get_evidence_for_run(run.run_id)
        assert len(envelopes) == 2
        assert envelopes[0].step_number == 3  # Extract Entities
        assert envelopes[1].step_number == 6  # Assess Risk

    def test_step7_crash_evidence_has_provenance(self, agent, store):
        """Each evidence envelope should have provenance and source."""
        run = agent.create_run("Provenance check")
        agent.run_all(run.run_id, crash_at_step=7)

        envelopes = store.get_evidence_for_run(run.run_id)
        for env in envelopes:
            assert env.provenance, f"Step {env.step_number}: missing provenance"
            assert env.source, f"Step {env.step_number}: missing source"
            assert env.summary, f"Step {env.step_number}: missing summary"
            assert env.content, f"Step {env.step_number}: missing content"

    def test_step7_crash_evidence_is_verified(self, agent, store):
        """Both envelopes should be verified at creation time."""
        run = agent.create_run("Verification status check")
        agent.run_all(run.run_id, crash_at_step=7)

        envelopes = store.get_evidence_for_run(run.run_id)
        for env in envelopes:
            assert env.verification_status == VerificationStatus.VERIFIED

    def test_step7_crash_no_step9_evidence(self, agent, store):
        """Step 9 checkpoint should NOT have fired (crash was at step 7)."""
        run = agent.create_run("Missing checkpoint check")
        agent.run_all(run.run_id, crash_at_step=7)

        envelopes = store.get_evidence_for_run(run.run_id)
        step_numbers = [e.step_number for e in envelopes]
        assert 9 not in step_numbers

    # -- Phase 3: Inspect verification history ----------------------------

    def test_step7_crash_verification_records(self, agent, store):
        """Two verification records (steps 3 and 6) with ACT decisions."""
        run = agent.create_run("Verification history check")
        agent.run_all(run.run_id, crash_at_step=7)

        verifications = store.get_verifications_for_run(run.run_id)
        assert len(verifications) == 2
        assert verifications[0].step_number == 3
        assert verifications[1].step_number == 6

        for v in verifications:
            assert v.policy_decision == PolicyDecision.ACT
            assert v.verification_status == VerificationStatus.VERIFIED
            assert v.reason, f"Step {v.step_number}: verification reason missing"

    # -- Phase 4: Resource accounting up to crash -------------------------

    def test_step7_crash_resources_for_completed_steps(self, agent, store):
        """Resource records should exist for steps 1-6 (completed) only."""
        run = agent.create_run("Resource accounting check")
        agent.run_all(run.run_id, crash_at_step=7)

        resources = store.get_resources_for_run(run.run_id)
        # Steps 1-6 completed, step 7 crashed (may or may not have resource)
        assert len(resources) >= 6
        for r in resources:
            assert r.total_tokens > 0
            assert r.cost_usd >= 0
            assert r.latency_ms >= 0

    # -- Phase 5: Traditional recovery — blind resume ---------------------

    def test_step7_traditional_recovery_resumes_blindly(self, agent, store, recovery):
        """Traditional recovery resumes at step 7 with no evidence checks."""
        run = agent.create_run("Traditional recovery")
        agent.run_all(run.run_id, crash_at_step=7)

        result = recovery.traditional_recovery(run.run_id)

        assert result["recovery_type"] == "traditional"
        assert result["crash_step"] == 7
        assert result["resume_from_step"] == 7
        assert result["execution_state_restored"] is True
        assert result["evidence_state_restored"] is False
        assert result["verification_history_checked"] is False
        assert result["safe_to_resume"] is True  # always True for traditional
        assert len(result["warnings"]) == 4

    def test_step7_traditional_warnings_content(self, agent, store, recovery):
        """Traditional recovery warnings should mention missing evidence checks."""
        run = agent.create_run("Warning content check")
        agent.run_all(run.run_id, crash_at_step=7)

        result = recovery.traditional_recovery(run.run_id)
        warnings_text = " ".join(result["warnings"])

        assert "evidence" in warnings_text.lower()
        assert "step 7" in warnings_text or "step" in warnings_text.lower()

    # -- Phase 6: EGAH recovery — evidence-governed analysis ---------------

    def test_step7_egah_recovery_restores_all_state(self, agent, store, recovery):
        """EGAH recovery restores execution, evidence, and verification state."""
        run = agent.create_run("EGAH state restoration")
        agent.run_all(run.run_id, crash_at_step=7)

        plan = recovery.egah_recovery(run.run_id, simulate_stale=True)

        assert plan.execution_state_restored is True
        assert plan.evidence_state_restored is True
        assert plan.verification_history_restored is True
        assert plan.crash_step == 7

    def test_step7_egah_recovery_analyses_two_envelopes(self, agent, store, recovery):
        """EGAH should analyse exactly 2 evidence envelopes (steps 3 and 6)."""
        run = agent.create_run("Envelope analysis count")
        agent.run_all(run.run_id, crash_at_step=7)

        plan = recovery.egah_recovery(run.run_id, simulate_stale=True)

        assert len(plan.evidence_analysis) == 2
        steps_analysed = [a.step_number for a in plan.evidence_analysis]
        assert 3 in steps_analysed
        assert 6 in steps_analysed

    def test_step7_egah_detects_step3_as_stale(self, agent, store, recovery):
        """With simulate_stale=True, step 3 evidence should be flagged stale."""
        run = agent.create_run("Stale detection — step 3")
        agent.run_all(run.run_id, crash_at_step=7)

        plan = recovery.egah_recovery(run.run_id, simulate_stale=True)

        step3 = [a for a in plan.evidence_analysis if a.step_number == 3][0]
        assert step3.needs_revalidation is True
        assert step3.current_freshness is False
        assert step3.recommendation == PolicyDecision.REFRESH

    def test_step7_egah_step6_is_fresh(self, agent, store, recovery):
        """With simulate_stale=True, step 6 evidence should remain fresh."""
        run = agent.create_run("Fresh detection — step 6")
        agent.run_all(run.run_id, crash_at_step=7)

        plan = recovery.egah_recovery(run.run_id, simulate_stale=True)

        step6 = [a for a in plan.evidence_analysis if a.step_number == 6][0]
        assert step6.current_freshness is True
        assert step6.recommendation == PolicyDecision.ACT

    def test_step7_egah_revalidation_list(self, agent, store, recovery):
        """Revalidation list should contain exactly the stale evidence IDs."""
        run = agent.create_run("Revalidation list check")
        agent.run_all(run.run_id, crash_at_step=7)

        plan = recovery.egah_recovery(run.run_id, simulate_stale=True)

        assert len(plan.revalidation_required) >= 1
        stale_ids = {a.evidence_id for a in plan.evidence_analysis if a.needs_revalidation}
        assert set(plan.revalidation_required) == stale_ids

    def test_step7_egah_not_safe_due_to_critical_stale(self, agent, store, recovery):
        """Step 3 is critical (early step, <=3) and stale — resume should be unsafe."""
        run = agent.create_run("Safety decision check")
        agent.run_all(run.run_id, crash_at_step=7)

        plan = recovery.egah_recovery(run.run_id, simulate_stale=True)

        assert plan.safe_to_resume is False
        assert "stale" in plan.recommendation.lower() or "revalidat" in plan.recommendation.lower()

    # -- Phase 7: Compare traditional vs EGAH ----------------------------

    def test_step7_traditional_vs_egah_comparison(self, agent, store, recovery):
        """Side-by-side: traditional says 'go', EGAH says 'wait and check'."""
        run = agent.create_run("Comparison test")
        agent.run_all(run.run_id, crash_at_step=7)

        trad = recovery.traditional_recovery(run.run_id)
        egah = recovery.egah_recovery(run.run_id, simulate_stale=True)

        # Traditional: always resumes, ignores evidence
        assert trad["safe_to_resume"] is True
        assert trad["evidence_state_restored"] is False

        # EGAH: detects stale evidence, blocks blind resume
        assert egah.safe_to_resume is False
        assert egah.evidence_state_restored is True
        assert len(egah.revalidation_required) >= 1

    # -- Phase 8: Resume after EGAH recovery and complete ----------------

    def test_step7_resume_and_complete_all_10_steps(self, agent, store, recovery):
        """After EGAH recovery, resume and complete remaining steps 7-10."""
        run = agent.create_run("Full resume test")
        agent.run_all(run.run_id, crash_at_step=7)

        # EGAH recovery
        plan = recovery.egah_recovery(run.run_id, simulate_stale=True)
        assert plan.crash_step == 7

        # Resume
        recovery.resume_after_egah_recovery(run.run_id)
        recovered_run = store.get_run(run.run_id)
        assert recovered_run.status == RunStatus.RECOVERED

        # Complete remaining steps
        remaining_results = agent.run_all(run.run_id)
        final_run = store.get_run(run.run_id)
        assert final_run.status == RunStatus.COMPLETED
        assert final_run.current_step == 10

    def test_step7_resume_produces_step9_checkpoint(self, agent, store, recovery):
        """After resume, step 9 checkpoint should fire — producing 3rd evidence envelope."""
        run = agent.create_run("Step 9 checkpoint after resume")
        agent.run_all(run.run_id, crash_at_step=7)

        recovery.resume_after_egah_recovery(run.run_id)
        agent.run_all(run.run_id)

        envelopes = store.get_evidence_for_run(run.run_id)
        assert len(envelopes) == 3
        assert [e.step_number for e in envelopes] == [3, 6, 9]

    # -- Phase 9: Full audit trail after completion ----------------------

    def test_step7_full_audit_trail(self, agent, store, recovery):
        """After crash + recovery + completion: full audit trail exists."""
        run = agent.create_run("Audit trail test")
        agent.run_all(run.run_id, crash_at_step=7)
        recovery.resume_after_egah_recovery(run.run_id)
        agent.run_all(run.run_id)

        # 3 evidence envelopes (steps 3, 6, 9)
        envelopes = store.get_evidence_for_run(run.run_id)
        assert len(envelopes) == 3

        # 3 verification records
        verifications = store.get_verifications_for_run(run.run_id)
        assert len(verifications) == 3

        # 10 resource records (all steps completed)
        resources = store.get_resources_for_run(run.run_id)
        assert len(resources) == 10

        # Total cost and tokens across all 10 steps
        total_cost = store.get_total_cost(run.run_id)
        total_tokens = store.get_total_tokens(run.run_id)
        assert total_cost > 0
        assert total_tokens > 0

        # Run status is completed
        final_run = store.get_run(run.run_id)
        assert final_run.status == RunStatus.COMPLETED
        assert final_run.current_step == 10
