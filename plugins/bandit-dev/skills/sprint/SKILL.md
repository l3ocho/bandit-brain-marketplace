---
name: "sprint"
description: "Plans, runs, debugs and closes a sprint on a dev project's Bandit Brain board: one approved plan in waves, one subagent per wave, evidence on the sprint card and in the sprint folder. Claude Code only. Use to plan a sprint, run its waves, or debug or close it."
---

# 🏃 Sprint

Turns a set of existing cards into one planned, approved sprint that a fresh chat can execute, test
and debug from documents alone. The cards stay on the board; the sprint adds a sprint card, a shared
plan, a live ledger and a handover.

> **The standard.** Every gate leaves evidence on the sprint card and in the sprint folder. If this
> chat vanished, the next one could continue from those two places.

## 🧭 Router

`/bandit-dev:sprint <command> {sprint card}`. No command → offer the table and ask which.

| Command | Input | Does | Reference |
|---|---|---|---|
| `plan` | Nothing (every open High card not in a sprint) or a list of card ids | The plan cycle below; no list means go straight: state the selection, list open Urgent cards as "not selected", start | `references/plan.md` |
| `execute` | Sprint card and wave (`execute {sprint card} wave 2`) | One wave, one chat, in order; refuses a batch card; moves cards on the Execution board | `references/execute.md` |
| `run` | One or more sprint cards; `--paced [minutes]` under `/loop` | Every open wave, each in its own subagent, strictly in sequence; checks each wave on the board; stops on a blocker | `references/run.md` |
| `debug` | Sprint card | Turns the user's adjustments into verified fixes | `references/debug.md` |
| `release` | Sprint card, with the user's deploy word | Preconditions (cards tested, debug done, deploy word, migration tail, backup), then the project's `bandit.yaml` recipe; plugin release for Marketplace cards; fills the deployment handover card | `references/release.md` |
| `close` | Sprint card | Refuses without a release line (unless "close without release"); completes the approved cards and the sprint card, archives the sprint folder | `references/close.md` |

| Read | When |
|---|---|
| `references/templates.md` | Writing a note or card: the shapes and filenames |
| `references/pace.md` | Once at the start of `plan`: one question list per gate, investigate before asking |
| `references/homes.md` | Before a step's first write: homes, write rules, owners |
| `references/gotchas.md` | Once at the start of any command |

## 🗺️ Gate 0: before step 1

1. **Surface.** Claude Code only. On Claude.ai say so and stop
2. **Project Context** from the repo `CLAUDE.md` (owner: bandit:project): `dev: true`, a `board:`
   project and `prefix`. Missing or not dev → say which and stop. Resolve the project, its columns
   and members **live**
3. **PM column.** The sprint card lives there. Missing → one fix row (add it right after Backlog),
   asked once with the opening line. Never created silently
4. **Repo state.** `git branch --show-current`, `git status --short`. Work on the deploy branch → say
   so and keep every commit for the trunk
5. **Tools.** Board server, BanditCloud server, a browser tool. A missing server stops the run

## 🔄 The plan cycle

The sprint card carries the steps as sub-tasks in this order, then one sub-task per wave (added at
step 12). **Tick a step only when its evidence is on the card**, one comment per step.

| # | Step | Done when |
|---|---|---|
| 1 | Select and freeze the batch | Sprint card in PM, the cards block it, the previous open sprint card blocks it, none in another sprint |
| 2 | Spec completeness, per card | Every card read against its brief; gaps as fix rows |
| 3 | Close the open questions | One interview answered and recorded |
| 4 | Size and classify | Every card at most L (XL split), lane and boundaries checked |
| 5 | Cross-card analysis | Migrations, shared files, hidden order, docs regeneration written down |
| 6 | Sequence | Waves with reasons, split with the WBS (`/bandit:plan wbs`, sprint mode) |
| 7 | Write the one technical plan | Plan note filed; every card's Technical plan filled |
| 8 | Risk and rollback | Per card and for the sprint, in the plan |
| 9 | Definition of ready, per card | Each Spec reconciled; stage moved on; fix rows for failures |
| 10 | Approval gate | The user's explicit approval, quoted on the card |
| 11 | Independent plan review | The `plan-reviewer` agent's record in the sprint folder; majors applied; no blocker open (the only stop) |
| 12 | Commit the sprint | Tag, assignee, due date, size, execution prompt, ledger with `Committed:`; one sub-task per wave; the handover card |

## 🔒 Hard rules

1. **The checker is the proof.** `python3 ${CLAUDE_SKILL_DIR}/scripts/check_sprint.py` enforces the
   vault rules (SP1–SP7). Step 12, every wave end, `run` and `close` run it and paste its output; a
   step with a failing check is not done. The plugin's Stop hook runs it too
2. **Gates read the recipe, never guess it:** `scripts/recipe.py` reads the project's `bandit.yaml`; a
   missing key refuses by name. `development` and `main` in the references mean `branches.trunk` and
   `branches.deploy`
3. **The sprint card's section 1 Status line is current** after every wave, debug, release and close
4. **A new kind of mistake becomes a checker rule**, not a new sentence here
5. **Rules have owners:** board rules are bandit:tasks', vault rules bandit:notes', the Project Context
   bandit:project's. Name the owner; never copy the rule (`references/homes.md`)

## ⚠️ Gotchas

The full list is `references/gotchas.md`: read it once at the start of any command.

## 🚫 Never

- Run any command on a project without `dev: true`, or from Claude.ai
- Ask which cards when no list was given
- Mark a card complete or call anything approved, except `close` completing cards the user approved in that chat
- Rewrite a locked Spec without showing old and new and getting a yes
- Write to a card outside the batch, the sprint card and its handover card; create columns, projects or tags other than `sprint/{name}`
- Merge into the deploy branch or deploy outside `release`; force-push, or push anything but the trunk (`references/execute.md` → Pushing)
- Run two wave agents at once, two waves in one chat, a single card, or a wave out of order without the user's say-so
- Move a card to Done by anything but `close`, or treat an urgency remark as approval
- Edit the user's verbatim documents or any rule in `CLAUDE.md` without permission
- Store IDs, write inside the skill folder, or tick a step without its evidence on the card
- Write one card's Spec or plan (`/bandit:tasks spec`, `plan-tech`) or file notes (bandit:notes)
