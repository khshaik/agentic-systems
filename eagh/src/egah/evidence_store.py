"""
EGAH PoC — SQLite-backed Evidence Store

Provides durable persistence for:
- WorkflowRun (execution state)
- EvidenceEnvelopes (evidence state)
- VerificationRecords (verification history)
- ResourceRecords (cost/token accounting)

This is the "Durable Evidence State" layer from the EGAH architecture.
Observability (Langfuse / OTel) sits *below* this layer — it records telemetry.
This layer records decision-bearing evidence.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from egah.models import (
    EvidenceEnvelope,
    EvidenceValidityResult,
    PolicyDecision,
    ResourceRecord,
    RunStatus,
    StepRecord,
    VerificationRecord,
    VerificationStatus,
    WorkflowRun,
)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = _PROJECT_ROOT / "data" / "egah.db"


class EvidenceStore:
    """SQLite-backed store for EGAH runtime state."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self._init_db()

    # ------------------------------------------------------------------
    # Database initialisation
    # ------------------------------------------------------------------

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._conn()
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS workflow_runs (
                run_id TEXT PRIMARY KEY,
                data TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS evidence_envelopes (
                evidence_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                step_number INTEGER NOT NULL,
                data TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS verification_records (
                verification_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                step_number INTEGER NOT NULL,
                evidence_id TEXT NOT NULL,
                data TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS resource_records (
                record_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                step_number INTEGER NOT NULL,
                data TEXT NOT NULL
            );
            """
        )
        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    # WorkflowRun CRUD
    # ------------------------------------------------------------------

    def save_run(self, run: WorkflowRun):
        conn = self._conn()
        conn.execute(
            "INSERT OR REPLACE INTO workflow_runs (run_id, data) VALUES (?, ?)",
            (run.run_id, run.json()),
        )
        conn.commit()
        conn.close()

    def get_run(self, run_id: str) -> Optional[WorkflowRun]:
        conn = self._conn()
        row = conn.execute(
            "SELECT data FROM workflow_runs WHERE run_id = ?", (run_id,)
        ).fetchone()
        conn.close()
        if row:
            return WorkflowRun.parse_raw(row["data"])
        return None

    def list_runs(self) -> list[WorkflowRun]:
        conn = self._conn()
        rows = conn.execute("SELECT data FROM workflow_runs ORDER BY rowid DESC").fetchall()
        conn.close()
        return [WorkflowRun.parse_raw(r["data"]) for r in rows]

    def delete_run(self, run_id: str):
        conn = self._conn()
        conn.execute("DELETE FROM workflow_runs WHERE run_id = ?", (run_id,))
        conn.execute("DELETE FROM evidence_envelopes WHERE run_id = ?", (run_id,))
        conn.execute("DELETE FROM verification_records WHERE run_id = ?", (run_id,))
        conn.execute("DELETE FROM resource_records WHERE run_id = ?", (run_id,))
        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    # Evidence Envelope CRUD
    # ------------------------------------------------------------------

    def save_evidence(self, envelope: EvidenceEnvelope):
        conn = self._conn()
        conn.execute(
            "INSERT OR REPLACE INTO evidence_envelopes "
            "(evidence_id, run_id, step_number, data) VALUES (?, ?, ?, ?)",
            (envelope.evidence_id, envelope.run_id, envelope.step_number, envelope.json()),
        )
        conn.commit()
        conn.close()

    def get_evidence_for_run(self, run_id: str) -> list[EvidenceEnvelope]:
        conn = self._conn()
        rows = conn.execute(
            "SELECT data FROM evidence_envelopes WHERE run_id = ? ORDER BY step_number",
            (run_id,),
        ).fetchall()
        conn.close()
        return [EvidenceEnvelope.parse_raw(r["data"]) for r in rows]

    def get_evidence_by_id(self, evidence_id: str) -> Optional[EvidenceEnvelope]:
        conn = self._conn()
        row = conn.execute(
            "SELECT data FROM evidence_envelopes WHERE evidence_id = ?",
            (evidence_id,),
        ).fetchone()
        conn.close()
        if row:
            return EvidenceEnvelope.parse_raw(row["data"])
        return None

    def get_evidence_up_to_step(self, run_id: str, step: int) -> list[EvidenceEnvelope]:
        conn = self._conn()
        rows = conn.execute(
            "SELECT data FROM evidence_envelopes WHERE run_id = ? AND step_number <= ? "
            "ORDER BY step_number",
            (run_id, step),
        ).fetchall()
        conn.close()
        return [EvidenceEnvelope.parse_raw(r["data"]) for r in rows]

    # ------------------------------------------------------------------
    # Verification Record CRUD
    # ------------------------------------------------------------------

    def save_verification(self, record: VerificationRecord):
        conn = self._conn()
        conn.execute(
            "INSERT OR REPLACE INTO verification_records "
            "(verification_id, run_id, step_number, evidence_id, data) VALUES (?, ?, ?, ?, ?)",
            (
                record.verification_id,
                record.run_id,
                record.step_number,
                record.evidence_id,
                record.json(),
            ),
        )
        conn.commit()
        conn.close()

    def get_verifications_for_run(self, run_id: str) -> list[VerificationRecord]:
        conn = self._conn()
        rows = conn.execute(
            "SELECT data FROM verification_records WHERE run_id = ? ORDER BY step_number",
            (run_id,),
        ).fetchall()
        conn.close()
        return [VerificationRecord.parse_raw(r["data"]) for r in rows]

    # ------------------------------------------------------------------
    # Resource Record CRUD
    # ------------------------------------------------------------------

    def save_resource(self, record: ResourceRecord):
        conn = self._conn()
        conn.execute(
            "INSERT OR REPLACE INTO resource_records "
            "(record_id, run_id, step_number, data) VALUES (?, ?, ?, ?)",
            (record.record_id, record.run_id, record.step_number, record.json()),
        )
        conn.commit()
        conn.close()

    def get_resources_for_run(self, run_id: str) -> list[ResourceRecord]:
        conn = self._conn()
        rows = conn.execute(
            "SELECT data FROM resource_records WHERE run_id = ? ORDER BY step_number",
            (run_id,),
        ).fetchall()
        conn.close()
        return [ResourceRecord.parse_raw(r["data"]) for r in rows]

    def get_total_cost(self, run_id: str) -> float:
        records = self.get_resources_for_run(run_id)
        return sum(r.cost_usd for r in records)

    def get_total_tokens(self, run_id: str) -> int:
        records = self.get_resources_for_run(run_id)
        return sum(r.total_tokens for r in records)

    # ------------------------------------------------------------------
    # Convenience: reset database
    # ------------------------------------------------------------------

    def reset(self):
        """Drop all data — useful for demo resets."""
        conn = self._conn()
        conn.executescript(
            """
            DELETE FROM workflow_runs;
            DELETE FROM evidence_envelopes;
            DELETE FROM verification_records;
            DELETE FROM resource_records;
            """
        )
        conn.commit()
        conn.close()
