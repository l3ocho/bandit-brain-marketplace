# 🧹 Audit

**Command:** `/bandit:tasks audit`
**Owns:** hygiene checks · `archive_project`

---

## 🎯 Posture

**Audit finds and fixes. It never tidies behind the user's back.**

**Findings come fixed.** Every finding comes back as a count and a **numbered fix row** with the exact tool call, target and recommended fix, all in one proposal. Nothing is ever just flagged. A finding with two valid fixes (archive or reschedule, merge or keep both) is one row with both, recommended first. The user answers all, a list or none; only approved rows run. A board that quietly reorganised itself overnight is worse than a messy one.

---

## 🔍 The checks

Run them all, report only the ones that fire, each with its fix row. **Over the domain only:**
every read goes through `references/scope.md` → Filtering; check 1 runs from the workflow project
only, and checks 6–7 read tag names, which are household-wide by nature.

| # | Check | How |
|---|---|---|
| 1 | **Untriaged pile** | `get_inbox_board` → Untriaged count. Over ~15 is a triage backlog, not a hygiene problem |
| 2 | **Untriaged parked cards** | `list_tasks(projectColumnId: null)` — in a project, in no column. Age via `list_events(taskId)`. Fires on a **workflow** project for any card older than a day (the daily sweep missed it), and on any type for a card older than ~30 days with no field answered. Fix row per project: run triage's **Leaving the inbox** for them (`references/triage.md`), or, on a deliverable project, keep them parked as ideas with the user's yes |
| 3 | **Stale overdue** | `get_week_board` → Due column. Anything overdue by more than a month is a decision, not a date |
| 4 | **Stand By rot** | `get_execution_board` → Stand By. Nothing should sit there indefinitely. **Exempt:** cards carrying a `sprint/*` tag and sprint cards (`references/dev.md` → Sprint card): they wait there for the user's test |
| 5 | **Dead dependencies** | `get_task` on anything with `blockedBy` — links pointing at completed tasks |
| 6 | **Orphan tags** | `list_tags` → `taskCount: 0`. **Exempt:** `sprint/*` (a closed sprint's tag is its record; `list_sprints` lists them) |
| 7 | **Off-vocabulary tags** | `list_tags` → anything outside the vocabulary (`references/board.md` → Tags: three axes, dev tags, sprint tags). **Exempt:** `sprint/*` |
| 8 | **Untouched projects** | `list_projects`, then `list_events` per project. No activity in ~60 days → archive candidate |
| 9 | **Unreadable rules** | `get_repeat_rule` → `rule: null` on a recurring task. Fix row: `update_repeat_rule` with the rule read from its occurrence history (`list_occurrences`), shown in full and marked **unchecked**. History too thin to read → the row asks for the schedule instead. Never rewritten without that row's yes |
| 10 | **Effort/complexity blanks** | Only worth flagging on tasks in Next or Doing |

### 🧱 Board structure — every project

Columns and lanes are two axes of one view (columns: the process or groups of work; lanes: a second
grouping across them). A board that piles its needs into columns still works, and this check says
how to do better. Read the project's columns and lanes (`list_projects`, `get_lane_template`), the
household members (`list_household_members`) and the project's members (`list_project_members`).

| # | Check | Fires when | Fix row (recommended first) |
|---|---|---|---|
| G1 | **A column named like a person** | A column's name matches a member's name or display name, or reads as one ("Kid", "Mom", a first name) | Make it a **lane** for that person: a tag for them, the tag on the column's cards, a lane on that tag, each card moved to the real column of its work, then the empty column deleted (confirm). Option two: keep it, with the reason |
| G2 | **Too many columns** | More than ~8 columns | Group them: name the two or three axes the columns mix, move one axis into lanes or tags, merge columns that hold the same stage. The row lists which columns go where |
| G3 | **A column that groups by a tag's job** | A column named for a priority, a person, a status (Waiting, Urgent, Someday) or a kind of work that a lane or tag already carries | Replace it with that tag or a lane on it, cards re-filed by their process column |

Each row is a design proposal: it opens the design conversation at the same approval, and nothing
runs until the user settles it (**🚫 Outside audit**). Structure fixes run with raw tools after that yes.

### 🛠️ Dev-card checks — `dev: true` only, current board only

Rules in `references/dev.md` and `references/dev-workflow.md`. Every finding is a fix row; the fix for a stage tag runs through `stage`.

| # | Check | How |
|---|---|---|
| V1 | **Lane and stage tags** | Every open card has exactly one `lane/*` tag and, except `lane/incident`, exactly one `stage/*` tag. Sprint cards are exempt (`references/dev.md` → Sprint card) |
| V2 | **Plan note present** | `stage/planned` and `stage/ready` cards name a plan-note filename under `Technical plan`, and bandit:notes finds it filed (its lookup; this skill never restates vault paths). A recurring card may carry a `Runbook:` line instead (`references/dev-workflow.md` → Record homes). A shared sprint plan counts for every card that names it |
| V3 | **XL cards** | `effort` 5 → split candidate (B7, `references/dev-workflow.md`); the new cards stay in the same sprint. Sprint cards are exempt |
| V4 | **Possible duplicates** | Two open cards in the same area column and lane with the same outcome (B6, `references/dev-workflow.md`). Judgment call: show both |
| V5 | **Open spec changes** | Cards with a comment starting `Spec change needed:` (`get_task` → `comments`), or a legacy line of it under `Technical plan` |
| V6 | **Card complete** | Every open card holds every **🧾 Card fields** value and every heading of its lane template (`references/dev.md`). One fix row per card: the missing values and headings, the exact `update_task` / `set_task_tags` call. Sprint cards are exempt |

**No age check.** Time spent in a stage is never a finding.

---

## 📜 Reading history

`list_events(start?, end?, taskId?)` — newest first. Every entry carries an **actor**:

| Actor | Means |
|---|---|
| `user` | Someone in the app |
| `mcp` | A client — this |
| `system` | The nightly job |

Use it to answer *what changed and who changed it*. A task that "moved on its own" is almost always `system`: the midnight job pulling due-or-overdue work into Assigned.

📌 Events record the task title **as it was at the time**. A renamed task will show its old name in old events. That is correct, not a bug.

---

## 📦 Archiving

`archive_project(projectId)` is the answer to almost every *"get rid of this."*

**Nothing is destroyed.** Tasks, columns, dates, states, tags, comments, dependencies and history are all kept exactly as they are. It disappears from Inbox, Execution, Week, Tags and the default project listing. `restore_project` puts it back precisely as it was.

🔴 **It is never refused for having unfinished work inside.** The reply returns `incomplete` and `overdue` — how many unfinished tasks, and how many of those were past due, just left the boards.

**If either is above zero, say so.** That is the whole point of the return value. Silently archiving nine overdue tasks is how work disappears.

📌 Archived tasks are excluded from `list_tasks` by default. Pass `includeArchived: true` to see them.

---

## 🛡️ Destructive operations

🔴 **Confirm before calling. None are recoverable.**

| Tool | Blast radius |
|---|---|
| `delete_project` | **Every task inside it** |
| `delete_folder` | The folder |
| `delete_tag` | Stripped from **every task carrying it** |
| `delete_task` | Its subtasks, comments and dependency links |
| `delete_subtask` | The line |
| `delete_project_column` | The column |
| `delete_series` | **Every occurrence, including completed history** |
| `delete_series_occurrence` | That occurrence's subtasks and comments |

**Archive before you delete.** Offer it every time.

### 🏷️ Retiring a tag

Never delete a tag with a live count.

1. `list_tags` → confirm the count
2. `list_tasks(tagId)` → the carriers
3. `get_task` each → read current tags
4. `bulk_set_task_tags` with the **full corrected set per task**
5. `list_tags` again → confirm **zero**
6. Then, and only then, confirm and `delete_tag`

⛔ `delete_task` is **refused on a recurring occurrence** — it would stall the series. Recurring deletion is only available in the app itself. Offer `end_repeat_rule` or `skip_occurrence`.

---

## 🔒 The protected column

The `Backlog` column at position 0 refuses rename and delete with `PROTECTED_COLUMN`.

**That is correct.** Report it and move on. Do not propose a workaround, a rebuild, or a new column that impersonates it.

---

## 🚫 Outside audit

Creating projects, renaming columns, configuring lanes — **a design conversation, every time** (except the three procedures in `references/board.md` → Outside this skill: load, onboard, dev board shape with its PM column). When a board's shape is causing the mess, audit still brings the fix: a row with the concrete change it recommends (which column, which name, which move) and why. That row opens the design conversation at the same approval; nothing runs until the user settles it.

`archive_project` is the single exception, and it lives here because audit is what discovers the need for it.
