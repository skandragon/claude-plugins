#!/usr/bin/env python3
"""Backlinks for any markdown wiki: list files that link to a given note.

Usage: backlinks.py <note-stem-or-path> [wiki-root]
Matches markdown links whose target filename stem matches, and [[wiki-links]].
Root defaults to $CLAUDE_BRAIN_DIR, else ~/brain. Backlinks are always derived,
never stored — a maintained list rots; this is one scan and always correct.
"""
import os, re, pathlib, sys

if len(sys.argv) < 2:
    sys.exit(__doc__)
stem = pathlib.Path(sys.argv[1]).stem
root = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else \
    pathlib.Path(os.environ.get("CLAUDE_BRAIN_DIR", os.path.expanduser("~/brain")))

pat = re.compile(r"\]\(([^)\s#]*/)?%s\.md(#[^)]*)?\)|\[\[%s([|#][^\]]*)?\]\]" % (re.escape(stem), re.escape(stem)))
hits = 0
for p in sorted(root.rglob("*.md")):
    if ".obsidian" in p.parts or p.stem == stem:
        continue
    for i, line in enumerate(p.read_text().split("\n"), 1):
        if pat.search(line):
            print(f"{p.relative_to(root)}:{i}: {line.strip()}")
            hits += 1
print(f"\n{hits} backlink(s) to {stem}.md")
