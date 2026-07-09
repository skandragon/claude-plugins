#!/usr/bin/env bash
# Inject the brain's directory indexes into every session (OKF progressive disclosure).
# Silent no-op when no brain exists yet.
set -u

BRAIN="${CLAUDE_BRAIN_DIR:-$HOME/brain}"
SKILL_DIR="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}/skills/brain"

[ -f "$BRAIN/index.md" ] || exit 0

echo "BRAIN — cross-project knowledge base at $BRAIN"
echo "Scripts: $SKILL_DIR/{search,backlinks,check-links}.py — use the brain skill to read/write concepts."
echo "Indexes:"
find "$BRAIN" -name index.md -not -path '*/.obsidian/*' | sort | while IFS= read -r f; do
  echo
  echo "<!-- ${f#"$BRAIN"/} -->"
  cat "$f"
done
