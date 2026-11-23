# 🔍 Domain audit (`audit {domain}` · `audit all`) and `close`

> Scores domains against the structure rulebook with `scripts/check_structure.py` and writes one
> report per domain, with its snapshot. Runs every fix row it can reach in the same turn: no approval asked.

**Run from Claude Code.** The snapshot is a data file in `.audit/` at the root of the folder
Claude Code runs from (`paths.snapshots`), so `audit` and `close` run there; from Claude.ai, say so
and stop. Pick a folder whose root may hold `.audit/`: a repository, or an agent's folder
without the working-folder guard (the guard keeps a root to the S12 layout and refuses it). A
repository that does not ignore `.audit/` in its `.gitignore`: say so, as the sprint helper does
for `.sprint/`.

## 📥 Gather (read-only)

Build the three input files exactly as `references/snapshot.md` says: `rules.yaml`,
`rulebook.md`, `snapshot.json`. **One snapshot per run.** `audit all` scores every domain from that
single pull, so all the reports describe the same moment.

A domain is a top-level board folder (`get_context`). Not there → stop and list the ones that exist.

## 🧮 Score: the script's job

```
python {skill folder}/scripts/check_structure.py --rules rules.yaml --rulebook rulebook.md \
    --snapshot snapshot.json [--domain {domain}] --out out
```

- **Never score, count, reword or drop a result by hand.** The script's output is the report.
- Exit `2` → an input broke its contract. Say what it printed and fix the input (usually the
  snapshot). Never work around it.
- The script already builds the fix rows, each with its owner from the rules file.
- Show each report in chat as printed. The script's rows are only the start: **every finding gets
  fixed.**
- **Extra fix rows.** A finding the rules don't cover yet goes **below** the report, never inside
  it, as an `Extra fix rows` table numbered after the script's rows: action, owner (**🔧 Who fixes
  what** in `references/fix-rows.md`), exact target, why. They run with the script's rows.
  A finding with two valid fixes is one row with both options: the recommended one runs, the report
  names the other.
- Pure context that needs no fix (e.g. the denominator change below) is a one-line **Note**, never
  a finding.

## ▶️ Run every row

Right after the report is shown, no question:

1. Execute in the order `references/fix-rows.md` sets (notes → board), each row through its owner's
   procedure. Skip rows that depend on a failed row.
2. **Rows inside another project** (its Project Context, its working-folder guard, its layout, a
   Claude.ai rename) are out of reach from here: only that project's own chat can change it. They
   are not run and not dropped: each becomes one close-out line, per project, saying where to run
   what (`references/fix-rows.md` → Close the run).
3. Report per row, then the close-out lines.

## 📄 Report

Per domain, written every run: the report as a note, and the snapshot in `.audit/`.

| What | Where |
|---|---|
| The report: the script's `out/audit-{domain}-{date}.md`, **byte for byte** | A note of kind `log`, title `audit-{YYYY-MM-DD}`, summary the report's score line, on the board that holds the domain's stamps note, written straight in through bandit:notes (create without a duplicate, then filed) |
| The snapshot it scored | `.audit/audit-{domain}-{YYYY-MM-DD}.snapshot.json` |

- A domain with no stamps note yet has no project checked in: the report says so in its Unchecked
  list, and the note goes on the domain's workflow board (`references/self-check.md`, step 4, says
  how that board is found).
- A live report already there (valid or **superseded**, see Replay) → archive it as-is before the
  new report is written, through `/bandit:notes archive`: its status set to `archived`
  (`notes_set_status`). Its snapshot in `.audit/` moves to `.audit/_archive/`. An invalid one is
  archived too; say it failed replay.
- **Finding the live reports.** By the title prefix `audit-` and a date, whatever the note's kind:
  the notes of the domain's boards (`notes_list`) whose title is `audit-{YYYY-MM-DD}`. The stamps
  note (`…-audit-stamps`) is never a report. Every live one found is archived.

## 🔁 Replay

```
python {skill folder}/scripts/check_structure.py --rules rules.yaml --rulebook rulebook.md \
    --snapshot .audit/audit-{domain}-{date}.snapshot.json --replay {saved report}
```

`{saved report}` is the report's text written to a file in `.audit/` as read (`notes_get`). The
script compares it byte for byte, trailing newlines aside.

- **Superseded first.** No footer, a footer whose rules or script hash differs from today's, a
  snapshot of an earlier schema, or no snapshot of that date in `.audit/` → the report can never
  replay. It isn't invalid, it's superseded: don't replay it, don't act on its rows, and say which
  hashes differ. It leaves only through a fresh audit (the archive row under Report).
- `REPLAY OK` → the report is exactly what its snapshot produces.
- Exit `3` → **the report is invalid**: someone (or some chat) edited it. Say so and don't act on
  its rows.
- The report's footer names the rules and script hashes it was built with. If today's rules file
  or script differ, replay can't pass: say so, and offer a fresh audit instead. A rule change is
  the moment: close live reports **before** it's installed.
- **Denominator change.** The first audit after rules are added or retired scores each project
  against a different number of rules. Say so in a Note below the report, so it doesn't read as a
  regression or a gain.

## 📦 Close (`close {domain}`)

Run from Claude Code, in the folder that holds the report's snapshot in `.audit/`.

1. Find the live report (Report, above) and its snapshot in `.audit/`. None → say so.
2. **Replay** it. Superseded → stop and offer a fresh audit, which archives it. Invalid → stop
   and say why.
3. Archive the report through `/bandit:notes archive`: its status set to `archived`
   (`notes_set_status`). Move its snapshot to `.audit/_archive/`.
4. Confirm: the note read back with status `archived`, and `.audit/_archive/` listed.
