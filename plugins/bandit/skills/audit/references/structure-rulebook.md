---
type: reference
summary: House standard for the user's domains and projects across Claude.ai, each project's own folder and the Bandit Brain boards. bandit:audit scores against these 8 rules.
updated: 2026-11-22
---

# 🧱 Structure Rulebook

> House standard for the user's domains and projects across Claude.ai, each project's own folder and the Bandit Brain boards. bandit:audit scores against these 8 rules.

## 🗺️ Overview

- **6 musts** (S1–S4, S9, S12): a break is ❌ and gets a fix row.
- **2 shoulds** (S6, S13): a break is ⚠️, fixed when the project is touched anyway or when the user asks.
- **Retired**, their numbers never reused: S5, S7, S8, S10, S11 (2026-11-22) and S14, S15, S16 (2026-11-20).
- A rule that doesn't apply scores **—**. Anything the auditor couldn't read scores **unchecked**, never a guess.
- **Score line:** `musts 6/6 · shoulds 2/2 · 2026-11-22`, one per project, plus one for the domain.
- **Exempt:** boards with a `systemOwner` (e.g. Finance in Money). Listed as "system, not audited".
- **Scored by a script, never by hand.** `structure-rules.yaml`, next to this file, holds these rules as data. bandit:audit's `check_structure.py` scores against it. Change a rule → change both files in the same approved proposal, and keep `rulebook_updated` there equal to `updated:` here: the script refuses to run when they differ.

### Where a project lives

| Place | Holds | Named |
|---|---|---|
| The project's own surface | Its **one** instructions file, with its Project Context: a Claude.ai project's instructions, or `CLAUDE.md` and `.claude/` in the folder a Claude Code project runs from. Working files (data, scripts, outputs) stay in that folder | Claude.ai: `{L} - Name` (workflow project: the domain's display name). Claude Code: the folder is the user's |
| Bandit Brain | Its board, filed in the domain's folder, and on it its notes: the hub note, its reference doc, plans, reports, briefs | `Name` (workflow board: `Name - wkflw`) |

A **domain** is a top-level board folder. A **project** is known to the audit by its stamp: what
it says about itself when `/bandit:audit check` runs inside it.

The `{L} - ` prefix exists only in Claude.ai, as a workaround until Claude.ai can group projects by domain. When it can, the prefix goes, and S1 and S2 drop that part.

**One configuration.** A project runs on one surface and has one instructions file (bandit:project). There is no second copy for another surface and no settings folder kept elsewhere.

---

## ❌ Musts

### S1 · Domain alignment

- The domain is a top-level board folder; its name is canonical. Subfolders are allowed and don't count as domains.
- Every Claude.ai project in the domain starts with the domain's letter.
- A project that runs in Claude Code has no Claude.ai name: its part scores **—**.
- **Check:** the domain's folder exists at the top level; each Claude.ai project's name, from its stamp, starts with the letter. A stamp with no name → **unchecked**.

### S2 · One name

- One `Name` per project on Claude.ai and on its board: Claude.ai `{L} - Name`, board `Name`.
- The workflow board alone adds ` - wkflw`.
- No other prefixes or suffixes on boards (`App:`, `APP:`, `DBT:`, `…flow`).
- A project that runs in Claude Code has no second name to match: its part scores **—**. The board rule still applies to every board.
- **Check:** strip `{L} - ` from the Claude.ai name (and ` - wkflw` from a workflow board). The board must equal it exactly. The two differ → the user says which is right.

### S3 · One workflow per domain

- Each domain has exactly one workflow project and one workflow board.
- The workflow board is named `{Name} - wkflw` **and** has profile Workflow. The two must agree.
- The workflow board holds only tasks that belong to no project in the domain. Task placement is the user's call and isn't audited.
- The workflow project's `board:` names its own workflow board: `project "{Name} - wkflw"`. Every project reads and writes across its domain folder; the workflow project also owns the Untriaged cards. What each may do there is bandit:tasks' rule (`references/scope.md`).
- **Check:** exactly one board per domain folder ends in ` - wkflw`, and its profile is `workflow` (fix: its creator switches it, through bandit:tasks). Other boards may be Workflow too: it is every everyday board's profile. Exactly one stamped project has `type: workflow`, and its `board:` names that board.

### S4 · Project Context

- The `## 🧭 Project Context` block (owned by `bandit:project`) has all 5 required keys: `domain`, `project`, `type`, `board`, `prefix`.
- Two optional keys: `dev`, valid value `true`, and `notes`, valid values `none` (the helpers keep no notes for the project) and `app` (the older way to say the default). Each is such a value or its line is absent. Any other value is ❌. A project without the line is never flagged: its notes are in the app's Notes.
- `domain` is the board folder the project is scored in. `board` is `project "{name}"` naming an existing board, or `none`. `folder "…"`, `global` and `pending` don't pass. `prefix` is 2–3 letters, or `none`.
- The `board` line's board is filed in the domain's board folder or one of its subfolders: `domain` and `board` together are the project's board scope (bandit:tasks `references/scope.md`). A home board outside its domain folder is ❌.
- **Check:** read from the project's stamp. Keys missing, a value invalid, `board` unresolved or outside the domain folder → ❌. The fix is made in the project itself (`/bandit:project audit` there).

### S9 · Dev board shape

Numbered after the shoulds so old reports keep their numbers; it's a must.

- **With `dev: true`** in the project's Project Context: its board's profile is Technical (lanes are hidden on a Workflow board), it has a lane for each tag `lane/incident · lane/issue · lane/feature · lane/maintenance · lane/content · lane/tech-debt`, the **first** lane is Incident, and the tags `stage/spec · stage/planned · stage/ready` exist too.
- **Without it:** the board has no lane matching any `lane/*` or `stage/*` tag. A board no project has checked in for follows the same rule.
- Scores **—** on `board: none` and on system-owned boards.
- Card tags (a stray `lane/*` tag on a non-dev card) aren't checked here: tags are account-wide, and card hygiene is `bandit:tasks audit`.
- **Check:** profile, lanes and tags from the snapshot. Fix rows go to bandit:tasks' dev board shape procedure; dev lanes on a non-dev board are the user's call.

### S12 · Working folder

Numbered last so old reports keep their numbers; it's a must.

- For a project that runs in Claude Code without `dev: true`: the folder it runs from keeps one layout. At the root: `CLAUDE.md`, `REFERENCE.md`, `.claude/`, `repos/`, `work/`, `data/`, `scratch/`, `_closed/`, `_backup/`, and hosted projects (a folder with its own `CLAUDE.md`). Nothing else.
- `work/`, `data/` and `_closed/` hold only task folders named `{prefix}-{task}`: `{task}` is the board task's title in kebab-case, never an ID. No loose files. Superseded work stays in its task folder (`work/{prefix}-{task}/superseded/`) and leaves with it at close.
- `_backup/` holds settings rollback copies only, flat: `CLAUDE.md.{version}`, `REFERENCE.md.{version}`, `settings.json.{version}`, `workdir.py.{version}` (`s12.backup_name_pattern`). No retention clock; deleted only by a fix row. Never work, never data.
- Data files (`s12.data_extensions`) live only in `data/{prefix}-{task}/`. `data/` is purged when its task closes, never archived. The manifest never records a file name under `data/`; customer data in notes stays under each project's own rule.
- Retention: `scratch/` files older than 7 days and `_closed/` folders older than 30 days get a delete row, run by the audit with the rest.
- Enforced at write time by the folder's guard: `.claude/hooks/workdir.py`, hash `s12.hook_sha12`, run by a `PreToolUse` and a `SessionStart` hook in `.claude/settings.json` (bandit:project, `references/workdir.md`). The guard's constants mirror `s12`: change both.
- The `SessionStart` hook writes a manifest in `.claude/` (paths, dates, counts; no contents). It stays on the machine: `check`, run in the folder, copies it into the project's stamp. No manifest in the stamp, or one older than 7 days → **unchecked**.
- Fix rows: guard missing or outdated → bandit:project, in the project. Layout rows → the project's Claude Code session, targets written `{slug}:{path}`, relative to its folder. Any move ends by searching the project's notes for the old paths and proposing the note edits.
- Scores **—** for `dev: true` (the repository keeps its own layout) and for a project on Claude.ai.
- **Check:** guard file hash and hooks, and the layout from the manifest, all from the stamp.

---

## ⚠️ Shoulds

### S6 · Complete footprint

- Every project has a board, or declares `board: none` in its Project Context.
- Every board belongs to a project that has checked in: a board no stamp names is ⚠️, with an Unchecked line saying to run `check` in its project, or to archive the board if it has none.
- **Check:** stamps with no board, and boards with no stamp.

### S13 · Sprint briefs

Numbered last so old reports keep their numbers. The conventions are bandit:notes'; this rule only
scores them. bandit-dev:sprint's local checker (`check_sprint.py`, a `Stop` hook) reads the project's
notes file, and its SP2 is this rule at write time. The audit scores it from the snapshot and never
replaces that checker.

- A brief (a note of kind `brief`) whose card is in sprint `{name}` (a real sprint, or its old
  `sprint/{name}` tag) carries the tag `sprint-{name}`, `{name}` in kebab-case.
- No brief of a sprint card, no board of its own, or `notes: none` → **—**.
- Fix row: bandit:notes tags it (`notes_set_fields`, the other tags kept).
- **Check:** the project's notes with their kind, cards and a brief's tags, and the cards in a
  sprint (real sprints, and `sprint/*` tags until they retire), from the snapshot.

### Retired

- **S5 (production version), S7 (one production version kept), S8 (file names in the settings
  folder), S10 (the copy for another surface), S11 (the dev mirror):** retired 2026-11-22. They
  compared the files of a settings folder kept outside the project, and a second copy of the
  instructions for another surface. A project now has one instructions file, on its own surface,
  and nothing to compare it with.
- **S14, S15, S16:** retired 2026-11-20 with the move of the notes into the app (one filename,
  frontmatter that parses, a sprint project's root). The app has ids, fields and no folders.

Their numbers are never reused, and a snapshot taken before 2026-11-22 no longer loads: its report
is superseded (**📄 Report lifecycle**).

---

## 📄 Report lifecycle

- One live report per domain: a note of kind `log` titled `audit-{YYYY-MM-DD}` on the board that holds the domain's stamps note (its workflow project's board), written straight in through bandit:notes.
- Per project: the score line, then numbered fix rows `| # | Action | Target | Owner | Rule |`. The audit runs every row in reach in the same turn; no approval is asked. A row inside another project is handed over as one line saying where to run what.
- **The stamps** are a note too: `{domain}-audit-stamps`, kind `reference`, one section per project, each written only by `check` run inside that project.
- **The snapshot** the script scored is a data file, not a note: `audit-{Domain}-{YYYY-MM-DD}.snapshot.json` in `.audit/` at the root of the folder Claude Code runs the audit from (`paths.snapshots`), git-ignored. So `audit` and `close` run from Claude Code; `check` runs in the project, on its surface. The report is written exactly as the script printed it; its footer carries the rules, snapshot and script hashes.
- **Replay:** `close` and the next audit re-run the script on the saved snapshot. A report that doesn't reproduce byte for byte (trailing newlines aside) is invalid.
- **Superseded:** a report with no footer, built with other rules or script hashes, from a snapshot of an earlier schema, or whose snapshot isn't in `.audit/`, can't replay. The fresh audit that replaces it archives it as-is; its rows are never run.
- When the fixes are done, `close` archives the report (status `archived`) and moves its snapshot to `.audit/_archive/`.

---

## 🔄 Changing this rulebook

- Changes follow the usual proposal flow, and the user approves them.
- A rule gets added when the same finding turns up in **two or more domains**.
- **Exception:** S9 was added as a preventive rule with the user's explicit approval (2026-09-28), before the finding had appeared in two domains.
- **Exception:** S12 and its guard were added as preventive rules with the user's explicit approval (2026-09-29), before the finding had appeared in two domains.
- **2026-09-30 · S12 amended** after its first rollout, with the user's explicit approval: `_backup/` for settings rollback copies, superseded work kept in its task folder, moves update the project's notes, and the `data/` file-name rule scoped to the manifest.
- **Exception:** S13 was added as a preventive should with the user's explicit approval (2026-10-09), so bandit-dev:sprint's local checker cites one rulebook, before the finding had appeared in two domains.
- **2026-10-13 · Moved into the marketplace repo** with the skills: this file and `structure-rules.yaml` live in bandit:audit's `references/`, and owner names follow the plugin names. No rule changed.
- **2026-10-29 · Board profile**, with the user's approval: the app replaced Type with a profile on boards (Workflow or Technical). S3 checks the workflow board's profile, and no longer asks that no other board be Workflow; S9 adds that a dev project's board is Technical.
- **2026-11-20 · Notes in the app**, with the user's approval: S13 scores a brief's sprint tag; S14, S15 and S16 are retired. The report is a note; the snapshot moves to `.audit/` in the folder Claude Code runs from.
- **2026-11-22 · One storage, one configuration**, on the user's word (everything locked into the app; one configuration per project): the notes storage outside the app is gone, and so are the settings folder, the second copy of a project's instructions and the dev mirror. A project is known by its stamp, and a domain is a board folder. S5, S7, S8, S10 and S11 are retired; S1, S2, S4, S6, S12 and S13 are restated on the stamp. S4 accepts `notes: none`. Snapshot schema 8; earlier snapshots no longer load.
- A rules or script change stops earlier reports from replaying (their footer hashes differ). Close live reports before installing one if their fixes are done; any left live become superseded (**📄 Report lifecycle**), and the next fresh audit archives them.
