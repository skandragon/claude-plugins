---
name: brain
description: Read/write the brain — a durable cross-project knowledge base kept as an Open Knowledge Format (OKF) markdown wiki. Use when saving durable facts ("remember this", "save to brain"), recalling infrastructure/practices/decisions, or on /brain.
---

# Brain

The brain is a markdown wiki that survives sessions, projects, and machines. It lives at:

```
$CODEX_BRAIN_DIR or $CLAUDE_BRAIN_DIR
```

Resolve it with `brain_root.py` next to this skill. It checks those environment variables,
then the `CLAUDE_BRAIN_DIR` value in `~/.claude/settings.json`, then `$HOME/brain`. Never
hardcode a path; the user may keep the brain in a synced folder.

It is an [OKF v0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf)
bundle, and also a valid Obsidian vault. **Every directory has its own `index.md`** (OKF
progressive disclosure): the root index maps areas, each directory's index lists its
concepts one line each. This plugin's SessionStart hook injects all indexes into new
Claude Code and Codex sessions. Read individual concept files on demand.

The hook also prints the absolute path of this skill's scripts. If it didn't run, the
scripts sit next to this `SKILL.md`.

## Layout

The root index defines the areas. A conventional starting set:

- `people/` — who the user is: accounts, ownership, working preferences (type: person)
- `practices/` — how the assistant should work: rules, preferences, corrections (type: practice)
- `infrastructure/` — servers, registries, DBs, creds, runbooks (types: service, credential, database, runbook)
- `projects/<name>/` — durable project-scoped knowledge (types: project, config, decision, …)
- `index.md` — OKF reserved filename (at any level); never give it frontmatter. (`log.md` is
  also reserved: an append-only changelog. Most brains don't need one — git history and
  concept timestamps are history enough.)

If a `policy.md` exists at the root, read it: that's the user's vault-specific structure,
frontmatter, and tag rules, and it wins over the defaults here.

## Reading

Each directory's `index.md` gives one line per concept. Follow the markdown link and Read
the file. Trust but verify: facts reflect when they were written (check `timestamp` and
inline dates) — if a concept names a file, flag, or endpoint, confirm it still exists
before acting on it.

## Writing a concept

One fact/topic per file, kebab-case filename, in the directory that fits. Frontmatter —
`type` is REQUIRED (OKF conformance), the rest recommended:

```markdown
---
type: runbook            # person|practice|service|credential|database|runbook|project|config|decision — or coin a fitting one
title: Short human name
description: One line — this is what future sessions use to decide relevance.
resource: https://…      # optional link to the real thing
tags: [a, b]
timestamp: 2026-01-01T12:00:00Z
---

The fact. For practices include **Why:** and **How to apply:**.
Link related concepts with relative markdown links: [some service](../infrastructure/thing.md).
Links to not-yet-written concepts are fine (OKF tolerates broken links — they mark future work).
```

Then, ALWAYS (both or it didn't happen):

1. Write/update the concept file.
2. Add or update its one-line entry in **its directory's** `index.md`. A new directory gets
   its own `index.md` and a link from the parent index (the root index only changes when a
   new area appears).

Updating: prefer editing the existing concept over creating a near-duplicate; bump
`timestamp`. Delete concepts that turn out wrong (and their index line).

## What belongs here

Durable, cross-project or cross-machine facts: infra endpoints and credentials, working
preferences and corrections (with the why), project decisions worth surviving a session.

NOT: things the repo already records (code structure, git history, AGENTS.md or CLAUDE.md),
transient session state, or purely local scratch. Project-scoped working memory can stay in
the assistant's scratch space; promote it to the brain when it proves durable.

## Bootstrapping a new brain

If the resolved brain's `index.md` doesn't exist, ask the user before creating one. Then make
the root `index.md` (no frontmatter) listing the areas above, and create each area
directory with its own `index.md` as concepts arrive — don't pre-create empty ones.

## Security

The brain is private but often synced, and may be open on screen in an editor. Credentials
stored here must never be committed to repos, pasted into shared transcripts, or echoed
unnecessarily. If the user's brain is a git repo, check it is private before writing
secrets into it.

## Wiki rules (apply to the brain and any other markdown wiki we maintain)

- **Search recipe, in order:** (1) ranked search —
  `python3 <skill-dir>/search.py <terms> [tag:x type:y dir:z] [--root DIR]` —
  field-weighted (tags/title > description/filename > body), rarer terms rank higher;
  (2) full-text `grep -ril` for exact error strings the ranker might tokenize away;
  (3) walk the directory indexes. Don't Read files hop-by-hop when a search answers it.
  Tags are the precision signal: a tag match means a human said the note is *about* that
  term, so it outranks prose mentions and works as a facet filter (`tag:postgres`).
- **Descriptions are for the searcher, not the author:** include symptoms and literal
  error strings ("422 No commit found"), not just component nouns — that's what a
  future session greps for.
- **Backlinks are derived, never stored.** No "what links here" sections in notes —
  they rot on the next edit. Filename stems are unique, so one scan is always correct:
  `python3 <skill-dir>/backlinks.py <stem> [wiki-root]`. Run it BEFORE renaming,
  deleting, or splitting a note, and fix the referrers it lists.
- **After renames/deletes/batch edits:** run the link check (below) — invariants that
  aren't testable are aspirational.

All scripts use the same brain resolution and take an explicit root for other wikis.

## Link check

`python3 <skill-dir>/check-links.py [wiki-root]` reports dangling markdown links and
`[[wiki-links]]` (wiki links resolve Obsidian-style by filename stem). Run it after
renames, deletions, or batch migrations. Broken links to *future* concepts are tolerated
by OKF, but links to renamed/deleted concepts should be fixed or downgraded to plain text.

## Conformance check

After a batch of writes, verify OKF conformance (every non-reserved `.md` has frontmatter
with a non-empty `type`):

```bash
python3 - <<'EOF'
import pathlib, re, subprocess, sys
root = pathlib.Path(subprocess.check_output(["python3", "<skill-dir>/brain_root.py"], text=True).strip())
bad = []
for p in root.rglob("*.md"):
    if ".obsidian" in p.parts or p.name in ("index.md", "log.md", "policy.md"):
        continue
    m = re.match(r"^---\n(.*?)\n---\n", p.read_text(), re.S)
    if not m or not re.search(r"^type:\s*\S", m.group(1), re.M):
        bad.append(str(p.relative_to(root)))
print("OKF conformant" if not bad else f"NON-CONFORMANT: {bad}")
sys.exit(1 if bad else 0)
EOF
```
