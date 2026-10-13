---
name: "tasks"
description: "Works the Bandit Brain task board: capture, inbox triage, today, the week, recurring rules, audits, email to tasks, WBS load and, on dev projects, the card workflow (spec, plan-tech, stage). Use for any request to add, file, schedule, complete or review tasks."
---

# 🗂️ Tasks

One skill for the board. The router names each command's reference file: **read it before acting**.

> **The sleep test.** Go to bed knowing everything has been *addressed*: captured, sized correctly,
> and sitting somewhere it will surface on its own. Nothing floating in your head as the only copy.

## 🧭 Router

`/bandit:tasks <command> [args]`. No command → offer this table as a numbered list and ask which.
Natural language always works; a request that spans two surfaces reads both files.

| Surface | Commands | Reference | Owns |
|---|---|---|---|
| 📥 Triage | `triage` `inbox` | `references/triage.md` | Inbox board, leaving the inbox. **The only holder of `move_task` and `bulk_move_tasks`** |
| ▶️ Execution | `today` `doing` `done` `bump` | `references/execution.md` | The six Execution columns, dependency gates, the five-item cap |
| 📅 Week | `week` `review` | `references/week.md` | Week board, workload, projections, dating the week, `skip_occurrence` |
| ✍️ Capture | `capture` | `references/capture.md` | Task creation, brain dumps, the whole repeat-rule lifecycle |
| 🧹 Audit | `audit` | `references/audit.md` | Hygiene and structure checks, `archive_project` |
| 📧 Email | `email` | `references/email.md` | Gmail → proposals only, zero writes |
| 🏗️ Load | `load` | `references/load.md` | WBS → a new Deliverable project |
| 🚀 Onboard | `onboard` | `references/onboard.md` | The board step of project onboarding, run by bandit:project |
| 🛠️ Dev | `spec` `plan-tech` `stage` `pick-ready` | `references/dev.md` · `references/dev-workflow.md` | Dev projects only: lanes, stages, card sections · the card procedures |

| Also read | When |
|---|---|
| `references/scope.md` | Before every write: resolve the `board:` scope |
| `references/board.md` | Taxonomy, right-sizing, planning variables, tags, bulk writes, card descriptions, sub-tasks, safety, refusals, what lies outside this skill |
| `references/errors.md` | A call comes back `{ ok: false, code, … }` |
| `references/gotchas.md` | Once, at the start of a session that writes to the board |

🚦 **Dev gate.** The Dev surface, `lane/*` / `stage/*` rules, card boundaries and dev audit checks
apply **only** when the Project Context has `dev: true`. Without it a Dev command says the project
isn't a dev project and stops. Surface roles: `references/dev-workflow.md` → Surface.

**Only Load and Onboard create projects.** Only Load, and the dev board shape's `PM` step, create columns.

## 🔒 Hard rules

1. 📅 **Date is king.** A due date is the single strongest signal on a task
2. 🅿️ **Parked ≠ dated.** A parked task given a due date moves into the project's first column, so
   a parked task never holds a date. The date is set last, when a card leaves the inbox
3. 🔀 **Move is triage-only.** `move_task` belongs to Inbox review. It is not a general verb
4. 👻 **Projections aren't rows.** Week-board items may be recurring projections with no task record
5. 🗣️ **Never say bare "backlog."** Say **project Backlog** or **Execution Backlog**
6. 🗺️ **Read anywhere, write inside the declared `board:` only** (`references/scope.md`). Names
   resolve live with `list_projects`; no stored ID, ever. A name that doesn't resolve → stop
7. 🏷️ **`set_task_tags` replaces the whole set:** `get_task`, merge, then write (`references/board.md` → Tags)
8. 📝 **Descriptions are block-tag HTML, read back after every write** (`references/board.md` → Card descriptions)
9. 🛡️ **Write freely, confirm destructive.** Every `delete_*` is confirmed; archive before delete
   (`references/board.md` → Safety)

## ⚠️ Gotchas

The full list is `references/gotchas.md`: read it once at the start of a session that writes.

## 🚫 Never

- Design a board freehand inside a procedure: board structure is a conversation (`references/board.md` → Outside this skill)
- Retry a variant of a refused call, or round a rule outside the vocabulary to the nearest fit
- Resize a task silently, in either direction: propose
- Write the WBS (`/bandit:plan wbs`), plan notes (bandit:notes) or plan a sprint (`/bandit-dev:sprint plan`)
- Praise, nag or perform urgency: dry and direct, counts and proposals
