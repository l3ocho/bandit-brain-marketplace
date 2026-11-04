---
name: "sprint"
description: "Plans, runs, debugs and closes a sprint on a dev project's Bandit Brain board: a real sprint in the app, one approved plan in waves, one subagent per wave, evidence in the sprint folder. Claude Code only. Use to plan a sprint, run its waves, or debug or close it."
---

# 🏃 Sprint

Turns a set of existing cards into one planned, approved sprint that a fresh chat can execute, test
and debug from documents alone. The cards stay on the board; the sprint is a **real sprint** in the
app (its status and its ordered cards) and adds a shared plan, a live ledger and a handover in the
vault. No sprint card, no sprint tag. A card with no due date gets the sprint date at commit, so the
Execution board shows it; a card with its own date keeps it.

> **The standard.** Every gate leaves evidence in the sprint's ledger and in the app's sprint. If this
> chat vanished, the next one could continue from those two places.

> **Stick to the Spec unless the user asks you to be "creative".** A card's Spec is what gets
> built. Planning means planning its execution: analyse the dependencies and address them in the
> plan. Never change, improve or question a Spec. What an investigation finds is settled from the
> Spec, the card's decisions or how the product already works, and goes in the plan; it is not a
> question for the user.

## 🧭 Router

`/bandit-dev:sprint <command> {sprint}`, `{sprint}` the sprint's name on the home board (resolved
live, `get_sprints { boardId }`). A **sprint card** id instead (a card with `Wave n:` sub-tasks) is an
old-way sprint: follow `references/old-way.md`. No command → offer the table and ask which.

| Command | Input | Does | Reference |
|---|---|---|---|
| `plan` | Nothing (every open High card not in a sprint) or a list of card ids | The plan cycle below; no list means go straight: state the selection, list open Urgent cards as "not selected", start | `references/plan.md` |
| `execute` | Sprint and wave (`execute {sprint} wave 2`) | One wave, one chat, in order; refuses a batch card; moves cards on the Execution board | `references/execute.md` |
| `run` | One or more sprints; `--paced [minutes]` under `/loop` | Every open wave, each in its own subagent, strictly in sequence; checks each wave on the board; stops on a blocker | `references/run.md` |
| `debug` | Sprint | Turns the user's adjustments into verified fixes | `references/debug.md` |
| `release` | Sprint, with the user's deploy word | Preconditions (cards tested, debug done, deploy word, migration tail, backup), then the project's `bandit.yaml` recipe; plugin release for Marketplace cards; fills the production handover card when the recipe names one | `references/release.md` |
| `close` | Sprint | Releasing is optional (no app release: `Release: deferred`, the next release covers it; helpers changed: their release first); completes the approved cards, closes the sprint, archives the sprint folder; brings an old-way sprint into the app first | `references/close.md` |

| Read | When |
|---|---|
| `references/templates.md` | Writing a note or card: the shapes and filenames |
| `references/pace.md` | Once at the start of `plan`: one question list per gate, investigate before asking |
| `references/homes.md` | Before a step's first write: homes, write rules, owners |
| `references/gotchas.md` | Once at the start of any command |
| `references/bandit-yaml.md` | The project recipe: every key, section and refusal |
| `references/old-way.md` | A sprint card instead of a sprint: what changes in every command, and its close |

## 🗺️ Gate 0: before step 1

1. **Surface.** Claude Code only. On Claude.ai say so and stop
2. **Project Context** from the repo `CLAUDE.md` (owner: bandit:project): `dev: true`, a `board:`
   project and `prefix`. Missing or not dev → say which and stop. Resolve the board, its columns
   and members **live**. The board must be Technical (sprints live only there)
3. **Sprints on.** `get_sprints { boardId }` answers. `MODULE_DISABLED` → say Sprints is off and who
   turns it on (bandit:tasks `references/errors.md`), and stop. An old-way sprint card skips this step,
   except at its Close (`references/old-way.md`)
4. **Repo state.** `git branch --show-current`, `git status --short`. Work on the deploy branch → say
   so and keep every commit for the trunk
5. **Tools.** Board server, BanditCloud server, a browser tool. A missing server stops the run

## 🔄 The plan cycle

The ledger's **Plan steps** table carries the steps in this order, and its **Waves** table one row
per wave (added at step 12) (`references/templates.md` → Ledger). **Mark a step done only with its
evidence in its row**; the checker (SP9, SP10) refuses a done row without it.

| # | Step | Done when |
|---|---|---|
| 1 | Select and freeze the batch | The sprint created in Planning with the batch as its cards, in no other sprint; the previous open sprint blocks it |
| 2 | Spec completeness check, per card | Every card read against its brief; gaps as fix rows |
| 3 | Close the open questions | The open questions the cards list answered and recorded; none listed: "none", no stop |
| 4 | Size and classify | Every card at most L (XL split), lane and boundaries checked |
| 5 | Cross-card analysis | Migrations, shared files, hidden order, docs regeneration written down |
| 6 | Sequence | Waves with reasons, split with the WBS (`/bandit:plan wbs`, sprint mode) |
| 7 | Write the one technical plan | Plan note filed; every card's Technical plan filled |
| 8 | Risk and rollback | Per card and for the sprint, in the plan |
| 9 | Definition of ready, per card | Each card checked; stage moved on; fix rows for failures |
| 10 | Approval gate | The user's explicit approval, quoted in the ledger |
| 11 | Independent plan review | The `plan-reviewer` agent's record in the sprint folder; majors applied; no blocker open (the only stop) |
| 12 | Commit the sprint | Assignee, undated cards given the sprint date and checked against this week's Sunday, the sprint's expected date, Ready to execute, execution prompt, ledger with `Committed:` and its Waves table, the handover cards the recipe names, the sprint map |

## 🔒 Hard rules

1. **The checker is the proof.** `python3 ${CLAUDE_SKILL_DIR}/scripts/check_sprint.py` enforces the
   vault rules (SP1–SP12). Step 12, every wave end, `run` and `close` run it and paste its output; a
   step with a failing check is not done. The plugin's Stop hook runs it too
2. **Gates read the recipe, never guess it:** `scripts/recipe.py` reads the project's `bandit.yaml`; a
   missing key refuses by name. `development` and `main` in the references mean `branches.trunk` and
   `branches.deploy`
3. **The ledger's Status line is current** after every wave, debug, release and close; the sprint's
   status in the app follows it (`references/execute.md` → Sprint status)
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
- Write to a card outside the batch and its handover cards (old way: and the sprint card), or to a sprint but this one; create columns, boards or tags
- Merge into the deploy branch or deploy outside `release`; force-push, or push anything but the trunk (`references/execute.md` → Pushing)
- Run two wave agents at once, two waves in one chat, a single card, or a wave out of order without the user's say-so
- Move a card to Done by anything but `close`, or treat an urgency remark as approval
- Edit the user's verbatim documents or any rule in `CLAUDE.md` without permission
- Store IDs, write inside the skill folder, or mark a step done without its evidence in the ledger
- Write one card's Spec or plan (`/bandit:tasks spec`, `plan-tech`) or file notes (bandit:notes)
