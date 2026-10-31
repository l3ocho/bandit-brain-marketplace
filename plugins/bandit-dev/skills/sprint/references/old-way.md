# 🕰️ Old-way sprints

Part of `bandit-dev:sprint`. Read when a command names a **sprint card** instead of a sprint. An
old-way sprint was planned before sprints were records in the app: a sprint card in the `PM` column
(title `Sprint {Name}`, the twelve step sub-tasks, then one `Wave n: {ids}` sub-task per wave, the
batch cards as its blockers) and a `sprint/{name}` tag on each batch card. This file keeps those
sprints running to their close. It goes once no old-way sprint is left (an open item in the app repo).

Contents: Recognise · What changes per command · Close · Never

## 🔎 Recognise

A card id whose card carries `Wave n:` sub-tasks is an old-way sprint. Every command runs on it
**whatever the Sprints switch** says, except Close, which creates a real sprint and so needs Sprints
on. A batch card is refused as in `execute.md`. No new sprint is planned this way: `plan` always
creates a real sprint.

## 🔁 What changes per command

Everything else in each reference applies as written.

| Where | A real sprint | Old way |
|---|---|---|
| Start (`execute.md`, `run.md`) | The ledger's Plan steps done to 12, its Waves table | The sprint card's twelve step sub-tasks ticked (step 11 the review), its wave sub-tasks present. **Order gate:** the sprint card blocked by an incomplete sprint card (`get_task` → `blockedBy`) |
| The batch | `get_sprints { sprintId }` → `cards` | The sprint card's blockers; while the tag exists also `list_tasks({ tagName: 'sprint/{name}' })` |
| Reading the board (`execute.md`) | `list_tasks({ sprintId, executionState })` | `list_tasks({ tagName: 'sprint/{name}', executionState })` while the tag exists; once the tags have retired, the batch's ids from the sprint card's blockers |
| Sprint status (`execute.md`) | The app's status moves | No status. **The sprint card** is not moved while any wave runs, goes to `standby` once, when the last card of the last wave reaches `standby`, is never `next` or `doing`, never counts in the five-item cap and is completed only by Close |
| Wave done (`execute.md` → Finishing a wave) | The ledger's Waves row | Also tick the wave's sub-task (`manage_subtasks { action: "tick" }`), only when every card is delivered and verified |
| Status line (every command) | The ledger's Status line | Also the sprint card's section 1 Status line (`get_task` first, change only that line) |
| Wave, debug, release notes | The ledger's Milestone log | Also one comment on the sprint card with the same line |
| `run`'s wave check | Waves row, sprint status | The wave sub-task ticked; the sprint card unmoved while waves remain and in `standby` after the last |
| The checker | SP9 and SP10 read the ledger's `Sprint record:` line | An old-way ledger has none, so SP9 and SP10 skip it; SP1 to SP7 hold. Never add that line to an old-way ledger |

## 🏁 Close

`close.md`'s preconditions first. Then bring the sprint into the app, in this order (each step is
forced by the app's rules: a card joins only while open, Ready to execute needs a date and a card,
Closed needs every card complete). Each step reads before it writes, so a close cut off halfway
resumes where it stopped.

1. **Sprints on.** `get_sprints { boardId }` on the sprint card's board answers; `MODULE_DISABLED` →
   say so and stop.
2. **Create the sprint:** `manage_sprints { action: "create", boardId, name: "{name}", papersUrl }`
   (the sprint folder's path). A sprint of that name already on the board from an earlier attempt:
   use it.
3. **Add its cards while they are open:** `manage_sprints { action: "add_cards", sprintId, taskIds }`
   with the batch in wave order. A card completed by hand before the close cannot join
   (`SPRINT_CARD_COMPLETED`): leave it out and name it in the ledger and the report.
4. **Date and status:** `update` `expectedDate` = the sprint card's due date, then `move` to
   `ready_to_execute`, then to `executing`. Read it back.
5. **Complete the cards:** `close.md` step 1.
6. **Close the sprint:** `move` to `closed` (Executing to Closed is the one skip).
7. **Retire the tag:** remove `sprint/{name}` from every batch card (`get_task`, merge, `update_tasks`
   with the full `tagIds`), then delete the tag once no card carries it (`delete_board_items`, kind
   tag). A refusal (`REQUIRES_ADMIN`) goes under "Needs the user".
8. **Complete the sprint card:** every sub-task ticked, section 1's Status line `Closed {date}: {n} of
   {n} cards delivered and tested by the user`, section 12 the same close-out as the ledger's Decisions
   log, then `update_tasks { items: [{ taskId, complete: true }] }`
   (its blockers are complete now).
9. **Archive the sprint card:** no tool sets a card's archive date, so the production handover card
   (the ledger's `Production handover:` line) is refilled, reopened first with `reopen_tasks` when the
   user closed it, with the one archive statement the app's runbook names
   (`handover.production.runbook`), copied, never written here. The runbook names none → one line
   under "Needs the user".
10. Then `close.md` steps 2 to 5 (statuses, archive, verify, report), with the sprint card's rows
    from this file.

## 🚫 Never

- Plan a new sprint the old way, or add a sprint card or a sprint tag to a real sprint
- Add the `Sprint record:` line to an old-way ledger
- Complete a batch card by hand to get past step 3, or skip a step of Close's order
