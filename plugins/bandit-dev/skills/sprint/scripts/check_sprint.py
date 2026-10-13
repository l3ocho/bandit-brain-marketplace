#!/usr/bin/env python3
"""Checks bandit-dev:sprint records in a MyNotes domain vault. Exit 1 on any error.

Rules (each one a failure, not a warning):
  SP1  every sprint folder has its plan, handover prompt and ledger, named {project}-sprint-{name}-{record}.md
  SP2  a brief whose board-task is a card of a sprint (from the ledger's wave table) lives inside that sprint folder
  SP3  no two .md files in the domain share a filename (Obsidian links resolve by filename)
  SP5  a project with sprint folders keeps only its hub note {project}.md, its sprint-* folders and planning/ (WBS, project plan, architecture) at its root
  SP4  frontmatter parses as YAML (skipped for Leo's own inbox notes: no frontmatter or status inbox)
  SP6  one brief per card: a card has at most one brief outside _archive (a card detached from a closing sprint carries
       everything into that one note, which waits in the inbox; its ledger row says "detached")
  SP7  a sprint whose ledger says it is committed (a `Committed:` line, written at plan step 12) has its independent
       plan review record, {project}-review-sprint-{name}-YYYY-MM-DD.md, in the sprint folder

Usage:
  check_sprint.py [--vault DIR] [--domain NAME]   (defaults: $MYNOTES_DIR or ~/Documents/MyNotes;
                                                the `domain:` of the repo CLAUDE.md Project Context)
  check_sprint.py --hook   (Stop hook: reads the hook JSON on stdin, checks only when the
                            session touched the vault, blocks the stop once with exit 2)
"""
import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

RECORDS = ("plan", "handover-prompt", "progress")
CARD_ROW = re.compile(r"^\|\s*[^|]+\|\s*((?:[A-Z]+-\d+)(?:\s*,\s*[A-Z]+-\d+)*)\s*\|", re.M)
CARD_ID = re.compile(r"[A-Z]+-\d+")
COMMITTED = re.compile(r"^\W*Committed:", re.M)


def frontmatter(path: Path) -> tuple[dict | None, str | None]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---\n"):
        return None, None
    end = text.find("\n---", 4)
    if end < 0:
        return None, "frontmatter has no closing ---"
    try:
        data = yaml.safe_load(text[4:end])
    except yaml.YAMLError as exc:
        return None, f"frontmatter is not valid YAML ({str(exc).splitlines()[0]})"
    return (data if isinstance(data, dict) else {}), None


def sprint_folders(domain: Path) -> list[tuple[str, Path]]:
    found = []
    for base in (domain / "Projects", domain / "_archive" / "Projects"):
        if not base.is_dir():
            continue
        for project in sorted(p for p in base.iterdir() if p.is_dir()):
            for folder in sorted(project.glob("sprint-*")):
                if folder.is_dir():
                    found.append((project.name, folder))
    return found


def check(domain: Path) -> list[str]:
    errors: list[str] = []
    md_files = [p for p in domain.rglob("*.md") if not any(part.startswith(".") for part in p.relative_to(domain).parts)]
    # Settings mirrors (Claude/, its archive), templates (Templater syntax) and the retired skill
    # sources (_archive/skills/, every skill has a SKILL.md) are not notes.
    md_files = [p for p in md_files if not (set(p.relative_to(domain).parts[:2]) & {"Claude", "_templates"})
                and p.relative_to(domain).parts[:2] != ("_archive", "skills")]

    # SP3 duplicate filenames
    by_name = defaultdict(list)
    for p in md_files:
        by_name[p.name].append(p.relative_to(domain))
    for name, paths in sorted(by_name.items()):
        if len(paths) > 1 and name != "README.md":
            errors.append(f"SP3 duplicate filename {name}: " + ", ".join(str(x) for x in paths))

    # SP4 frontmatter, and an index of briefs by board-task
    briefs_by_card = defaultdict(list)
    for p in md_files:
        rel = p.relative_to(domain)
        data, problem = frontmatter(p)
        in_inbox = rel.parts[0] == "_inbox"
        if problem:
            if in_inbox and data is None and "status: triaged" not in p.read_text(errors="replace")[:600]:
                continue
            errors.append(f"SP4 {rel}: {problem}")
            continue
        if not data:
            continue
        card = data.get("board-task")
        dated = re.search(r"-\d{4}-\d{2}-\d{2}\.md$", p.name) and data.get("type") in (None, "brief")
        if card and (data.get("type") == "brief" or dated):
            briefs_by_card[str(card)].append(rel)

    # SP6 one brief per card outside the archive
    for card, paths in sorted(briefs_by_card.items()):
        live = [x for x in paths if x.parts[0] != "_archive"]
        if len(live) > 1:
            errors.append(f"SP6 more than one brief for {card}: " + ", ".join(str(x) for x in live) + " (merge them into one note per card)")

    # SP5 project root holds only the hub and sprint folders
    projects = domain / "Projects"
    if projects.is_dir():
        for project in sorted(p for p in projects.iterdir() if p.is_dir()):
            if not any(c.is_dir() and c.name.startswith("sprint-") for c in project.iterdir()):
                continue
            for item in sorted(project.iterdir()):
                if item.name.startswith("."):
                    continue
                if item.is_dir() and item.name.startswith("sprint-"):
                    continue
                if item.is_dir() and item.name == "planning":
                    continue
                if item.name == f"{project.name}.md":
                    continue
                errors.append(f"SP5 {item.relative_to(domain)}: only {project.name}.md, sprint-* folders and planning/ may sit in Projects/{project.name}/; move it into the sprint folder it belongs to")

    # SP1 and SP2
    for project, folder in sprint_folders(domain):
        name = folder.name[len("sprint-"):]
        rel_folder = folder.relative_to(domain)
        for record in RECORDS:
            expected = folder / f"{project}-sprint-{name}-{record}.md"
            if not expected.exists():
                errors.append(f"SP1 {rel_folder}: missing {expected.name}")
        ledger = folder / f"{project}-sprint-{name}-progress.md"
        if not ledger.exists():
            continue
        if COMMITTED.search(ledger.read_text(errors="replace")) and not any(
                re.fullmatch(rf"{re.escape(project)}-review-sprint-{re.escape(name)}-\d{{4}}-\d{{2}}-\d{{2}}\.md", f.name)
                for f in folder.iterdir()):
            errors.append(f"SP7 {rel_folder}: the ledger says committed but there is no "
                          f"{project}-review-sprint-{name}-YYYY-MM-DD.md (plan step 11, the independent review)")
        cards = set()
        detached = set()
        for match in CARD_ROW.finditer(ledger.read_text(errors="replace")):
            ids = CARD_ID.findall(match.group(1))
            line_end = ledger.read_text(errors="replace").find("\n", match.start())
            row = ledger.read_text(errors="replace")[match.start():line_end if line_end > 0 else None]
            if "detached" in row.lower():
                detached.update(ids)
            cards.update(ids)
        # A card detached at close keeps its single brief in the inbox for the next plan to file.
        for card in sorted(cards - detached):
            for brief in briefs_by_card.get(card, []):
                if brief.parent != rel_folder:
                    errors.append(f"SP2 brief for {card} is outside its sprint: {brief} (belongs in {rel_folder}/)")
    return errors


def session_touched_vault(payload: dict) -> bool:
    transcript = payload.get("transcript_path")
    if not transcript or not os.path.exists(transcript):
        return False
    with open(transcript, encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    return "MyNotes/" in text or "bandit-dev:sprint" in text


def context_domain() -> str | None:
    """The `domain:` of the Project Context in the repo's CLAUDE.md (the project owns its domain)."""
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    try:
        text = (root / "CLAUDE.md").read_text(encoding="utf-8")
    except OSError:
        return None
    block = text.split("## 🧭 Project Context", 1)
    m = re.search(r"^domain:\s*(\S+)", block[1], re.M) if len(block) > 1 else None
    return m.group(1) if m and m.group(1) != "none" else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", default=os.environ.get("MYNOTES_DIR") or os.path.expanduser("~/Documents/MyNotes"))
    ap.add_argument("--domain", default=None)
    ap.add_argument("--hook", action="store_true")
    args = ap.parse_args()

    if args.hook:
        try:
            payload = json.load(sys.stdin)
        except Exception:
            payload = {}
        if payload.get("stop_hook_active") or not session_touched_vault(payload):
            return 0

    name = args.domain or context_domain()
    if not name:
        if args.hook:
            return 0  # not a project with a vault domain: nothing to check
        print("check_sprint: no --domain and no Project Context `domain:` in CLAUDE.md", file=sys.stderr)
        return 1
    domain = Path(args.vault).expanduser() / name
    if not domain.is_dir():
        print(f"check_sprint: no domain folder at {domain}", file=sys.stderr)
        return 0 if args.hook else 1

    errors = check(domain)
    if not errors:
        if not args.hook:
            print(f"OK: {domain} passes SP1-SP7 ({len(sprint_folders(domain))} sprint folders)")
        return 0
    out = sys.stderr if args.hook else sys.stdout
    print(f"bandit-dev:sprint check FAILED in {domain} ({len(errors)}). Fix these before finishing:", file=out)
    for line in errors:
        print(f"- {line}", file=out)
    return 2 if args.hook else 1


if __name__ == "__main__":
    sys.exit(main())
