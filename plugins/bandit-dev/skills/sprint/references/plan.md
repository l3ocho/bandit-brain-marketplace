# 📋 The plan cycle, step by step

Part of `bandit-dev:sprint`. Read before running `/bandit-dev:sprint plan`. Card sections, lanes, stages and the Spec lock are owned by bandit:tasks (`references/dev.md`); vault paths and write rules by bandit:notes. This file only says how the steps run.

Contents: Conventions · Steps 1 to 12 · Investigator brief · Handover

## Conventions for every step

- **Order and evidence.** Do the step, write its comment on the sprint card, tick its sub-task. The comment says what was found and done, in a few lines, with ids.
- **Read before every write.** `get_task` right before any description or tag write. A card changed since the last read: use the new text.
- **Fix rows.** A problem is a numbered row: action, target, owner, recommendation (two options in one row, recommended first). Applied only on approval.
- **Decisions** go on the card they concern as a comment starting `Planning decisions {date}`, and into the Spec at step 9.
- **Date.** Today is in the session context. Convert "tomorrow" to an absolute date.

## 1 · Select and freeze the batch

1. Resolve the selection (SKILL.md). Open cards only, not archived, not in a `sprint/*` tag (`list_sprints`, `list_tasks` with `tagPrefix`). Cards already in a sprint are excluded with a fix row.
2. For every card read `blockedBy` and `blocks`. Report cards **outside** the batch that it blocks or is blocked by; none of them need links, but the sprint card records them under "Out of this sprint".
3. Create the sprint card in the `PM` column: title `Sprint {Name}` (name given, else the ISO week, `2026-w42`); description from `references/templates.md`; the 12 step names as sub-tasks, added **one at a time**, then **always** set with `reorder_subtasks` using the full explicit order and read back (insertion order cannot be trusted: new sub-tasks have landed at the top, reversed); `dependencies.blockedBy` = the batch. Verify with `get_task`.
4. **Sprint order.** Find the previous open sprint: `list_sprints` for sprints with open cards, then
   their sprint cards in the `PM` column (title `Sprint …`, not complete). One exists → `add_dependency`
   so the new sprint card is **blocked by** it. `run` and `execute` refuse a sprint card that an
   incomplete sprint card blocks, so sprints ship in order.
5. Comment: selection rule, count, ids, the sprint it waits for; list open Urgent cards as not selected.

**Done when** the card shows every batch card as a blocker, the previous open sprint card as a blocker
when there is one, and the 12 sub-tasks in order.

## 2 · Spec completeness check

For each card: `get_task`; find its brief (bandit:notes lookup by filename from the Spec's `Brief:` line); compare card and brief; check Outcome, Scope in and out, Acceptance, Decisions and Open questions exist; check referenced cards, files and idea ids resolve; note sub-tasks, tags, effort, complexity, lane and stage.

**Fix rows for:** missing sections, card and brief disagreement, an unresolved reference, a `Brief:` line carrying a folder (filename only).

## 3 · Close the open questions

1. Collect every open question across the batch, plus questions the checks raised.
2. **Investigate first, read-only, in parallel**: one investigator per card (brief below). One live-browser check at a time, only for what code cannot answer (touch behaviour, what the UI shows).
3. **Spot-check** the decisive facts in code before they go into a card.
4. Present **one list**, grouped by card, each with the finding and a recommendation. Decisions that need the user only; defaults go in a separate "applied unless you object" block.
5. Record the answers (comment per card). Ask follow-ups only for what the answers raise.
6. A large new requirement that surfaces: record the rule, create a parked card **outside** the sprint, ask one yes or no whether it joins.

**Done when** every question on every card is answered and recorded, or parked with its card.

## 4 · Size and classify

Effort and complexity per card; lane per card. Check the card boundaries in bandit:tasks `dev.md`: one lane, one branch, one landing, up to L; **XL splits into two or more cards** now. A split card keeps its Spec's intent, gets its own brief and Spec, blocks or is blocked by its sibling, and **joins the sprint** and the sprint card's blockers. Record old and new sizes in one comment.

## 5 · Cross-card analysis

**Migration tail.** Run `python3 ${CLAUDE_SKILL_DIR}/scripts/recipe.py tail` (the project's
`bandit.yaml` `migrations.check`) and write the tail the sprint starts from into the plan, then a
**Migration tail** table: one row per wave, the tail that wave must start from and the numbers it
adds. A missing key refuses by name: the project adds it to `bandit.yaml` before planning goes on.

From the investigations and a quick code check: migrations (one at a time, numbered in order), files several cards edit (state the order), hidden dependencies (what must land before another card's tests), generated artefacts that need regenerating after each card, tests that pin behaviour a card changes, docs each card must update. Output: one comment, and the "Cross-card" section of the plan.

## 6 · Sequence

**Split with the WBS.** Before drawing the waves, run `/bandit:plan wbs` for the batch in sprint mode (input: the batch cards and their briefs; skip its reconcile phase, which would edit the briefs; no size estimates). The WBS is its own note, `{project}-wbs.md` in `Projects/{slug}/planning/` (bandit:notes owns the path and the Card links rows; bandit:plan owns the format), and the plan note links it. Use each card's lowest-level tasks to see what truly depends on what; sizes stay with step 4. The WBS decides the wave split: a wave is a set of cards (or card pieces) that can be built and verified together. No wave split without it.

Waves with a reason each. Parallel only where cards touch different files and no migration is shared; merges, migrations and shared board components are sequential. Record the order on the sprint card (Order column).

## 7 · Write the one technical plan

One plan note in the sprint folder (template). Per card: approach, tests, docs, "Verify first", acceptance-to-proof table. Then fill each card's `Technical plan` section (outside the locked Spec, so no override): plan filename, branch, size, short bullets. Branch names follow the project's branching document; round numbers are taken at execution. The plan also carries a **Final push** section (the push of `development` to origin at the end of the last wave that changes code; the rules are `execute.md` → Pushing `development`), unless the user removes it at approval.

## 8 · Risk and rollback

In the plan: how rollback works for every card (code, schema, backups, deploy shape), then per card a table (risk, likelihood, impact, mitigation) and a rollback line, then sprint-wide risks.

## 9 · Definition of ready, per card

Ready means: Spec clear with no open questions, acceptance testable, dependencies resolved or sequenced, Technical plan written with filename, branch and size, effort at most L, plan note filed.

1. Check each card strictly and report who passes and who fails, with fix rows.
2. **Reconcile each Spec once**: answered questions into Decisions, open questions cleared, wrong lines fixed, acceptance lines brought in line with decisions. Show old and new per card in one table; on the user's yes write with the Spec-lock override, after `get_task`.
3. Update each brief: requirements, decisions with reasons, verified facts with where each was checked, no open questions, a dated **Change log** of what changed and why, and no card state (column, lane, stage) in the body.
4. Move passing cards to `stage/planned`, then `stage/ready` on the user's approval (step 10), through the stage procedure in bandit:tasks.

## 10 · Approval gate

Present the state in a short summary (cards, waves, plan, risks, what needs the user). Take the user's explicit approval or return to the step it names. Quote the approval on the sprint card. If the user's wording is ambiguous ("approved" mid-list), state the reading you applied in one line. **An urgency remark ("I want this today", "go fast") is not an approval of the plan**: put the summary in front of them and ask one yes or no. A date they give is used as the sprint date; it does not commit the sprint.

## 11 · Independent plan review

Automatic, after the approval and before the commit. It stops the user only on a blocker.

1. **Launch the `plan-reviewer` agent** (the Agent tool, `bandit-dev` agent `plan-reviewer`) and wait
   for it. Its prompt carries: the sprint name and card, the plan note's full text, each batch card's
   Spec and brief, the WBS, the Migration tail table, the repo path and the project's `bandit.yaml`.
2. **Write the review record** into the sprint folder: `{project}-review-sprint-{name}-YYYY-MM-DD.md`,
   `type: log`, `board-task` = the sprint card (bandit:notes conventions §1). Body: the agent's
   verdict and findings table as returned, then the risk additions and questions.
3. **Apply** every major finding, and each minor one that is cheap, to the plan (read, then the etag
   edit) and fill the record's "Applied via" column (`plan §…`, `card {id} Technical plan`). Notes stay.
4. **A blocker stops the step:** put the blockers to the user in one list, each with its recommendation;
   apply their answers, record them in the review, and re-run the review once if they change the plan's
   approach. This is the only stop the review adds.
5. Comment on the sprint card with the verdict, counts by severity and the record's filename.

**Done when** the review record is in the sprint folder, every major finding is applied and no
blocker is open. `run` and `execute` refuse a sprint whose step 11 sub-task is unticked; the checker
(SP7) fails a committed sprint with no review record.

## 12 · Commit the sprint

Per batch card: tag `sprint/{name}` (create the tag once; merge with the card's current tags), assign to the user (the signed-in member, live lookup), due date = the sprint date, `stage/ready`. Sprint card: assignee, due date, size (umbrella, usually XL and Complex), header filled (dates, owner, capacity = total effort), decisions log, readiness line. Write the execution prompt and the ledger (templates). **Add the wave sub-tasks last**: one per wave, at the very end of the sprint card after the 12 step sub-tasks, named `Wave {n}: {card ids}` (for example `Wave 2: {id}, {id}`), added one at a time, then **always** put the whole list in order with `reorder_subtasks` (12 steps first, then the waves) and read the card back to confirm. They stay unticked until the execution delivers and verifies that wave. Move every batch brief into the sprint folder (`Projects/{slug}/sprint-{name}/`) and archive every source the planning consumed (inbox drafts, spec notes, a superseded WBS draft; `references/homes.md` → Leftovers), then run `python3 ${CLAUDE_SKILL_DIR}/scripts/check_sprint.py` and paste its output into the step comment; step 12 is not ticked until it prints OK. Write `Committed: {date}` in the ledger's At a glance: the line the checker's SP7 reads. Seed the Execution board: every batch card to `assigned` with `bulk_set_execution_state` (so the user sees the whole sprint before work starts). Verify the board with `list_sprints`, `get_execution_board` and a read of the sprint card.

## Investigator brief

Read-only. Give each investigator: the card's Spec, the repo path, what to find, and the report shape.

1. Current state: what exists today that the card touches, with `file:line`.
2. The card's claims checked against the code; wrong ones named.
3. Constraints that apply (project hard rules, boundaries, tests that pin behaviour).
4. Risks, and the questions the user must answer, **each with a recommendation**.
5. Mark anything not verified. Do not edit, run migrations or touch credentials; do not propose scope or cards.

A live-browser investigator **at planning time** is told which controls write (sorts, toggles) on existing data, to open and cancel, and to report what it could not check. That read-only rule belongs to planning only; it never goes into an execution prompt or plan section.

## Test data (plan and execution prompt)

**Test data is never a reason to skip a test.** An execution-time check (ui-verifier, integration test, script) that needs data the dev database lacks (a folder, a second member, a private project, a card assigned to someone) creates that data itself, runs the check, and removes what it created. Reporting "could not exercise X because the dev database has no Y" is a failed check, not a limitation: the wave is not done until the case ran. The only limits are: never modify or delete a record the check did not create, never touch credentials, never run against production. Every plan section that lists a UI or live check must name the data the check needs and say the verifier builds it. At step 7, for each card with a live check, ask "what data does this case need, and does the dev database have it?"; if not, write the setup and cleanup into the plan section.

## Plan final message

End of step 12: ten lines at most, and one exact paste per wave, each naming the sprint card and the wave: `/bandit-dev:sprint execute {sprint card} wave 1`, `... wave 2`, and so on, then `/bandit-dev:sprint debug {sprint card}` and `/bandit-dev:sprint close {sprint card}`. Never one generic paste for every wave.

## Handover

At step 12 write `references/templates.md` → Execution prompt and Ledger into the sprint folder. The execution prompt runs one wave per run without questions, merges passing cards into the local development branch, pushes `development` once at the end of the last code wave (never `main`, never a deploy), keeps the ledger after every milestone and writes the handover test report. A new chat resumes from the ledger. The commands that run it are `execute`, `debug` and `close` (`references/execute.md`, `debug.md`, `close.md`). The prompt points to `execute.md` for board moves and the wave rules, to `debug.md` for bug reports and to `close.md` for closing; it carries no copy of their procedures. Its start paste names the wave.
