#!/usr/bin/env bash
# EGAH PoC — Launch script
# Usage: ./run.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Activate virtual environment
source "$SCRIPT_DIR/.venv/bin/activate"

# Launch Streamlit
echo "🛡️  Starting EGAH — Evidence-Governed Agent Harness"
echo "   http://localhost:8501"
echo ""

streamlit run "$SCRIPT_DIR/src/egah/app.py" \
    --server.port 8501 \
    --server.headless true
