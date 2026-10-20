# ✍️ Capture

**Command:** `/bandit:tasks capture`
**Owns:** task creation · brain dumps · **the whole repeat-rule lifecycle**

---

## 🎯 The rule of capture

**Getting it in beats getting it right.**

A titled task in Untriaged is a success. An interrogation that ends with a perfectly-filed task is a failure — the next thing will not get captured.

**Ask at most one question, and only when the answer changes where it lands.** Everything else is Triage's job.

---

## ➕ Creating

`create_tasks { items: [{ title, … }] }` — one entry per task; only `title` is required. Read
`results`: one entry per task, a refusal on one doesn't undo the others (`references/board.md` → Many cards in one call).

| Field | Values |
|---|---|
| `dueDate` | `YYYY-MM-DD` |
| `dueTime` | `HH:MM` — **display only**, affects nothing |
| `priority` | Low 1 · Medium 2 · High 3 · Urgent 4 |
| `effort` | XS 1 · S 2 · M 3 · L 4 · XL 5 |
| `complexity` | Simple 1 · Medium 2 · Complex 3 |
| `description` | Simple HTML for bold, headings, lists |
| `tagIds` | See tags, below |

**Placement:**

| Given | Lands |
|---|---|
| No `projectId` | Untriaged |
| `projectId`, no column, no date | That project's Inbox — **parked** |
| `projectId`, no column, **with date** | The project's **first column** |
| `projectId` + `projectColumnId` | That column |

**No project named** → Untriaged from the domain's workflow project or a plain chat; from any other
project, the home board's Inbox (parked), so the card stays in this project's sight
(`references/scope.md`). A project named in the request must be in the domain.

🚫 **Never set `origin`.** It is only for a task created on behalf of another system, all three fields are required together, and none can ever be changed afterwards. A person asking for a task is not an origin.

---

## 🧠 Brain dumps

1. One task per line, titles only
2. One `create_tasks` call, one entry per line (split above 100)
3. Land them in **Untriaged** unless the project is obvious from the line itself
4. Report the count created, and every refused entry by title
5. Offer `/bandit:tasks triage`. Do not start triaging

⛔ Do not de-duplicate, re-order, re-word or merge lines during a dump. That is triage, and doing it here loses the user's own phrasing.

---

## ☑️ Subtasks

`manage_subtasks { action: "add", taskId, title }` — a plain checklist inside the task.

🔁 **Order.** A new task's checklist goes in its `create_tasks` entry as `subtasks`, top to bottom:
it is stored in the order given. `manage_subtasks` add puts the new line **at the top**, so after
adding lines that belong lower (or a promote): `get_task` → `manage_subtasks { action: "reorder",
subtasks: [{ id, position }] }` with **every** sub-task of the parent and its intended position
(0 = top; a partial list is refused). After any sub-task write, `get_task` and check the order. Still
wrong → tell the user which card.

- No dates, no priorities, no dependencies of their own
- **Ticking them all does not complete the parent**
- `manage_subtasks` with `action: "tick"` (`subtaskId`, `completed`) / `"rename"` (`subtaskId`, `title`) · delete: `delete_tasks { items: [{ kind: "subtask", subtaskId }] }`

`manage_subtasks { action: "promote", subtaskId }` when a line turns out to need its own date or dependency. It takes the parent's **project and column and nothing else** — no date, no priority, no effort, no complexity, no tags. It is removed from the parent. Returns the new `taskId`.

---

## 🔗 Dependencies

`link_tasks { blockerTaskId, blockedTaskId }`.

⛔ Refused when:

- it would create a cycle — the refusal names the link responsible
- **either task is recurring** — recurring tasks cannot take part in dependencies
- the blocker is due **after** the task it would block

Read links with `get_task`: in `blockedBy` and `blocks`, `id` is the **link** (pass to `delete_tasks { items: [{ kind: "link", dependencyId }] }`) and `taskId` is the other task. Confusing the two removes the wrong thing.

---

## 🔁 The recurrence vocabulary — complete

🔴 **This is the whole thing.** Anything outside it is **refused, never rounded to the nearest thing that fits.** Report the refusal. Do not substitute an approximation.

**The tool's `rule` schema is the source of truth.** Read it before telling the user a rule can't be done. When the schema and this table disagree, the schema wins: use it, and report the drift so this file gets fixed.

| Field | Values | Notes |
|---|---|---|
| `basis` | `schedule` · `completion` | **Required** |
| `every` | whole number ≥ 1 | **Required** |
| `unit` | `day` · `week` · `month` · `year` | **Required.** `year` unavailable with `completion` |
| `days` | list of weekdays, `1` = Mon … `7` = Sun | **Only with `unit: week`** (any other unit is refused). Picks the days a weekly rule fires on: Sun–Thu = `[7, 1, 2, 3, 4]`, every other Tuesday = `every: 2` + `[2]`. The due date sets which **weeks** fire, not which days: its own weekday isn't included unless listed. With `completion`, the next one is the first listed day after it's marked done |
| `weekdaysOnly` | boolean | Mon–Fri. Only with `schedule`, `every: 1`, `unit: day`. **There is no "every 3 weekdays"**. For any other set of days, use `unit: week` + `days` |
| `ends` | `{type: never}` · `{type: on, date}` · `{type: after, count}` | Omit for never. **Unavailable with `completion`** |

**`schedule`** fires on the calendar date whether or not the last one was done on time → rent, bills.
**`completion`** fires N periods after it is actually marked done → water the plants every 3 days.

**The anchor is the task's own due date.** Monthly repeats on that day of the month; yearly on that month and day. The first occurrence *is* the due date.

### 🚫 Not expressible — say so plainly

- "the second Tuesday of the month", "last Friday of the month" — no ordinal weekday in a month
- "twice a month" (e.g. the 1st and 15th) — a monthly rule has one day; weekly `days` can't express it
- "every 3 weekdays" — `weekdaysOnly` carries no interval
- any rule with an end date on a `completion` basis

---

## 🔧 The lifecycle

| Want | Call | What survives |
|---|---|---|
| New repeating task | `create_tasks { items: [{ title, dueDate, repeat: rule }] }` | `dueDate` **required** — it is the anchor and the first occurrence |
| Make an existing task repeat | `manage_recurrence { action: "attach", taskId, rule }` | Same id, subtasks, comments, tags |
| Read the rule | `manage_recurrence { action: "get", taskId }` | Also `nextDueDate` and `endedAt` |
| Change the rule | `manage_recurrence { action: "update", taskId, rule }` | Replaces it **whole** — read first, send complete |
| Stop repeating | `manage_recurrence { action: "end", taskId }` | Current occurrence becomes an ordinary task, same id, same date |

Every `manage_recurrence` action takes the `taskId` of any occurrence, never the series.

⛔ `attach` is refused when the task: already repeats · has **no due date** to anchor to · is already complete · takes part in a dependency.

⛔ `update` is refused on an ended series. The current occurrence keeps its id and everything attached; only its date moves to the first date the new rule produces — which for `completion` is today.

⚠️ **`get` returning `rule: null` means unreadable, not "no rule."** The series carries a rule this app cannot author. Do not approximate it to the nearest case. `NOT_RECURRING` is the code that actually means it does not repeat.

⚠️ A day interval divisible by 7 always reads back as weeks. Same rule, different words — not a discrepancy.

📌 **Only the current occurrence exists as a real task.** Completing one is what creates the next.

---

## 🏷️ Tags

The three axes, and the rule that `update_tasks` `tagIds` **replaces the whole set**, live in `references/board.md` → *Tags*. Read it before tagging.

📌 On a recurring task, tags live on the **series**. Every occurrence carries them.
