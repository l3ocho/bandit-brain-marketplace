# ⚠️ Gotchas, full list

Part of `bandit-dev:sprint`. Read once at the start of a run. Each line: what went wrong → what to do instead. Every one happened in a real planning chat.

Contents: Interview and pace · Scope · Cards and Specs · Agents and checks · Notes and vault · Repo and hooks · Process · Execute, debug, close · Owner changes proposed

## Interview and pace

- Asked for the sprint date after the user had set every due date → scan the chat, cards and ledger before any question; use and record what is there.
- Opened with eleven questions and then a second list → one consolidated list per gate, grouped by card, each with a recommendation; "go with the recommendations" applies to all; ask only follow-ups.
- Buried a one-sentence rule (shared Finance account, equal rights, privacy even from the admin) under option questions → restate the rule in the user's words first, confirm it in one line, then check where the code differs.
- Left a task as "still to do" that an earlier instruction already covered → close it from the instruction.
- Took "approved" as a gate and moved cards to ready without saying so → state the reading in one line when a vague approval is taken to mean a gate.

- Asked the user things the repo and the cards already answered, and labelled questions with invented codes (Q2, A3) → read first, ask only what nothing can answer, in plain words.
- A new chat acted on an old memory note instead of the ledger → the ledger and the board win over memory; read them first.

## Scope

- Slipped invented rules (a move-out guard, a child comment ban, a rule exception) into "applied defaults" the user never saw, then asked about them for an hour → add nothing not asked for; anything code forces is a table row that differs, before it is written anywhere.
- Put decisions in three formats (old/new Spec lines, "calls", numbered fix rows) with cross-references → one decision table, `Issue | Recommendation | Different from what you requested? | If yes, how?`, plain words, no numbers.
- Answered "what is missing" with sections, housekeeping and recaps → the missing list only.
- Ran the same greps while two investigators were already on it → once delegated, wait for the reports.
- Followed a side requirement (Finance sharing) into a large investigation and a new XL card inside the sprint → park the new requirement outside the sprint, record the rule, ask one yes or no; a card the user requires in the sprint stays in.
- Offered a "recommended" answer that contradicted an earlier one without saying so → when a later finding changes a recommendation, say it changed and why.

## Cards and Specs

- Sized a card XL and found the L ceiling at the gate → check the boundary at step 4 and split then; the new card joins the sprint and blocks it.
- Specs still listed answered questions because the decisions lived in comments and the Spec was locked → collect decisions at step 3 and reconcile each Spec once at step 9, old and new in one table.
- Rewrote descriptions from memory after someone edited the Spec (a parenthetical on the `Brief:` line) → `get_task` right before every write; on `SPEC_LOCKED` re-read, never override to get past it.
- Wrote `Brief:` lines with a folder in brackets → filename only.
- `set_task_tags` replaced the whole set → read, merge, write.
- Sub-tasks added in parallel came out reversed → add one at a time or reorder, then read back.
- A due date given as "tomorrow" → convert to an absolute date from the session date and write it once.
- A card's `Scope out` stated a wrong fact (new Finance accounts "private by default") → spot-check any factual line a card makes against code.

## Agents and checks

- A live-check agent clicked a control that writes (a column sort) in the dev database → at planning, brief investigators: open and cancel, write nothing on existing data, report what could not be checked; name the known write controls. This is planning-only.
- Sprint Privacy A wave 1: the execution prompt copied "live checks write nothing", so the ui-verifier skipped a card's key case (a folder with projects) because the dev database had none, and the report presented it as normal → execution prompts say the verifier creates and removes its own test data; a case not run for lack of data is a failed check.
- Investigator reports mixed verified facts and guesses → require "not verified" markers and spot-check the decisive facts before they enter a card.
- The browser tool the brief named was not available to the sub-agent → state the tools that exist; accept an equivalent and note it.
- One long sub-agent report per card flooded the chat → read the report, pass on only the merged list of findings and questions.

## Notes and vault

- Rewrote a 40 KB plan note several times for one-line changes → keep the plan stable after approval, put live state in the ledger, batch edits into one write.
- Moved the briefs out of the inbox before the cards' `Brief:` lines were checked → the cards point by filename, so a move is safe, but check uniqueness first.
- Edited a brief without a change log → every brief edit adds a dated change-log entry saying what and why.

## Repo and hooks

- A read-only search was blocked by a hook because the command named a credential script → never name credential scripts in commands; search with neutral terms.
- Work sat on the main branch with uncommitted docs and the stop hook demanded a commit; the user thought something had been merged into main → run `git branch --show-current` first, say plainly that nothing was merged or pushed, switch to `development`, commit docs there only.
- A large `list_tasks` result overflowed the context → filter by tag, date or priority and parse the saved result with a script.

## Process

- Left out the wave sub-tasks, so the sprint card could not show wave progress → step 11 adds one sub-task per wave at the very end of the sprint card, and the execution prompt ticks each as its wave is delivered.
- Ticked a step before its evidence was on the card → tick last.
- Reported cards as ready while their Specs listed open questions → run the definition of ready strictly, report who passes, fix rows for the rest.
- Edited a verbatim document of the user's only after they asked → ask for permission once, with the exact row to change; after permission, edit it and note the old wording in the row.
- Wrote a gate list, then found a gate (XL split) at the end → run the checklist in `plan.md` in order; do not skip ahead.

## Execute, debug, close

Written before the first real run; correct them with what happens.

- Execute ran two waves in one chat and compressed the context → one wave per run; stop and give the paste for the next chat.
- The cap of five across Next + Doing hit when the next wave was pulled forward → count Next + Doing with `list_tasks` by state before each move; overflow waits in Assigned and is reported.
- The skill said the board refuses Doing while a blocker is in Stand By, after the app had stopped doing so → a blocker never stops a move between Execution columns; only completing waits for blockers. Re-read the board tool's own description before writing a board rule.
- A finished card was completed instead of parked → delivery is `standby`; only `close` completes, on the user's quoted approval.
- Sub-tasks ticked in a batch at the end → tick each as it is done so the card shows live progress.
- Debug fixed things nobody approved → every adjustment is a row in the decision table; apply only approved rows.
- Close archived before the cards were complete → order is cards, sprint card, then folder; verify each.

- Wave sub-tasks landed at the top of the card, reversed, even when added one at a time → always `reorder_subtasks` with the full order and read back.
- Every wave got the same paste (`execute {sprint card}`) and it read like a per-card trigger → the command names the sprint card and the wave (`execute {sprint card} wave N`); a batch card id is refused.
- "I want this today" was taken as approval to commit → urgency is not approval; ask one yes or no.
- The execution prompt carried its own debug procedure beside `debug.md` → the prompt only points to the references.
- Waves were split without the WBS the user asked for → step 6 runs `/bandit:plan wbs` first.

- Nested agents are documented (three layers by default), so a wave subagent should run code-reviewer and ui-verifier itself; `GATES NEEDED` is only a fallback. Not yet seen in a real run: record what the first `run` shows.
- An unattended paced run needs the terminal open, the computer awake and "Continue automatically at usage limit" on in `/config`; the model cannot read plan usage, so pacing is by time.
- Two sprints planned separately can claim the same migration number → `run` checks plans across sprints before the first wave.

- Briefs for sprint privacy-a were left at the project root by the same agent that filed two other sprints correctly → rules that matter are enforced by `scripts/check_sprint.py` and the Stop hook, not by prose.
- A WBS and an out-of-sprint brief were left at the project root → SP5: a sprint project's root holds only `{project}.md`, `sprint-*` folders and `planning/`; the WBS, the project plan and the architecture live in `planning/`; an out-of-sprint brief lives in the folder of the sprint it follows.

- Leftovers stayed behind after the work that used them; then two notes were archived on a guess → write No leftovers into every command, and archive only on proof that the successor exists.
- Inbox drafts stayed behind after their brief was filed, a WBS draft after the WBS was filed, a brief after its card was deleted → archive what a step consumed in that same step; SP2, SP3 and SP5 catch the sprint cases.

- In `run`, the second wave never moved its working cards to Doing: its cards were chained behind first-wave cards sitting in Stand By, the board still refuses Doing while a blocker is incomplete, and the skill said Stand By counted (an app change, not built) → never write a rule the board does not enforce; setting the board happens at the start of every wave; a refused move is recorded on the card and in the ledger, never skipped silently.

- The sprint card moved along with its batch and sat in the way → it stays untouched until the last card of the last wave is in Stand By, then moves to Stand By once, and `close` completes it.

- A planned push was refused or left undone because the skill, an older prompt or a memory said "never push" → the user lifted that rule on 2026-10-10 (it dated from when testing and staging did not exist). `development` is pushed as `execute.md` → Pushing `development` says; `main` and deploy stay the user's. Execution prompts restate this so an old note cannot block it.

## Owner changes proposed

- A card was detached at close (production steps moved to the next sprint) while its brief stayed in the sprint folder that was about to be archived, and the checker still counted the card as part of the sprint → write "detached" on its ledger row, and merge everything about the card into one note in the inbox before archiving (`close.md` step 3a); SP2 skips detached cards and SP6 fails a second brief for a card.
- Sent a second long question list after the first → one list per gate with recommendations; follow up only on what the answers raise.
- Sprint shared-finance, wave 2: the next wave's cards stayed in Assigned after the wave's cards reached Stand By, because the move waited for the wave-end checks and the orchestrator waited for the report → the next wave goes to Next the moment the last card reaches Stand By (`execute.md` → The wave, step 7), and the orchestrator sets the board before checking anything, whatever the wave reported (`run.md` → The loop, step 2).
- `get_execution_board` with no filter returned 385,000 characters (every household card with its description) and overflowed the tool output on every board check; a wave agent was also cut off by a usage limit and left the board unset → read the sprint's cards by column with `list_tasks` (`execute.md` → Reading the board); `run` sets the board even when the wave sent no report.
