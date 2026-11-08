#!/usr/bin/env python3
"""Shows a project's approved sprint targets against the sprint data: the wave report's Targets block, the closing
report's sprint table, and the lessons a miss leaves. Reads the same records as sprint_data.py (its waves and its one
measures list); a target lives in the project's targets note, never in a script.

The targets note (`Projects/{slug}/planning/{project}-sprint-targets.md`) holds one table, keyed by measure name:
  | Measure | Target | Direction | Status | Approved | Words |
  Direction `at most` or `at least`; Status `proposed` or `approved`. A target is used only when its status is
  `approved` AND the approval date and the user's words are filled; a proposed target is never shown as met or missed.
Only a measure whose `Measure` line in sprint_data.py names a direction can carry a target.

Usage:
  sprint_targets.py [--vault DIR] --domain NAME --project SLUG --sprint NAME --wave N [--targets FILE]
      the wave's Targets block (measure, value, target, met or missed) and its Lessons lines; nothing when no target is approved
  sprint_targets.py ... --sprint NAME                    the same for the whole sprint (the closing report)
  sprint_targets.py ... --propose                        proposed rows from the median of every row of the project's data, for
                                                         measures the note has no row for (written to the note as `proposed`)
Exit codes: 0 ok · 2 usage or a targets note that cannot be used.
"""
import argparse
import os
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sprint_data  # noqa: E402

DIRECTIONS = ("at most", "at least")
COLUMNS = ("measure", "target", "direction", "status", "approved", "words")


def parse_targets(text):
    """The rows of the targets note as dicts, plus the problems that make a row unusable."""
    rows, problems = [], []
    table = [r for r in text.splitlines() if r.startswith("|")]
    if len(table) < 3:
        return rows, problems
    head = [c.strip().lower() for c in table[0].strip().strip("|").split("|")]
    if tuple(head) != COLUMNS:
        return rows, [f"the targets table needs the columns {' | '.join(COLUMNS)}"]
    known = {m.name: m for m in sprint_data.MEASURES}
    for r in table[2:]:
        row = dict(zip(head, [c.strip() for c in r.strip().strip("|").split("|")]))
        name = row["measure"]
        if name not in known:
            problems.append(f"{name}: not a measure in the list")
        elif not known[name].direction:
            problems.append(f"{name}: this measure cannot carry a target")
        elif row["direction"] not in DIRECTIONS:
            problems.append(f"{name}: direction must be one of {', '.join(DIRECTIONS)}")
        elif not _is_number(row["target"]):
            problems.append(f"{name}: the target is not a number")
        elif row["status"] not in ("proposed", "approved"):
            problems.append(f"{name}: status must be proposed or approved")
        else:
            rows.append(row)
    return rows, problems


def _is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def approved(rows):
    """The targets in use: approved, with the approval date and the user's words written down."""
    return [r for r in rows if r["status"] == "approved" and r["approved"] and r["words"]]


def verdict(value, row):
    if value == "":
        return "not measured"
    v, t = float(value), float(row["target"])
    return "met" if (v <= t if row["direction"] == "at most" else v >= t) else "missed"


def _shown(row):
    return f"{row['direction']} {row['target']}"


def values(wave):
    return {m.name: m.reader(wave) for m in sprint_data.MEASURES}


def render(waves, rows, sprint, wave=None):
    """The block for one wave (`wave` set) or the sprint table. Empty text when no approved target exists."""
    used = approved(rows)
    mine = [w for w in waves if w.sprint == sprint]
    if not used or not mine:
        return ""
    got = {w.number: values(w) for w in mine}
    out = []
    if wave is not None:
        upto = [w.number for w in mine if w.number <= wave]
        if wave not in got:
            return ""
        out += ["#### 🎯 Targets", "| Measure | Value | Target | Result |", "|---|---|---|---|"]
        for r in used:
            v = got[wave][r["measure"]]
            out.append(f"| {r['measure']} | {v or 'not measured'} | {_shown(r)} | {verdict(v, r)} |")
    else:
        upto = [w.number for w in mine]
        out += ["## 🎯 Targets", "| Measure | Target | Waves met | Waves missed | Result |", "|---|---|---|---|---|"]
        for r in used:
            marks = [verdict(got[n][r["measure"]], r) for n in upto]
            met, missed = marks.count("met"), marks.count("missed")
            result = "not measured" if not (met or missed) else ("missed" if missed else "met")
            out.append(f"| {r['measure']} | {_shown(r)} | {met} | {missed} | {result} |")
    lessons = []
    for r in used:
        missed = [n for n in upto if verdict(got[n][r["measure"]], r) == "missed"]
        if missed and (wave is None or wave in missed):
            k = len(missed)
            lessons.append(f"### {r['measure']} missed its target · seen {k}× · waves {', '.join(str(n) for n in missed)}")
            if k >= 2:
                lessons.append(f"Seen twice: list {r['measure']} in Open calls as a proposed change to CLAUDE.md or a helper, "
                               "for the user's yes.")
    if lessons:
        out += ["", "Lessons (templates.md, Wave report rule 4):", *lessons]
    return "\n".join(out) + "\n"


def propose(waves, rows):
    """Proposed rows from the median of every wave's value, for measures that can carry a target and have no row yet."""
    have = {r["measure"] for r in rows}
    out = []
    for m in sprint_data.MEASURES:
        if not m.direction or m.name in have:
            continue
        nums = [float(v) for v in (m.reader(w) for w in waves) if v != ""]
        if nums:
            med = statistics.median(nums)
            out.append(f"| {m.name} | {round(med, 2):g} | {m.direction} | proposed | | |")
    return "\n".join(out) + ("\n" if out else "")


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--vault", default=os.environ.get("MYNOTES_DIR") or os.path.expanduser("~/Documents/MyNotes"))
    ap.add_argument("--domain", required=True)
    ap.add_argument("--project", required=True)
    ap.add_argument("--sprint")
    ap.add_argument("--wave", type=int)
    ap.add_argument("--targets")
    ap.add_argument("--propose", action="store_true")
    args = ap.parse_args(argv)
    domain = Path(args.vault).expanduser() / args.domain
    waves, notes = sprint_data.collect(domain, args.project)
    path = Path(args.targets) if args.targets else domain / "Projects" / args.project / "planning" / f"{args.project}-sprint-targets.md"
    rows, problems = parse_targets(path.read_text(encoding="utf-8")) if path.is_file() else ([], [])
    if problems:
        print("sprint_targets: " + "; ".join(problems), file=sys.stderr)
        return 2
    if args.propose:
        sys.stdout.write(propose(waves, rows))
        return 0
    if not args.sprint:
        print("sprint_targets: --sprint is required (or --propose)", file=sys.stderr)
        return 2
    text = render(waves, rows, args.sprint, args.wave)
    if not text:
        print("sprint_targets: no approved target in use, no Targets block", file=sys.stderr)
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
