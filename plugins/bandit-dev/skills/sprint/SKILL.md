---
name: "sprint"
description: "Plans, runs, debugs and closes a sprint on a dev project's Bandit Brain board: a real sprint in the app, one approved plan in waves, one subagent per wave, evidence in the sprint's notes. Claude Code only. Use to plan a sprint, run its waves, or debug or close it."
---

# 🏃 Sprint

Turns a set of existing cards into one planned, approved sprint that a fresh chat can execute, test
and debug from documents alone. The cards stay on the board; the sprint is a **real sprint** in the
app (its status and its ordered cards) and adds a shared plan, a live ledger and a handover as the
sprint's notes, in the project's notes storage (bandit:notes). No sprint card, no sprint tag. A card with no due date gets the sprint date at commit, so the
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
live, `get_sprints { boardId }`). No command → offer the table and ask which.

| Command | Input | Does | Reference |
|---|---|---|---|
| `plan` | Nothing (every open High card not in a sprint) or a list of card ids | The plan cycle (`references/plan.md`); no list means go straight: state the selection, list open Urgent cards as "not selected", start | `references/plan.md` |
| `execute` | Sprint and wave (`execute {sprint} wave 2`) | One wave, one chat; refuses a wave whose cards depend on an undelivered card; refuses a batch card; moves cards on the Execution board | `references/execute.md` |
| `run` | One or more sprints; `--paced [minutes]` under `/loop` | Every open wave, each in its own subagent (a wave's side-by-side cards one agent each), one wave at a time, each once its dependencies are delivered; checks each wave on the board; stops on a blocker | `references/run.md` |
| `debug` | Sprint | Turns the user's adjustments into verified fixes | `references/debug.md` |
| `release` | Sprint, with the user's deploy word | Preconditions (cards tested, debug done, deploy word, migration tail, backup), then the project's `bandit.yaml` recipe; plugin release for Marketplace cards | `references/release.md` |
| `close` | Sprint | Releasing is optional (no app release: `Release: deferred`, the next release covers it; helpers changed: their release first); once every approval line on the debug card is ticked, sizes and completes the debug card, closes the sprint, archives the sprint's papers | `references/close.md` |

| Read | When |
|---|---|
| `references/templates.md` | Writing a note or card: the shapes, titles and kinds |
| `references/pace.md` | Once at the start of `plan`: one question list per gate, investigate before asking |
| `references/homes.md` | Before a step's first write: homes, write rules, owners |
| `references/gotchas.md` | Once at the start of any command |
| `references/bandit-yaml.md` | The project recipe: every key, section and refusal |

**A wave reads less.** `execute` and a `run` wave agent read what `references/execute.md` → Start lists, and nothing beyond it.

## 🗺️ Gate 0: before step 1

1. **Surface.** Claude Code only. On Claude.ai say so and stop
2. **Project Context** from the repo `CLAUDE.md` (owner: bandit:project): `dev: true`, a `board:`
   project and `prefix`. Missing or not dev → say which and stop. Resolve the board, its columns
   and members **live**. The board must be Technical (sprints live only there)
3. **Sprints on.** `get_sprints { boardId }` answers. `MODULE_DISABLED` → say Sprints is off and who
   turns it on (bandit:tasks `references/errors.md`), and stop
4. **Repo state.** `git branch --show-current`, `git status --short`. Work on the deploy branch → say
   so and keep every commit for the trunk
5. **Tools.** Board server and a browser tool. A missing server stops the run

## 🔄 The plan cycle

Twelve steps, one row each in the ledger's **Plan steps** table, and one row per wave in its **Waves**
table from step 12: the table and every step are in `references/plan.md`. **Mark a step done only
with its evidence in its row**; the checker (SP9, SP10) refuses a done row without it.

## 🔒 Hard rules

1. **The checker is the proof.** `python3 ${CLAUDE_SKILL_DIR}/scripts/check_sprint.py` enforces the
   sprint rules (SP1–SP3, SP6, SP7, SP9–SP11, SP13–SP15) on the project's notes file, built fresh before each run
   (`references/templates.md` → Notes file). Step 12, every wave end, `run` and `close` run it and
   paste its output; a step with a failing check is not done. The plugin's Stop hook runs it too
2. **Gates read the recipe, never guess it:** `scripts/recipe.py` reads the project's `bandit.yaml`; a
   missing key refuses by name. `development` and `main` in the references mean `branches.trunk` and
   `branches.deploy`
3. **The ledger's Status line is current** after every wave, debug, release and close; the sprint's
   status in the app follows it (`references/execute.md` → Sprint status)
4. **A new kind of mistake becomes a checker rule**, not a new sentence here
5. **Rules have owners:** board rules are bandit:tasks', note rules bandit:notes', the Project Context
   bandit:project's. Name the owner; never copy the rule (`references/homes.md`)

## ⚠️ Gotchas

The full list is `references/gotchas.md`: read it once at the start of any command.

## 🚫 Never

- Break a hard rule (bandit:tasks `references/hard-rules.md`): names, tool limits, field limits, where information goes
- Run any command on a project without `dev: true`, or from Claude.ai
- Ask which cards when no list was given
- Complete a card other than as `references/templates.md` → Check lines says (a build card at its delivery, every sub-task ticked; the debug card at `close`), tick an approval line or call anything approved, except `close` doing so for cards the user approved (approval line ticked by the user, or approved in that chat)
- Rewrite a locked Spec without showing old and new and getting a yes
- Write to a card outside the batch and its debug card, or to a sprint but this one; create columns or boards
- Merge into the deploy branch or deploy outside `release`; force-push, or push anything but the trunk (`references/execute.md` → Pushing)
- Run two waves at once, two agents in one working copy, two waves in one chat, a single card, or a wave before the cards it depends on are delivered without the user's say-so
- Tick a sub-task ahead of its work, reopen a completed build card, or treat an urgency remark as approval
- Edit the user's verbatim documents or any rule in `CLAUDE.md` without permission
- Store IDs, write inside the skill folder, or mark a step done without its evidence in the ledger
- Write one card's Spec or plan (`/bandit:tasks spec`, `plan-tech`) or file notes (bandit:notes)
