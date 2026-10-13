# ⛔ Refusal codes

Read when a BanditBrains call comes back `{ ok: false, code, reason, relatedId? }`. Act on `code`,
show `reason`, and resolve `relatedId` (the task responsible) to a title before reporting. Never
retry a variant of the same call to get past a refusal. Codes are from the tools' own schemas unless
a row says otherwise.

## 🗂️ Codes

| Code | Means | Where | Do |
|---|---|---|---|
| `NOT_FOUND` | The id names nothing. Also what `get_task` returns for an unknown uuid or short id (checked 2026-10-09) | Any call that takes an id | Re-resolve the name live (`list_tasks`, `list_projects`); never guess the nearest match |
| `INVALID_ARGUMENTS` | A malformed call: a partial or gapped list in `reorder_subtasks` / `reorder_project_columns`, a filter value out of range | Reorders, `list_tasks` | Fix the call: reorders need **every** item, positions 0..n-1 once |
| `BLOCKED_BY_INCOMPLETE_TASK` | A blocker isn't complete. **Stand By is not complete** | `set_task_execution_state` → `doing`, and its bulk form (seen 2026-10-08, BB-94). The code on `next` and on `complete_task`: **unchecked** | Name the blocker and stop (`references/execution.md` → gates) |
| `TAG_RULE_VIOLATION` | Two `stage/*` tags, or `lane/incident` with a `stage/*` | `create_task`, `set_task_tags`, `bulk_set_task_tags` (per task) | Merge the tags right (`references/dev.md` → Tag merging) |
| `SPEC_LOCKED` | The write changes a Spec that holds text | `update_task` | Comment `Spec change needed:`, or override only on Leo's yes (`references/dev.md` → Spec lock) |
| `PROTECTED_COLUMN` | Backlog at position 0: no rename, no delete, never moved off 0 | `rename_project_column`, `delete_project_column`, `reorder_project_columns` | Correct. Report it; no workaround |
| `ORIGIN_TASK_READ_ONLY` | Another module created the task: its title, description, due date, priority and removal are that module's | `update_task`, `set_task_due_date`, `move_task`, `delete_task`, repeat-rule tools | You can still complete, move on Execution, tag, comment, set effort and complexity |
| `SYSTEM_OWNED_PROJECT` | The project is kept in step with another module (`systemOwner`) | `create_task`, `add_project_column` (other project tools: **unchecked**) | Tell Leo to change it there |
| `ROLE_CANNOT` | The household role doesn't allow it on this board | Any write | Stop: it is the role, not the arguments |
| `ASSIGNEE_NOT_ELIGIBLE` | The assignee can't take work in a restricted project | `create_task`, `update_task`, `update_repeat_rule` | Ask Leo who |
| `TASK_HAS_NO_PROJECT` | Assigning someone to a task with no project | `create_task`, `update_task` | File it into a project first |
| `REMINDER_NEEDS_DATE_AND_TIME` | A reminder without both a due date and a time | `create_task`, `update_task` | Set both, or no reminder |
| `NOT_RECURRING` | The task doesn't repeat. (`rule: null` is different: a rule this app can't author) | `get_repeat_rule` | `references/capture.md` → lifecycle |
| `RECURRING_NEXT_CHANGED` · `RECURRING_NOT_LATEST_COMPLETION` · `RECURRING_SERIES_ENDED` · `RECURRING_MULTIPLE_OPEN` | Reopening a recurring occurrence isn't safe | `uncomplete_task` | Report it; nothing changed |

## 🔕 Refusals with no documented code

The tool text names these refusals but not their code. Act on `reason`.

| Refusal | Where |
|---|---|
| Out of order with a dependency (the reason names every link) | `set_task_due_date`, `update_task`, `bulk_set_due_date` |
| Any write against a recurring occurrence's date rule, a cleared date, a completed occurrence | `update_task`, `set_task_due_date` |
| Already repeating, no due date, complete, or in a dependency | `attach_repeat_rule` |
| A rule outside the closed vocabulary (never rounded to the nearest fit) | All rule-authoring tools |
| A cycle, a recurring task, a blocker due after, a blocker with no project, 30 links | `add_dependency`, `create_task` (`dependencies`) |
| Back to Untriaged while it blocks something; a completed task | `move_task` |
| A whole bulk call: malformed or over 100 → **nothing changed** | Every `bulk_*` tool |
