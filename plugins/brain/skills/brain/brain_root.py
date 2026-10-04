"""Resolve the shared brain location for Claude Code and Codex."""

import json
import os
from pathlib import Path


def brain_root():
    for name in ("CODEX_BRAIN_DIR", "CLAUDE_BRAIN_DIR"):
        if value := os.environ.get(name):
            return Path(value).expanduser()

    # Codex may start from a GUI without inheriting the shell environment.
    # Reuse an existing Claude Code user setting when available.
    settings = Path.home() / ".claude" / "settings.json"
    try:
        value = json.loads(settings.read_text()).get("env", {}).get("CLAUDE_BRAIN_DIR")
        if value:
            return Path(value).expanduser()
    except (OSError, ValueError, AttributeError):
        pass

    return Path.home() / "brain"


if __name__ == "__main__":
    print(brain_root())
