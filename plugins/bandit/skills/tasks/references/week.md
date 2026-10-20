# 📅 Week

**Commands:** `/bandit:tasks week` `/bandit:tasks review`
**Owns:** the Week board · workload · projections · `manage_recurrence { action: "skip" }`

---

## 🗓️ What the Week board is

`list_tasks { view: "week", weekStart?, assignee? }` — `weekStart` is a **Monday**, `YYYY-MM-DD`. Defaults to the current week.
A view takes only its own arguments and refuses any other filter, naming it.

| Column | When it appears |
|---|---|
| **Due** | Only when something is overdue. Holds everything overdue **at any age** |
| Mon → Sun | Always. One per day of the named week |

📌 **Seven columns or eight. Never an empty Due column.** If there is no Due column, nothing is overdue — say that rather than reporting an empty one.

---

## 👻 Projections

Recurring tasks appear on this board as **projections computed from the rule**, including on future dates where **no task row exists**.

🔴 A projection has no id. It cannot be:

- completed
- re-dated
- moved
- tagged

Only the **current occurrence** exists as a real task. Everything further out is arithmetic.

**When asked to act on a future occurrence:** say it is a projection, and name what *is* available — `manage_recurrence { action: "skip", taskId }` on the current one, or
`manage_recurrence { action: "update", taskId, rule }` to change the pattern.

---

## 📊 Workload

`list_tasks { view: "workload", start, end }` returns the tasks falling on each day across a range, for counting.

Use it to answer *"is this week overloaded"* — the Week board shows placement, workload shows density.

Both are counts. **Neither knows how long anything takes.** Weight by `effort` if the tasks carry it, and say that is what you did.

---

## ⚙️ Procedures

### `/bandit:tasks week` — read, then date on request

1. `list_tasks { view: "week" }`, filtered to the domain (`references/scope.md` → Filtering)
2. Report: overdue first (if the Due column exists), then day by day
3. Mark projections explicitly as recurring, not as tasks
4. Flag the heaviest day and any empty stretch
5. **Stop.** No writes, unless the user asks to plan or date the week: then run **Dating the week** below.

🪫 **If the board is empty**, check before concluding under-planning:
`list_tasks { completed: false }` — zero incomplete tasks means the board is **unpopulated**, which is a capture problem, not a planning one. Say which.

#### Dating the week — write, on request (folds the former week-planning verb)

1. Read the week first. Always
2. `list_tasks { completed: false, projectId }` for candidates — undated tasks in the domain's
   projects, the home board first (`[project]` narrows it to one of them).
   **`stage/ready` filter** (called by `/bandit:tasks pick-ready` on a dev project): add `tagId` = the
   `stage/ready` tag and `noTagWithPrefix: "sprint/"`, so only approved cards outside a sprint are
   candidates (a sprint's dates are its plan's, `references/dev.md` → Card fields). Nothing else changes
3. Propose dates as a list. One line per task
4. On confirmation: `update_tasks { items: [{ taskId, dueDate }, …] }`, ≤100 per call
5. Read `results` and report refused entries by name (`references/board.md` → Many cards in one call)

⚠️ Dating a **parked** task moves it into the project's first column. Say so before doing it in bulk — it changes where things live, not just when.

⛔ Dating is refused where it would put a task out of order with a dependency. The refusal names the other task.

⛔ Dating is refused outright on a recurring occurrence.

### `/bandit:tasks review` — read, then propose

1. `list_tasks { view: "week", weekStart }` for the week ending, filtered to the domain (`references/scope.md` → Filtering)
2. `list_events { start, end }` — every state change, with actor; keep the domain's tasks only
3. Separate by actor: `user` · `mcp` · `system` (the midnight job)
4. Report: completed · still overdue · rescheduled more than once
5. **Three or more reschedules on one task** → propose a resize or a drop. Once. Do not moralise

---

## ⏭️ Skipping

`manage_recurrence { action: "skip", taskId }` — the honest way past a week it did not happen. Completing it would claim it did.

🔴 **The next occurrence is a NEW task with a new id.** The id passed in no longer exists afterwards. Use the returned `taskId` for anything further in the same turn.

| Want | Use | Destroys |
|---|---|---|
| Not this time | `manage_recurrence { action: "skip", taskId }` | Nothing |
| Stop repeating, keep everything | `manage_recurrence { action: "end", taskId }` | Nothing |
| This occurrence gone entirely | `delete_tasks { items: [{ kind: "occurrence", taskId }] }` | Its subtasks and comments. **Confirm** |
| The whole thing, all history | `delete_tasks { items: [{ kind: "series", taskId }] }` | Everything, permanently. **Confirm** |

---

## 🔍 Enumerating future dates

`manage_recurrence { action: "list_occurrences", taskId, from, to }` — computed from the rule, creates nothing, never returns dates before the series started.

⛔ **Refused for a completion-anchored rule** (`RULE_CASE_NOT_SUPPORTED`). Its next date depends on when each one is actually done, so there is no calendar to list. Read `manage_recurrence { action: "get", taskId }` → `nextDueDate` instead.

An ended series returns no dates.
