# 🔍 Domain audit (`audit {domain}` · `audit all`) and `close`

> Scores domains against the structure rulebook with `scripts/check_structure.py` and writes one
> report per domain, with its snapshot, on approval. Read-only until Leo approves the report row.

## 📥 Gather (read-only)

Build the three input files exactly as `references/snapshot.md` says: `rules.yaml`,
`rulebook.md`, `snapshot.json`. **One snapshot per run.** `audit all` scores every domain from that
single pull, so all four reports describe the same moment.

The domain must be a folder in `MyNotes`. Not there → stop and list the domains that exist.

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
  what** in `references/fix-rows.md`), exact target, why. Leo approves them with the script's rows in one answer.
  A finding with two valid fixes is one row with both options, the recommended one first.
- Pure context that needs no fix (e.g. the denominator change below) is a one-line **Note**, never
  a finding.

## ▶️ Run the approved rows

1. Execute in the order SKILL.md sets (vault → settings → board), each row through its owner's
   procedure. Skip rows that depend on a declined or failed row.
2. Settings rows: load `bandit:project` and run its targeted update **from the vault**, with the
   project's folder, its production file (the one matching the stamp) and the change. It writes
   the next version file and returns the text to paste.
3. Report per row, then the close-out lines from SKILL.md.

## 📄 Report

Two new files per domain, both written on one approved row (new files: omit `if_match`):

| File | Content |
|---|---|
| `MyNotes/{domain}/Projects/{workflow-project}/audit-{YYYY-MM-DD}.md` | The script's `out/audit-{domain}-{date}.md`, **byte for byte** |
| `MyNotes/{domain}/Projects/{workflow-project}/audit-{YYYY-MM-DD}.snapshot.json` | The `snapshot.json` it scored |

- Never into `Claude/ai-*`: that's the settings folder, for instructions and the reference doc only — never project logs, working notes, decision journals, discussion records, reports, briefs, plans or drafts.
- The workflow project's `Projects/` folder missing → a separate row (`bandit:notes` creates it).
- A live report already there → replay it first (see Close), then ask: close it, or replace it (an
  edit with its etag, the snapshot too). A **superseded** one (see Replay) gets one more row in the
  same proposal: archive it and its snapshot, as-is, before the new report is written.

## 🔁 Replay

```
python {skill folder}/scripts/check_structure.py --rules rules.yaml --rulebook rulebook.md \
    --snapshot {saved snapshot} --replay {saved report}
```

- **Superseded first.** No footer, or a footer whose rules or script hash differs from today's →
  the report was built under other rules and can never replay. It isn't invalid, it's superseded:
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

1. Find the live `audit-*.md` and its `.snapshot.json` in
   `MyNotes/{domain}/Projects/{workflow-project}/`. None → say so.
2. **Replay** it. Superseded → stop and offer a fresh audit, which archives it. Invalid → stop
   and say why.
3. Ask Leo whether its fix rows are done. Not done → stop; closing is his call.
4. One row: move both files to `MyNotes/{domain}/_archive/Projects/{workflow-project}/` with
   `nc_webdav_move_resource`. A missing target folder is a separate row (`bandit:notes` creates it).
5. Confirm by listing both folders.
