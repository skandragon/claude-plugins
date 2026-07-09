#!/usr/bin/env python3
"""Link checker: reports dangling markdown links and [[wiki-links]].

Usage: check-links.py [wiki-root]   (default: $CLAUDE_BRAIN_DIR, else ~/brain)

Markdown links are resolved relative to the containing file. Wiki links resolve
Obsidian-style: by filename stem anywhere in the vault. External (scheme://) and
anchor-only links are ignored. Exit 1 if any dangling links are found.
"""
import os, re, pathlib, sys, urllib.parse

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else \
    pathlib.Path(os.environ.get("CLAUDE_BRAIN_DIR", os.path.expanduser("~/brain")))

md_files = [p for p in ROOT.rglob("*.md") if ".obsidian" not in p.parts]
stems = {p.stem for p in md_files}

MD_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
WIKI_LINK = re.compile(r"\[\[([^\]|#]+)")

dangling = []
for p in md_files:
    text = p.read_text()
    for m in MD_LINK.finditer(text):
        target = urllib.parse.unquote(m.group(1).split("#")[0])
        if not target or "://" in m.group(1) or target.startswith("mailto:"):
            continue
        if not (p.parent / target).exists():
            line = text[:m.start()].count("\n") + 1
            dangling.append((p.relative_to(ROOT), line, m.group(1), "md"))
    for m in WIKI_LINK.finditer(text):
        target = m.group(1).strip()
        if pathlib.Path(target).stem not in stems:
            line = text[:m.start()].count("\n") + 1
            dangling.append((p.relative_to(ROOT), line, f"[[{target}]]", "wiki"))

for f, line, target, kind in dangling:
    print(f"{f}:{line}: {target}")
print(f"\n{len(dangling)} dangling link(s) in {len(md_files)} files" if dangling else f"all links resolve ({len(md_files)} files)")
sys.exit(1 if dangling else 0)
