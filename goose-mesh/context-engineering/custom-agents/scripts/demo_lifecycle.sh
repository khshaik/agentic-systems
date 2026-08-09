#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
AGENTS_DIR="$TMP/project/.agents/agents"
EXPORT_DIR="$TMP/exported"
mkdir -p "$AGENTS_DIR"

cat > "$TMP/instructions-v1.md" <<'TEXT'
You are a dependency reviewer. Identify outdated or risky dependencies and provide evidence-based upgrade advice. Do not modify files unless explicitly asked.
TEXT

cat > "$TMP/instructions-v2.md" <<'TEXT'
You are a dependency and software-supply-chain reviewer. Identify outdated, vulnerable, unpinned, abandoned, or suspicious dependencies. Separate confirmed findings from items that require external verification. Do not modify files unless explicitly asked.
TEXT

CTL=(python3 "$REPO_ROOT/scripts/agentctl.py" --agents-dir "$AGENTS_DIR")

printf '\n1. CREATE\n'
"${CTL[@]}" create dependency-reviewer \
  --description "Reviews dependency health and software-supply-chain risk" \
  --instructions-file "$TMP/instructions-v1.md"

printf '\n2. EDIT\n'
"${CTL[@]}" edit dependency-reviewer \
  --instructions-file "$TMP/instructions-v2.md"

printf '\n3. VALIDATE AND LIST\n'
"${CTL[@]}" validate
"${CTL[@]}" list

printf '\n4. EXPORT\n'
"${CTL[@]}" export dependency-reviewer --output "$EXPORT_DIR"

printf '\n5. IMPORT INTO A SECOND PROJECT\n'
SECOND_DIR="$TMP/second-project/.agents/agents"
python3 "$REPO_ROOT/scripts/agentctl.py" --agents-dir "$SECOND_DIR" \
  import "$EXPORT_DIR/dependency-reviewer.md"
python3 "$REPO_ROOT/scripts/agentctl.py" --agents-dir "$SECOND_DIR" validate

printf '\nLifecycle demonstration completed successfully.\n'
