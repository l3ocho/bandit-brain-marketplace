# 🔍 Domain audit (`audit {domain}` · `audit all`) and `close`

> Scores domains against the structure rulebook with `scripts/check_structure.py` and writes one
> report per domain, with its snapshot. Runs every fix row in the same turn: no approval asked.

**Run from Claude Code.** The snapshot is a data file in `.audit/` at the root of the folder
Claude Code runs from (`paths.snapshots`), so `audit` and `close` run there; from Claude.ai, say so
and stop. Pick a folder whose root may hold `.audit/`: a repository, or an agent's folder
without the working-folder guard. A Claude Code twin's working folder refuses it (its guard keeps
the root to the S12 layout). A repository that does not ignore `.audit/` in its `.gitignore`: say
so, as the sprint helper does for `.sprint/`.

## 📥 Gather (read-only)

Build the three input files exactly as `references/snapshot.md` says: `rules.yaml`,
`rulebook.md`, `snapshot.json`. **One snapshot per run.** `audit all` scores every domain from that
single pull, so all four reports describe the same moment.

The domain must be a folder in `MyNotes` (its settings live there whichever storage holds its
notes). Not there → stop and list the domains that exist.

## 🧮 Score: the script's job

```
python {skill folder}/scripts/check_structure.py --rules rules.yaml --rulebook rulebook.md \
    --snapshot snapshot.json [--domain {domain}] --out out
```

- **Never score, count, reword or drop a result by hand.** The script's output is the report.
- Exit `2` → an input broke its contract. Say what it printed and fix the input (usually the
  snapshot). Never work around it.
- The script already builds the fix rows: the owner from the rules file, linked rename pairs
  (`S2 · with 3`), S7 archive rows only where S5 is known, and paste rows instead of fix rows
  for findings a pending paste already fixes.
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

1. Execute in the order `references/fix-rows.md` sets (notes rows, the vault's or the app's → settings → board), each row through
   its owner's procedure. Skip rows that depend on a failed row.
2. Settings rows: load `bandit:project` and run its targeted update **from the vault**, with the
   project's folder, its production file (the one matching the stamp) and the change. It writes
   the next version file and returns the text to paste.
3. Report per row, then the close-out lines from SKILL.md.

## 📄 Report

Per domain, written every run: the report where the domain's **workflow project** keeps its notes
(its Project Context: `notes: app`, or no line for the vault), and the snapshot in `.audit/`.

| What | Notes in the app (`notes: app`) | Notes in the vault |
|---|---|---|
| The report: the script's `out/audit-{domain}-{date}.md`, **byte for byte** | A note of kind `log`, title `audit-{YYYY-MM-DD}`, summary the report's score line, on the workflow project's board, written straight in through bandit:notes (create without a duplicate, then filed) | `MyNotes/{domain}/Projects/{workflow-project}/audit-{YYYY-MM-DD}.md`, a new file (omit `if_match`) |
| The snapshot it scored | `.audit/audit-{domain}-{YYYY-MM-DD}.snapshot.json` | the same |

- Never into `Claude/ai-*`: that's the settings folder, for instructions and the reference doc only — never project logs, working notes, decision journals, discussion records, reports, briefs, plans or drafts.
- In the vault, the workflow project's `Projects/` folder missing → a separate row (`bandit:notes` creates it).
- A live report already there (valid or **superseded**, see Replay) → archive it as-is before the
  new report is written, through `/bandit:notes archive`: in the app its status set to `archived`
  (`notes_set_status`), in the vault moved to `_archive/Projects/{workflow-project}/` with its old
  vault snapshot, if any. Its snapshot in `.audit/` moves to `.audit/_archive/`. An invalid one is
  archived too; say it failed replay.
- **Finding the live reports.** By the title prefix `audit-`, whatever the note's kind (a report the
  vault move carried into the app may have another kind): in the app, the workflow board's notes
  (`notes_list`) whose title starts `audit-`; in the vault, `audit-*.md` in the workflow project's
  folder. A workflow project with `notes: app` is also looked for in that vault folder, so a report
  written before the switch is found and archived by the first audit after it; every live one found,
  in either place, is archived.

## 🔁 Replay

```
python {skill folder}/scripts/check_structure.py --rules rules.yaml --rulebook rulebook.md \
    --snapshot .audit/audit-{domain}-{date}.snapshot.json --replay {saved report}
```

`{saved report}` is the report's text written to a file in `.audit/` as read: the note's text
(`notes_get`) or the vault file, raw. The script compares it byte for byte, trailing newlines aside.

- **Superseded first.** No footer, a footer whose rules or script hash differs from today's, or no
  snapshot of that date in `.audit/` (an audit run before the snapshot moved to `.audit/`, or from
  another folder) → the report can never replay. It isn't invalid, it's superseded:
  don't replay it, don't act on its rows, and say which hashes differ. It leaves only through a
  fresh audit (the archive row under Report).
- `REPLAY OK` → the report is exactly what its snapshot produces.
- Exit `3` → **the report is invalid**: someone (or some chat) edited it. Say so and don't act on
  its rows.
- The report's footer names the rules and script hashes it was built with. If today's rules file
  or script differ, replay can't pass: say so, and offer a fresh audit instead. A rule change
  (e.g. adding S9) is the moment: close live reports **before** it's installed.
- **Denominator change.** The first audit after a rule is added scores each project against more
  rules (S12: 8 musts, was 7), and new rows can appear, S12's for projects with a Claude Code twin.
  Say so in a Note below the report, so it doesn't read as a regression.

## 📦 Close (`close {domain}`)

Run from Claude Code, in the folder that holds the report's snapshot in `.audit/`.

1. Find the live report (Report, above) and its snapshot in `.audit/`. None → say so.
2. **Replay** it. Superseded → stop and offer a fresh audit, which archives it. Invalid → stop
   and say why.
3. Archive the report through `/bandit:notes archive`: in the app its status set to `archived`
   (`notes_set_status`); in the vault moved to `MyNotes/{domain}/_archive/Projects/{workflow-project}/`
   (`nc_webdav_move_resource`; a missing target folder → `bandit:notes` creates it first). Move its
   snapshot to `.audit/_archive/`.
4. Confirm: the note read back with status `archived` (in the vault, both folders listed), and
   `.audit/_archive/` listed.
