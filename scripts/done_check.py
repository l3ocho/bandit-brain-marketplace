#!/usr/bin/env python3
"""Done check: what changed since the last release, and what has to change with it.

Usage:
    python3 scripts/done_check.py            # since the last vX.Y.Z tag
    python3 scripts/done_check.py v0.5.2     # since a given ref

Reads the map in docs/dependencies.md. For every row whose first column matches a changed file,
lists each place in its second column: ✅ changed too, ☑️ listed under "Checked, nothing to change",
or ⚠️ open (update it, or check it needs nothing and list it there). Then lists the changes that start outside the repo, which no file triggers.
Exit 0 = nothing open · 1 = open rows. scripts/release.py refuses to release while it exits 1.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "docs" / "dependencies.md"


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout


def glob_re(pattern):
    out = re.escape(pattern).replace(r"\*\*", "\0").replace(r"\*", "[^/]*").replace("\0", ".*")
    return re.compile(f"^{out}$")


def section(text, heading):
    part = text.split(heading, 1)[1]
    return part.split("\n## ", 1)[0]


def rows(block):
    for line in block.splitlines():
        if line.startswith("| `"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            yield cells


def main(argv):
    base = argv[0] if argv else git("describe", "--tags", "--abbrev=0", "--match", "v*").strip()
    if not base:
        sys.exit("no release tag to compare with; pass a ref")
    changed = set(git("diff", "--name-only", base).split())
    changed |= set(git("ls-files", "--others", "--exclude-standard").split())
    changed = {f for f in changed if "__pycache__" not in f}
    tracked = set(git("ls-files").split()) | changed
    text = MAP.read_text(encoding="utf-8")

    checked = dict(re.findall(r"^- `([^`]+)` — (.+)$", section(text, "## ☑️ Checked, nothing to change"), re.M))
    print(f"Changed since {base}: {len(changed)} files\n")
    open_rows = 0
    for when, also, enforced in rows(section(text, "## 📋 The map")):
        triggers = [p.strip("`") for p in re.findall(r"`[^`]+`", when)]
        hit = sorted(f for f in changed if any(glob_re(t).match(f) for t in triggers))
        if not hit:
            continue
        print(f"▶ {', '.join(triggers)} changed ({len(hit)}: {', '.join(hit[:3])}{' …' if len(hit) > 3 else ''})"
              f"  [{enforced}]")
        for dep in (p.strip("`") for p in re.findall(r"`[^`]+`", also)):
            files = [f for f in tracked if glob_re(dep).match(f)]
            done = [f for f in files if f in changed]
            if done:
                print(f"   ✅ {dep}  ({len(done)} changed)")
            elif dep in checked:
                print(f"   ☑️  {dep}  checked: {checked[dep]}")
            else:
                open_rows += 1
                print(f"   ⚠️  {dep}  open: update it, or check it needs nothing")
        print()

    print("Changes that start outside the repo (check each that applies):")
    for line in section(text, "## 🌐 Changes from outside the repo").splitlines():
        if line.startswith("| ") and not line.startswith(("| When", "|---")):
            when = line.strip("|").split("|")[0].strip()
            print(f"   • {when}")
    print(f"\n{'Nothing open.' if not open_rows else f'{open_rows} open.'}")
    return 1 if open_rows else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
