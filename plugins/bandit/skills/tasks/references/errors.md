# ⛔ Refusal codes

Read when a Bandit Brain call, or one entry of it, comes back `{ ok: false, code, reason, field,
relatedId? }`. Act on `code`, show `reason`, and resolve `relatedId` (the task responsible) to a
title before reporting. Never retry a variant of the same call to get past a refusal. Codes are from
the app's own refusal set and the tools that return them.

## 📦 The answer shape

- **Array calls** (`create_tasks`, `update_tasks`, `reopen_tasks`, `delete_tasks`,
  `delete_board_items`) answer `{ ok, applied, refused, results }`, one result per entry, in order.
  **One entry's refusal does not undo the others.** Read `results` and report every refused entry
  by card name with its reason; a partly applied call is a success. The whole call is refused,
  **nothing changed**, only when `items` is malformed or empty (`INVALID_ARGUMENTS`) or holds more
  than 100 (`BULK_SET_TOO_LARGE`).
- **Entries run in list order.** In `update_tasks`, list a blocker before the cards it blocks.
- **One `update_tasks` entry is all or nothing**: refused → nothing on that card changed.
- **`field`** names the argument that failed, as a path (`items[2].tagIds`). Use it to say which
  part of which entry was refused.
- 👶 **A child's assistant** lists only `get_context`, `list_tasks`, `get_task`, `create_tasks`,
  `update_tasks` and `manage_subtasks`. Any other tool is refused with `ROLE_CANNOT`.

## 🗂️ Codes

| Code | Means | Where | Do |
|---|---|---|---|
| `NOT_FOUND` | The id names nothing, or something hidden from you. Also an unknown or deleted task in `get_task`, an unknown short id, and a malformed id (in an array call, that entry's `NOT_FOUND`) | Any call that takes an id. `update_tasks` by origin with no match: not an error | Re-resolve the name live (`list_tasks`, `get_context`); never guess the nearest match |
| `NOT_VISIBLE_TO_MEMBER` | The task is in your household but not shared with you | Writes on a task by id: `update_tasks`, `reopen_tasks`, `delete_tasks`, `manage_subtasks`, `manage_recurrence` | Tell the user it is not shared with them; stop |
| `INVALID_ARGUMENTS` | A malformed call: a missing or wrong-type argument, a bad date, `weekStart` not a Monday, a `view` with another filter, an action given another action's argument, a patch naming no change, two entries for one task (the first applies), a partial or gapped reorder, a filter value out of range, a malformed rule, a recurring occurrence's date cleared, a rule attached to a task with no due date | Every tool | Fix the call: reorders need **every** item, positions 0..n-1 once; merge two entries for one task |
| `UNKNOWN_FIELD` | An argument the tool or entry does not take; the reason lists what it takes | Structure tools, array-call entries | Fix the call |
| `BULK_SET_TOO_LARGE` | More than 100 entries: the whole call is refused, nothing changed | The array calls | Split the set and call again |
| `INTERNAL` | The server failed; the same call will fail again | Any tool | Report it; no retry |
| `BLOCKED_BY_INCOMPLETE_TASK` | A blocker isn't complete. **Stand By is not complete**. Moving a blocked card to Next or Doing is not refused | `update_tasks` with `complete: true`, also by origin | Name the blocker and stop; list blockers before their dependents (`references/execution.md` → gates) |
| `DONE_REACHED_BY_COMPLETION_ONLY` | Done is not a state you set | `update_tasks` (`executionState: "done"`) | Use `complete: true` |
| `COMPLETED_CANNOT_MOVE` | A completed task can't move, or take a repeat rule | `update_tasks` (`boardId`, `executionState`), `manage_recurrence { action: "attach" }` | Report it; reopen first only if the user asks |
| `DEPENDENCY_CYCLE` | The link would make a loop, or a task block itself; the reason names the link responsible | `link_tasks`, `create_tasks` (`dependencies`) | Report the link; no workaround |
| `DEPENDENCY_DATE_ORDER` | A blocker would be due after the task it blocks; the reason names **every** link | `link_tasks`, `create_tasks` (`dependencies`), `update_tasks` (`dueDate`) | Report the links; clearing them is a separate call, after the user agrees |
| `DEPENDENCY_LIMIT` | A task already holds 30 links, both directions counted | `link_tasks`, `create_tasks` (`dependencies`) | Report it; the user picks a link to remove |
| `DEPENDENCY_AUDIENCE` | Someone who can see the blocked task can't see the blocker | `link_tasks`, `create_tasks` (`dependencies`) | Report it; the reason names neither card |
| `ALREADY_LINKED` | The link exists | `link_tasks`, `create_tasks` (`dependencies`) | Nothing to do; say so |
| `RECURRING_CANNOT_DEPEND` | A recurring task can't take part in a link | `link_tasks`, `create_tasks` (`dependencies`), `manage_recurrence { action: "attach" }` on a linked task | Report it; no workaround |
| `TAG_RULE_VIOLATION` | Two `stage/*` tags, or `lane/incident` with a `stage/*` | `create_tasks`, `update_tasks` (`tagIds`), per entry | Merge the tags right (`references/dev.md` → Tag merging) |
| `TAG_WRONG_BOARD` | A Board tag of another board, or on a card with no board | `create_tasks`, `update_tasks` (`tagIds`) | Use an App tag or this board's own |
| `SPEC_LOCKED` | The write changes a Spec that holds text | `update_tasks` (`description`) | Settled change → override and report; not settled → comment `Spec change needed:` (`references/dev.md` → Spec lock) |
| `PROTECTED_COLUMN` | Backlog at position 0: no rename, no delete, never moved off 0 | `manage_columns_lanes` (rename, reorder), `delete_board_items` (column) | Correct. Report it; no workaround |
| `BOARD_ARCHIVED` | The board is archived: it takes no writes until restored | Card writes on its tasks, a move or create into it, `manage_columns_lanes` | Report it; restoring is the user's call |
| `ORIGIN_TASK_READ_ONLY` | Another module created the task: its title, description, due date, priority and removal are that module's | `update_tasks`, `delete_tasks`, `manage_recurrence` | You can still complete, move on Execution, tag, comment, set effort and complexity |
| `ORIGIN_FIELD_READ_ONLY` | A task's origin never changes | `update_tasks` entry with a `taskId` and an origin | Drop the origin, or name the origin alone to complete its cards |
| `ORIGIN_INCOMPLETE` · `ORIGIN_LINK_NOT_IN_APP` | An origin needs system, reference and link; the link is a path in the app | `create_tasks` (`origin`) | Fix it, or leave `origin` out for anything a person asked for |
| `SYSTEM_OWNED_BOARD` | The board is kept in step with another module (`systemOwner`) | `create_tasks`, `update_tasks` (move), `delete_tasks` (series), `manage_subtasks` (promote), `manage_recurrence`, `manage_boards`, `manage_columns_lanes`, `manage_tags`, `set_visibility`, `delete_board_items` | Tell the user to change it there |
| `ROLE_CANNOT` | The household role doesn't allow it on this board, or a child's assistant called a tool outside its six | Any card write; a Board tag in `manage_tags` or `delete_board_items`; for a child, any tool outside the six | Stop: it is the role, not the arguments |
| `ASSISTANT_CANNOT` | An assistant never does this: complete, reopen or delete a card another member created; change a board's sharing; delete a board or column | `update_tasks` (`complete`), `reopen_tasks`, `delete_tasks`, `set_visibility`, `delete_board_items` | Tell the user to do it in the app |
| `REQUIRES_ADMIN` | Only the board's creator or the admin may do this; App tags are the admin's | `manage_boards`, `manage_columns_lanes`, `set_visibility`, `delete_board_items`, `manage_tags` | Name who can; stop |
| `BOARD_HAS_OTHERS_CARDS` | Not the admin, and the board holds other people's cards | `manage_boards` (archive), `delete_board_items` (board) | Ask the admin to do it |
| `RESTRICTED_BOARD_NEEDS_MEMBER` | Narrowing a board with no creator on record to nobody | `set_visibility` (`memberIds`) | Name at least one member |
| `SHORT_PREFIX_TAKEN` | Another board uses that card id prefix (`relatedId`) | `manage_boards` (`shortPrefix`) | Offer another prefix; the user picks |
| `TAG_SYSTEM_LOCKED` | A System tag (`lane/*`, `stage/*`) is locked for everyone | `manage_tags` (update, promote), `delete_board_items` (tag) | Correct. Report it; no workaround |
| `TAG_NAME_TAKEN` · `TAG_NAME_RESERVED` | The name is another tag's, or starts with `lane/`, `stage/` (or `sprint/` for a Board tag) | `manage_tags` (create, update, promote) | Offer another name; the user picks |
| `FOLDER_NESTING_DEPTH` | Folders nest one level only | `manage_folders` (`parentFolderId`) | Nest it at the top level instead |
| `ASSIGNEE_NOT_ELIGIBLE` | The assignee can't take work on a restricted board, or is not on the account's list of a card another module made | `create_tasks`, `update_tasks`, `manage_recurrence` (update, set_assignee) | Ask the user who |
| `TASK_HAS_NO_BOARD` | The task has no board: it can't be assigned, completed, block a task or repeat, and can't go back to Untriaged while it blocks one | `create_tasks`, `update_tasks`, `link_tasks`, `manage_recurrence { action: "attach" }` | File it into a board first, or remove the link |
| `REMINDER_NEEDS_DATE_AND_TIME` | A reminder without both a due date and a time | `create_tasks`, `update_tasks` | Set both, or no reminder |
| `RECURRING_CANNOT_RESCHEDULE` | An occurrence's time and reminder are the series'; a completed occurrence keeps its date | `update_tasks` (`dueTime`, `reminderEnabled`, `dueDate`) | Change the series (`manage_recurrence` update), or report it |
| `RECURRING_CANNOT_DELETE` | Deleting an occurrence as a card would stall its series | `delete_tasks` (kind card) | Use kind `occurrence` or `series`, as the user means |
| `RECURRING_CANNOT_PROMOTE` | A sub-task of an occurrence can't become a task | `manage_subtasks { action: "promote" }` | Create a task with its text instead, if the user wants |
| `TASK_ALREADY_RECURRING` | The task already repeats | `manage_recurrence { action: "attach" }` | Use `update` to change the rule |
| `NOT_RECURRING` | The task doesn't repeat. (`rule: null` is different: a rule this app can't author) | `manage_recurrence` (every action but attach), `delete_tasks` (series, occurrence) | `references/capture.md` → lifecycle |
| `RULE_CASE_NOT_SUPPORTED` | A rule outside the closed vocabulary, never rounded to the nearest fit; on `action: "list_occurrences"`, a completion-anchored rule | `create_tasks` (`repeat`), `manage_recurrence` (attach, update, and `action: "list_occurrences"`) | Report it; offer the nearest rule the app can author, the user picks |
| `RULE_YIELDS_NO_OCCURRENCE` | The rule never fires, e.g. its end date is past | `create_tasks` (`repeat`), `manage_recurrence` (attach, update) | Fix the end, after the user agrees |
| `SERIES_UNREADABLE` | The stored rule can't be read; nothing changed | `update_tasks`, `reopen_tasks`, `delete_tasks`, `manage_recurrence` | Report it; the user fixes it in the app |
| `RECURRING_NEXT_CHANGED` · `RECURRING_NOT_LATEST_COMPLETION` · `RECURRING_SERIES_ENDED` · `RECURRING_MULTIPLE_OPEN` · `RECURRING_COMPLETION_UNVERIFIABLE` | Reopening a recurring occurrence isn't safe | `reopen_tasks` | Report it; nothing changed |

## 🔕 Refusals with no documented code

None. Every refusal the tools return carries a code from the table above. If one ever comes back
without a code, act on `reason` and `field`, and report it.
