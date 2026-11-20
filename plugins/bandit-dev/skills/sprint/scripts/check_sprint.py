#!/usr/bin/env python3
"""Checks a project's bandit-dev:sprint papers from its notes file. Exit 1 on any error.

The notes file is built by the sprint helper through bandit:notes, in whichever storage the project uses
(references/templates.md → Notes file): `.sprint/{project}-sprint-notes.json` at the root of the repository, a JSON
object `{"project", "built", "notes": [{"title", "kind", "status", "tags", "cards", "text"}]}`. A sprint's papers are
the notes tagged `sprint-{name}`; a paper is found by its title. No script reads a vault folder or the app.

Rules (each one a failure, not a warning):
  SP1  every sprint has its plan, handover prompt and ledger: notes titled {project}-sprint-{name}-{record} with its tag
       (a sprint kept in the app: the ledger from plan step 1, the plan once step 7 is done, the prompt once committed)
  SP2  a brief (kind brief) linked to a card of a sprint (a card row of the ledger's tables) carries that sprint's tag
  SP3  no two notes in the file share a title (the scripts find a paper by its title)
  SP6  one brief per card: a card has at most one brief that is not archived (a card detached from a closing sprint
       carries everything into that one note, which waits in the inbox; its ledger row says "detached")
  SP7  a sprint whose ledger says it is committed (a `Committed:` line, written at plan step 12) has its independent
       plan review record, a note titled {project}-review-sprint-{name}-YYYY-MM-DD with the sprint's tag
  SP9  a sprint kept in the app (its ledger has a `Sprint record:` line) lists the 12 plan steps in order in
       its ## Plan steps table; a step marked done carries a YYYY-MM-DD date and its evidence; a committed ledger has steps 1 to 11 done
  SP10 a committed sprint kept in the app has a ## Waves table, one row per wave in order; a wave marked done
       carries its evidence and needs only the waves it depends on to be done (a card under `Blocked by` in the
       ## Batch table, or a pair on the plan's `Lands after:` line); every card it names is in the Waves and cards table
       (an old-way ledger, with no `Sprint record:` line, is skipped by SP9 and SP10)
  SP11 a committed sprint kept in the app has, for every wave marked done in its ## Waves table, a section
       (sprints committed after 2026-11-04) `## 🌊 Wave {n}` in its wave report {project}-sprint-{name}-wave-report holding a `#### ⏱️ Flow` and a `#### 🪙 Tokens` block
  SP12 a live sprint (its ledger not archived) kept in the app and committed after 2026-11-04 has its map
       {project}-sprint-{name}-map.html beside the notes file, redrawn after every wave: its
       `sprint-map-waves-done` marker lists every wave marked done in the ## Waves table (temporary, decisions RS16)
  SP13 a committed sprint kept in the app (committed after 2026-11-08) has, in its step 9 evidence, `{card}: {n} steps`
       (n at least 1, build steps only) for every card in its ## Batch table: every planned card carries its build steps as sub-tasks
  SP14 a live sprint's plan (not archived) leaves nothing for after debug: its `Items to register` section
       schedules no item for the close, the release or after the sprint (`trigger: sprint close`, `at close`,
       `after the release`, `after the sprint`); a repository change is done in a wave or in debug, before the release
  SP15 a closed sprint keeps no paper and no WBS unarchived: a sprint whose ledger records the close (`Status: Closed …`,
       `Current wave: Sprint closed`), whose ledger is archived, or that is named in `--closed` (closed in the app)
       fails while a note with its tag, or its WBS note {project}-sprint-{name}-wbs, has a status other than archived
Retired with the vault folder: SP4 (frontmatter YAML), SP5 (the project folder's root) and the `--listing`
mode; SP8 is the repo checker's rule on this script's Stop hook.

Usage:
  check_sprint.py [--notes FILE] [--closed NAME[,NAME…]]
                           (--notes defaults to .sprint/{project}-sprint-notes.json at the root of the repository,
                            {project} from the `project:` line of the repo CLAUDE.md Project Context;
                            --closed: sprints closed in the app, from get_sprints)
  No notes file, or one that is not a notes file: says it could not read the notes file (exit 1).
  check_sprint.py --hook   (Stop hook: reads the hook JSON on stdin, checks only when the session named the sprint
                            helper or the notes file; the project is the repository's own (its Project Context), so
                            no vault is needed. A missing notes file, or one built before the session began, is said
                            in a notice (exit 0); an error in a notes file built in this session blocks the stop once (exit 2))
"""
import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

RECORDS = ("plan", "handover-prompt", "progress")
CARD_ROW = re.compile(r"^\|\s*[^|]+\|\s*((?:[A-Z]+-T?\d+)(?:\s*,\s*[A-Z]+-T?\d+)*)\s*\|", re.M)
CARD_ID = re.compile(r"[A-Z]+-T?\d+")  # a proper id ({prefix}-{n}) or a temporary one ({prefix}-T{n})
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
BATCH_CARD = re.compile(r"^\|\s*([A-Z]+-T?\d+)\s*\|", re.M)
COMMITTED_ON = re.compile(r"^\W*Committed:\W*(\d{4}-\d{2}-\d{2})", re.M)
LANDS_AFTER = re.compile(r"^\W*Lands after:\s*(.+)$", re.M)
LANDS_PAIR = re.compile(r"^\s*([A-Z]+-T?\d+)\s+after\s+(.+?)\s*\.?\s*$")
CLOSED = re.compile(r"^\W*(?:Status:\W*Closed\b|Current wave:\W*Sprint closed\b)", re.M | re.I)
OWED = re.compile(r"trigger\s*:[^)\n]*\b(?:close|closing|release)\b|\b(?:at|on|during|after)\s+(?:the\s+)?(?:sprint\s+)?"
                  r"(?:close|closing|release)\b|\bafter the sprint\b", re.I)
WAVE_ROW = re.compile(r"^\|\s*Wave\s+(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|\s*((?:[^|\\]|\\.)*?)\s*\|\s*$", re.M)
SPRINT_TAG = re.compile(r"^sprint-(.+)$")
NOTES_NAME = "{project}-sprint-notes.json"
FIELDS = ("title", "kind", "status", "tags", "cards", "text")


def section(text: str, heading: str) -> str:
    m = re.search(rf"^##\s+{re.escape(heading)}\s*$", text, re.M)
    if not m:
        return ""
    nxt = re.search(r"^##\s", text[m.end():], re.M)
    return text[m.end(): m.end() + nxt.start() if nxt else None]


class NotesFileError(Exception):
    """The notes file is missing, is not JSON, or is not in the notes file's shape."""


def load_notes(path) -> dict:
    """The notes file as a dict, each note with every field (title and text strings, tags and cards lists)."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise NotesFileError(f"could not read the notes file {path}: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("notes"), list):
        raise NotesFileError(f"could not read the notes file {path}: not a JSON object with a `notes` list")
    notes = []
    for i, note in enumerate(data["notes"]):
        if not isinstance(note, dict) or not isinstance(note.get("title"), str) or not note["title"]:
            raise NotesFileError(f"could not read the notes file {path}: note {i} has no title")
        notes.append({"title": note["title"], "kind": str(note.get("kind") or ""), "status": str(note.get("status") or ""),
                      "tags": [str(t) for t in note.get("tags") or []], "cards": [str(c) for c in note.get("cards") or []],
                      "text": str(note.get("text") or "")})
    return {"project": str(data.get("project") or ""), "built": str(data.get("built") or ""), "notes": notes}


def sprints_of(notes: list) -> dict:
    """Sprint name -> its papers (the notes carrying the tag `sprint-{name}`), title -> note."""
    papers = defaultdict(dict)
    for note in notes:
        for tag in note["tags"]:
            m = SPRINT_TAG.match(tag)
            if m:
                papers[m.group(1)].setdefault(note["title"], note)
    return dict(papers)


def is_archived(note) -> bool:
    return bool(note) and note["status"] == "archived"


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


def check_record_ledger(where, text: str, table_cards: set, plan_text: str = "") -> list[str]:
    """SP9 and SP10: a sprint kept as a record in the app tracks its steps and waves in the ledger."""
    errors = []
    steps = [(int(n), name, done, ev) for n, name, done, ev in STEP_ROW.findall(section(text, "Plan steps"))]
    if [(n, name) for n, name, _, _ in steps] != list(enumerate(STEPS, 1)):
        errors.append(f"SP9 {where}: the ledger's ## Plan steps table must list the 12 plan steps in order, "
                      "one row each: | n | step | done date | evidence |")
    else:
        for n, name, done, ev in steps:
            if done and not DATE.match(done):
                errors.append(f"SP9 {where}: step {n} ({name}) has `{done}` as its done date, not YYYY-MM-DD")
            elif done and not ev:
                errors.append(f"SP9 {where}: step {n} ({name}) is marked done with no evidence")
        # Step 12 is the commit itself: its row is marked once the checker passes.
        if COMMITTED.search(text) and any(not done for n, _, done, _ in steps if n < 12):
            errors.append(f"SP9 {where}: the ledger says committed but a plan step before 12 is not done")
    if COMMITTED.search(text):
        waves = WAVE_ROW.findall(section(text, "Waves"))
        if not waves or [int(n) for n, *_ in waves] != list(range(1, len(waves) + 1)):
            errors.append(f"SP10 {where}: a committed sprint's ledger has a ## Waves table, one row per wave "
                          "in order: | Wave n | card ids | done date | evidence |")
        else:
            wave_of = {c: int(n) for n, ids, *_ in waves for c in CARD_ID.findall(ids)}
            open_waves = {int(n) for n, _, done, _ in waves if not done}
            deps = card_dependencies(text, plan_text)
            for n, ids, done, ev in waves:
                if done and not DATE.match(done):
                    errors.append(f"SP10 {where}: Wave {n} has `{done}` as its done date, not YYYY-MM-DD")
                if done:
                    # Only the waves a card depends on must be done; where no dependency is written, no order is checked.
                    needs = {wave_of[d] for c in CARD_ID.findall(ids) for d in deps.get(c, ()) if d in wave_of} - {int(n)}
                    for m in sorted(needs & open_waves):
                        errors.append(f"SP10 {where}: Wave {n} is done while Wave {m}, which it depends on, is not")
                if done and not ev:
                    errors.append(f"SP10 {where}: Wave {n} is marked done with no evidence")
                missing = set(CARD_ID.findall(ids)) - table_cards
                if missing:
                    errors.append(f"SP10 {where}: Wave {n} names {', '.join(sorted(missing))}, "
                                  "not in the Waves and cards table")
    return errors


def check_build_steps(where, text: str) -> list[str]:
    """SP13: step 9's evidence gives every Batch card its build-step count (the sub-tasks planning wrote)."""
    on = COMMITTED_ON.search(text)
    if not on or on.group(1) <= STEPS_FROM:
        return []
    cards = BATCH_CARD.findall(section(text, "Batch"))
    if not cards:
        return [f"SP13 {where}: the ledger has no ## Batch table to hold step 9's build-step counts against"]
    row = next((ev for n, _, _, ev in STEP_ROW.findall(section(text, "Plan steps")) if n == "9"), "")
    return [f"SP13 {where}: step 9's evidence has no `{c}: {{n}} steps` (n at least 1): every planned card "
            "carries its build steps as sub-tasks" for c in cards
            if not any(int(n) >= 1 for n in re.findall(rf"\b{re.escape(c)}:\s*(\d+)\s+steps?\b", row))]


def check_wave_report(where, ledger_text: str, title: str, report) -> list[str]:
    """SP11: every done wave has its section, Flow block and Tokens block in the wave report (`report` is its note)."""
    on = COMMITTED_ON.search(ledger_text)
    if not on or on.group(1) <= REPORTS_FROM:
        return []
    done = [n for n, _, d, _ in WAVE_ROW.findall(section(ledger_text, "Waves")) if d]
    if not done:
        return []
    if report is None:
        return [f"SP11 {where}: Wave {', '.join(done)} done but there is no wave report {title} (the wave-end rebuild)"]
    text = report["text"]
    errors = []
    for n in done:
        m = re.search(rf"^##\s+\S*\s*Wave\s+{n}\b.*$", text, re.M)
        if not m:
            errors.append(f"SP11 {where}: Wave {n} is done but {title} has no `## 🌊 Wave {n}` section")
            continue
        nxt = re.search(r"^##\s", text[m.end():], re.M)
        body = text[m.end(): m.end() + nxt.start() if nxt else None]
        for block in ("Flow", "Tokens"):
            if not re.search(rf"^####\s+\S*\s*{block}\s*$", body, re.M):
                errors.append(f"SP11 {where}: Wave {n}'s section in {title} has no `{block}` block")
    return errors


def check_map(where, ledger_text: str, page: Path) -> list[str]:
    """SP12: the sprint map beside the notes file was redrawn after every done wave (its marker lists them)."""
    on = COMMITTED_ON.search(ledger_text)
    if not on or on.group(1) <= REPORTS_FROM:
        return []
    done = [n for n, _, d, _ in WAVE_ROW.findall(section(ledger_text, "Waves")) if d]
    if not page.exists():
        return [f"SP12 {where}: committed but there is no {page.name} beside the notes file "
                "(drawn at plan step 12, redrawn every wave)"]
    m = re.search(r'name="sprint-map-waves-done"\s+content="([^"]*)"', page.read_text(encoding="utf-8", errors="replace"))
    drawn = set((m.group(1) if m else "").replace(" ", "").split(",")) - {""}
    missing = [n for n in done if n not in drawn]
    return [f"SP12 {where}: Wave {', '.join(missing)} done but {page.name} was not redrawn after it"] if missing else []


def check_owed(where, plan_text: str) -> list[str]:
    """SP14: the plan's Items to register leaves no item for the close, the release or after the sprint."""
    m = re.search(r"^#+[^\n]*Items to register[^\n]*$", plan_text, re.M)
    if not m:
        return []
    nxt = re.search(r"^#{1,%d}\s" % len(re.match(r"#+", m.group(0)).group(0)), plan_text[m.end():], re.M)
    body = plan_text[m.end(): m.end() + nxt.start() if nxt else None]
    return [f"SP14 {where}: Items to register leaves this for after debug: \"{line.strip()[:120]}\". "
            "A repository change is done in a wave or in debug (trigger: wave n or debug), never at close or after the release"
            for line in body.splitlines() if line.strip() and OWED.search(line)]


def check_closed(project: str, notes: list, papers: dict, closed_in_app: set) -> list[str]:
    """SP15: a closed sprint's papers and WBS note are all archived."""
    errors = []
    by_title = {n["title"]: n for n in notes}
    for name in sorted(set(papers) | set(closed_in_app)):
        mine = papers.get(name, {})
        ledger = mine.get(f"{project}-sprint-{name}-progress")
        closed = name in closed_in_app or is_archived(ledger) or bool(ledger and CLOSED.search(ledger["text"]))
        if not closed:
            continue
        left = sorted(t for t, n in mine.items() if not is_archived(n))
        if left:
            errors.append(f"SP15 sprint {name}: closed, but {len(left)} of its papers are not archived: {', '.join(left)} "
                          "(close step 3 sets every note with the sprint's tag to archived)")
        wbs = by_title.get(f"{project}-sprint-{name}-wbs")
        if wbs and not is_archived(wbs):
            errors.append(f"SP15 {wbs['title']}: the WBS of closed sprint {name} is not archived "
                          "(close step 3 archives it in the same step as the papers)")
    return errors


def records_due(ledger) -> tuple:
    """SP1: a sprint kept in the app writes its ledger at plan step 1, its plan at step 7 and its
    execution prompt at step 12, so a sprint still in planning holds only what is due so far."""
    if ledger is None:
        return RECORDS
    text = ledger["text"]
    if not SPRINT_RECORD.search(text):
        return RECORDS
    done = {int(n) for n, _, d, _ in STEP_ROW.findall(section(text, "Plan steps")) if d}
    due = ["progress"]
    if 7 in done or COMMITTED.search(text):
        due.append("plan")
    if COMMITTED.search(text):
        due.append("handover-prompt")
    return tuple(due)


def ordered_sprints(project: str, papers: dict) -> list[str]:
    """Sprint names, live sprints first, then archived ones (an archived ledger), each by name."""
    def archived(name):
        return is_archived(papers[name].get(f"{project}-sprint-{name}-progress"))
    return sorted(papers, key=lambda n: (archived(n), n))


def check(data: dict, folder: Path, closed_in_app: set = frozenset()) -> list[str]:
    """Every rule on one notes file; `folder` is where the file sits (the sprint maps sit beside it)."""
    errors: list[str] = []
    project, notes = data["project"], data["notes"]
    papers = sprints_of(notes)

    # SP3 two notes with one title
    by_title = defaultdict(int)
    for note in notes:
        by_title[note["title"]] += 1
    for title, count in sorted(by_title.items()):
        if count > 1:
            errors.append(f"SP3 {count} notes are titled {title}: the scripts find a paper by its title "
                          "(archive or rename one through bandit:notes)")

    # SP6 one brief per card that is not archived; and the briefs by card for SP2
    briefs_by_card = defaultdict(list)
    for note in notes:
        if note["kind"] == "brief":
            for card in note["cards"]:
                briefs_by_card[card].append(note)
    for card, briefs in sorted(briefs_by_card.items()):
        live = [b["title"] for b in briefs if not is_archived(b)]
        if len(live) > 1:
            errors.append(f"SP6 more than one brief for {card}: " + ", ".join(live) + " (merge them into one note per card)")

    for name in ordered_sprints(project, papers):
        mine = papers[name]
        where = f"sprint {name}"
        ledger = mine.get(f"{project}-sprint-{name}-progress")
        for record in records_due(ledger):
            if f"{project}-sprint-{name}-{record}" not in mine:
                errors.append(f"SP1 {where}: missing {project}-sprint-{name}-{record} (a note tagged sprint-{name})")
        if ledger is None:
            continue
        ledger_text = ledger["text"]
        if COMMITTED.search(ledger_text) and not any(
                re.fullmatch(rf"{re.escape(project)}-review-sprint-{re.escape(name)}-\d{{4}}-\d{{2}}-\d{{2}}", t) for t in mine):
            errors.append(f"SP7 {where}: the ledger says committed but there is no "
                          f"{project}-review-sprint-{name}-YYYY-MM-DD (plan step 11, the independent review)")
        plan = mine.get(f"{project}-sprint-{name}-plan")
        plan_text = plan["text"] if plan else ""
        if SPRINT_RECORD.search(ledger_text):
            table_cards = {i for m in CARD_ROW.finditer(section(ledger_text, "Waves and cards"))
                           for i in CARD_ID.findall(m.group(1))}
            errors.extend(check_record_ledger(where, ledger_text, table_cards, plan_text))
            errors.extend(check_build_steps(where, ledger_text))
            report_title = f"{project}-sprint-{name}-wave-report"
            errors.extend(check_wave_report(where, ledger_text, report_title, mine.get(report_title)))
            if not is_archived(ledger):
                errors.extend(check_map(where, ledger_text, folder / f"{project}-sprint-{name}-map.html"))
        if not is_archived(plan):
            errors.extend(check_owed(where, plan_text))
        cards, detached = set(), set()
        for match in CARD_ROW.finditer(ledger_text):
            ids = CARD_ID.findall(match.group(1))
            line_end = ledger_text.find("\n", match.start())
            if "detached" in ledger_text[match.start():line_end if line_end > 0 else None].lower():
                detached.update(ids)
            cards.update(ids)
        # A card detached at close keeps its single brief in the inbox for the next plan to file.
        for card in sorted(cards - detached):
            for brief in briefs_by_card.get(card, []):
                if f"sprint-{name}" not in brief["tags"]:
                    errors.append(f"SP2 brief for {card} is outside its sprint: {brief['title']} "
                                  f"(a brief of a card of sprint {name} carries the tag sprint-{name})")
    errors.extend(check_closed(project, notes, papers, closed_in_app))
    return errors


def transcript_text(payload: dict) -> str:
    transcript = payload.get("transcript_path")
    if not transcript or not os.path.exists(transcript):
        return ""
    with open(transcript, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def session_names_sprint(text: str) -> bool:
    """The session used the sprint helper or named a notes file."""
    return "bandit-dev:sprint" in text or "-sprint-notes.json" in text


def session_start(text: str) -> str:
    """The first timestamp the transcript holds (when the session began), or ""."""
    m = re.search(r'"timestamp"\s*:\s*"([^"]+)"', text)
    return m.group(1) if m else ""


def repo_root() -> Path:
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())


def context_project() -> str | None:
    """The `project:` of the Project Context in the repo's CLAUDE.md (the repository's own project)."""
    try:
        text = (repo_root() / "CLAUDE.md").read_text(encoding="utf-8")
    except OSError:
        return None
    block = text.split("## 🧭 Project Context", 1)
    m = re.search(r"^project:\s*(\S+)", block[1], re.M) if len(block) > 1 else None
    return m.group(1) if m else None


def default_notes(project: str) -> Path:
    return repo_root() / ".sprint" / NOTES_NAME.format(project=project)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--notes", default=None, help="the project's notes file (default: .sprint/{project}-sprint-notes.json)")
    ap.add_argument("--hook", action="store_true")
    ap.add_argument("--closed", default="", help="comma-separated names of sprints closed in the app")
    args = ap.parse_args()
    closed = {n.strip() for n in args.closed.split(",") if n.strip()}

    text = ""
    if args.hook:
        try:
            payload = json.load(sys.stdin)
        except Exception:
            payload = {}
        text = transcript_text(payload)
        if payload.get("stop_hook_active") or not session_names_sprint(text):
            return 0

    if args.notes:
        path = Path(args.notes).expanduser()
    else:
        project = context_project()
        if not project:
            if args.hook:
                return 0  # not a repository with a Project Context: nothing to check
            print("check_sprint: no --notes and no Project Context `project:` in CLAUDE.md", file=sys.stderr)
            return 1
        path = default_notes(project)

    try:
        data = load_notes(path)
    except NotesFileError as exc:
        if args.hook:
            print(json.dumps({"systemMessage": f"bandit-dev:sprint check: {exc}; nothing was checked. Build the notes "
                              "file through bandit:notes (templates.md → Notes file) and run check_sprint.py."}))
            return 0
        print(f"check_sprint: {exc}. Build it through bandit:notes (templates.md → Notes file)", file=sys.stderr)
        return 1

    errors = check(data, path.parent, closed)
    if args.hook:
        start = session_start(text)
        if data["built"] and start and data["built"] < start:
            note = (f"bandit-dev:sprint check: the notes file {path.name} was built {data['built']}, before this session "
                    "began, so it may not hold this session's writes: rebuild it and run check_sprint.py.")
            if errors:
                note += f" On that copy, {len(errors)} problem(s), not blocking: " + " | ".join(errors)
            print(json.dumps({"systemMessage": note}))
            return 0
    if not errors:
        if not args.hook:
            print(f"OK: {path.name} passes the sprint rules SP1-SP3, SP6, SP7, SP9-SP15 "
                  f"({len(sprints_of(data['notes']))} sprint(s))")
        return 0
    out = sys.stderr if args.hook else sys.stdout
    print(f"bandit-dev:sprint check FAILED on {path.name} ({len(errors)}). Fix these before finishing "
          "(then rebuild the notes file and run it again):", file=out)
    for line in errors:
        print(f"- {line}", file=out)
    return 2 if args.hook else 1


if __name__ == "__main__":
    sys.exit(main())
