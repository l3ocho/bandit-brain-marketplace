# 📋 The plan cycle, step by step

Part of `bandit-dev:sprint`. Read before running `/bandit-dev:sprint plan`. Card sections, lanes, stages and the Spec lock are owned by bandit:tasks (`references/dev.md`); vault paths and write rules by bandit:notes. This file only says how the steps run.

Contents: Conventions · Steps 1 to 12 · Investigator brief · Handover

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

## 1 · Select and freeze the batch

1. Resolve the selection (SKILL.md). Open cards only, not archived, in no sprint: none held by a real sprint (`list_tasks { noSprint: true }`) and none carrying a `sprint/*` tag while the tags exist (bandit:tasks `references/board.md` → Tags). Cards already in a sprint are excluded with a fix row. A card on the Inbox cannot join (`SPRINT_CARD_ON_INBOX`): a fix row to file it first.
2. For every card read `blockedBy` and `blocks`. Report cards **outside** the batch that it blocks or is blocked by; none of them need links, but the ledger records them under "Out of this sprint".
3. **Create the sprint** on the home board: `manage_sprints { action: "create", boardId, name, papersUrl }` (name given, else the ISO week, `2026-w42`, kebab-case; `papersUrl` = the sprint folder's path), then `manage_sprints { action: "add_cards", sprintId, taskIds }` with the batch, all or none (a refusal names the card and why: a fix row). Read it back with `get_sprints { sprintId }`.
4. **Write the ledger** in the new sprint folder (`references/templates.md` → Ledger), through bandit:notes: At a glance with `Sprint record: {name} on {board}` and the Status line, the twelve-row **Plan steps** table, the Batch table and Out of this sprint.
5. **Sprint order.** The previous open sprint on the board (`get_sprints { boardId }`, status not `closed`), or an open old-way sprint card (`references/old-way.md`). One exists → `link_tasks { blockerSprintId (or blockerTaskId for a sprint card), blockedSprintId }` so the new sprint is **blocked by** it. `run` and `execute` refuse a sprint that an open sprint blocks, so sprints ship in order.
6. Step 1's row: selection rule, count, ids, the sprint it waits for; open Urgent cards listed as not selected.

**Done when** `get_sprints { sprintId }` shows the batch as its cards and the previous open sprint in
`blockedBy` when there is one, and the ledger holds the Plan steps table.

## 2 · Spec completeness check

For each card: `get_task`; find its brief (bandit:notes lookup by filename from the Spec's `Brief:` line); compare card and brief; check Outcome, Scope in and out, Acceptance, Decisions and Open questions exist; check referenced cards, files and idea ids resolve; note sub-tasks, tags, effort, complexity, lane and stage.

**Fix rows for:** missing sections, card and brief disagreement, an unresolved reference, a `Brief:` line carrying a folder (filename only), a screen-changing card without its linked, approved design (bandit:tasks `dev-workflow.md` → Design step), and, when the Project Context has a `design:` line, a screen-changing card whose design card is still open (`get_task` → `blockedBy`; bandit:tasks `dev-workflow.md` → Design card). No fix row for Spec or brief wording older than a decision on the card: the decision wins.

## 3 · Close the open questions

**Lessons from earlier sprints, before anything else.** Read the Lessons of the project's earlier wave reports (`Projects/{slug}/sprint-*/` and `_archive/Projects/{slug}/sprint-*/`). A lesson whose When matches a card puts its Do into that card's brief and its plan section, quoted with its sprint; a workflow or settings lesson seen more than once becomes a proposed change to the helper, the project's rules or the Claude settings, in the approval summary.
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

From the investigations and a quick code check: migrations (one at a time, numbered in order), files several cards edit (state the order), hidden dependencies (what must land before another card's tests), generated artefacts that need regenerating after each card, tests that pin behaviour a card changes, docs each card must update. Output: one comment, and the "Cross-card" section of the plan.

## 6 · Sequence

**Split with the WBS.** Before drawing the waves, run `/bandit:plan wbs` for the batch in sprint mode (input: the batch cards and their briefs; skip its reconcile phase, which would edit the briefs; no size estimates). The WBS is its own note, `{project}-wbs.md` in `Projects/{slug}/planning/` (bandit:notes owns the path and the Card links rows; bandit:plan owns the format), and the plan note links it. Use each card's lowest-level tasks to see what truly depends on what; sizes stay with step 4. The WBS decides the wave split: a wave is a set of cards (or card pieces) that can be built and verified together. No wave split without it.

Waves with a reason each. Parallel only where cards touch different files and no migration is shared; merges, migrations and shared board components are sequential. Record the order in the ledger's Batch table (Order column), and set the sprint's run order to it: `manage_sprints { action: "reorder_cards" }`, wave order, then the plan's order inside a wave. The app holds only that order; the waves stay in the plan.

## 7 · Write the one technical plan

One plan note in the sprint folder (template). Per card: approach, tests, docs, "Verify first", acceptance-to-proof table. The plan carries the **Gaps answered by convention** block: one line per gap, the card, and the convention that answered it ("keeps how the app works today", or "{doc} says …"); `execute.md` → The wave, step 4a is how execution uses it. Then fill each card's `Technical plan` section (outside the locked Spec, so no override): plan filename, branch, size, short bullets. Branch names follow the project's branching document; round numbers are taken at execution. The plan also carries a **Final push** section (the push of `development` to origin at the end of the last wave that changes code; the rules are `execute.md` → Pushing `development`), unless the user removes it at approval. It also carries a **Deployment handover** section by default: the staging card on `handover.board`, with its column and the runbook its prompt is built from (`recipe.py require handover.board handover.staging.column handover.staging.runbook`), and the production card beside it only when the recipe names one (`recipe.py opt handover.production.column` prints a column, then `require handover.production.runbook`); the lines "the Final push fills the staging card; `release` fills the production card; the user fires each hook", or, with no production card, "the Final push fills the staging card; `release` runs the production deploy itself through the recipe's steps". A recipe with no `handover` section (`recipe.py opt handover.board` prints `none`) is one fix row, asked once: the project adds the section or the user drops the handover for this sprint, quoted in the plan.

## 8 · Risk and rollback

In the plan: how rollback works for every card (code, schema, backups, deploy shape), then per card a table (risk, likelihood, impact, mitigation) and a rollback line, then sprint-wide risks.

## 9 · Definition of ready, per card

Ready means: Spec clear with no open questions, acceptance testable, dependencies resolved or sequenced, Technical plan written with filename, branch and size, effort at most L, plan note filed.

1. Check each card strictly and report who passes and who fails, with fix rows. Answered questions count as answered by their `Planning decisions` comment: the Spec and the brief are not edited unless the user asks. A section outside the Spec (Technical plan) is written by copying the stored Spec text byte for byte from `get_task`, never retyped.
2. Move passing cards to `stage/planned`, then `stage/ready` on the user's approval (step 10), through the stage procedure in bandit:tasks.

## 10 · Approval gate

Present the state in a short summary (cards, waves, plan, risks, what needs the user, and the Gaps answered by convention block as one short list). Take the user's explicit approval or return to the step it names. Quote the approval in the ledger's Decisions log and the step's row. If the user's wording is ambiguous ("approved" mid-list), state the reading you applied in one line. **An urgency remark ("I want this today", "go fast") is not an approval of the plan**: put the summary in front of them and ask one yes or no. A date they give is used as the sprint date; it does not commit the sprint. **No date given: the sprint date is this week's Sunday** (the week runs Monday to Sunday, from the session date).

## 11 · Independent plan review

Automatic, after the approval and before the commit. It stops the user only on a blocker.

1. **Launch the `plan-reviewer` agent** (the Agent tool, `bandit-dev` agent `plan-reviewer`) and wait
   for it. Its prompt carries: the sprint's name, the plan note's full text, each batch card's
   Spec and brief, the WBS, the Migration tail table, the repo path and the project's `bandit.yaml`.
2. **Write the review record** into the sprint folder: `{project}-review-sprint-{name}-YYYY-MM-DD.md`,
   `type: log`, `sprint` = the sprint's name (bandit:notes conventions §1). Body: the agent's
   verdict and findings table as returned, then the risk additions.
3. **Apply** every major finding, and each minor one that is cheap, to the plan (read, then the etag
   edit) and fill the record's "Applied via" column (`plan §…`, `card {id} Technical plan`). Notes stay.
4. **A blocker stops the step:** put the blockers to the user in one list, each with its recommendation;
   apply their answers, record them in the review, and re-run the review once if they change the plan's
   approach. This is the only stop the review adds.
5. Step 11's row: the verdict, counts by severity and the record's filename.

**Done when** the review record is in the sprint folder, every major finding is applied and no
blocker is open. `run` and `execute` refuse a sprint whose step 11 row is not done; the checker
(SP7) fails a committed sprint with no review record.

## 12 · Commit the sprint

1. **Batch cards:** assign each to the user (the signed-in member, live lookup) and set `stage/ready`. No tag. **A card with no due date gets the sprint date** (`update_tasks { dueDate }`); a card with its own due date keeps it. A refused date names the links responsible: the card keeps no date and is named as not on the Execution board yet, with the reason. The Execution board shows an open card only by its own due date, on or before this week's Sunday; the sprint's date is not read there.
2. **The sprint:** `manage_sprints { action: "update", expectedDate }` = the sprint date, then `move` to `ready_to_execute` (it needs the date and a card; a refusal names what is missing). Read it back.
3. **Ledger:** the **Waves** table, one row per wave in order (`| Wave {n} | {card ids} | | |`), the Decisions log, `Committed: {date}` in At a glance (the line SP7, SP9 and SP10 read; SP9 then needs steps 1 to 11 done) and the Status line `Committed {date}; next: Wave 1`. Write the execution prompt (templates).
4. **Briefs and leftovers:** move every batch brief into the sprint folder (`Projects/{slug}/sprint-{name}/`) and archive every source the planning consumed (inbox drafts, spec notes, a superseded WBS draft; `references/homes.md` → Leftovers).
5. **Create the handover cards** (unless the plan dropped them): one `create_tasks` call on the `handover.board` board, the staging card in `handover.staging.column` and, only when the recipe names one, the production card in `handover.production.column` (resolved live by name), titles and descriptions from `references/templates.md` → Handover cards, in their not-ready form; write `Staging handover: {short id}` in At a glance, and `Production handover: {short id}` when that card exists.
6. **Seed the Execution board:** every batch card to `assigned` with `update_tasks { items: [{ taskId, executionState: "assigned" }, …] }`, reading `results` per card, so the user sees the whole sprint before work starts. **Verify by date, not by column:** `get_task` each batch card and compare its due date with this week's Sunday. On or before it: on the Execution board. After it, or none: not on the board yet. The step's row lists every card and where it stands; the sprint's columns alone never prove the board shows a card.
7. Run `python3 ${CLAUDE_SKILL_DIR}/scripts/check_sprint.py` and paste its output into the Milestone log; only once it prints OK, mark step 12's row done ("committed, checker OK").

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

End of step 12: ten lines at most. A sprint date after this week's Sunday: say the cards stay off the Execution board until that week. Name every card not on the board yet, with why. Then one exact paste per wave, each naming the sprint and the wave: `/bandit-dev:sprint execute {sprint} wave 1`, `... wave 2`, and so on, then `/bandit-dev:sprint debug {sprint}` and `/bandit-dev:sprint close {sprint}`. Never one generic paste for every wave.

## Handover

At step 12 write `references/templates.md` → Execution prompt and Ledger into the sprint folder. The execution prompt runs one wave per run without questions, merges passing cards into the local development branch, pushes `development` once at the end of the last code wave (never `main`, never a deploy) and then fills the staging handover card, keeps the ledger after every milestone and writes the handover test report. A new chat resumes from the ledger. The commands that run it are `execute`, `debug` and `close` (`references/execute.md`, `debug.md`, `close.md`). The prompt points to `execute.md` for board moves and the wave rules, to `debug.md` for bug reports and to `close.md` for closing; it carries no copy of their procedures. Its start paste names the wave.
