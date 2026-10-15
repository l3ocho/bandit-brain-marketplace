---
type: reference
summary: House standard for the user's domains and projects across Claude.ai, the MyNotes vault and BanditBrains. bandit:audit scores against these 16 rules.
updated: 2026-10-15
---

# 🧱 Structure Rulebook

> House standard for the user's domains and projects across Claude.ai, the MyNotes vault and BanditBrains. bandit:audit scores against these 16 rules.

## 🗺️ Overview

- **8 musts** (S1–S5, S9, S10, S12): a break is ❌ and gets a fix row.
- **8 shoulds** (S6–S8, S11, S13–S16): a break is ⚠️, fixed when the project is touched anyway or when the user asks.
- A rule that doesn't apply scores **—**. Anything the auditor couldn't read scores **unchecked**, never a guess.
- **Score line:** `musts 8/8 · shoulds 7/8 · 2026-10-09`, one per project, plus one for the domain.
- **Exempt:** boards with a `systemOwner` (e.g. Finance in Money). Listed as "system, not audited".
- **Scored by a script, never by hand.** `structure-rules.yaml`, next to this file, holds these rules as data. bandit:audit's `check_structure.py` scores against it. Change a rule → change both files in the same approved proposal, and keep `rulebook_updated` there equal to `updated:` here: the script refuses to run when they differ.

### The three places

| Place | Holds | Named |
|---|---|---|
| Claude.ai | Project instructions, in production | `{L} - Name` (workflow project: the domain's display name) |
| MyNotes vault | `{Domain}/Claude/ai-{slug}/`: **settings only**, the production instructions and reference docs. Work output (reports, notes, plans) goes in `{Domain}/Projects/{slug}/`. The project's other surfaces sit beside it, settings only too: `code-{slug}/` (Claude Code) and `design-{slug}/` (Claude Design) | `ai-{slug}` · `code-{slug}` · `design-{slug}` |
| BanditBrains | Board, filed in the domain folder | `Name` (workflow board: `Name - wkflw`) |

The `{L} - ` prefix exists only in Claude.ai, as a workaround until Claude.ai can group projects by domain. When it can, the prefix goes, and S2 drops that part.

**Settings means settings.** A settings folder never holds workflows, reports, audits or anything else a project produces. That separation is the reason the folder exists.

---

## ❌ Musts

### S1 · Domain alignment

- The vault domain folder name is canonical (`BanditLabs`, `Summitt`, `Personal`, `Family`).
- The BanditBrains top-level folder has the same name. Subfolders (e.g. `Career`, `S Projects`) are allowed and don't count as domains.
- Every Claude.ai project in the domain starts with the domain's letter.
- **Check:** each domain resolves in all three places. A board folder with no vault domain (and not exempt) is ❌.

### S2 · One name

- One `Name` per project. Claude.ai `{L} - Name`, board `Name`, vault `ai-{slug(Name)}` (kebab-case).
- The workflow board alone adds ` - wkflw`: `Bandit Labs - wkflw`. The vault folder stays `ai-bandit-labs`.
- No other prefixes or suffixes on boards (`App:`, `APP:`, `DBT:`, `…flow`).
- `code-{slug}/` and `design-{slug}/` are **surfaces of the same project** as `ai-{slug}/` (same slug), not projects of their own. A surface with no `ai-{slug}/` isn't scored: it's listed as unchecked.
- **Check:** strip `{L} - ` from the Claude.ai name (and ` - wkflw` from a workflow board). Board must equal it exactly, and the vault folder must equal its slug.

### S3 · One workflow per domain

- Each domain has exactly one workflow project: one Claude.ai project, one board, one `ai-{slug}` folder.
- The workflow board is named `{Name} - wkflw` **and** has type `workflow`. The two must agree.
- The workflow board holds only tasks that belong to no project in the domain. Task placement is the user's call and isn't audited.
- The workflow project's `board:` names its own workflow board: `project "{Name} - wkflw"`. Every project reads and writes across its domain folder; the workflow project also owns the Untriaged cards. What each may do there is bandit:tasks' rule (`references/scope.md`).
- **Check:** exactly one board per domain folder ends in ` - wkflw`, its type is `workflow`, and no other board in the folder has type `workflow`. Exactly one project has `type: workflow`, and its `board:` names that board.

### S4 · Project Context

- The `## 🧭 Project Context` block (owned by `bandit:project`) has all 5 required keys: `domain`, `project`, `type`, `board`, `prefix`.
- One optional key: `dev`. Valid value `true`, or the line is absent. Any other value is ❌. A project without the line is never flagged.
- `domain` is the vault domain. `board` is `project "{name}"` naming an existing board, or `none`. `folder "…"`, `global` and `pending` don't pass.
- The `board` project is filed in the domain's board folder or one of its subfolders: `domain` and `board` together are the project's board scope (bandit:tasks `references/scope.md`). A home board outside its domain folder is ❌.
- **Check:** read from the production instructions file in the vault. Keys missing, `dev` invalid, `board` unresolved or outside the domain folder → ❌.

### S5 · Production version

- The production file is the `{prefix}-instructions-v{N}.md` whose `**Version:**` matches the project's self-check stamp.
- **Drift levels:**

Checked top to bottom; the first case that matches wins.

| # | Case | Score | Fix |
|---|---|---|---|
| 1 | No stamp | unchecked | Run the self-check in that project |
| 2 | Stamp matches a vault file, and it's the newest | ✅ | — |
| 3 | Stamp matches a vault file, and a newer one exists | ⚠️ not pasted yet | Paste it into Claude.ai, run the self-check. Both files stay until then |
| 4 | Stamp matches no file and is newer than every vault file | ❌ critical | Vault copy lost or rolled back: recover it before anything else |
| 5 | Stamp matches no file and is older than the newest file's date | unchecked | Run the self-check in that project |
| 6 | Anything else | ⚠️ drift | Say both versions; the user decides |

While a newer file waits to be pasted (case 3), findings that the newer file already fixes score ⚠️ "paste pending" and get no fix row of their own: the paste is the fix.

- **Check:** stamp vs vault. Nothing is moved while the result is unchecked.

### S9 · Dev board shape

Numbered after the shoulds so old reports keep their numbers; it's a must.

- **With `dev: true`** in the project's Project Context: its board has a lane for each tag `lane/incident · lane/issue · lane/feature · lane/maintenance · lane/content · lane/tech-debt`, the **first** lane is Incident, and the tags `stage/spec · stage/planned · stage/ready` exist too.
- **Without it:** the board has no lane matching any `lane/*` or `stage/*` tag. A board with no vault project follows the same rule.
- Scores **—** on `board: none` and on system-owned boards.
- Card tags (a stray `lane/*` tag on a non-dev card) aren't checked here: tags are account-wide, and card hygiene is `bandit:tasks audit`.
- **Check:** lanes and tags from the snapshot (schema 2). A schema-1 snapshot has no lanes: S9 scores **unchecked**. Fix rows go to bandit:tasks' dev board shape procedure; dev lanes on a non-dev board are the user's call.

### S10 · Claude Code twin

- For any project without `dev: true` (any `type:`) with a `code-{slug}/`: its `CLAUDE.md` is the Claude Code twin of the Claude.ai instructions (bandit:project). `claude/settings.json` and `claude/hooks/workdir.py` next to it hold the permission rules and the working-folder guard (S12): S8 allows them, S10 doesn't compare them.
- The twin's `**Version:**` equals the `ai-{slug}/` production version (S5), and the text outside `## 🖥️ Environment` hashes the same.
- Twin behind production → ⚠️ not applied yet. Twin at a newer file still waiting to be pasted → ⚠️ paste pending (the S5 paste is the fix). Same version, core differs → ❌. The script never picks which copy is right.
- Scores **—** when the project has `dev: true` (its surface is the dev mirror, S11) or has no `code-{slug}/`; **unchecked** while S5 is unchecked.
- **Check:** version token and core hash, twin vs production file. Fix rows go to bandit:project.

### S12 · Claude Code working folder

Numbered last so old reports keep their numbers; it's a must.

- For any project with a Claude Code twin (S10): the local folder Claude Code runs from keeps one layout. At the root: `CLAUDE.md`, `.claude/`, `repos/`, `work/`, `data/`, `scratch/`, `_closed/`, `_backup/`, and hosted projects (a folder with its own `CLAUDE.md`). Nothing else.
- `work/`, `data/` and `_closed/` hold only task folders named `{prefix}-{task}`: `{task}` is the board task's title in kebab-case, never an ID. No loose files. Superseded work stays in its task folder (`work/{prefix}-{task}/superseded/`) and leaves with it at close.
- `_backup/` holds settings rollback copies only, flat: `CLAUDE.md.{version}`, `settings.json.{version}`, `workdir.py.{version}` (`s12.backup_name_pattern`). No retention clock; deleted only by a fix row. Never work, never data.
- Data files (`s12.data_extensions`) live only in `data/{prefix}-{task}/`. `data/` is purged when its task closes, never archived. The manifest never records a file name under `data/`; customer data in notes stays under each project's own rule.
- Retention: `scratch/` files older than 7 days and `_closed/` folders older than 30 days get a delete row, run by the audit with the rest.
- Enforced at write time by the twin's guard: `code-{slug}/claude/hooks/workdir.py`, hash `s12.hook_sha12`, run by a `PreToolUse` and a `SessionStart` hook in `claude/settings.json` (bandit:project, `references/workdir.md`). The guard's constants mirror `s12`: change both.
- The `SessionStart` hook writes a manifest (paths, dates, counts; no contents), and Claude Code uploads it to `{Domain}/Projects/{slug}/workdir-manifest.json`. No manifest, or one older than 7 days → **unchecked**.
- Fix rows: guard missing or outdated → bandit:project. Layout rows → the project's Claude Code session, targets written `{slug}:{path}`, relative to its working folder. Any move ends by searching `{Domain}/Projects/{slug}/` for the old paths and proposing the note edits.
- Scores **—** for `dev: true` (the repo keeps its own layout) and without `code-{slug}/`.
- **Check:** guard file, hash and hooks from the snapshot (schema 4); the layout from the manifest.

---

## ⚠️ Shoulds

### S6 · Complete footprint

- Every project has a vault folder and a board, or declares `board: none` in its Project Context.
- `code-{slug}/` and `design-{slug}/` don't count as vault folders with no board: they inherit the project's board through the shared slug.
- **Check:** vault folders with no board, and boards with no vault folder.

### S7 · One production version in the vault

- `ai-{slug}/` keeps only the production file, plus a newer not-yet-pasted file under S5.
- Covers both `{prefix}-instructions-v{N}.md` and `{prefix}-prompt-reference-v{N}.md`. No stamp exists for the prompt reference, so its highest `v{N}` is the one that stays.
- Older `v{N}` files move to `{Domain}/_archive/`, mirroring the domain structure: `{Domain}/_archive/Claude/ai-{slug}/`.
- Applies to `ai-{slug}/` only.
- **Check:** count of `v{N}` files per folder.

### S8 · Filename format and settings-only

- `{prefix}-instructions-v{N}.md` and `{prefix}-prompt-reference-v{N}.md`: the short `prefix` from Project Context, integer `N`, flat inside `ai-{slug}/`.
- No full names as the prefix (`cs-notes-`), no semver (`v0.5.0`), no nested subfolders (`ai-fran/claude-ai-settings/`).
- Nothing else in `ai-{slug}/`: any other file (a report, an audit, a note) is ❌, and its fix row moves it to `{Domain}/Projects/{slug}/`.
- The `{prefix}-{type}-v{N}.md` pattern applies to `ai-{slug}/` only. `code-{slug}/` holds, per kind: the Claude Code twin, `CLAUDE.md` plus `claude/settings.json` and `claude/hooks/workdir.py` (no `dev: true`, S12), or the dev mirror, `CLAUDE.md` + `claude/` (`dev: true`). Anything else there is ⚠️. A `.claude/` folder or a `settings.local.json` is ❌: hidden from Obsidian, or a local secrets file.
- **Check:** filename pattern, depth, and no files other than the two settings types; for `code-{slug}/`, its kind's files.

### S11 · Dev mirror

- For `dev: true`: `code-{slug}/` has `CLAUDE.md`, `claude/settings.json` with the `Stop` hook that runs `mirror-check.py`, and `claude/hooks/mirror-check.py` (bandit:project' dev mirror).
- Freshness isn't scored. GitHub's last push lags the repo's real remote, so it can't date the mirror, and nothing else the auditor can read can either. The hook reports a failed copy in the Claude Code session itself.
- **Check:** files and hook from the snapshot (schema 3). Folder missing → bandit:notes creates it; hook or script missing → bandit:project.

### S13–S16 · Vault content of a sprint project

Numbered last so old reports keep their numbers. The conventions are bandit:notes' (§1 Sprint
folders, §4 uniqueness, §5 YAML style); these rules only score them. A **sprint project** is a
`Projects/{slug}/` with at least one `sprint-{name}/` folder at its root. bandit-dev:sprint's local
checker (`check_sprint.py`, a `Stop` hook) enforces the same rules at write time as SP2–SP5; the
audit scores them from the snapshot (schema 5) and never replaces that checker.

| Rule | Holds | Scope | Fix row |
|---|---|---|---|
| **S13 · Sprint briefs** (SP2) | A `type: brief` note whose `board-task` card carries `sprint/{name}` sits in `sprint-{name}/` | Sprint projects | bandit:notes: move it |
| **S14 · One filename** (SP3) | No `.md` filename twice across `Projects/` and `_inbox/`. `README.md` exempt | The domain | bandit:notes: archive the consumed copy on proof, or rename one |
| **S15 · Frontmatter parses** (SP4) | Every note's frontmatter is valid YAML | Sprint projects | bandit:notes: quote the value on the failing line |
| **S16 · Sprint project root** (SP5) | The root holds only the hub `{slug}.md`, `sprint-*` folders and `planning/` | Sprint projects | bandit:notes: move it into `planning/` (or its card's sprint folder) |

- Not a sprint project → S13, S15, S16 score **—**. A schema-4 or older snapshot → **unchecked**.
- **Check:** project files and frontmatter, `_inbox/` filenames and the cards carrying a `sprint/*`
  tag, from the snapshot (schema 5).

---

## 📄 Report lifecycle

- One live report per domain, in the workflow project's own folder: `MyNotes/{Domain}/Projects/{workflow-project}/audit-{YYYY-MM-DD}.md`. Never in a settings folder.
- Per project: the score line, then numbered fix rows `| # | Action | Path | Effect | Why |`. The audit runs every row in the same turn; no approval is asked.
- The snapshot the script scored sits next to the report: `audit-{YYYY-MM-DD}.snapshot.json`. The report is written exactly as the script printed it; its footer carries the rules, snapshot and script hashes.
- **Replay:** `close` and the next audit re-run the script on the saved snapshot. A report that doesn't reproduce byte for byte is invalid.
- **Superseded:** a report with no footer, or built with other rules or script hashes, can't replay. It's archived as-is by the fresh audit that replaces it; its rows are never run.
- When the fixes are done, the report and its snapshot move to `{Domain}/_archive/Projects/{workflow-project}/`.

---

## 🔄 Changing this rulebook

- Changes follow the usual proposal flow, and the user approves them.
- A rule gets added when the same finding turns up in **two or more domains**.
- **Exception:** S9 was added as a preventive rule with the user's explicit approval (2026-09-28), before the finding had appeared in two domains.
- **Exception:** S10 and S11, and the `code-{slug}/` rows, were added as preventive rules with the user's explicit approval (2026-09-28), before the finding had appeared in two domains.
- **Exception:** S10 was widened from workflow projects to every project without `dev: true`, with the twin's optional `claude/settings.json`, with the user's explicit approval (2026-09-29), before the finding had appeared in two domains.
- **Exception:** S12 and the twin's `claude/hooks/workdir.py` were added as preventive rules with the user's explicit approval (2026-09-29), before the finding had appeared in two domains.
- **2026-09-30 · S12 amended** after the first Summitt rollout, with the user's explicit approval: `_backup/` for settings rollback copies, superseded work kept in its task folder, moves update the project's notes, and the `data/` file-name rule scoped to the manifest.
- **2026-09-30 · S11 freshness dropped**, with the user's explicit approval: GitHub's `pushed_at` lagged the CS Notes repo by a month (2026-08-28 in the 2026-09-29 snapshot), so S11 would have passed a stale mirror. `s11.repos` removed from the YAML.
- **Exception:** S13–S16 were added as preventive shoulds with the user's explicit approval (2026-10-09), so bandit-dev:sprint's local checker cites one rulebook, before the findings had appeared in two domains.
- **2026-10-13 · Moved into the bandit-brain-marketplace repo** with the skills (sprint marketplace-v1): this file and `structure-rules.yaml` now live in bandit:audit's `references/`, owner names follow the plugin names (`bandit:tasks`, `bandit:notes`, `bandit:project`), `s12.hook_sha12` follows the renamed guard script, and the YAML gains `paths.stamps`, the stamp ledger's home. No rule changed.
- A rules or script change stops earlier reports from replaying (their footer hashes differ). Close live reports before installing one if their fixes are done; any left live become superseded (**📄 Report lifecycle**), and the next fresh audit archives them.
