#!/usr/bin/env python3
"""Ranked search over a markdown wiki (default: $CLAUDE_BRAIN_DIR, else ~/brain).

Usage: search.py [--root DIR] [-n N] term [term ...]
Filters: tag:foo type:runbook dir:someproject (all must match; remaining terms rank).

Field-weighted lexical ranking, stdlib only: tags/title matches outrank
description/filename, which outrank body mentions; rarer terms weigh more (idf).
# ponytail: full scan per query, fine to ~5k notes; add a cached index if it ever drags.
"""
import os, re, math, pathlib, argparse

ap = argparse.ArgumentParser()
ap.add_argument("--root", default=os.environ.get("CLAUDE_BRAIN_DIR", os.path.expanduser("~/brain")))
ap.add_argument("-n", type=int, default=10)
ap.add_argument("terms", nargs="+")
args = ap.parse_args()

WEIGHTS = {"tags": 5, "title": 4, "stem": 3, "description": 3, "body": 1}
filters, terms = [], []
for t in args.terms:
    (filters if re.match(r"^(tag|type|dir):", t) else terms).append(t.lower())

notes = []
for p in pathlib.Path(args.root).rglob("*.md"):
    if ".obsidian" in p.parts or p.name == "index.md":
        continue
    text = p.read_text()
    fm = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
    meta = dict(re.findall(r"^(\w+):\s*(.+)$", fm.group(1), re.M)) if fm else {}
    fields = {
        "tags": meta.get("tags", "").lower(),
        "title": meta.get("title", "").lower(),
        "description": meta.get("description", "").lower(),
        "stem": p.stem.replace("-", " ").lower(),
        "body": text[fm.end():].lower() if fm else text.lower(),
    }
    rel = str(p.relative_to(args.root))
    ok = True
    for f in filters:
        k, v = f.split(":", 1)
        hay = {"tag": fields["tags"], "type": meta.get("type", ""), "dir": rel}[k].lower()
        ok &= v in hay
    if ok:
        notes.append((rel, meta, fields))

# idf per term over all candidate notes
df = {t: sum(1 for _, _, f in notes if any(t in v for v in f.values())) for t in terms}
scored = []
for rel, meta, fields in notes:
    score = 0.0
    for t in terms:
        w = sum(wt for fld, wt in WEIGHTS.items() if t in fields[fld])
        if w:
            score += w * math.log(1 + len(notes) / (df[t] or 1))
    if score or (filters and not terms):
        scored.append((score, rel, meta.get("description", "").strip('"')))

scored.sort(reverse=True)
for score, rel, desc in scored[:args.n]:
    print(f"{score:6.1f}  {rel}\n        {desc}")
if not scored:
    print("no matches")
