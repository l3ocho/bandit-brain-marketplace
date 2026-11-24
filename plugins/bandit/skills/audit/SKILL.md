---
name: "audit"
description: "Audits domain and project structure across the Bandit Brain boards, each project's Project Context and its working folder against the structure rulebook, scored by a script into a replayable report of fix rows run through their owner skills. Use to check a project, audit a domain, or close a report."
---

# 🧱 Audit

Keeps every domain on one pattern. It checks, scores and **fixes**: every finding is a numbered fix
row in the same report, and every row runs through the skill that owns that thing. It never makes
a change with its own calls. **One command does it all:** `check` and `audit` run every row they
can reach in the same turn and report what they did. Nothing waits for a yes.

## 🧭 Router

`/bandit:audit <command>`. No command → offer the table as a numbered list and ask. Natural language
works too: "is this project in sync" → `check`.

| Command | Run from | Does | Reference |
|---|---|---|---|
| `check` | Inside the project being checked, on its own surface | Reads this project's running `**Version:**`, Project Context and, in Claude Code, its working folder; writes its stamp; scores this project; runs its fix rows | `references/self-check.md` |
| `audit {domain}` · `audit all` | Claude Code | One snapshot, the script, its report unedited, every fix row it can reach run, report + snapshot written | `references/domain-audit.md` · `references/snapshot.md` |
| `close {domain}` | Claude Code, in the folder that holds its snapshot | Replays the live report; valid → archives it and moves its snapshot to `.audit/_archive/` | `references/domain-audit.md` → Close |

| Read | When |
|---|---|
| `references/structure-rulebook.md` · `references/structure-rules.yaml` | Every run, fresh: the standard and the same rules as data |
| `references/fix-rows.md` | Building fix rows, and before running them: owners, linked rows, order |
| `references/gotchas.md` | Once, before a `check` or an `audit` |

## 🗄️ Where things live

| Thing | Where | Written by |
|---|---|---|
| Rulebook, rules, scorer | `references/structure-rulebook.md`, `references/structure-rules.yaml`, `scripts/check_structure.py` | The marketplace repo. Read-only here |
| Stamps | One note per domain, `{domain}-audit-stamps` (`stamps.note_title`), kind `reference`, on the domain's workflow project's board: one section per project | `check` |
| Domain report | A `log` note `audit-{YYYY-MM-DD}` on the same board | `audit` |
| Domain snapshot | `.audit/audit-{Domain}-{YYYY-MM-DD}.snapshot.json` at the root of the folder Claude Code runs from (`paths.snapshots`), git-ignored | `audit` |
| Archived report + snapshot | The note's status `archived`; the snapshot in `.audit/_archive/` | `audit` (old report), `close` |

**Why stamps:** only a project can see its own running instructions and its own folder, so each one
checks in with `check`, and `audit` scores the domain from the stamps and the boards. A board no
stamp names → **unchecked**, never a guess. A domain is a top-level board folder.

## 🔒 Hard rules

1. **Scoring is the script's.** Build the snapshot, run `scripts/check_structure.py`, show its output
   as printed. Never score, count or reword a result by hand. No script run → no report
2. **Findings come fixed.** A problem left without a fix row is a failed audit; a real either/or runs
   its recommended option and the report names the other one
3. **No approvals.** Every row this chat can reach runs in the same turn, in order, through its
   owner (`references/fix-rows.md`), never with this skill's own calls. The owner doesn't ask
   again: the command is the go. Its own writes are the report, the snapshot and the stamp. Left
   for the user: what only another project's chat can do (a change to its instructions or its
   folder), each as one line saying where to run what
4. **Writes follow bandit:notes write safety** (the report and the stamps note): look before
   creating, read right before editing, names resolve live, nothing is deleted (`close` archives,
   never deletes)
5. **A project changes only itself.** `check` never edits another project's stamp section, and
   `audit` never edits a project's instructions or folder from outside it

## ⚠️ Gotchas

The full list is `references/gotchas.md`: read it once before a `check` or an `audit`.

## 🚫 Never

- Break a hard rule (bandit:tasks `references/hard-rules.md`): names, tool limits, field limits, where information goes
- Leave a finding without a fix row, or list a problem as a note and walk away
- Fix anything with its own calls, run half of a linked pair, or a board rename before its settings row
- Guess a Claude.ai name or version: not in a stamp → **unchecked**
- Restate the rulebook's rules: read the file, quote rule numbers
- Write a report the script didn't print byte for byte, or act on a report that fails replay
- Audit task placement, or boards with a `systemOwner` (the rulebook exempts both)
- Write a stamp for a project this chat is not running in
- Audit a skill (bandit-maker:skill), rewrite instructions (bandit:project), board hygiene
  (`/bandit:tasks audit`) or note lint (`/bandit:notes lint`): name the owner
