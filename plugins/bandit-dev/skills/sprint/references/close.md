# 🏁 The close cycle

Part of `bandit-dev:sprint`. Read before running `/bandit-dev:sprint close {sprint card}`. Run only after debug and release are done. Archive rules are owned by bandit:notes (`references/conventions.md` §7); completion rules by bandit:tasks.

Contents: Preconditions · Steps · Never

## Preconditions

Check all, report any miss as a fix row, and stop:

1. Ledger "At a glance" says debug is done and no row is open (or debug never ran and the user says so: record that).
2. Every batch card is in `standby`, or already complete (the user may have completed some by hand: that is fine, close is idempotent). None has an open sub-task. An open sub-task: name it.
3. **The user's approval, or their statement that they tested them, is in this chat**, in their own words. Quote it in the ledger and on the sprint card. Nothing from an earlier chat counts. If they cover only some cards, close only those and leave the rest.
4. **A release line.** The ledger has a `Released:` line (written by `release`), unless the user says "close without release" in this chat: quote it in the ledger. Neither → refuse and give the paste for `release`.
5. Nothing needs the user that blocks closing. The ledger's needs-the-user list is read to them once; items for deploy, or a push that failed, stay open and go to the sprint card comment (step 5), they do not block.

## Steps

Read the live state first (`get_task` for every card and the sprint card, the ledger, the report). **Every step checks before it writes: a state already correct is left alone and reported as "already done".**

1. **Complete the cards.** `update_tasks { items: [{ taskId, complete: true }, …] }` for the approved batch cards not yet complete. Chained batch cards complete blockers first: a card cannot be completed while a blocker is incomplete, so call it for the cards with no incomplete blocker, then again for the cards they unblocked, until none remain. Read `results` entry by entry: a refused entry does not undo the others. A refusal on a blocker outside the batch: name it and stop that card.
2. **Reconcile the statuses (the checklist).** Each row is checked against its live value and written only if different. One `get_task` immediately before each card or note write.

   | Where | Field | Becomes |
   |---|---|---|
   | Batch cards | completed, Execution column | Done (step 1). Sub-tasks all ticked. Tags `sprint/{name}` and `stage/ready` stay: stage has no done value |
   | Sprint card sub-tasks | 12 steps and every wave | All ticked, each with its comment already on the card |
   | Sprint card section 1 | Status line | `Closed {date}: {n} of {n} cards delivered and tested by the user` |
   | Sprint card section 12 | Approval and close-out | The user's quoted approval and date, what shipped, what carried over, where the report lives, lessons |
   | Sprint card | completion | `update_tasks { items: [{ taskId, complete: true }] }`, only once every blocker is complete |
   | Ledger, At a glance | Current wave, Next action, Handover report, Last update | "Sprint closed", "none", FINAL, today |
   | Ledger, Waves and cards | Status per card | `Tested by the user` |
   | Ledger | Milestone log | One line: close date, approval quoted, cards completed |
   | Handover report | Status marker | FINAL, with the regression list filled or marked "not run" with the reason |
   | Plan, briefs, ledger, prompt, report | `status` | `done` (stamped in step 3 together with the archive stamps) |

3a. **Cards that do not close (detached or carried).** For every batch card left open (one detached to the next sprint, or one that waits for a trigger): remove its `sprint/{name}` tag and its link to the sprint card, leave it in Backlog, and write "detached" on its ledger row. **Then merge everything the sprint knows about it into one note, in the inbox, before the archive**: its brief (same filename, so the card's `Brief:` line still resolves; `status: inbox`, `file-to:`), plus what the plan, ledger and report say about the card (state, remaining steps, findings, decisions, acceptance-to-proof) in a closing section. The original leaves the sprint folder (it is moved, not copied). One document per card; the next `plan` files it into the next sprint folder. The checker enforces it (SP2 skips a detached card, SP6 fails a second brief for the same card).
3. **Archive the sprint folder through bandit:notes.** Folder `Projects/{slug}/sprint-{name}/` moves to `_archive/Projects/{slug}/sprint-{name}/`, every note stamped `status: done`, `archived-from` and `archived`, mirror folders listed in the proposal, applied on the user's yes (one numbered proposal for the whole folder). Briefs, report and ledger go with it, and any leftover the sprint consumed outside its folder (an inbox draft, a superseded copy) is archived in the same proposal. Ledger edits in step 2 are made **before** the move, so the archived copy is final.
4. **Verify.** Run `python3 ${CLAUDE_SKILL_DIR}/scripts/check_sprint.py` and show its OK. Re-read live state and show it: `list_tasks({ tagName: 'sprint/{name}', completed: true })` (cards in Done), `list_tasks { view: "sprint" }` (sprint closed), the sprint card (every sub-task ticked, section 1 and 12 filled), the vault listing (folder under `_archive/`, nowhere else) and one archived note's frontmatter. Any row still wrong is fixed or reported, not skipped.
5. **Report.** Ten lines at most: cards completed, sprint card completed, statuses reconciled, folder archived, what stays open (push, deploy, production audits, `CLAUDE.md` corrections) and the line to restore if needed. Open items go on the sprint card as one comment so they stay visible after the archive.

## Never

- Complete a card the user has not approved or confirmed tested in this chat, or infer approval from the debug result.
- Write a status that is already correct, or overwrite a card or note without reading it first.
- Delete anything. Archive mirrors the path and can be reversed.
- Archive before the cards are complete, or complete the sprint card before its blockers.
- Merge into the deploy branch or deploy: that is `release`, on the user's deploy word. Close does not push; execution and debug push `development`, and close only reports whether it is level with origin.
