---
name: "audit"
description: "Audits domain and project structure across Claude.ai, the MyNotes vault and the Bandit Brain board against the structure rulebook, scored by a script into a replayable report of numbered fix rows run through their owner skills. Use to check a project, audit a domain, or close a report."
---

# 🧱 Audit

Keeps every domain on one pattern. It checks, scores and **fixes**: every finding is a numbered fix
row in the same report, and approved rows run through the skill that owns that thing. It never makes
a change with its own calls.

## 🧭 Router

`/bandit:audit <command>`. No command → offer the table as a numbered list and ask. Natural language
works too: "is this project in sync" → `check`.

| Command | Run from | Does | Reference |
|---|---|---|---|
| `check` | Inside the project being checked | Reads this project's running `**Version:**` and Project Context, compares with the vault, proposes one stamp row, scores this project | `references/self-check.md` |
| `audit {domain}` · `audit all` | Anywhere | One snapshot, the script, its report unedited; report + snapshot written on approval | `references/domain-audit.md` · `references/snapshot.md` |
| `close {domain}` | Anywhere | Replays the live report; valid and done → moves it and its snapshot to `_archive/` | `references/domain-audit.md` → Close |

| Read | When |
|---|---|
| `references/structure-rulebook.md` · `references/structure-rules.yaml` | Every run, fresh: the standard (S1–S16) and the same rules as data, with `paths.stamps` (the stamp ledger) |
| `references/fix-rows.md` | Building fix rows, and before running approved ones: owners, linked rows, order |
| `references/gotchas.md` | Once, before a `check` or an `audit` |

## 🗄️ Where things live

| Thing | Path | Written by |
|---|---|---|
| Rulebook, rules, scorer | `references/structure-rulebook.md`, `references/structure-rules.yaml`, `scripts/check_structure.py` | The bandit-brain-marketplace repo. Read-only here |
| Stamp ledger | `paths.stamps` in `references/structure-rules.yaml` | `check`, on approval |
| Domain report + snapshot | `MyNotes/{Domain}/Projects/{workflow-project}/audit-{YYYY-MM-DD}.md` and `.snapshot.json` | `audit`, on approval |
| Archived report + snapshot | `MyNotes/{Domain}/_archive/Projects/{workflow-project}/` | `close`, on approval |

`{workflow-project}` = the `project:` key of the domain's workflow project. A repo's `CLAUDE.md` +
`.claude/` are scored through its mirror in `code-{slug}/`, never the lagging GitHub copy.
**Why stamps:** only a project can see its own running instructions, so each one stamps its version
with `check`, and `audit` compares stamps with the vault. No stamp → **unchecked**, never a guess.

## 🔒 Hard rules

1. **Scoring is the script's.** Build the snapshot, run `scripts/check_structure.py`, show its output
   as printed. Never score, count or reword a result by hand. No script run → no report
2. **Findings come fixed.** A problem left without a fix row is a failed audit; only a real either/or
   goes back as a question, inside the same proposal, recommended first
3. **Approved rows run through their owners** (`references/fix-rows.md`), never with this skill's
   own calls. Its own writes are the report, the snapshot and the stamp ledger
4. **Writes follow bandit:notes write safety**: new files fail closed, edits carry the bare-hex etag (strip `W/`, `"` and `-gzip`), never `if_match: "*"`,
   names resolve live, nothing is deleted (`close` moves, never deletes)
5. **Settings means settings:** a report never goes in a `Claude/ai-*` folder

## ⚠️ Gotchas

The full list is `references/gotchas.md`: read it once before a `check` or an `audit`.

## 🚫 Never

- Leave a finding without a fix row, or list a problem as a note and walk away
- Fix anything with its own calls, run half of a linked pair, or a board rename before its settings row
- Guess a Claude.ai name or version: no stamp → **unchecked**
- Restate the rulebook's rules: read the file, quote rule numbers
- Write a report the script didn't print byte for byte, or act on a report that fails replay
- Audit task placement, or boards with a `systemOwner` (the rulebook exempts both)
- Move a version file while S5 is **unchecked** for that project
- Write to `.obsidian/`, a settings folder, or anywhere outside the paths above
- Audit a skill (bandit-maker:skill), rewrite instructions (bandit:project), board hygiene
  (`/bandit:tasks audit`) or note lint (`/bandit:notes lint`): name the owner
