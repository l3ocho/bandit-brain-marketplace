#!/usr/bin/env python3
"""Builds a project's sprint data file from its sprint records: one CSV row per wave, every sprint folder of the
project, live (`Projects/{slug}/sprint-*`) and archived (`_archive/Projects/{slug}/sprint-*`). Numbers come only from
the records (the ledger and the wave report); a measure a record does not hold is an empty cell, never an estimate.

Where each part is read (the measures list below is the one place a measure lives):
  ledger       `## Waves` (cards, done date; an older ledger: the cards of `## Waves and cards`, no date) · `## Batch` (effort, XS=1 S=2 M=3 L=4 XL=5) · `## Plan deviations`
  wave report  the section `## 🌊 Wave {n}`: its `#### ⏱️ Flow` and `#### 🪙 Tokens` lines, and `## 🐞 Debug` (a card's rows)

Add a measure: one `Measure(name, source, reader)` line in MEASURES. `reader` takes the wave (see Wave) and returns the
cell text, or "" when the record does not hold it. The new measure is one new column; nothing else changes.

Usage:
  sprint_data.py [--vault DIR] --domain NAME --project SLUG [--out FILE]   CSV to stdout, or to FILE
  sprint_data.py --list                                                    the measures and their sources
  (--vault defaults to $MYNOTES_DIR or ~/Documents/MyNotes)
Exit codes: 0 ok · 2 usage (no such project folder).
"""
import argparse
import csv
import io
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_sprint import CARD_ID, COMMITTED_ON, WAVE_ROW, section  # noqa: E402  (one reading of the ledger tables)

EFFORT = {"XS": 1, "S": 2, "M": 3, "L": 4, "XL": 5}
FIXED = ("sprint", "where", "wave")


@dataclass
class Wave:
    """One wave of one sprint, with the records it is read from."""
    sprint: str
    where: str
    number: int
    cards: list
    done: str
    ledger: str
    report: str = ""  # the wave report's whole text ("" when the sprint has none)
    section: str = field(init=False, default="")  # this wave's `## 🌊 Wave n` section ("" when absent)

    def __post_init__(self):
        m = re.search(rf"^##\s+\S*\s*Wave\s+{self.number}\b.*$", self.report, re.M)
        if m:
            nxt = re.search(r"^##\s", self.report[m.end():], re.M)
            self.section = self.report[m.end(): m.end() + nxt.start() if nxt else None]

    def line(self, pattern):
        """The match of `pattern` on the wave section's lines, or None."""
        return re.search(pattern, self.section, re.M)

    def table(self, text, heading):
        """A markdown table of `## heading` in `text` as a list of {lower-case column: cell}."""
        rows = [r for r in section(text, heading).splitlines() if r.startswith("|")]
        if len(rows) < 3:
            return []
        head = [c.strip().lower() for c in rows[0].strip().strip("|").split("|")]
        return [dict(zip(head, [c.strip() for c in r.strip().strip("|").split("|")])) for r in rows[2:]]


def num(value, unit=""):
    """A number from the records in thousands: `5.3 M` is 5300, `524 K` is 524."""
    return str(round(float(value) * (1000 if unit == "M" else 1)))


def _time(w):
    m = w.line(r"^- Time: (\d+):(\d{2})")
    return str(int(m.group(1)) * 60 + int(m.group(2))) if m else ""


def _group(w, pattern, index):
    m = w.line(pattern)
    return m.group(index) if m else ""


def _tokens(w, index):
    m = w.line(r"^- Total: ([\d.]+) ([KM]) re-read from cache · ([\d.]+) ([KM]) new · ([\d.]+) ([KM]) written")
    return num(m.group(2 * index - 1), m.group(2 * index)) if m else ""


def _peak(w):
    m = w.line(r"^- Main chat: .*peak context ([\d.]+) ([KM])")
    return num(m.group(1), m.group(2)) if m else ""


def _effort(w):
    rows = {r.get("card"): r.get("effort", "") for r in w.table(w.ledger, "Batch")}
    values = [EFFORT.get(rows.get(c, "")) for c in w.cards]
    return str(sum(values)) if w.cards and all(values) else ""


def _debug(w):
    rows = {r.get("card"): r for r in w.table(w.report, "🐞 Debug")}
    if not rows:
        return ""
    return str(sum(int(rows[c].get(k, "0") or 0) for c in w.cards if c in rows for k in ("expected", "found", "process")))


def _deviations(w):
    """Bullets of Plan deviations that name one of the wave's cards. A bullet naming no card cannot be placed on a
    wave, so any such bullet leaves the cell empty rather than a count that might be short."""
    body = section(w.ledger, "Plan deviations")
    bullets = re.findall(r"^-\s+(.*)$", body, re.M)
    if not body.strip():
        return ""
    if any(not CARD_ID.search(b) for b in bullets):
        return ""
    return str(sum(1 for b in bullets if set(CARD_ID.findall(b)) & set(w.cards)))


@dataclass
class Measure:
    name: str
    source: str
    reader: Callable[[Wave], str]


# One line per measure. A new measure is one more line here.
MEASURES = [
    Measure("done", "ledger Waves table: the wave's done date", lambda w: w.done),
    Measure("cards", "ledger Waves table: how many cards the wave holds", lambda w: str(len(w.cards))),
    Measure("card_ids", "ledger Waves table: the card ids", lambda w: " ".join(w.cards)),
    Measure("effort", "ledger Batch table: the cards' effort summed (XS=1 S=2 M=3 L=4 XL=5)", _effort),
    Measure("plan_deviations", "ledger Plan deviations: lines that name one of the wave's cards (empty when a line names no card)", _deviations),
    Measure("time_min", "wave report Flow: `- Time`, in minutes", _time),
    Measure("full_check_runs", "wave report Flow: `- Full checks`, runs",
            lambda w: _group(w, r"^- Full checks: (\d+) runs?", 1)),
    Measure("full_check_min", "wave report Flow: `- Full checks`, total minutes",
            lambda w: _group(w, r"^- Full checks: \d+ runs?, (\d+) min", 1)),
    Measure("full_check_failed", "wave report Flow: `- Full checks`, failed",
            lambda w: _group(w, r"^- Full checks: .*?(\d+) failed", 1)),
    Measure("test_runs", "wave report Flow: `- Test runs`, when measured",
            lambda w: str(sum(int(n) for n in re.findall(r"(\d+) (?:whole suite|targeted)", _group(w, r"^- Test runs: (.*)$", 1))))
            if _group(w, r"^- Test runs: (?!not measured)(.*)$", 1) else ""),
    Measure("code_review_rounds", "wave report Flow: `- Gates`, code review rounds",
            lambda w: _group(w, r"^- Gates: code review (\d+) rounds?", 1)),
    Measure("ui_check_rounds", "wave report Flow: `- Gates`, UI check rounds",
            lambda w: _group(w, r"^- Gates: .*UI check (\d+) rounds?", 1)),
    Measure("repeat_runs", "wave report Flow: `- Repeat runs`", lambda w: _group(w, r"^- Repeat runs: (\d+)", 1)),
    Measure("tokens_reread_k", "wave report Tokens: `- Total`, re-read from cache, in thousands", lambda w: _tokens(w, 1)),
    Measure("tokens_new_k", "wave report Tokens: `- Total`, new, in thousands", lambda w: _tokens(w, 2)),
    Measure("tokens_written_k", "wave report Tokens: `- Total`, written, in thousands", lambda w: _tokens(w, 3)),
    Measure("peak_context_k", "wave report Tokens: `- Main chat`, peak context, in thousands", _peak),
    Measure("est_cost_usd", "wave report Tokens: `- Estimated cost` (an estimate the report itself marks)",
            lambda w: _group(w, r"^- Estimated cost: \$([\d.]+)", 1)),
    Measure("hook_runs", "wave report Tokens: `- Hooks`, runs", lambda w: _group(w, r"^- Hooks: (\d+) runs?", 1)),
    Measure("debug_lines", "wave report Debug table: Expected + Found + Process of the wave's cards", _debug),
]


def waves_of(folder: Path, where: str) -> tuple[list, str]:
    """The waves of one sprint folder, or a note saying why it has none."""
    name = folder.name.removeprefix("sprint-")
    ledgers = sorted(folder.glob("*-progress.md"))
    if not ledgers:
        return [], f"{folder}: no ledger (*-progress.md)"
    ledger = ledgers[0].read_text(encoding="utf-8", errors="replace")
    rows = WAVE_ROW.findall(section(ledger, "Waves"))
    if not rows:
        # An older ledger has only `## Waves and cards` (wave, card, ...): the cards are known, the done date is not.
        by_wave = {}
        for m in re.finditer(r"^\|\s*(\d+)\s*\|\s*([A-Z]+-\d+)\s*\|", section(ledger, "Waves and cards"), re.M):
            by_wave.setdefault(int(m.group(1)), []).append(m.group(2))
        rows = [(str(n), " ".join(ids), "", "") for n, ids in sorted(by_wave.items())]
    if not rows:
        return [], f"{folder}: the ledger has neither a ## Waves nor a ## Waves and cards table"
    reports = sorted(folder.glob("*-wave-report.md"))
    report = reports[0].read_text(encoding="utf-8", errors="replace") if reports else ""
    return [Wave(name, where, int(n), CARD_ID.findall(ids), done, ledger, report) for n, ids, done, _ in rows], ""


def collect(domain: Path, project: str) -> tuple[list, list]:
    """Every wave of every sprint of the project, live then archived, in the order sprints were committed."""
    waves, notes = [], []
    for where, base in (("live", domain / "Projects" / project), ("archived", domain / "_archive" / "Projects" / project)):
        found = []
        for folder in sorted(base.glob("sprint-*")) if base.is_dir() else []:
            got, note = waves_of(folder, where)
            if note:
                notes.append(note)
            if got:
                on = COMMITTED_ON.search(got[0].ledger)
                found.append((on.group(1) if on else "", got[0].sprint, got))
        waves += [w for _, _, ws in sorted(found, key=lambda f: f[:2]) for w in ws]
    return waves, notes


def to_csv(waves: list, measures: list = None) -> str:
    measures = MEASURES if measures is None else measures
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow([*FIXED, *(m.name for m in measures)])
    for w in waves:
        writer.writerow([w.sprint, w.where, w.number, *(m.reader(w) for m in measures)])
    return out.getvalue()


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--vault", default=os.environ.get("MYNOTES_DIR") or os.path.expanduser("~/Documents/MyNotes"))
    ap.add_argument("--domain")
    ap.add_argument("--project")
    ap.add_argument("--out")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args(argv)
    if args.list:
        for m in MEASURES:
            print(f"{m.name}\t{m.source}")
        return 0
    if not args.domain or not args.project:
        print("sprint_data: --domain and --project are required", file=sys.stderr)
        return 2
    domain = Path(args.vault).expanduser() / args.domain
    if not (domain / "Projects" / args.project).is_dir() and not (domain / "_archive" / "Projects" / args.project).is_dir():
        print(f"sprint_data: no project folder {args.project} in {domain}", file=sys.stderr)
        return 2
    waves, notes = collect(domain, args.project)
    for n in notes:
        print(f"sprint_data: skipped {n}", file=sys.stderr)
    text = to_csv(waves)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
