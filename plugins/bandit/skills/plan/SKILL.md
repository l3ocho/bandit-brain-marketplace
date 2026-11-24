---
name: "plan"
description: "Plans a project in two modes: project (idea → Project Plan → Architecture Document, saved as notes) and wbs (docs or a batch of cards → a numbered, gap-checked Work Breakdown Structure). Use to plan a project, write its architecture or break it down. Not for loading the board."
---

# 🧭 Plan

One skill, two modes. Each mode's whole procedure lives in its reference file: read it before acting.

## 🧭 Router

`/bandit:plan <mode>`. No mode → offer the table as a numbered list and ask.

| Mode | Does | Reference |
|---|---|---|
| `project` | Idea → Project Plan (Phase 1) → Architecture Document (Phase 2), saved as notes in the project's place through bandit:notes; state read from those notes | `references/project.md` |
| `wbs` | Project docs → gap analysis → numbered WBS; sprint mode (a batch of existing cards, run by `/bandit-dev:sprint plan`) and migration mode (an existing WBS) | `references/wbs.md` |

The order is `project` → `wbs` → the board (`/bandit:tasks load`, or the dev route on a Technical home board).

## ⚠️ Gotchas

- **Reported 2026-10-09 · A WBS draft stayed in the inbox.** It was saved to the inbox and the final
  went to the project, leaving a leftover. → Save only the final note, in the place bandit:notes
  names (`references/wbs.md` → **💾 Saving the WBS as a Note**).

## 🚫 Never

- Break a hard rule (bandit:tasks `references/hard-rules.md`): names, tool limits, field limits, where information goes
- Put tasks on the board: that's `/bandit:tasks load` (and `/bandit:tasks spec` on dev projects)
- Edit project instructions: that's bandit:project
- Change the WBS output structure `/bandit:tasks load` parses
- Add time or cost estimates to a WBS unless asked, and then as a separate column (never in sprint mode)
- Replace a note without reading it first, write one other than through bandit:notes, delete anything, or store note or task IDs
- Write code
