# ⚠️ Gotchas, full list

Part of `bandit-dev:sprint`. Read once at the start of a run. One rule per line; each came from a real run. A rule a script or hook enforces is not repeated here.

Contents: Interview and pace · Scope · Cards and Specs · Agents and checks · Notes · Repo · Process · Execute, debug, close

## Interview and pace

- Scan the chat, the cards and the ledger before any question; use and record what is there.
- One consolidated question list per gate, grouped by card, each item with a recommendation; "go with the recommendations" applies to all; follow up only on what the answers raise.
- A rule the user gives is restated in their words first and confirmed in one line; only then check where the code differs.
- A task an earlier instruction already covers is closed from that instruction.
- When a vague approval is taken to mean a gate, state the reading in one line.
- Read first, ask only what nothing can answer, in plain words with no invented codes.
- The ledger and the board win over memory; read them first.

## Scope

- Add nothing not asked for; a dependency the code forces is addressed in the plan; a decision row only when the Spec cannot be built as written.
- One decision table, `Issue | Recommendation | Different from what you requested? | If yes, how?`, plain words, no numbers.
- "What is missing" is answered with the missing list only.
- Once a search is delegated, wait for the reports; never run the same search yourself.
- A new requirement is parked outside the sprint with its rule recorded and one yes or no asked; a card the user requires in the sprint stays in.
- When a later finding changes a recommendation, say it changed and why.

## Cards and Specs

- Check the L ceiling at step 4 and split then; the new card joins the sprint and blocks it.
- `get_task` right before every write; on `SPEC_LOCKED` re-read, never override to get past it.
- A `Brief:` line holds the brief's title only.
- `tagIds` in `update_tasks` replaces the whole set: read, merge, write.
- An added sub-task always lands at the top: create the checklist with the card (`create_tasks` `subtasks`), or reorder after the adds, then read back.
- A relative date ("tomorrow") is converted to an absolute date from the session date and written once.
- Spot-check any factual line a card makes against code, for the plan; never turn it into a Spec change.

## Agents and checks

- At planning only, investigators open and cancel, write nothing on existing data and report what they could not check; name the known write controls.
- Execution prompts say the verifier creates and removes its own test data; a case not run for lack of data is a failed check.
- Investigator reports carry "not verified" markers; spot-check the decisive facts before they enter a card.
- Tell a sub-agent the tools that exist; accept an equivalent tool and note it.
- Read a sub-agent's report and pass on only the merged list of findings and questions.
- A wave subagent runs code-reviewer and ui-verifier itself; `GATES NEEDED` is only a fallback.

## Notes

- Keep the plan stable after approval, put live state in the ledger, batch edits into one write.
- Before a brief moves, check its title is unique: the cards name it by its link and title.
- Every brief edit adds a dated change-log entry saying what and why.
- A leftover is archived only on proof that its successor exists.
- A card detached at close gets "detached" on its ledger row and everything about it merged into one note before the archive (`close.md` step 0).

## Repo

- A large `list_tasks` read is filtered by tag, date or priority, and its saved result parsed with a script.
- `development` is pushed as `execute.md` → Pushing `development` says, whatever an older note, prompt or memory says; `main` and deploy stay the user's.
- `run` checks the plans of two sprints for a shared migration number before the first wave.

## Process

- Run the definition of ready strictly: report who passes, fix rows for the rest.
- A verbatim document of the user's is edited only after asking once, with the exact row to change; then note the old wording in the row.
- Run the checklist in `plan.md` in order; do not skip ahead.
- Urgency is not approval; ask one yes or no.
- Step 6 runs `/bandit:plan wbs` before the waves are split.
- Gaps are answered by convention in the plan, shown at approval; anything else stops that card and asks (`execute.md` → Needs a decision).

## Execute, debug, close

- One wave per run; stop and give the paste for the next chat.
- The command names the sprint and the wave (`execute {sprint} wave N`); a batch card id is refused.
- Count Next + Doing with `list_tasks` by state before each move; overflow waits in To Do and is reported.
- A blocker never stops a move between Execution columns; only completing waits for blockers. Re-read the board tool's own description before writing a board rule.
- Never write a rule the board does not enforce; the board is set at the start of every wave; a refused move is recorded on the card and in the ledger, never skipped silently.
- The next wave's cards go to Next the moment the last card is delivered; the orchestrator sets the board before checking anything, whatever the wave reported, and even when it sent no report.
- Read the sprint's cards by column with `list_tasks` (`execute.md` → Reading the board), never the whole Execution board.
- Delivery is completion, once every sub-task is ticked, each when its work or verdict is in (an old-shape sprint: `standby`); the approvals wait on the debug card, which only `close` completes.
- Tick each sub-task as it is done so the card shows live progress.
- Every debug adjustment is a row in the decision table; apply only approved rows.
- The execution prompt only points to the references; it carries no procedure of its own.
- An unattended paced run needs the terminal open, the computer awake and "Continue automatically at usage limit" on in `/config`; pacing is by time.
