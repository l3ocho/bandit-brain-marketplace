---
name: "skill"
description: "Builds, evaluates and lints the marketplace skills: create or improve a skill, run evals with baselines, optimize a description's triggering, and run the house gate (lint) over skills. Use for \"make a skill\", \"lint the skills\" or \"make it house-standard\". Not for prompts or project instructions."
---

# 🛠️ Skill

Creates skills and improves them in a loop: draft, run test prompts, evaluate with the user, rewrite,
repeat. Forked from the upstream skill creator: the reference files keep its text so upstream
updates merge as a diff; this page is the house layer.

## 🧭 Router

`/bandit-maker:skill <command>`. Figure out where the user is in the loop and jump in there.

| Command | Does | Reference |
|---|---|---|
| `create` | Capture intent, interview, write the `SKILL.md` and its test prompts | `references/create.md` |
| `eval` · `improve` | Run test prompts with and without the skill, grade, show the viewer, rewrite from feedback | `references/eval.md` |
| `describe` | Optimize the description's triggering with a train/test eval set | `references/description.md` |
| `lint` | The house gate over skills; every failure a fix row | `references/lint.md` |
| `package` | Build a `.skill` file (`scripts/package_skill.py`, lint first) | `references/description.md` → Package and Present |

| Read | When |
|---|---|
| `references/rulebook.md` | Before any draft: the house standard (R1–R15). It wins over this page |
| `references/surfaces.md` | On Claude.ai or in Cowork: what changes without subagents or a display |
| `references/schemas.md` | Writing `evals.json`, `grading.json` or benchmark files |
| `agents/grader.md` · `agents/comparator.md` · `agents/analyzer.md` | Spawning a grader, a blind comparison, or an analysis |

## 🏠 House standard

Every skill built or edited here passes `references/rulebook.md`. In this marketplace also:

- **Description ≤ 300 characters** (L1): what the skill does and when to use it, at most one
  "not for X" clause naming the neighbour. The rulebook's 1,024 is the save limit, not the target
- **`SKILL.md` ≤ 150 lines** (L2): a router table (command → `references/{command}.md`) plus hard
  rules; each procedure in its reference file
- **One home per rule** (L3), **no project details** (L4): names, IDs, paths come from the Project
  Context or `bandit.yaml`
- **Short names:** the plugin namespace is the brand (`bandit:tasks`); a skill's name never repeats it
- **`## ⚠️ Gotchas`** (one line per real failure, "what went wrong → what to do instead"; a new skill
  starts with `None logged yet.`) and a **`## 🚫 Never`** section; an emoji-anchored H2 per section
- **The gate is code:** `scripts/house_lint.py` and the repo's `scripts/check_repo.py` must pass
  before a commit. Marketplace skills ship by commit to the repo, never as an uploaded copy
- **Command names are unique (R15)** across every skill in `plugins/*/skills/`

## ⚠️ Gotchas

- Ran `quick_validate.py` inside the installed skill folder and left `__pycache__` there → run scripts from a copy (or `python3 -B`), and delete any stray cache.
- Sent a skill-update card with a short summary as `description` → it replaced the full trigger description; always send the complete text.
- Built a new skill with plain H2s, no Gotchas and no not-for line → apply the 🏠 House standard before the first draft goes to Leo.

## 🚫 Never

- Run scripts inside an installed skill folder
- Name an updated skill `-v2`, or add version lines, version folders or changelogs inside a skill folder
- Send a card whose `description` is anything but the full trigger text
- Write a prompt for Claude Code or an agent, or Claude.ai project instructions (bandit:project)
