"""
EGAH PoC — Configuration Settings

Centralised configuration for the EGAH proof-of-concept.
Values are loaded from environment variables with sensible defaults.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = PROJECT_ROOT / "docs"
SRC_DIR = PROJECT_ROOT / "src"

# Load .env from project root
load_dotenv(PROJECT_ROOT / ".env")

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

DB_PATH = DATA_DIR / "egah.db"

# ---------------------------------------------------------------------------
# LLM
# ---------------------------------------------------------------------------

OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "200"))
OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))

# Cost per million tokens (GPT-4o-mini pricing)
COST_PER_M_PROMPT_TOKENS: float = 0.15
COST_PER_M_COMPLETION_TOKENS: float = 0.60

# ---------------------------------------------------------------------------
# EGAH Evidence Settings
# ---------------------------------------------------------------------------

CHECKPOINT_STEPS: list[int] = [3, 6, 9]
EVIDENCE_FRESHNESS_SECONDS: int = int(os.getenv("EVIDENCE_FRESHNESS_SECONDS", "300"))
TOTAL_WORKFLOW_STEPS: int = 10

# ---------------------------------------------------------------------------
# Streamlit
# ---------------------------------------------------------------------------

STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", "8501"))
PAGE_TITLE: str = "EGAH — Evidence-Governed Agent Harness"
PAGE_ICON: str = "🛡️"
