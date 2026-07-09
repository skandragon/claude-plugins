# skandragon's Claude Code plugins

```
/plugin marketplace add skandragon/claude-plugins
/plugin install brain@skandragon
```

## brain

A durable, cross-project knowledge base for Claude: an [OKF](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf)
markdown wiki (also a valid Obsidian vault) that Claude reads, writes, and searches. Facts
that should outlive a session — infrastructure, credentials, working preferences, project
decisions — go in the brain instead of being re-derived every time.

**Setup.** Point `CLAUDE_BRAIN_DIR` at wherever you want it, e.g. in `~/.claude/settings.json`:

```json
{ "env": { "CLAUDE_BRAIN_DIR": "/Users/you/Library/Mobile Documents/iCloud~md~obsidian/Documents/MyBrain" } }
```

Defaults to `~/brain`. Put it in a synced folder (iCloud, Dropbox, a private git repo) and
the brain follows you across machines. Ask Claude to "set up my brain" to bootstrap it.

**What you get.**

- A `brain` skill teaching Claude the conventions: one concept per file, required `type`
  frontmatter, per-directory `index.md`, searcher-oriented descriptions, derived backlinks.
- A SessionStart hook that injects every directory `index.md` into context, so Claude knows
  what it knows without reading a single concept file (OKF progressive disclosure).
- `search.py` (field-weighted ranked search, stdlib only), `backlinks.py` (derived, run
  before renames), `check-links.py` (dangling-link check). All default to `$CLAUDE_BRAIN_DIR`
  and take an explicit root for other wikis.

Your brain's contents stay yours — the plugin ships the method, not the knowledge. Note the
brain is often synced and may be open on screen; treat credentials in it accordingly.

MIT.
