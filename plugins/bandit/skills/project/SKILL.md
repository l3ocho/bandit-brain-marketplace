---
name: "project"
description: "Onboards a project in one approval (vault, board and settings rows), writes and audits its Claude.ai instructions, owns the Project Context block every skill reads, and syncs the instructions to the project's vault settings folder. Use for project setup, instructions, or the Project Context."
---

# 🛠️ Project

The one way a project gets onboarded, and the owner of its instructions and its Project Context.
bandit:notes and bandit:tasks keep their own rules: this skill runs their onboarding steps, never
restates them.

## 🧭 Router

`/bandit:project <command>`. No command → detect the mode (`references/audit.md` → Mode Detection).

| Command | Does | Reference |
|---|---|---|
| `onboard` | New or existing project: interview or audit, then **one proposal** of vault, board and settings rows, executed on approval, instructions handed over to paste | `references/onboard.md` · `references/interview.md` (new) |
| `audit` | Scores this project's instructions against the template; builds the updated version straight away | `references/audit.md` |
| `update {project}` | Targeted change to **another** project's instructions from its vault copy (used by bandit:audit settings rows) | `references/update.md` |
| `sync` | Saves the instructions and reference doc to the vault settings folder | `references/output.md` · `references/vault-storage.md` |
| `instructions` | Generates the project's instructions from the one-page template for its type (workflow, product_service, dev) | `references/instructions.md` |

| Read | When |
|---|---|
| `references/reference-template.md` | **Before anything else**: every section, its audit criteria, the metadata block, the token budget |
| `references/project-context.md` | The Project Context block: keys, format, repo copy, dev mirror, Claude Code twin |
| `references/dev-mirror.md` | Onboarding or auditing a `dev: true` project |
| `references/workdir.md` | A Claude Code twin: onboarding, a twin version change, an S12 row |
| `references/gotchas.md` | Once, before onboarding or an audit |

## 🔒 Hard rules

1. **Length gate first.** Count the instructions' words without the metadata line before any
   interview, audit, update or write; over the tier's budget (never above 1,000) → the trim is row 1
2. **One proposal, approved rows only.** Every finding is a fix row in it; a row that depends on a
   declined row is skipped and reported. End with: *Nothing is created or changed until you answer
   all, a list, or none.* A row bandit:audit runs is already the go: no new proposal
3. **Owners run their own steps.** Vault rows come from bandit:notes, board rows from bandit:tasks'
   `onboard`, loaded and run: never swapped for a quick check of your own
4. **Instructions come from the templates** in `assets/instructions/` (`references/instructions.md`); the
   Claude.ai agent of a `dev: true` project stops at spec
5. **The user pastes.** Instructions are never written into Claude.ai by a tool; the repo `CLAUDE.md` is a
   hand-over to Claude Code, never written by this skill
6. **No IDs, ever.** Names and paths only, resolved live
7. **Vault writes follow bandit:notes write safety**; settings files are versioned, never overwritten,
   moved or deleted (`references/vault-storage.md`)

## ⚠️ Gotchas

The full list is `references/gotchas.md`: read it once before onboarding or an audit.

## 🚫 Never

- Leave a finding without a fix row, or stop an audit at a question when the fix is known
- Create, rename or restructure anything on a board beyond bandit:tasks' onboard rows (one empty
  board, and for `dev: true` its dev board shape)
- Call `project_write` on a path already in the project's doc list, or `project_delete`
- Inject content not gathered from the user, or cut content the user wants to keep (ask first in an audit)
- Write or hand over instructions over the token budget, or duplicate information across sections
- Change `webdav_folder` or the Project Context `prefix:` without an explicit request
- Reference a prompt-reference version that doesn't match the metadata
- Create a vault folder outside an approved row, or move or rename a settings folder (bandit:notes `onboard`'s job)
- Put anything but the two settings files into `Claude/ai-{slug}/`, or add frontmatter to them
- Write to the Nextcloud Notes app, or add a lifecycle block or section
- Write past a file missing from the listing (`references/vault-storage.md`)
