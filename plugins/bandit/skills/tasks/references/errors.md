# ⛔ Refusal codes

Read when a Bandit Brain call, or one entry of it, comes back `{ ok: false, code, reason, field,
relatedId? }`. Act on `code`, show `reason`, and resolve `relatedId` (the task responsible) to a
title before reporting. Never retry a variant of the same call to get past a refusal. Codes are from
the tools' own schemas unless a row says otherwise.

## 📦 The answer shape

- **Array calls** (`create_tasks`, `update_tasks`, `reopen_tasks`, `delete_tasks`,
  `delete_board_items`) answer `{ ok, applied, refused, results }`, one result per entry, in order.
  **One entry's refusal does not undo the others.** Read `results` and report every refused entry
  by card name with its reason; a partly applied call is a success. The whole call is refused,
  **nothing changed**, only when `items` is malformed or holds more than 100.
- **One `update_tasks` entry is all or nothing**: refused → nothing on that card changed.
- **`field`** names the argument that failed, as a path (`items[2].tagIds`). Use it to say which
  part of which entry was refused.
- 👶 **A child's assistant** lists only `get_context`, `list_tasks`, `get_task`, `create_tasks`,
  `update_tasks` and `manage_subtasks`. Any other tool is refused with `ROLE_CANNOT`.

## 🗂️ Codes

| Code | Means | Where | Do |
|---|---|---|---|
| `NOT_FOUND` | The id names nothing. Also what `get_task` returns for an unknown uuid or short id (checked 2026-10-09); in an array call, a malformed id is that entry's `NOT_FOUND` | Any call that takes an id. `update_tasks` by origin with no match: not an error | Re-resolve the name live (`list_tasks`, `get_context`); never guess the nearest match |
| `INVALID_ARGUMENTS` | A malformed call: a partial or gapped list in `manage_subtasks { action: "reorder" }` / `manage_columns_lanes { action: "reorder" }`, a filter value out of range | Reorders, `list_tasks` | Fix the call: reorders need **every** item, positions 0..n-1 once |
| `BLOCKED_BY_INCOMPLETE_TASK` | A blocker isn't complete. **Stand By is not complete** | `update_tasks` with `executionState: "doing"` (seen 2026-10-08). The code on `next` and on `complete: true`: **unchecked** | Name the blocker and stop (`references/execution.md` → gates) |
| `TAG_RULE_VIOLATION` | Two `stage/*` tags, or `lane/incident` with a `stage/*` | `create_tasks`, `update_tasks` (`tagIds`), per entry | Merge the tags right (`references/dev.md` → Tag merging) |
| `SPEC_LOCKED` | The write changes a Spec that holds text | `update_tasks` (`description`) | Settled change → override and report; not settled → comment `Spec change needed:` (`references/dev.md` → Spec lock) |
| `PROTECTED_COLUMN` | Backlog at position 0: no rename, no delete, never moved off 0 | `manage_columns_lanes` (rename, reorder), `delete_board_items` (column) | Correct. Report it; no workaround |
| `ORIGIN_TASK_READ_ONLY` | Another module created the task: its title, description, due date, priority and removal are that module's | `update_tasks`, `delete_tasks`, `manage_recurrence` | You can still complete, move on Execution, tag, comment, set effort and complexity |
| `SYSTEM_OWNED_PROJECT` | The project is kept in step with another module (`systemOwner`) | `create_tasks`, `update_tasks`, `manage_subtasks`, `manage_projects`, `manage_columns_lanes`, `manage_tags`, `delete_board_items` | Tell the user to change it there |
| `ROLE_CANNOT` | The household role doesn't allow it on this board, or a child's assistant called a tool outside its six | Any write; for a child, any tool outside the six | Stop: it is the role, not the arguments |
| `ASSIGNEE_NOT_ELIGIBLE` | The assignee can't take work in a restricted project | `create_tasks`, `update_tasks`, `manage_recurrence { action: "update" }` | Ask the user who |
| `TASK_HAS_NO_PROJECT` | Assigning someone to a task with no project (a move in the same entry counts) | `create_tasks`, `update_tasks` | File it into a project first |
| `REMINDER_NEEDS_DATE_AND_TIME` | A reminder without both a due date and a time | `create_tasks`, `update_tasks` | Set both, or no reminder |
| `NOT_RECURRING` | The task doesn't repeat. (`rule: null` is different: a rule this app can't author) | `manage_recurrence { action: "get" }` | `references/capture.md` → lifecycle |
| `RECURRING_NEXT_CHANGED` · `RECURRING_NOT_LATEST_COMPLETION` · `RECURRING_SERIES_ENDED` · `RECURRING_MULTIPLE_OPEN` | Reopening a recurring occurrence isn't safe | `reopen_tasks` | Report it; nothing changed |

## 🔕 Refusals with no documented code

The tool text names these refusals but not their code. Act on `reason` and `field`.

| Refusal | Where |
|---|---|
| Out of order with a dependency (the reason names every link) | `update_tasks` (`dueDate`) |
| Any write against a recurring occurrence's date rule, a cleared date, a completed occurrence | `update_tasks` (`dueDate`) |
| Already repeating, no due date, complete, or in a dependency | `manage_recurrence { action: "attach" }` |
| A rule outside the closed vocabulary (never rounded to the nearest fit) | `create_tasks` (`repeat`), `manage_recurrence` (attach, update) |
| A cycle, a recurring task, a blocker due after, a blocker with no project, 30 links | `link_tasks`, `create_tasks` (`dependencies`) |
| Back to Untriaged while it blocks something; a completed task | `update_tasks` (`projectId`) |
| Two entries for one task (merge them) | `update_tasks` |
| A view given another filter, or an action given another action's argument (the refusal names it) | `list_tasks { view }`, `manage_*` |
