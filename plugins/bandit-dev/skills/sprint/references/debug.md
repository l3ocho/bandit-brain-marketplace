# 🔍 The debug cycle

Part of `bandit-dev:sprint`. Read before running `/bandit-dev:sprint debug {sprint}`. Run in a fresh chat after the last wave is done. The user tests the delivered sprint and brings the adjustments; this chat turns them into verified fixes with the sprint's own documents and diff as context.

Contents: Rules · Read first · Intake · Combined test · Fix loop · Pushing · Board · Finishing · Never

## Rules

- **Documents first, then code.** Read the sprint folder before the diff, so each fix is judged against what was promised.
- **The user's words are the baseline.** Each adjustment is judged against what they asked for, never against the plan's summary of it.
- **Every adjustment is a row in the one decision table** (`references/plan.md` → Conventions), plain words, no numbers or codes: what the user saw, the card, the cause, the fix, the recommendation. A fix is applied only on the user's say-so, or under their standing "go with the recommendations".
- **The debug list holds defects only:** what does not match its card's Spec or the project's approved design. A visual point is checked against the card's design handover (its files are found through the `Handover:` line: the design card's, or the build card's own Source without a design card; the `Design:` line is the page to look at) before it is called a defect. Anything new (more than the card asked for, a better layout, an idea) goes to the board as a card for a later sprint, through bandit:tasks capture, with no question about joining this one.
- **Same authority as `execute`:** work on the trunk; pushes follow `execute.md` → Pushing `development`, staging handover included: each debug push refills the staging handover card with the new hash, so every build the user tests on staging comes with its card (a card the user already closed is reopened with `reopen_tasks`, then refilled). Never deploy or touch production: release is its own command.

## Read first

0. **The ledger and the board win over memory.** A memory note that disagrees with them is stale: use the documents and say so in one line.
1. The sprint (`get_sprints { sprintId }`: status, cards in run order) and the ledger's Plan steps, Waves and Decisions log.
2. In the sprint folder: plan, execution prompt, ledger (needs-the-user list, deviations, bug log, conventions applied), the handover report and every brief with its change log.
3. The code changes: every card's branch and commit from the ledger, then the combined diff against the sprint's starting commit. Read the diff per card, not as one block.
4. State what each card promised in one line, so adjustments can be checked against it.

## Intake

1. **The debug card first.** Move the sprint's debug card (`Debug card:` in the ledger) to `doing` (`update_tasks`, read back; a refused move is a Process line and a line under "Needs the user", never a stop). Read it: its `Expected:`, `Found:` and `Process:` lines are the starting list. Every point the user raises in chat becomes a `Found:` line on it before it is worked (`references/templates.md` → Debug card). The user gives adjustments in any form, questions included (a question that ends in a choice is an adjustment). Restate them in their own words as table rows, each tied to a card and to the document line, acceptance row or design point it breaks. One that breaks none is new: a card for a later sprint (Rules).
2. Investigate read-only first, in parallel where cards differ (the investigator brief in `plan.md`). A live check at this stage writes nothing on existing data; if a case needs data the database lacks, it creates it and removes it afterwards, through `/bandit-dev:testdata` when the project has a `testdata` section (Test data in `plan.md`).
3. Present one list with a recommendation per row. Ask follow-ups only for what the answers raise.

## Process lines

A build, check, push, gate, board move or run of this command that stalls or fails writes its Process line on the debug card at once (`references/templates.md` → Debug card, Process lines); the fix or the lesson ticks it.

## Combined test

For a sprint whose Marketplace cards change the helpers along with the app: the user tests both together on staging before either is released.

1. **The test session.** The helpers come from the marketplace repo, loaded by path in a separate session (the repo's own test launcher), never the installed copy; the production board server is blocked and the staging one used.
2. **Prove it first,** from the session's startup record, not its answer: which plugins loaded and from where, which board server it called. A run that called production does not count: say so and run it again.
3. **Before each round,** compare the sprint's cards on staging with production: staging is a copy from its last refresh. Bring their columns in line, or name what differs.
4. Each case the helpers need runs through the test session; its log is the evidence in the Bug log.
5. Release then ships the app, and the helpers right after it (`release.md` → Marketplace cards).

## Fix loop

Per approved row, in card order and wave order where they interact:

1. Reproduce or confirm from the code. If it does not reproduce, say so and ask.
2. Fix with a test that fails against the old behaviour. Then the fix's own gates, lighter than a wave's: the targeted tests of the files it touched, code review, and the UI check only on the screens the fix changed. No full check per fix: it runs once before each push (Pushing).
3. Commit on the local development branch (or the card's branch if it is still open).
4. Record in the ledger Bug log: row, card, the debug card line it fixes, cause, fix, commit, how verified (the targeted tests it ran, by name or pattern). Tick that line, or end it with its outcome (`templates.md` → Debug card). Update the handover report's card section.
5. Comment on the card: what was adjusted and why. Reopen nothing; the card stays in Stand By.

## Pushing

Several fixes may share one push. Right before each push of `development` (the push that refills the staging handover card, Rules): one full check, the recipe's `verify`, on the code being pushed. Red stops the push: fix it first, as a row of its own if it is a new defect. The Milestone log names that full check (green, and the commit it ran on) next to the push.

## Board

- A card with an adjustment moves `standby` → `doing` while being fixed, back to `standby` when done. The cap applies as in `execute.md`; a blocker never stops the move.
- Nothing is completed here, and the approval line is never ticked here (`templates.md` → Approval line). The user's approval and `close` do that.

## Finishing

**No leftovers.** Before this step ends, anything it used to make something else and no longer needs (a draft, a scratch file, a superseded copy, a test fixture, a temporary branch) is archived or deleted, only on proof that its successor exists (`references/homes.md` → Leftovers). A fix branch is deleted once merged; test data is removed.


Every row fixed or declined with the user's word; anything new filed as a card. Ledger Status per card moves to `Tested by the user` for every card the user says they tested; every debug card line (a Process line too: fixed, or its lesson recorded) is ticked with its outcome and the wave report's Debug section counts them (`templates.md` → Debug card); the ledger's Status line becomes `Debug done, ready to release`, and At a glance says debug is done; Milestone log `Debug done: {n} adjustments, {n} new cards. Ready to release.` The sprint stays `debugging`; final message of ten lines at most with the paste for `release`.

## Never

- Rewrite a locked Spec (show old and new, get a yes, use the bandit:tasks Spec lock rules).
- Edit the plan after approval; live changes go in the ledger.
- Fix something nobody approved because it looked wrong. Raise it as a row.
- Complete cards, merge into `main`, deploy, force-push.
