#!/usr/bin/env python3
"""Check relative links, heading anchors and banned writing patterns in every .md file."""
import re, sys, glob, os

STRICT = "--strict" in sys.argv
files = [f for f in glob.glob("**/*.md", recursive=True) if not f.startswith(".git")]
text = {f: open(f, encoding="utf-8").read() for f in files}

def slug(h):
    h = h.strip().lower()
    h = re.sub(r"[^\w\s-]", "", h)
    return re.sub(r"\s+", "-", h)

anchors = {f: {slug(h) for h in re.findall(r"^#{1,6}\s+(.*)", text[f], re.M)} for f in files}
errors, warnings = [], []

# The cleanup plan and this script describe files that later tasks create, so they are
# exempt from both checks.
SKIP = {"AGENTS.md", "maintenance/2026-09-17-consistency-cleanup.md", "maintenance/check-plans.py"}

for f in files:
    if f in SKIP:
        continue
    for target in re.findall(r"\]\(([^)\s]+)\)", text[f]):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        path, _, frag = target.partition("#")
        dest = os.path.normpath(os.path.join(os.path.dirname(f), path)) if path else f
        if not os.path.exists(dest):
            errors.append(f"{f}: missing file {target}")
        elif frag and dest in anchors and frag not in anchors[dest]:
            errors.append(f"{f}: missing anchor {target}")

banned = {
    "em dash": r"—",
    "curly quote": r"[“”‘’]",
    "mid-sentence semicolon": r"[a-z0-9)]; [a-zA-Z]",
    "British spelling": r"\b(authoris|synchronis|fulfilment|localisation|behaviour|organisation)",
    "release 'channel' (use version)": r"(?<!broker )(?<!private )\bchannel\b(?! ownership)",
    "'alone does not' pattern": r"\balone\b[^.]*\b(does|do|is) not\b",
}
for f in files:
    if f in SKIP:
        continue
    for name, pat in banned.items():
        for m in re.finditer(pat, text[f]):
            line = text[f].count("\n", 0, m.start()) + 1
            warnings.append(f"{f}:{line}: {name}")

for e in errors: print("ERROR", e)
for w in warnings: print("WARN ", w)
print(f"{len(errors)} errors, {len(warnings)} warnings")
sys.exit(1 if errors or (STRICT and warnings) else 0)
