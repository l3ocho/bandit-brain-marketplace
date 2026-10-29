# ▶️ Execution

**Commands:** `/bandit:tasks today` `/bandit:tasks doing` `/bandit:tasks done` `/bandit:tasks bump`
**Owns:** the six Execution columns · the dependency gate · the five-item cap

---

## 🗂️ The six columns

`list_tasks { view: "execution" }` returns them in fixed order, but for **every card in the household with full descriptions**: on a busy household it overflows the tool output. Read one column at a time instead: `list_tasks({ executionState, boardId })` per board of the domain (add `tagName` for a sprint). Use the `execution` view only with `assignee` on a small board (a view refuses any other filter).

| # | Column | Settable via `update_tasks` `executionState`? |
|---|---|---|
| 1 | **Backlog** | ✅ `backlog` |
| 2 | **Assigned** | ✅ `assigned` |
| 3 | **Next** | ✅ `next` |
| 4 | **Doing** | ✅ `doing` |
| 5 | **Stand By** | ✅ `standby` |
| 6 | **Done** | 🔴 **Not settable.** A task reaches Done by being completed |

🗣️ **This is the Execution Backlog.** Never say bare "backlog" — the board Backlog column is a different thing entirely.

---

## 🚧 The dependency gate

**One gate: completing.** `complete: true` is refused with `BLOCKED_BY_INCOMPLETE_TASK` while any
blocking task is incomplete; a blocker in **Stand By is not complete**. A blocking task never stops
a move to Next, Doing or Stand By (checked on the app 2026-10-20): a chained card can be worked
while its blocker waits for the user's test.

**Any column but Done can be set explicitly**, from any column. A sprint plan may seed its whole
batch to Assigned in one `update_tasks` call, one entry per card.

⛔ When the gate refuses: **name the blocking task**, do not retry, do not route around it. `relatedId` in the refusal is the blocker — resolve it to a title before reporting. Codes: `references/errors.md`.

---

## 📥 What the board contains

Tasks that are **assigned to a board** and either:

- still due at any age, or
- due this week, or
- completed this week

📌 Tasks with no board never appear here. They are in Untriaged — that is Triage's problem, not Execution's.

📌 **The midnight job** (`actor: system`) already moved anything due today or overdue into **Assigned**. `/bandit:tasks today` reads that result. **Do not synthesise a today-list** — the board is the list.

---

## 🖐️ The five-item cap

More than five items live across **Next + Doing** is the signal to stop and say so.

Report the breach. Propose what moves back to Assigned or Stand By. **Do not silently trim.**

---

## ⚙️ Procedures

### `/bandit:tasks today`

1. `list_tasks({ executionState, boardId })` for `doing`, `next`, `assigned` and `standby`, one call per board of the domain (`references/scope.md` → Filtering)
2. Report **Doing** first, then **Next**, then Assigned; inside each, the home board first, then
   the rest of the domain by board
3. Flag: cap breach · anything overdue · anything in Stand By older than a week, **except** a
   card carrying a `sprint/*` tag or a sprint card (`references/dev.md` → Sprint card): those wait
   in Stand By for the user's test on purpose
4. Stop. `/bandit:tasks today` is a read.

### `/bandit:tasks doing`

1. Resolve the named task — `list_tasks` or the board just read
2. `update_tasks { items: [{ taskId, executionState: "doing" }] }`
3. The card still has an incomplete blocker (`get_task` → `blockedBy`) → say so: it can be worked,
   not completed, until the blocker is. A refusal → report its reason and stop

### `/bandit:tasks done`

1. `update_tasks { items: [{ taskId, complete: true }] }` — this is what moves it to Done. Every
   card another system made for one record: `{ originSystem, originReference, complete: true }`
2. **If it was a recurring occurrence**, completion advances the series and creates the next occurrence. Say so, and report the next date
3. If the whole series just ended because the rule ran out, say that too

⚠️ `reopen_tasks { taskIds }` returns the task to Backlog and makes it movable. On a recurring occurrence it also removes the next occurrence, and only when that one is an unedited fresh copy and this is the series' latest completion; otherwise it is refused (`references/errors.md`).

### `/bandit:tasks bump`

Bumping is a **date** change, not a column change.

1. `update_tasks { items: [{ taskId, dueDate }] }`, one entry per task for several
2. Refused if the new date puts it out of order with something it blocks or that blocks it — report which
3. Refused outright on a recurring occurrence — **its date comes from the rule.** Offer `manage_recurrence { action: "skip", taskId }` instead (the next occurrence is a new task: use the id it returns)

📌 Three bumps on the same task is a right-sizing signal. Say it once. Do not nag.

---

## 📦 Bulk

`update_tasks` with `executionState` — applied per entry. Done is not a destination;
`executionState` and `complete` never share an entry.

`update_tasks` with `complete: true` or `dueDate` — cap 100, one result per entry
(`references/board.md` → Many cards in one call).

**Completing blockers and their dependents:** entries apply in list order, so one call works with
every blocker **listed before** its dependents (checked on the app 2026-10-20). A dependent listed
before its blocker is refused with `BLOCKED_BY_INCOMPLETE_TASK`; the rest still apply.

Over 100, or malformed → **whole call refused, nothing changed.**

---

## 🎚️ The three variables

Read them off the task; do not invent them.

| Field | Scale |
|---|---|
| 🧩 **Complexity** | Simple 1 · Medium 2 · Complex 3 |
| ⏱️ **Effort** | XS 1 · S 2 · M 3 · L 4 · XL 5 |
| 🔺 **Priority** | Low 1 · Medium 2 · High 3 · Urgent 4 |

Priority is **urgency only** and is independent. A Complex XL task can be Urgent.

Effort L or XL sitting in Doing is a split candidate — propose, never act. On a Technical board only XL is (L cards are allowed there, `references/dev-workflow.md` B7).

---

## 🕐 A note on `dueTime`

`HH:MM`, 24-hour, **display only.** It never affects placement and never affects whether something is overdue. Do not use it to sequence a day.
