---
name: "project"
description: "Onboards a project in one approval (hub note, board and settings rows), writes and audits its one instructions file (Claude.ai instructions, or CLAUDE.md and .claude/ in Claude Code), and owns the Project Context block every skill reads. Use for project setup, instructions, or the Project Context."
---

# 🛠️ Project

The one way a project gets onboarded, and the owner of its instructions and its Project Context.
A project has **one** configuration, on the surface it runs on. bandit:notes and bandit:tasks keep
their own rules: this skill runs their onboarding steps, never restates them.

## 🧭 Router

`/bandit:project <command>`. No command → detect the mode (`references/audit.md` → Mode Detection).

| Command | Does | Reference |
|---|---|---|
| `onboard` | New or existing project: interview or audit, then **one proposal** of notes, board and settings rows, executed on approval | `references/onboard.md` · `references/interview.md` (new) |
| `audit` | Scores this project's instructions and settings against the template; builds the updated version straight away, as rows | `references/audit.md` |
| `instructions` | Generates the project's instructions from the one-page template for its type (workflow, product_service, dev) | `references/instructions.md` |

| Read | When |
|---|---|
| `references/surfaces.md` | **First**: which surface this project runs on, where its instructions and settings live, workflow agent or technical one, what this skill may write |
| `references/reference-template.md` | Before an interview or an audit: every section, its audit criteria, the token budget |
| `references/project-context.md` | The Project Context block: keys, format, the one copy |
| `references/output.md` | Before any deliverable: the instructions, the reference doc and the two reference notes |
| `references/workdir.md` | A project in Claude Code without `dev: true`: its working-folder guard, onboarding, an S12 row |
| `references/gotchas.md` | Once, before onboarding or an audit |

## 🔒 Hard rules

1. **Length gate first.** Count the instructions' words before any interview, audit or write; over
   the tier's budget (never above 1,000) → the trim is row 1
2. **One proposal, approved rows only.** Every finding is a fix row in it; a row that depends on a
   declined row is skipped and reported. End with: *Nothing is created or changed until you answer
   all, a list, or none.* A row bandit:audit runs is already the go: no new proposal
3. **This skill proposes; the user decides.** Every change to a project's instructions or
   settings is a row showing the file and the exact change. Nothing is written, in the folder or
   anywhere else, before the yes
4. **Owners run their own steps.** Notes rows come from bandit:notes, board rows from bandit:tasks'
   `onboard`, loaded and run: never swapped for a quick check of your own
5. **Instructions come from the templates** in `assets/instructions/` (`references/instructions.md`)
6. **One configuration.** A project runs on one surface and has one instructions file. A second
   copy for another surface is never created (`references/surfaces.md`)
7. **No IDs, ever.** Names and paths only, resolved live

## ⚠️ Gotchas

The full list is `references/gotchas.md`: read it once before onboarding or an audit.

## 🚫 Never

- Leave a finding without a fix row, or stop an audit at a question when the fix is known
- Create, rename or restructure anything on a board beyond bandit:tasks' onboard rows (one empty
  board, and for `dev: true` its dev board shape)
- Write the user's own preferences: `~/.claude/`, a `settings.local.json`, a permission mode, a
  model choice, or anything outside the project's folder
- Remove or loosen a permission rule or a hook the project already has; a row may only add
- Write a file in the folder without a row the user approved for exactly that file
- Write instructions into Claude.ai with a tool: on that surface the user pastes
- Inject content not gathered from the user, or cut content the user wants to keep (ask first in an audit)
- Write or hand over instructions over the token budget, or duplicate information across sections
- Change the Project Context `project:` or `prefix:` without an explicit request
- Keep a copy of the instructions or the reference doc anywhere but the two reference notes
  (`references/output.md`)
