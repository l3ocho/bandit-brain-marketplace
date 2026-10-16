# 🔍 The debug cycle

Part of `bandit-dev:sprint`. Read before running `/bandit-dev:sprint debug {sprint card}`. Run in a fresh chat after the last wave is ticked. The user tests the delivered sprint and brings the adjustments; this chat turns them into verified fixes with the sprint's own documents and diff as context.

Contents: Rules · Read first · Intake · Fix loop · Board · Finishing · Never

## Rules

- **Documents first, then code.** Read the sprint folder before the diff, so each fix is judged against what was promised.
- **The user's words are the baseline.** Each adjustment is judged against what they asked for, never against the plan's summary of it.
- **Every adjustment is a row in the one decision table** (`references/plan.md` → Conventions), plain words, no numbers or codes: what the user saw, the card, the cause, the fix, the recommendation. A fix is applied only on the user's say-so, or under their standing "go with the recommendations".
- **Bug fixes for defects in delivered cards are not new scope.** New requirements are parked as a card outside the sprint, with one yes or no on whether they join.
- **Same authority as `execute`:** work on the trunk; pushes follow `execute.md` → Pushing `development`. Never deploy or touch production: release is its own command.

## Read first

0. **The ledger and the board win over memory.** A memory note that disagrees with them is stale: use the documents and say so in one line.
1. The sprint card: Spec-adjacent sections, decisions log, comments per step and wave.
2. In the sprint folder: plan, execution prompt, ledger (needs-the-user list, deviations, bug log, decisions taken without the user), the handover report and every brief with its change log.
3. The code changes: every card's branch and commit from the ledger, then the combined diff against the sprint's starting commit. Read the diff per card, not as one block.
4. State what each card promised in one line, so adjustments can be checked against it.

## Intake

1. The user gives adjustments in any form. Restate them in their own words as table rows, each tied to a card and to the document line or acceptance row it breaks, or marked "new".
2. Investigate read-only first, in parallel where cards differ (the investigator brief in `plan.md`). A live check at this stage writes nothing on existing data; if a case needs data the database lacks, it creates it and removes it afterwards, through `/bandit-dev:testdata` when the project has a `testdata` section (Test data in `plan.md`).
3. Present one list with a recommendation per row. Ask follow-ups only for what the answers raise.

## Fix loop

Per approved row, in card order and wave order where they interact:

1. Reproduce or confirm from the code. If it does not reproduce, say so and ask.
2. Fix with a test that fails against the old behaviour, then the gates in the execution prompt (code review, verify, UI check when the UI changed).
3. Commit on the local development branch (or the card's branch if it is still open).
4. Record in the ledger Bug log: row, card, cause, fix, commit, how verified. Update the handover report's card section.
5. Comment on the card: what was adjusted and why. Reopen nothing; the card stays in Stand By.

## Board

- A card with an adjustment moves `standby` → `doing` while being fixed, back to `standby` when done. The cap applies as in `execute.md`; a blocker never stops the move.
- Nothing is completed here. The user's approval and `close` do that.

## Finishing

**No leftovers.** Before this step ends, anything it used to make something else and no longer needs (a draft, a scratch file, a superseded copy, a test fixture, a temporary branch) is archived or deleted, only on proof that its successor exists (`references/homes.md` → Leftovers). A fix branch is deleted once merged; test data is removed.


Every row fixed, parked or declined with the user's word. Ledger Status per card moves to `Tested by the user` for every card the user says they tested; sprint card section 1 Status line becomes `Debug done, ready to release`. Ledger "At a glance" says debug is done; sprint card comment `Debug done: {n} adjustments, {n} parked. Ready to release.`; final message of ten lines at most with the paste for `release`.

## Never

- Rewrite a locked Spec (show old and new, get a yes, use the bandit:tasks Spec lock rules).
- Edit the plan after approval; live changes go in the ledger.
- Fix something nobody approved because it looked wrong. Raise it as a row.
- Complete cards, merge into `main`, deploy, force-push.
