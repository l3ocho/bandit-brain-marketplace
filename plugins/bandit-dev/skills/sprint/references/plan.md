# 📋 The plan cycle, step by step

Part of `bandit-dev:sprint`. Read before running `/bandit-dev:sprint plan`. Card sections, lanes, stages and the Spec lock are owned by bandit:tasks (`references/dev.md`); note places, storage and write rules by bandit:notes. This file only says how the steps run.

Contents: Conventions · The twelve steps · Steps 1 to 12 · Investigator brief · Handover

## Conventions for every step

- **Order and evidence.** Do the step, then fill its row in the ledger's **Plan steps** table (date and evidence: what was found and done, in a few lines, with ids). The ledger exists from step 1, so a lost chat resumes from it.
- **Read before every write.** `get_task` right before any description or tag write. A card changed since the last read: use the new text.
- **Decisions to the user: one table, one format.** Columns exactly `Issue | Recommendation | Different from what you requested? | If yes, how?`. Plain words in every cell; no row numbers, no references to other rows or earlier messages. Open questions, a Spec that cannot be built as written, and fix rows all use it; never a second format.
- **The user's original request is the baseline.** Compare against their own words (the card's original-request comment, the brief), never against an earlier summary of yours. Only rows that differ from the request need a decision; the rest are applied without asking.
- **Add nothing the user did not ask for.** No invented rule, no "applied unless you object" block. A gap is answered only by a **convention**: the app keeps how it works today, or the project's own rule says so (its `CLAUDE.md`, `.claude` folder or docs). Each such gap is one line in the plan's **Gaps answered by convention** block, shown at approval. A dependency the code forces goes in the plan, addressed there. A decision row exists only when the Spec truly cannot be built as written, saying why.
- **Questions in the user's terms.** Each says what is needed and what it changes for the user, with the recommendation, briefly. Not asked: technical choices (they are the executor's), and anything the project's design handover already fixes, small fit adjustments included.
- **"What is missing"** is answered with that list only: each missing item and who owes it. No summaries, no housekeeping, no recap.
- **Decisions** go on the card they concern as a comment starting `Planning decisions {date}`. The Spec and the brief are edited only when the user asks.
- **Date.** Today is in the session context. Convert "tomorrow" to an absolute date.

## The twelve steps

The ledger's **Plan steps** table carries the steps in this order (`references/templates.md` → Ledger), with these names.

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
| 11 | Independent plan review | The `plan-reviewer` agent's record with the sprint's papers; majors applied; no blocker open (the only stop) |
| 12 | Commit the sprint | Assignee, undated cards given the sprint date and checked against this week's Sunday, the sprint's expected date, Ready to execute, execution prompt, the waves and lands-after links in the app, ledger with `Committed:` and its Waves table, one wave note per wave, the debug card alone in the last wave, each wave's estimate in the plan |

## 1 · Select and freeze the batch

0. **Closed sprints left behind, first.** List the home board's closed and cancelled sprints (`get_sprints { boardId }`, status `closed` or `cancelled`: both are final) and run the archive check on them (Closed-sprint check, below). Any SP15 line → one archive proposal through bandit:notes for those papers and WBS notes (the same move as `close.md` step 3), applied on the user's yes, then the check again. Planning goes on only once it prints OK; a declined proposal stops planning here, named.
1. Resolve the selection (SKILL.md). Open cards only, not archived, in no sprint: none held by a sprint (`list_tasks { noSprint: true }`). Cards already in a sprint are excluded with a fix row. A card on the Inbox cannot join (`SPRINT_CARD_ON_INBOX`): a fix row to file it first.
2. For every card read `blockedBy` and `blocks`. Report cards **outside** the batch that it blocks or is blocked by; none of them need links, but the ledger records them under "Out of this sprint".
3. **Create the sprint** on the home board: `manage_sprints { action: "create", boardId, name, papersUrl }` (name given, else the ISO week, `2026-w42`, kebab-case; `papersUrl` = where its papers are, as text: `references/templates.md` → The sprint in the app), then `manage_sprints { action: "add_cards", sprintId, taskIds }` with the batch, all or none (a refusal names the card and why: a fix row). Read it back with `get_sprints { sprintId }`.
4. **Write the ledger**, the sprint's first paper (`references/templates.md` → Papers, Ledger), through bandit:notes, created with every section heading: At a glance with `Sprint record: {name} on {board}` and the Status line, the twelve-row **Plan steps** table, the Batch table and Out of this sprint.
5. **Sprint order.** The previous open sprint on the board (`get_sprints { boardId }`, status not `closed`). One exists → `link_tasks { blockerSprintId, blockedSprintId }` so the new sprint is **blocked by** it. `run` and `execute` refuse a sprint that an open sprint blocks, so sprints ship in order.
6. Step 1's row: selection rule, count, ids, the sprint it waits for; open Urgent cards listed as not selected.

**Closed-sprint check** (here and `close.md` step 4). Build the project's notes file (`references/templates.md` → Notes file), then run `python3 ${CLAUDE_SKILL_DIR}/scripts/check_sprint.py --closed {names}`: SP15 fails while a paper or the WBS note of a closed sprint is not archived (a plan linked to a done card stays Done and passes). "Could not read the notes file" is a failed check, never a pass.

**Done when** `get_sprints { sprintId }` shows the batch as its cards and the previous open sprint in
`blockedBy` when there is one, and the ledger holds the Plan steps table.

## 2 · Spec completeness check

For each card: `get_task`; find its brief (bandit:notes lookup: the note linked to the card, the title the Spec's `Brief:` line names); compare card and brief; check Outcome, Scope in and out, Acceptance, Decisions and Open questions exist; check referenced cards, files and idea ids resolve; note sub-tasks, tags, effort, complexity, lane and stage.

**Fix rows for:** missing sections, card and brief disagreement, an unresolved reference, a `Brief:` line carrying a folder or a path (the note's title only), a screen-changing card without its linked, approved design (bandit:tasks `dev-workflow.md` → Design step), a screen-changing card whose `Design:` line is missing or is not a full web address (`https://…`, the Claude.ai design page), and, when the Project Context has a `design:` line, a screen-changing card whose design card is still open (`get_task` → `blockedBy`; bandit:tasks `dev-workflow.md` → Design card). No fix row for Spec or brief wording older than a decision on the card: the decision wins.

## 3 · Close the open questions

**Lessons from earlier sprints, before anything else.** Read the Lessons of the project's earlier wave reports, live and archived (`references/templates.md` → Papers: the board's notes of kind `reference` titled `…-wave-report` with a `sprint-*` tag, `notes_list` then with `archived: true`). A lesson whose When matches a card puts its Do into that card's brief and its plan section, quoted with its sprint; a workflow or settings lesson seen more than once becomes a proposed change to the helper, the project's rules or the Claude settings, in the approval summary.
0. **The project's own rules first.** Read the cards and the batch's intended approach against the project's settings and docs (its `CLAUDE.md`, its `.claude` folder, its docs; `references/homes.md` → Owners). A conflict is addressed in the plan; it is a question only when the Spec cannot be built as written. Nothing from them is copied into the plan: it names the doc.
1. Collect the open questions the cards themselves list, and only those. None listed: the step's row says "none" and planning goes on without stopping. **Order:** conflicts first (between cards, and with what is already built), then each card's own, asked as Conventions says. What a check or an investigation finds is settled from the Spec, the card's decisions or how the product works today, and goes in the plan.
2. **Investigate first, read-only, in parallel**: one investigator per card (brief below). One live-browser check at a time, only for what code cannot answer (touch behaviour, what the UI shows).
3. **Spot-check** the decisive facts in code before they go into a card.
4. Present **one decision table** (Conventions), grouped by card: the cards' own open questions, and a Spec that cannot be built as written. Nothing is applied that the Gaps answered by convention block does not list. "Go with your recommendations" approves exactly the rows shown, nothing else.
5. Record the answers (comment per card). Ask follow-ups only for what the answers raise.
6. A large new requirement that surfaces: record the rule, create a parked card **outside** the sprint, ask one yes or no whether it joins.

**Done when** every question on every card is answered and recorded, or parked with its card.

## 4 · Size and classify

Effort and complexity per card; lane per card. Check the card boundaries in bandit:tasks `dev.md`: one lane, one branch, one landing, up to L; **XL splits into two or more cards** now. Apply bandit:tasks B7 (`references/dev-workflow.md`), its sizing and no-umbrella rules included; a split original or an umbrella leaves the sprint (`manage_sprints { action: "remove_card" }`). A split card keeps its Spec's intent, gets its own brief and Spec, blocks or is blocked by its sibling, and **joins the sprint** (`manage_sprints { action: "add_cards" }`). Record old and new sizes in the step's row.

## 5 · Cross-card analysis

**Migration tail.** Run `python3 ${CLAUDE_SKILL_DIR}/scripts/recipe.py tail` (the project's
`bandit.yaml` `migrations.check`) and write the tail the sprint starts from into the plan, then a
**Migration tail** table: one row per wave, the tail that wave must start from and the numbers it
adds. A missing key refuses by name: the project adds it to `bandit.yaml` before planning goes on.
A recipe with no `migrations` section prints `none`: write "No migrations" in the plan and skip the table.

From the investigations and a quick code check: migrations (one at a time, numbered in order), files several cards edit (state the order), hidden dependencies (what must land before another card's tests), generated artefacts that need regenerating after each card, tests that pin behaviour a card changes, docs each card must update. Output: one comment, and the "Cross-card" section of the plan. A card that must land after another without a blocker link goes on one line of that section, `Lands after: {card} after {card}[ and {card}]; …`: with the Batch table's `Blocked by` column it is how `execute`, `run` and SP10 know which waves depend on which (`execute.md` → Command).

## 6 · Sequence

**Split with the WBS.** Before drawing the waves, run `/bandit:plan wbs` for the batch in sprint mode (input: the batch cards and their briefs; skip its reconcile phase, which would edit the briefs; no size estimates). The WBS is its own note, `{project}-wbs`, in the project's place for planning documents (bandit:notes owns the place and the Card links rows; bandit:plan owns the format), and the plan note names it. Use each card's lowest-level tasks to see what truly depends on what; sizes stay with step 4. The WBS decides the wave split: a wave is a set of cards (or card pieces) that can be built and verified together. No wave split without it.

Waves with a reason each. Parallel only where cards touch different files and no migration is shared; merges, migrations and shared board components are sequential. **Side by side:** cards of one wave that can be built at the same time go on one line in the plan's Cross-card items, `Side by side: {card}, {card} (wave {n})`: they touch different files, at most one of them adds a migration, at most one needs a browser check (one app build and its port at a time), and neither lands after or depends on the other. `run` builds them one agent each, each in its own working copy (`references/run.md` → Side by side); `execute` builds them one after the other. While the first such wave is a trial (`run.md` → Side by side, step 6), a plan writes at most one line. Record the order in the ledger's **Waves** table, the one place of the wave order (`references/templates.md` → Ledger): one row per wave, its cards in the plan's order, no date yet; the step's row names the table and does not list the waves. Step 12 sets the waves in the app once the review's changes are in; a card never goes in an earlier wave than a card of the sprint that blocks it (the app refuses it, `SPRINT_WAVE_ORDER`).

## 7 · Write the one technical plan

One plan note, a paper of the sprint (`references/templates.md` → Papers, Plan note). Per card: approach, tests, docs, "Verify first", acceptance-to-proof table (a screen-changing card with a `Design:` line adds the row "matches the design handover" and the screen sizes to compare). The plan carries the **Gaps answered by convention** block: one line per gap, the card, and the convention that answered it ("keeps how the app works today", or "{doc} says …"); `execute.md` → The wave, step 4a is how execution uses it. Then, for each card, **first** write its **build steps** from its plan section as ordered sub-tasks (design lines first, existing `Gate:` lines after them), then its **check lines**, last (`references/templates.md` → Check lines; the browser check line only on a card that changes a screen), and read them back; no build card gets an approval line: the approvals go on the debug card at step 12 (`references/templates.md` → Approval line); the rule is bandit:tasks `references/dev.md` → Card fields and `references/board.md` → Sub-tasks. **Only then** fill the card's `Technical plan` section (outside the locked Spec, so no override): the plan note's title, branch, size, short bullets. **The sub-task gate** (`scripts/subtask_gate.py`, a hook on the board writes) enforces it: it refuses a Technical plan written for a card with no build step, and the commit (step 12) while any card of the sprint has none, naming each card; a card the chat has not read is named with its `get_task`. Branch names follow the project's branching document; round numbers are taken at execution. The plan also carries a **Final push** section (the push of `development` to origin at the end of the last wave that changes code; the rules are `execute.md` → Pushing `development`), unless the user removes it at approval.

## 8 · Risk and rollback

In the plan: how rollback works for every card (code, schema, backups, deploy shape), then per card a table (risk, likelihood, impact, mitigation) and a rollback line, then sprint-wide risks.

## 9 · Definition of ready, per card

Ready means: Spec clear with no open questions, acceptance testable, dependencies resolved or sequenced, Technical plan written with the plan note's title, branch and size, effort at most L, plan note filed, build sub-tasks written (step 7), followed by its check lines, last, and no approval line on it (`references/templates.md` → Check lines, Approval line). A card with no build sub-tasks fails readiness, and so does one whose check lines are missing or not last, or one that carries an approval line: one fix row, the sub-tasks or lines written or taken off, then the card is checked again.

1. Check each card strictly and report who passes and who fails, with fix rows. Answered questions count as answered by their `Planning decisions` comment: the Spec and the brief are not edited unless the user asks. A section outside the Spec (Technical plan) is written by copying the stored Spec text byte for byte from `get_task`, never retyped.
2. The step's evidence names each card's count of build steps only, never counting `Gate:` lines, check lines or an approval line (`{card id}: {n} steps`, one per card, in the evidence cell); the checker (SP13) reads it.
3. Move passing cards to `stage/planned`, then `stage/ready` on the user's approval (step 10), through the stage procedure in bandit:tasks.

## 10 · Approval gate

Present the state in a short summary (cards, waves, plan, risks, what needs the user, and the Gaps answered by convention block as one short list). Take the user's explicit approval or return to the step it names. Quote the approval in the ledger's Decisions log and the step's row. If the user's wording is ambiguous ("approved" mid-list), state the reading you applied in one line. **An urgency remark ("I want this today", "go fast") is not an approval of the plan**: put the summary in front of them and ask one yes or no. A date they give is used as the sprint date; it does not commit the sprint. **No date given: the sprint date is this week's Sunday** (the week runs Monday to Sunday, from the session date).

## 11 · Independent plan review

Automatic, after the approval and before the commit. It stops the user only on a blocker.

1. **Launch the `plan-reviewer` agent** (the Agent tool, `bandit-dev` agent `plan-reviewer`) and wait
   for it. Its definition names its model and effort (the top model, high effort), whatever model this chat
   uses: launch it with no model or effort of your own. Its prompt carries: the sprint's name, the plan note's full text, each batch card's
   Spec and brief, the WBS, the Migration tail table, the repo path and the project's `bandit.yaml`.
2. **Write the review record**, a paper of the sprint: `{project}-review-sprint-{name}-YYYY-MM-DD`,
   kind `log`, with the sprint's tag (`references/templates.md` → Papers). Body: the agent's
   verdict and findings table as returned, then the risk additions. Its first line names the model that ran
   the review, read from the agent's log (the model on its replies), never assumed from the definition.
3. **Apply** every major finding, and each minor one that is cheap, to the plan (read, then the edit of
   its section, through bandit:notes) and fill the record's "Applied via" column (`plan §…`, `card {id} Technical plan`). Notes stay.
4. **A blocker stops the step:** put the blockers to the user in one list, each with its recommendation;
   apply their answers, record them in the review, and re-run the review once if they change the plan's
   approach. This is the only stop the review adds.
5. Step 11's row: the verdict, counts by severity, the model that ran the review and the record's title.

**Done when** the review record is with the sprint's papers, every major finding is applied and no
blocker is open. `run` and `execute` refuse a sprint whose step 11 row is not done; the checker
(SP7) fails a committed sprint with no review record.

## 12 · Commit the sprint

1. **Batch cards:** assign each to the user (the signed-in member, live lookup) and set `stage/ready`. No tag. **A card with no due date gets the sprint date** (`update_tasks { dueDate }`); a card with its own due date keeps it. A refused date names the links responsible: the card keeps no date and is named as not on the Execution board yet, with the reason. The Execution board shows an open card only by its own due date, on or before this week's Sunday; the sprint's date is not read there.
2. **The sprint:** `manage_sprints { action: "update", expectedDate }` = the sprint date, then `move` to `ready_to_execute` (it needs the date and a card; a refusal names what is missing). Read it back. The sub-task gate refuses the move while a card has no build step (step 7): write them, read them back, move again.
3. **Waves in the app,** while the sprint is Ready to execute (no replan to confirm): `manage_sprints { action: "add_wave" }` until the sprint has the plan's number of waves, then `set_wave { taskId, wave }` for each card in the plan's order (last in its wave, so the order inside the wave is the plan's), then `link_tasks { blockerTaskId, blockedTaskId, kind: "lands_after" }` for each pair on the plan's `Lands after:` line (the card named first lands after the other). A `SPRINT_WAVE_ORDER` refusal means the waves break a blocker: a fix row, back to step 6. Read the sprint back (`get_sprints { sprintId }`): each card's `wave` matches the plan.
4. **Ledger:** the **Waves** table, rewritten from that read-back, one row per wave of work in order (`| Wave {n} | {card ids} | | |`; step 12's row and the Milestone log name it rather than list the waves), the Decisions log, `Committed: {date}` in At a glance (the line SP7, SP9 and SP10 read; SP9 then needs steps 1 to 11 done), `Approvals: debug card` in At a glance (the sprint's shape, which every later step reads: `references/templates.md` → Check lines) and the Status line `Committed {date}; next: Wave 1`. Write the execution prompt (templates).
5. **Wave notes:** one note per wave (`references/templates.md` → Wave note), written after the review's changes are in the plan: that wave's plan sections, the shared execution rules and the ledger lines it needs, copied word for word, each note read back. A wave starts from its note and never reads the whole plan or ledger to begin (`execute.md` → Start).
6. **Briefs and leftovers:** bring every batch brief to the sprint's papers through bandit:notes (the brief stays linked to its card and gets the sprint's tag, the user's tags kept) and archive every source the planning consumed (inbox drafts, spec notes, a superseded WBS draft; `references/homes.md` → Leftovers).
7. **Seed the Execution board:** every batch card to `assigned` with `update_tasks { items: [{ taskId, executionState: "assigned" }, …] }`, reading `results` per card, so the user sees the whole sprint before work starts. **Verify by date, not by column:** `get_task` each batch card and compare its due date with this week's Sunday. On or before it: on the Execution board. After it, or none: not on the board yet. The step's row lists every card and where it stands; the sprint's columns alone never prove the board shows a card.
8. **Create the debug card** (`references/templates.md` → Debug card): one `create_tasks` on the home board, assigned to the user, with the sprint date, its approval lines in `subtasks` (one per build card, in wave order: `references/templates.md` → Approval line) and the test plan in its description, then `manage_sprints { action: "add_cards" }`, `add_wave` and `set_wave` into that new last wave, alone, so the waves of work finish without it, and `executionState: "assigned"` so it shows on the Execution board; write `Debug card: {short id}` in At a glance. Read it back: one approval line per build card and one test plan entry each. **A sprint planned before this rule** (its build cards carry the old approval line, or no check lines): take each build card's approval line off (`delete_tasks` kind `subtask`) and add its check lines last, then read every card back; the step's row names the cards changed.
9. **The pre-sprint estimate** (`references/templates.md` → Pre-sprint estimate): each wave's time estimate into the plan's Summary wave table, the sprint's total for the report. The app's sprint page shows the map.
10. Build the notes file (`references/templates.md` → Notes file), run `python3 ${CLAUDE_SKILL_DIR}/scripts/check_sprint.py` and paste its output into the Milestone log; only once it prints OK, mark step 12's row done ("committed, checker OK").

## Investigator brief

Read-only. Give each investigator: the card's Spec, the repo path, what to find, and the report shape.

1. Current state: what exists today that the card touches, with `file:line`.
2. The card's claims checked against the code; wrong ones named.
3. Constraints that apply (project hard rules, boundaries, tests that pin behaviour).
4. Dependencies and risks only, each with how the plan addresses it. No questions for the user: a gap is settled from the Spec, the card's decisions, today's behaviour or the project's rules, and reported as such.
5. Mark anything not verified. Do not edit, run migrations or touch credentials; do not propose scope or cards.

A live-browser investigator **at planning time** is told which controls write (sorts, toggles) on existing data, to open and cancel, and to report what it could not check. That read-only rule belongs to planning only; it never goes into an execution prompt or plan section.

## Test data (plan and execution prompt)

**Test data is never a reason to skip a test.** An execution-time check (ui-verifier, integration test, script) that needs data the dev database lacks (a folder, a second member, a private board, a card assigned to someone) creates that data itself, runs the check, and removes what it created. Reporting "could not exercise X because the dev database has no Y" is a failed check, not a limitation: the wave is not done until the case ran. The only limits are: never modify or delete a record the check did not create, never touch credentials, never run against production.

**The data comes from `bandit-dev:testdata`** when the project's `bandit.yaml` has a `testdata` section (`recipe.py opt testdata.databases` prints something other than `none`):

- **Planning, step 7.** For each card with a live check, run `/bandit-dev:testdata make {card}` (read-only). The card's plan section names, per check, the data it needs in plain words, the label (the card id) and the line "created by `/bandit-dev:testdata create` before the check, removed by `clean` after it". No SQL in the plan: the wave makes it again on the code as built.
- **Execution.** Before a card's live check: `make` then `create` on the database the check runs against; right after the check, pass or fail: `clean {db} card {card id}`. Staging writes ask the user's yes, so an unattended wave runs its checks on `development` or `test`.
- **No `testdata` section.** The verifier builds and removes its own data as before, and the plan section says which data and how. Every plan section that lists a UI or live check names the data the check needs either way.

## Plan final message

End of step 12: ten lines at most. **First line: the pre-sprint report**, the sprint's estimated time (or "no estimate yet"), with the waves' estimates in the plan's Summary. A sprint date after this week's Sunday: say the cards stay off the Execution board until that week. Name every card not on the board yet, with why. Then one exact paste per wave, each naming the sprint and the wave: `/bandit-dev:sprint execute {sprint} wave 1`, `... wave 2`, and so on, then `/bandit-dev:sprint debug {sprint}` and `/bandit-dev:sprint close {sprint}`. Never one generic paste for every wave.

## Handover

At step 12 write `references/templates.md` → Execution prompt, Ledger and Wave note as the sprint's papers. The execution prompt runs one wave per run without questions, merges passing cards into the local development branch, pushes `development` once at the end of the last code wave (never `main`, never a deploy), keeps the ledger after every milestone and writes the handover test report. A wave starts from its wave note; a new chat resumes from the ledger. The commands that run it are `execute`, `debug` and `close` (`references/execute.md`, `debug.md`, `close.md`). The prompt points to `execute.md` for board moves and the wave rules, to `debug.md` for bug reports and to `close.md` for closing; it carries no copy of their procedures. Its start paste names the wave.
