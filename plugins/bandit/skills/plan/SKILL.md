---
name: "plan"
description: "Plans a project in two modes. project: takes a solo operator from raw idea to a Project Plan and an Architecture Document in the project's vault folder. wbs: turns project docs (plan, architecture, briefs, notes) into a numbered, gap-checked Work Breakdown Structure, with a sprint sub-mode for a batch of existing cards. Use for \"plan a project\", \"new project plan\", \"architecture document\", \"continue planning\", \"create a WBS\", \"break down this project\". Do NOT use to put the WBS on the board (/bandit:tasks load) or to plan a sprint (/bandit-dev:sprint plan)."
---

# 🧭 Plan

One skill, two modes. Each mode's whole procedure lives in its reference file: read it before acting.

## 🧭 Router

`/bandit:plan <mode>`. No mode → offer the table as a numbered list and ask.

| Mode | Does | Reference |
|---|---|---|
| `project` | Idea → Project Plan (Phase 1) → Architecture Document (Phase 2), saved in the project's vault folder; state read from those files | `references/project.md` |
| `wbs` | Project docs → gap analysis → numbered WBS; sprint mode (a batch of existing cards, run by `/bandit-dev:sprint plan`) and migration mode (an existing WBS) | `references/wbs.md` |

The order is `project` → `wbs` → the board (`/bandit:tasks load`, or the dev route on `dev: true`).

## ⚠️ Gotchas

- **Reported 2026-10-09 · A WBS draft stayed in the inbox.** It was saved to `_inbox/` and the final
  went to the project, leaving a leftover. → Save only the final file, in the folder bandit:notes
  names (`references/wbs.md` → **💾 Saving the WBS to the Vault**).

## 🚫 Never

- Put tasks on the board: that's `/bandit:tasks load` (and `/bandit:tasks spec` on dev projects)
- Edit project instructions: that's bandit:project
- Change the WBS output structure `/bandit:tasks load` parses
- Overwrite a vault file without its etag, delete anything, or store note or task IDs
- Write code
