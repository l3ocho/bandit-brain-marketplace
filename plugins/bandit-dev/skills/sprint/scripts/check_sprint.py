#!/usr/bin/env python3
"""Checks bandit-dev:sprint records in a MyNotes domain vault. Exit 1 on any error.

Rules (each one a failure, not a warning):
  SP1  every sprint folder has its plan, handover prompt and ledger, named {project}-sprint-{name}-{record}.md
       (a sprint kept in the app: the ledger from plan step 1, the plan once step 7 is done, the prompt once committed)
  SP2  a brief whose board-task is a card of a sprint (from the ledger's wave table) lives inside that sprint folder
  SP3  no two .md files in the domain share a filename (Obsidian links resolve by filename)
  SP5  a project with sprint folders keeps only its hub note {project}.md, its sprint-* folders and planning/ (WBS, project plan, architecture) at its root
  SP4  frontmatter parses as YAML (skipped for the user's own inbox notes: no frontmatter or status inbox)
  SP6  one brief per card: a card has at most one brief outside _archive (a card detached from a closing sprint carries
       everything into that one note, which waits in the inbox; its ledger row says "detached")
  SP7  a sprint whose ledger says it is committed (a `Committed:` line, written at plan step 12) has its independent
       plan review record, {project}-review-sprint-{name}-YYYY-MM-DD.md, in the sprint folder
  SP9  a sprint kept in the app (its ledger has a `Sprint record:` line) lists the 12 plan steps in order in
       its ## Plan steps table; a step marked done carries a YYYY-MM-DD date and its evidence; a committed ledger has steps 1 to 11 done
  SP10 a committed sprint kept in the app has a ## Waves table, one row per wave in order; a wave marked done
       carries its evidence and needs only the waves it depends on to be done (a card under `Blocked by` in the
       ## Batch table, or a pair on the plan's `Lands after:` line); every card it names is in the Waves and cards table
       (an old-way ledger, with no `Sprint record:` line, is skipped by SP9 and SP10)
  SP11 a committed sprint kept in the app has, for every wave marked done in its ## Waves table, a section
       (sprints committed after 2026-11-04) `## 🌊 Wave {n}` in {project}-sprint-{name}-wave-report.md holding a `#### ⏱️ Flow` and a `#### 🪙 Tokens` block
  SP12 a committed sprint kept in the app (committed after 2026-11-04) has {project}-sprint-{name}-map.html, redrawn after every wave: its
       `sprint-map-waves-done` marker lists every wave marked done in the ## Waves table (temporary, decisions RS16)
  SP13 a committed sprint kept in the app (committed after 2026-11-08) has, in its step 9 evidence, `{card}: {n} steps`
       (n at least 1, build steps only) for every card in its ## Batch table: every planned card carries its build steps as sub-tasks

Usage:
  check_sprint.py [--vault DIR] [--domain NAME]   (defaults: $MYNOTES_DIR or ~/Documents/MyNotes;
                                                the `domain:` of the repo CLAUDE.md Project Context)
  check_sprint.py --hook   (Stop hook: reads the hook JSON on stdin, checks only when the
                            session touched the vault; blocks the stop once with exit 2 only on
                            errors in a project the session named (`Projects/{slug}/` in its
                            transcript); errors elsewhere in the domain are a warning, exit 0)
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
STEPS = ("Select and freeze the batch", "Spec completeness check, per card", "Close the open questions",
         "Size and classify", "Cross-card analysis", "Sequence", "Write the one technical plan", "Risk and rollback",
         "Definition of ready, per card", "Approval gate", "Independent plan review", "Commit the sprint")
SPRINT_RECORD = re.compile(r"^\W*Sprint record:", re.M)
STEP_ROW = re.compile(r"^\|\s*(\d{1,2})\s*\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|\s*((?:[^|\\]|\\.)*?)\s*\|\s*$", re.M)
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# SP11 and SP12 hold for sprints committed after the release that brought the wave report and the map;
# an earlier sprint never had them.
REPORTS_FROM = "2026-11-04"
# SP13 holds for sprints committed after the release that brought the build-step count; an earlier sprint never had it.
STEPS_FROM = "2026-11-08"
BATCH_CARD = re.compile(r"^\|\s*([A-Z]+-\d+)\s*\|", re.M)
COMMITTED_ON = re.compile(r"^\W*Committed:\W*(\d{4}-\d{2}-\d{2})", re.M)
LANDS_AFTER = re.compile(r"^\W*Lands after:\s*(.+)$", re.M)
LANDS_PAIR = re.compile(r"^\s*([A-Z]+-\d+)\s+after\s+(.+?)\s*\.?\s*$")
WAVE_ROW = re.compile(r"^\|\s*Wave\s+(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|\s*((?:[^|\\]|\\.)*?)\s*\|\s*$", re.M)


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


def section(text: str, heading: str) -> str:
    m = re.search(rf"^##\s+{re.escape(heading)}\s*$", text, re.M)
    if not m:
        return ""
    nxt = re.search(r"^##\s", text[m.end():], re.M)
    return text[m.end(): m.end() + nxt.start() if nxt else None]


def card_dependencies(text: str, plan_text: str) -> dict:
    """card -> the cards it depends on: the Batch table's `Blocked by` column and the plan's `Lands after:` pairs."""
    deps = defaultdict(set)
    rows = [r for r in section(text, "Batch").splitlines() if r.startswith("|")]
    if rows:
        head = [c.strip().lower() for c in rows[0].strip().strip("|").split("|")]
        if "blocked by" in head:
            col = head.index("blocked by")
            for row in rows[2:]:
                cells = [c.strip() for c in row.strip().strip("|").split("|")]
                if len(cells) > col and BATCH_CARD.match(row):
                    deps[CARD_ID.findall(cells[0])[0]].update(CARD_ID.findall(cells[col]))
    for line in LANDS_AFTER.findall(plan_text):
        for pair in line.split(";"):
            m = LANDS_PAIR.match(pair)
            if m:
                deps[m.group(1)].update(CARD_ID.findall(m.group(2)))
    return deps


def check_record_ledger(rel_folder, text: str, table_cards: set, plan_text: str = "") -> list[str]:
    """SP9 and SP10: a sprint kept as a record in the app tracks its steps and waves in the ledger."""
    errors = []
    steps = [(int(n), name, done, ev) for n, name, done, ev in STEP_ROW.findall(section(text, "Plan steps"))]
    if [(n, name) for n, name, _, _ in steps] != list(enumerate(STEPS, 1)):
        errors.append(f"SP9 {rel_folder}: the ledger's ## Plan steps table must list the 12 plan steps in order, "
                      "one row each: | n | step | done date | evidence |")
    else:
        for n, name, done, ev in steps:
            if done and not DATE.match(done):
                errors.append(f"SP9 {rel_folder}: step {n} ({name}) has `{done}` as its done date, not YYYY-MM-DD")
            elif done and not ev:
                errors.append(f"SP9 {rel_folder}: step {n} ({name}) is marked done with no evidence")
        # Step 12 is the commit itself: its row is marked once the checker passes.
        if COMMITTED.search(text) and any(not done for n, _, done, _ in steps if n < 12):
            errors.append(f"SP9 {rel_folder}: the ledger says committed but a plan step before 12 is not done")
    if COMMITTED.search(text):
        waves = WAVE_ROW.findall(section(text, "Waves"))
        if not waves or [int(n) for n, *_ in waves] != list(range(1, len(waves) + 1)):
            errors.append(f"SP10 {rel_folder}: a committed sprint's ledger has a ## Waves table, one row per wave "
                          "in order: | Wave n | card ids | done date | evidence |")
        else:
            wave_of = {c: int(n) for n, ids, *_ in waves for c in CARD_ID.findall(ids)}
            open_waves = {int(n) for n, _, done, _ in waves if not done}
            deps = card_dependencies(text, plan_text)
            for n, ids, done, ev in waves:
                if done and not DATE.match(done):
                    errors.append(f"SP10 {rel_folder}: Wave {n} has `{done}` as its done date, not YYYY-MM-DD")
                if done:
                    # Only the waves a card depends on must be done; where no dependency is written, no order is checked.
                    needs = {wave_of[d] for c in CARD_ID.findall(ids) for d in deps.get(c, ()) if d in wave_of} - {int(n)}
                    for m in sorted(needs & open_waves):
                        errors.append(f"SP10 {rel_folder}: Wave {n} is done while Wave {m}, which it depends on, is not")
                if done and not ev:
                    errors.append(f"SP10 {rel_folder}: Wave {n} is marked done with no evidence")
                missing = set(CARD_ID.findall(ids)) - table_cards
                if missing:
                    errors.append(f"SP10 {rel_folder}: Wave {n} names {', '.join(sorted(missing))}, "
                                  "not in the Waves and cards table")
    return errors


def check_build_steps(rel_folder, text: str) -> list[str]:
    """SP13: step 9's evidence gives every Batch card its build-step count (the sub-tasks planning wrote)."""
    on = COMMITTED_ON.search(text)
    if not on or on.group(1) <= STEPS_FROM:
        return []
    cards = BATCH_CARD.findall(section(text, "Batch"))
    if not cards:
        return [f"SP13 {rel_folder}: the ledger has no ## Batch table to hold step 9's build-step counts against"]
    row = next((ev for n, _, _, ev in STEP_ROW.findall(section(text, "Plan steps")) if n == "9"), "")
    return [f"SP13 {rel_folder}: step 9's evidence has no `{c}: {{n}} steps` (n at least 1): every planned card "
            "carries its build steps as sub-tasks" for c in cards
            if not any(int(n) >= 1 for n in re.findall(rf"\b{re.escape(c)}:\s*(\d+)\s+steps?\b", row))]


def check_wave_report(rel_folder, ledger_text: str, report: Path) -> list[str]:
    """SP11: every done wave has its section, Flow block and Tokens block in the wave report."""
    on = COMMITTED_ON.search(ledger_text)
    if not on or on.group(1) <= REPORTS_FROM:
        return []
    done = [n for n, _, d, _ in WAVE_ROW.findall(section(ledger_text, "Waves")) if d]
    if not done:
        return []
    if not report.exists():
        return [f"SP11 {rel_folder}: Wave {', '.join(done)} done but there is no {report.name} (the wave-end rebuild)"]
    text = report.read_text(encoding="utf-8", errors="replace")
    errors = []
    for n in done:
        m = re.search(rf"^##\s+\S*\s*Wave\s+{n}\b.*$", text, re.M)
        if not m:
            errors.append(f"SP11 {rel_folder}: Wave {n} is done but {report.name} has no `## 🌊 Wave {n}` section")
            continue
        nxt = re.search(r"^##\s", text[m.end():], re.M)
        body = text[m.end(): m.end() + nxt.start() if nxt else None]
        for block in ("Flow", "Tokens"):
            if not re.search(rf"^####\s+\S*\s*{block}\s*$", body, re.M):
                errors.append(f"SP11 {rel_folder}: Wave {n}'s section in {report.name} has no `{block}` block")
    return errors


def check_map(rel_folder, ledger_text: str, page: Path) -> list[str]:
    """SP12: the sprint map was redrawn after every done wave (its marker lists them)."""
    on = COMMITTED_ON.search(ledger_text)
    if not on or on.group(1) <= REPORTS_FROM:
        return []
    done = [n for n, _, d, _ in WAVE_ROW.findall(section(ledger_text, "Waves")) if d]
    if not page.exists():
        return [f"SP12 {rel_folder}: committed but there is no {page.name} (drawn at plan step 12, redrawn every wave)"]
    m = re.search(r'name="sprint-map-waves-done"\s+content="([^"]*)"', page.read_text(encoding="utf-8", errors="replace"))
    drawn = set((m.group(1) if m else "").replace(" ", "").split(",")) - {""}
    missing = [n for n in done if n not in drawn]
    return [f"SP12 {rel_folder}: Wave {', '.join(missing)} done but {page.name} was not redrawn after it"] if missing else []


def records_due(ledger: Path) -> tuple:
    """SP1: a sprint kept in the app writes its ledger at plan step 1, its plan at step 7 and its
    execution prompt at step 12, so a folder still in planning holds only what is due so far."""
    if not ledger.exists():
        return RECORDS
    text = ledger.read_text(errors="replace")
    if not SPRINT_RECORD.search(text):
        return RECORDS
    done = {int(n) for n, _, d, _ in STEP_ROW.findall(section(text, "Plan steps")) if d}
    due = ["progress"]
    if 7 in done or COMMITTED.search(text):
        due.append("plan")
    if COMMITTED.search(text):
        due.append("handover-prompt")
    return tuple(due)


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
        ledger = folder / f"{project}-sprint-{name}-progress.md"
        for record in records_due(ledger):
            expected = folder / f"{project}-sprint-{name}-{record}.md"
            if not expected.exists():
                errors.append(f"SP1 {rel_folder}: missing {expected.name}")
        if not ledger.exists():
            continue
        if COMMITTED.search(ledger.read_text(errors="replace")) and not any(
                re.fullmatch(rf"{re.escape(project)}-review-sprint-{re.escape(name)}-\d{{4}}-\d{{2}}-\d{{2}}\.md", f.name)
                for f in folder.iterdir()):
            errors.append(f"SP7 {rel_folder}: the ledger says committed but there is no "
                          f"{project}-review-sprint-{name}-YYYY-MM-DD.md (plan step 11, the independent review)")
        ledger_text = ledger.read_text(errors="replace")
        if SPRINT_RECORD.search(ledger_text):
            table_cards = {i for m in CARD_ROW.finditer(section(ledger_text, "Waves and cards"))
                           for i in CARD_ID.findall(m.group(1))}
            plan_file = folder / f"{project}-sprint-{name}-plan.md"
            plan_text = plan_file.read_text(errors="replace") if plan_file.exists() else ""
            errors.extend(check_record_ledger(rel_folder, ledger_text, table_cards, plan_text))
            errors.extend(check_build_steps(rel_folder, ledger_text))
            errors.extend(check_wave_report(rel_folder, ledger_text, folder / f"{project}-sprint-{name}-wave-report.md"))
            errors.extend(check_map(rel_folder, ledger_text, folder / f"{project}-sprint-{name}-map.html"))
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


def transcript_text(payload: dict) -> str:
    transcript = payload.get("transcript_path")
    if not transcript or not os.path.exists(transcript):
        return ""
    with open(transcript, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def session_touched_vault(text: str) -> bool:
    return "MyNotes/" in text or "bandit-dev:sprint" in text


def touched_projects(text: str) -> set[str]:
    """Project folders the session named: `Projects/{slug}/` anywhere in its transcript."""
    return set(re.findall(r"Projects/([^/\s\"'`\\]+)/", text))


def own_error(line: str, projects: set[str]) -> bool:
    return any(f"Projects/{slug}/" in line for slug in projects)


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
        text = transcript_text(payload)
        if payload.get("stop_hook_active") or not session_touched_vault(text):
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
    if args.hook and errors:
        projects = touched_projects(text)
        others = [e for e in errors if not own_error(e, projects)]
        errors = [e for e in errors if own_error(e, projects)]
        if others and not errors:
            print(json.dumps({"systemMessage": f"bandit-dev:sprint check: {len(others)} problem(s) outside "
                              "this session's projects (not blocking): " + " | ".join(others)}))
            return 0
    if not errors:
        if not args.hook:
            print(f"OK: {domain} passes SP1-SP13 ({len(sprint_folders(domain))} sprint folders)")
        return 0
    out = sys.stderr if args.hook else sys.stdout
    print(f"bandit-dev:sprint check FAILED in {domain} ({len(errors)}). Fix these before finishing:", file=out)
    for line in errors:
        print(f"- {line}", file=out)
    return 2 if args.hook else 1


if __name__ == "__main__":
    sys.exit(main())
