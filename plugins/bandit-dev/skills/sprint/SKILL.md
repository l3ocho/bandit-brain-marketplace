---
name: "sprint"
description: "Plans, executes, debugs and closes a sprint on a dev project's BanditBrains board. Invoked as /bandit-dev:sprint plan [cards], /bandit-dev:sprint execute {sprint card} wave N (one wave per chat, cards moved across the Execution board), /bandit-dev:sprint run {sprint card} [more sprint cards] (every wave of one or more sprints, one subagent per wave, in sequence), /bandit-dev:sprint debug {sprint card} and /bandit-dev:sprint close {sprint card}. Plan: with no list it takes every open High-priority card on the board; with a list (BB-12 BB-15 …) it takes exactly those. Creates the sprint card in the PM column (cards as blockers, 11 gate sub-tasks), checks every Spec, runs one interview, sizes and splits, sequences waves, splits waves with the WBS, writes the shared plan with risks and rollback, readies, tags, assigns and dates the cards, and writes the execution prompt and ledger. Proactive: investigates before asking. Use when Leo says plan a sprint, sprint planning, group these cards, take all high priority cards or put these cards in a sprint. Claude Code only. Do NOT use to write one card's Spec or plan (bandit:tasks spec, plan-tech), to pick cards for the week (bandit:tasks plan, sprint) or to file notes (bandit:notes)."
---

# 🏃 Bandit Sprint

Turns a set of existing cards into one planned, approved sprint that a fresh chat can execute, test and debug from documents alone. The cards stay on the BanditBrains board; the sprint adds a sprint card, a shared plan, a live ledger and a handover.

> **The standard.** Every gate leaves evidence on the sprint card and in the sprint folder. If this chat vanished, the next one could continue from those two places.

> **The checker is the proof.** `python3 ${CLAUDE_SKILL_DIR}/scripts/check_sprint.py` enforces the vault rules as code (SP1 records present, SP2 briefs inside their sprint folder, SP3 no duplicate filenames, SP4 valid frontmatter, SP5 nothing but the hub note, the sprint folders and `planning/` at a sprint project's root, SP6 one brief per card outside the archive). Plan step 11, every wave end, `run` and `close` run it and paste its output; a step with a failing check is not done and is not ticked. A Stop hook runs it too, so a session that touched the vault cannot end with a failure. A new kind of mistake becomes a new checker rule, not a new sentence here.

---

## 🧭 Command

`/bandit-dev:sprint plan [cards]`, `/bandit-dev:sprint execute {sprint card} wave N`, `/bandit-dev:sprint run {sprint card} […]`, `/bandit-dev:sprint debug {sprint card}`, `/bandit-dev:sprint close {sprint card}`. With no command, offer the plan table below and the three commands, and ask which.

| Mode | Input | Selects |
|---|---|---|
| **All high** | `plan` and nothing else | Every **open** card on the project board with priority **High**, excluding archived cards and cards already in a `sprint/*` |
| **List** | `plan BB-12 BB-15 …` (short ids or ids) | Exactly those cards. Resolve each with `get_task`; an unknown id stops the run and is named |

**No list means go straight.** Do not ask which cards. State the selection in the opening line (count, ids, titles), list any open Urgent cards as "not selected", and start. Leo corrects by replying.

| Command | Input | Does | Reference |
|---|---|---|---|
| `execute` | The sprint card and the wave (`execute BB-67 wave 2`) | Runs that wave, **one wave per chat**, in order, refusing a batch card; moves cards across the Execution board, ticks sub-tasks, parks finished cards in Stand By | `references/execute.md` |
| `run` | One or more sprint cards (`run BB-67`, `run BB-67 BB-72`); `--paced [minutes]` under `/loop` for an unattended night | Runs **every open wave**, each in its **own subagent**, strictly one after another, sprint by sprint; checks each wave on the board before the next; stops on a blocker; never starts debug or close | `references/run.md` |
| `debug` | The sprint card | Reads the sprint documents and code changes, turns Leo's adjustments into verified fixes | `references/debug.md` |
| `close` | The sprint card | Completes the approved cards and the sprint card, archives the sprint folder | `references/close.md` |

Read the reference for the command you run before acting. For `plan`, read `references/plan.md`: it holds the 11 steps, their gates and what each step records. `references/templates.md` holds the note and card shapes. `references/gotchas.md` holds the full failure list: read it once at the start of a run.

---

## 🗺️ Gate 0: before step 1

1. **Surface.** Claude Code only: `stage … planned`, plan notes and Spec edits belong to it (bandit:tasks `references/dev.md`, Surface). On Claude.ai say so and stop.
2. **Project Context.** Read `## 🧭 Project Context` from the repo `CLAUDE.md` (owner: bandit:project). Need `dev: true`, a `board:` project and `prefix`. Missing or not dev: say which and stop. Resolve the project, its columns and members **live** with `list_projects` and `list_project_members`.
3. **PM column.** The sprint card lives in the project's `PM` column. Missing: one fix row (add the column right after Backlog, two calls), asked once with the opening line. Never create it silently.
4. **Repo state.** `git branch --show-current` and `git status --short`. Planning writes docs only; if work sits on `main`, say so and keep every commit for `development`.
5. **Tools.** Board server, BanditCloud server, and which browser tool exists. A missing server stops the run before step 1.

---

## 🔄 The cycle

The sprint card carries the steps as its sub-tasks, in this order, followed at the very end by one sub-task per wave (added at step 11). **Tick a step only when its evidence is on the card**, and add one comment per step. Wave sub-tasks are ticked later, as each wave is delivered and verified.

| # | Step | Done when |
|---|---|---|
| 1 | Select and freeze the batch | Sprint card exists in PM, the cards block it, no card is in another sprint, outside blockers noted |
| 2 | Spec completeness check, per card | Every card read against its brief; gaps listed as fix rows |
| 3 | Close the open questions | One interview answered and recorded; follow-ups asked |
| 4 | Size and classify | Every card at most L (XL split), lane and boundaries checked |
| 5 | Cross-card analysis | Migrations, shared files, hidden order, docs regeneration written down |
| 6 | Sequence | Waves with reasons; no parallel conflicts |
| 7 | Write the one technical plan | Plan note filed; every card's Technical plan filled |
| 8 | Risk and rollback | Per card and for the sprint, in the plan |
| 9 | Definition of ready, per card | Each Spec reconciled with the decisions; stage moved on; fix rows for failures |
| 10 | Approval gate | Leo's explicit approval, quoted on the card |
| 11 | Commit the sprint | Sprint tag, assignee, due date, size, execution prompt and ledger written; one sub-task per wave added at the end of the sprint card |

---

## 🎙️ Interview and pace

- **Gather before asking.** Run the read-only investigations first (below), so every question arrives with an answer to approve.
- **One consolidated list per gate**, grouped by card, each item with a recommendation. "Go with the recommendations" is a valid answer and applies to the whole list. Ask follow-ups only for what the answers raise.
- **Never re-ask.** Before any question, check the chat, the cards and the ledger for the answer (a date, a decision, an approval). Use it and record it.
- **Short reports.** After each step: what was found, what was done, what is next, in a few lines. No waiting between steps that need no input; stop only at steps 3, 9 and 10.
- A decision that opens a **large new requirement** is parked as a card outside the sprint, with the rule recorded; ask one yes or no whether it joins. Leo's word that a card stays in the sprint is final.

---

## 🛰️ Proactive means

- **Investigate in parallel, read-only.** One investigator per card for open questions (what exists in code, what the card claims, what is missing); at most one live-browser check at a time, told to write nothing on existing data (planning only; see Test data in `references/plan.md`). Brief them with the card's Spec and the report shape in `references/plan.md`.
- **Spot-check decisive claims** before they enter a card or plan; an unconfirmed claim goes under "Verify first".
- **Anticipate the usual traps** at the step where they bite: XL at sizing, stale Specs at step 9, migration numbers at step 5, a card edited by someone else before any rewrite.
- **Surface problems as fix rows**, numbered, each with the action, the target, the owner and the recommendation; one answer approves all, a list or none (the house rule for findings).
- **Offer the next move** at the end of every step in one line.

---

## 🧱 Homes and writes

| Record | Home |
|---|---|
| Sprint card | The project's `PM` column, title "Sprint {Name}", tag-free; blockers are the batch |
| Sprint folder | `Projects/{slug}/sprint-{name}/` in the domain vault |
| Plan, briefs, execution prompt, ledger, handover report | The sprint folder; filenames in `references/templates.md` |
| Sprint tag | `sprint/{name}` on the batch cards |

The sprint folder and its record types are owned by bandit:notes (conventions §1, Sprint folders, and §4 filenames). This skill follows them and restates none of them; `references/templates.md` mirrors the filenames only for convenience.

**Leftovers.** A document used only to make another one (an inbox brief or spec draft once its card and filed brief exist, a WBS draft once the WBS is filed, a feedback note once applied, a brief whose card was deleted) is archived to `_archive/` with the bandit:notes stamps, or deleted on Leo's word, in the same step that consumed it. Nothing consumed stays in `_inbox/` or at a project root. **Only on proof**: the successor exists and was read (the filed brief, the filed WBS, the applied change). A note is never archived because it looks done or because its card is missing; if unsure, it stays.

**Writes.** New notes fail closed; edits read first and carry the etag; never force. A card description is read with `get_task` immediately before it is written, and a Spec change is shown old and new and applied only on Leo's yes (bandit:tasks `references/dev.md`, Spec lock). Tags are read and merged before `set_task_tags`. Board writes touch only the batch cards and the sprint card. Nothing is stored inside this skill's folder.

---

## 🧩 Owners

| Need | Read it in |
|---|---|
| Lanes, stages, card sections, Spec lock, boundaries, `stage`, `spec` | bandit:tasks `references/dev.md` |
| Tags, handler and energy tags, five hard rules | bandit:tasks `SKILL.md` |
| Vault folders, filenames, frontmatter, etag writes, inbox rules | bandit:notes `SKILL.md` and `references/conventions.md` |
| Project Context keys | bandit:project |

---

## ⚠️ Gotchas

Ten of the most costly. The full list is `references/gotchas.md`.

- Asked for the sprint date after Leo had set every due date → scan the chat and cards before any question.
- Sent a second long question list after the first → one list per gate with recommendations; follow up only on what the answers raise.
- Followed a side requirement into a large investigation inside the sprint → park it as a card outside, record the rule, ask one yes or no.
- Sized a card XL and found the L ceiling at the gate → check the boundary at sizing and split there.
- Specs kept answered questions because decisions lived in comments → collect decisions at step 3, reconcile each Spec once at step 9.
- Rewrote a description from memory after someone edited the Spec → `get_task` immediately before every write.
- `set_task_tags` replaced the whole set → read, merge, then write.
- Sub-tasks added in parallel came out reversed → add one at a time, or reorder, then read back.
- A live-check agent clicked a control that writes to the dev database → at planning, brief investigators: open and cancel, write nothing on existing data.
- An execution-time UI check skipped its key case because the dev database had no folder, and the report called it normal → never acceptable. The verifier creates its own test data, runs the case and cleans up; "not exercised for lack of data" fails the wave.
- Work sat on `main` and the stop hook demanded a commit → check the branch first; docs commit on `development` only.

---

## 🚫 Never

- Run any command on a project without `dev: true`, or from Claude.ai.
- Ask which cards when no list was given.
- Mark a card complete or call anything approved, except `close` completing cards Leo approved in that chat; delivered means awaiting Leo's test.
- Rewrite a locked Spec without showing old and new and getting a yes.
- Write to a card outside the batch and the sprint card; create columns, projects or tags other than `sprint/{name}`.
- Merge into `main`, deploy, force-push, or push anything but `development`. Pushing `development` is allowed as `references/execute.md` → Pushing `development` says.
- Run two wave agents at once, or two waves in one chat, run a single card, run a wave out of order without Leo's say-so, or move a card to Done by anything but `close`.
- Treat an urgency remark as approval of the plan.
- Edit Leo's verbatim documents or any rule in `CLAUDE.md` without permission.
- Copy a rule from bandit:tasks or bandit:notes into this skill; name the owner.
- Store IDs, or write inside the skill folder.
- Tick a step without its evidence on the card.

## 🗣️ Tone

Dry and direct. Short step reports, numbered fix rows, one list of questions per gate, evidence over reassurance. When Leo is frustrated, fix the thing and say what changed.
