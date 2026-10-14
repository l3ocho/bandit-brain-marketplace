#!/usr/bin/env python3
"""Print one version's CHANGELOG section (its body, without the heading): the GitHub release notes.

  changelog_section.py X.Y.Z      exit 1 when the version has no entry
"""
import re
import sys
from pathlib import Path

text = (Path(__file__).resolve().parent.parent / "CHANGELOG.md").read_text(encoding="utf-8")
if len(sys.argv) != 2:
    sys.exit(__doc__)
m = re.search(rf"^## {re.escape(sys.argv[1])}\b[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
if not m:
    sys.exit(f"no CHANGELOG entry for {sys.argv[1]}")
print(m.group(1).strip())
