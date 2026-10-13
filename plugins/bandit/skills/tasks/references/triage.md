# 📥 Triage

**Commands:** `/bandit-tasks triage` `/bandit-tasks inbox`
**Owns:** the Inbox board · `move_task` · `bulk_move_tasks` · right-sizing during review

---

## 🗺️ What the Inbox board actually is

`get_inbox_board` returns:

| Column | Holds |
|---|---|
| **Untriaged** — always first | Tasks belonging to **no project at all** |
| One column per project | That project's tasks **not yet filed into a column** — "parked" |

🔴 Two different states, one board. **Untriaged** has no project. **Parked** has a project but no column.

That is why triage is two stages, not one.

---

## 🔁 The two stages

| Stage | Question | Result |
|---|---|---|
| **1 — Inbox review** | Which project does this belong to? | Untriaged → a project (parked) |
| **2 — In-project organisation** | Which column of that project? | Parked → filed |

Never collapse them. Asking "which project and which column" about twenty untriaged items produces guesses on the second half.

---

## ⚙️ Procedure

1. **Resolve scope.** `list_projects` once. Names → IDs, plus every project's columns and type
2. **Read the board.** `get_inbox_board`
3. **Report counts first.** Untriaged count, then parked count per project. Do not start proposing until the size is stated
4. **Right-size** — see below. Propose only
5. **Propose destinations** as a list the user can correct in one message
6. **On confirmation**, write with `bulk_move_tasks` — batches of ≤100
7. **Report per-task results.** Refusals by task name with the reason

---

## 🔀 Placement rules — memorise these

`move_task` and `bulk_move_tasks` behave identically on placement:

| You pass | Where it lands |
|---|---|
| `projectId` + `projectColumnId` | That column |
| `projectId`, no column, task **has no due date** | That project's Inbox — **parked** |
| `projectId`, no column, task **has a due date** | The project's **first column** |
| `projectId: null` | Untriaged |
| `projectColumnId: null` | Inside the project, unfiled |

🅿️ **A parked task can never hold a date.** Dating a parked task moves it into the first column automatically. This is the same rule from both directions — `set_task_due_date` does it too.

⛔ **A completed task cannot be moved.** The refusal is not a bug.

---

## ✂️ Right-sizing during review

Triage is where wrong-sized items get caught, because it is the only pass that sees them all together.

| Split it if | Merge it if |
|---|---|
| It needs more than one due date | Three items are one sitting |
| Parts have different execution states | They only make sense in sequence |
| One part blocks another | None of them would ever appear on a board alone |

**Propose. Never resize silently in either direction.**

- To split: `create_task` for the new pieces, then `delete_task` or `add_subtask` on the remainder
- To demote a task into a checklist line: `add_subtask` on the keeper, `delete_task` on the original — **confirm the delete**
- To promote a checklist line: `promote_subtask` — it takes the parent's project and column and **nothing else**, and returns the new id

---

## 🚫 Not triage's job

| | Use |
|---|---|
| Setting execution state | `/bandit-tasks today` — Execution |
| Setting due dates in bulk as a planning act | `/bandit-tasks plan` — Week |
| Creating tasks | `/bandit-tasks capture` |
| Creating or renaming columns | Design conversation. Outside the skill — except a WBS load (`/bandit-tasks load`) and the dev board shape's `PM` column (`references/dev.md`) |

🛠️ **Dev projects (`dev: true`).** Triage run **from the dev project** turns a parked item into a
card: the move into its area column stays here (`move_task`), and `spec` (`references/dev-workflow.md`)
writes its lane tag, `stage/spec` and `Spec` section. Triage run from a workflow project is
unchanged: a dev item is filed into the dev project parked, and that project's `spec` picks it up.

🔀 **`move_task` lives here and nowhere else.** If another surface needs a task moved, it says so explicitly and hands off.

---

## ⛔ Refusals

| Code path | Meaning |
|---|---|
| Completed task | Move refused. Uncomplete first, or leave it |
| Batch > 100 | **Whole call refused, nothing applied.** Split it yourself |
| Malformed set | Whole call refused, nothing applied |

Partial batches are **successes**. Nineteen applied and one refused is nineteen applied.
