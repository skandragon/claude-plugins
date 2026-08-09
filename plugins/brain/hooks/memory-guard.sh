#!/usr/bin/env bash
# Route memory to the Griffinbrain, not the per-project scratch dir.
#
# The harness injects a "Memory" section describing
# ~/.claude/projects/*/memory/ as the memory system. The user's CLAUDE.md and
# the brain's own `durable-knowledge-goes-in-the-brain` practice both say
# otherwise — durable facts belong in $CLAUDE_BRAIN_DIR as OKF concepts. The
# injected instruction is concrete and path-specific, so it wins on reflex
# unless something interrupts. This is that something.
#
# Blocks writes to the scratch memory dir; redirects searches of it to the
# brain's ranked search. Reads are left alone — reading back genuine
# same-session scratch is legitimate.
#
# PreToolUse contract: exit 2 blocks the call and shows stderr to Claude.
set -uo pipefail

payload="$(cat)"

read -r tool path <<<"$(
  printf '%s' "$payload" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    print(" "); sys.exit(0)
ti = d.get("tool_input") or {}
p = ti.get("file_path") or ti.get("path") or ti.get("pattern") or ""
print(f'"'"'{d.get("tool_name","")} {p}'"'"')
'
)"

# Match both the directory itself (Grep/Glob pass a bare dir) and paths under it.
case "$path" in
  */.claude/projects/*/memory|*/.claude/projects/*/memory/*) ;;
  *) exit 0 ;;
esac

BRAIN_SEARCH="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/cache/skandragon/brain/0.1.0}/skills/brain/search.py"

case "$tool" in
  Write|Edit|NotebookEdit)
    cat >&2 <<EOF
BLOCKED: do not write memories to ~/.claude/projects/*/memory/.

That directory is transient per-session scratch. Durable memory — cross-project
AND per-project — lives in the Griffinbrain (\$CLAUDE_BRAIN_DIR) as OKF concepts.

Use the \`brain\` skill instead:
  - per-project fact  -> \$CLAUDE_BRAIN_DIR/projects/<name>/<concept>.md
  - how-I-should-work -> \$CLAUDE_BRAIN_DIR/practices/<concept>.md
  - infra/creds       -> \$CLAUDE_BRAIN_DIR/infrastructure/<concept>.md
Then update that directory's index.md. Both, or it didn't happen.

If this really is single-session scratch, put it in the session scratchpad dir
instead of the memory dir.
EOF
    exit 2
    ;;
  Grep|Glob)
    cat >&2 <<EOF
BLOCKED: searching ~/.claude/projects/*/memory/ will not find your memories.

Durable memory lives in the Griffinbrain. Search it with the ranked search:
  python3 "$BRAIN_SEARCH" <terms> [tag:x type:y dir:z]

Fall back to \`grep -ril\` over \$CLAUDE_BRAIN_DIR for literal error strings the
ranker tokenizes away, then walk the directory index.md files.
EOF
    exit 2
    ;;
esac

exit 0
