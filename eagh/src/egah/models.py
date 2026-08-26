"""
EGAH PoC — Pydantic Data Models

Core data models for Evidence-Governed Agent Harness:
- EvidenceEnvelope: The fundamental unit of durable evidence state
- VerificationRecord: Tracks verification decisions
- ResourceRecord: Tracks token/cost consumption per step
- WorkflowRun: Top-level execution record
- RecoveryPlan: Output of the recovery controller
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class VerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    STALE = "stale"


class PolicyDecision(str, Enum):
    ACT = "act"
    REFRESH = "refresh"
    ASK = "ask"
    ABSTAIN = "abstain"


class EvidenceType(str, Enum):
    OBSERVATION = "observation"
    TOOL_RESULT = "tool_result"
    LLM_OUTPUT = "llm_output"
    VERIFICATION = "verification"
    HUMAN_INPUT = "human_input"


class RunStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    CRASHED = "crashed"
    RECOVERED = "recovered"
    PAUSED = "paused"


# ---------------------------------------------------------------------------
# Evidence Envelope — the heart of EGAH
# ---------------------------------------------------------------------------

class EvidenceEnvelope(BaseModel):
    """
    Durable evidence record.

    This is NOT telemetry. Telemetry records what happened.
    An evidence envelope records what is *known*, when it was verified,
    and whether it remains valid for future action.
    """

    evidence_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    run_id: str
    step_number: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # What was observed / produced
    evidence_type: EvidenceType
    source: str  # e.g. "tool:web_search", "llm:gpt-4o-mini", "human"
    content: dict[str, Any]  # the actual evidence payload
    summary: str  # human-readable summary

    # Provenance & validity
    provenance: str  # where this evidence came from
    verification_status: VerificationStatus = VerificationStatus.PENDING
    valid_from: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    valid_until: Optional[datetime] = None  # None = no explicit expiry
    freshness_seconds: int = 3600  # how long evidence is considered fresh

    # Resource accounting
    tokens_used: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0

    def is_fresh(self, at_time: Optional[datetime] = None) -> bool:
        """Check whether this evidence is still fresh."""
        now = at_time or datetime.now(timezone.utc)
        age = (now - self.timestamp).total_seconds()
        return age <= self.freshness_seconds

    def is_valid(self, at_time: Optional[datetime] = None) -> bool:
        """Check whether this evidence is still within its validity window."""
        now = at_time or datetime.now(timezone.utc)
        if self.valid_until and now > self.valid_until:
            return False
        return self.verification_status == VerificationStatus.VERIFIED


# ---------------------------------------------------------------------------
# Verification Record
# ---------------------------------------------------------------------------

class VerificationRecord(BaseModel):
    """Records a single verification decision at an evidence checkpoint."""

    verification_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    run_id: str
    step_number: int
    evidence_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    verification_status: VerificationStatus
    policy_decision: PolicyDecision
    reason: str  # why this decision was made
    verifier: str = "system"  # "system", "human", "llm"


# ---------------------------------------------------------------------------
# Resource Record
# ---------------------------------------------------------------------------

class ResourceRecord(BaseModel):
    """Per-step resource consumption record."""

    record_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    run_id: str
    step_number: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0


# ---------------------------------------------------------------------------
# Workflow Run
# ---------------------------------------------------------------------------

class StepRecord(BaseModel):
    """A single step in the workflow execution."""

    step_number: int
    step_name: str
    status: str  # "completed", "pending", "crashed", "skipped"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    output: Optional[str] = None
    evidence_id: Optional[str] = None
    has_checkpoint: bool = False  # whether this step is an evidence-checkpoint step


class WorkflowRun(BaseModel):
    """Top-level record for a workflow execution."""

    run_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_description: str
    status: RunStatus = RunStatus.RUNNING
    total_steps: int = 10
    current_step: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    steps: list[StepRecord] = []
    checkpoint_steps: list[int] = [3, 6, 9]  # steps where evidence checkpoints fire


# ---------------------------------------------------------------------------
# Recovery Plan — output of the recovery controller
# ---------------------------------------------------------------------------

class EvidenceValidityResult(BaseModel):
    """Validity assessment for a single evidence envelope during recovery."""

    evidence_id: str
    step_number: int
    summary: str
    original_status: VerificationStatus
    current_freshness: bool
    current_validity: bool
    needs_revalidation: bool
    recommendation: PolicyDecision


class RecoveryPlan(BaseModel):
    """The recovery controller's output after analyzing a crash."""

    run_id: str
    crash_step: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    execution_state_restored: bool = False
    evidence_state_restored: bool = False
    verification_history_restored: bool = False

    evidence_analysis: list[EvidenceValidityResult] = []

    safe_to_resume: bool = False
    resume_from_step: Optional[int] = None
    revalidation_required: list[str] = []  # evidence IDs that need refresh
    recommendation: str = ""
