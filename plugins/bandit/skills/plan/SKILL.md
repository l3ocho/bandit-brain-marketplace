---
name: "plan"
description: "Plans a project in two modes: project (idea → Project Plan → Architecture Document, saved in the vault) and wbs (docs or a batch of cards → a numbered, gap-checked Work Breakdown Structure). Use to plan a project, write its architecture or break it down. Not for loading the board."
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
- Add time or cost estimates to a WBS unless asked, and then as a separate column (never in sprint mode)
- Overwrite a vault file without its etag, delete anything, or store note or task IDs
- Write code
