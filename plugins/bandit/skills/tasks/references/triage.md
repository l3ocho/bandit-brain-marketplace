# 📥 Triage

**Commands:** `/bandit:tasks triage` `/bandit:tasks inbox`
**Owns:** the Inbox board · moves (an `update_tasks` entry with `boardId` / `boardColumnId`) · right-sizing during review

---

## 🗺️ What the Inbox board actually is

`list_tasks { view: "inbox" }` returns:

| Column | Holds |
|---|---|
| **Untriaged** — always first | Tasks belonging to **no board at all** |
| One column per board | That board's tasks **not yet filed into a column** — "parked" |

🔴 Two different states, one board. **Untriaged** has no board. **Parked** has a board but no column.

That is why triage is two stages, not one.

---

## 🔁 The two stages

| Stage | Question | Result |
|---|---|---|
| **1 — Inbox review** | Which board does this belong to? | Untriaged → a board (parked) |
| **2 — In-board organisation** | Which column of that board? | Parked → filed |

Never collapse them. Asking "which board and which column" about twenty untriaged items produces guesses on the second half.

---

## ⚙️ Procedure

1. **Resolve scope.** `get_context` once. Names → IDs, plus every board's columns;
   the domain's boards (`references/scope.md`)
2. **Read the board.** `list_tasks { view: "inbox" }`, filtered to the domain (`references/scope.md` →
   Filtering). **Untriaged is the workflow project's:** from any other project, Stage 1 is skipped
   and only the domain's parked columns are triaged
3. **Report counts first.** Untriaged count (workflow project only), then parked count per board of the domain. Do not start proposing until the size is stated
4. **Right-size** — see below. Propose only
5. **Stage 1 — propose boards** for the untriaged items, as a list the user can correct in one message
6. **Stage 2 — leave the inbox** (below) for the parked items the board's exit style lets out now
7. **On confirmation**, write one `update_tasks` call, one entry per card (batches of ≤100):
   `{ taskId, boardId, boardColumnId?, …fields, dueDate? }`. A move applies before fields, so
   the due date in the same entry still lands **last**. A refused entry changed nothing on that card
8. **Report per-task results** from `results`. Refusals by task name with the reason

---

## 🚪 Leaving the inbox

Capture asks for nothing; **every field is answered on the way out**. A card leaves the inbox only
with these answered, in this order, in one proposal row per card (the user corrects a row in one line):

| # | Field | How |
|---|---|---|
| 1 | Description | The high-level what and how, block-tag HTML (`references/board.md` → Card descriptions). Detail lives in notes |
| 2 | Priority | Urgency only |
| 3 | Effort | Too large → propose the split first (right-sizing below) |
| 4 | Complexity | High is fine now; it is driven down before execution |
| 5 | Assignee | `get_context` → `boardMembers[boardId]` (or `members` on a shared board), resolved live |
| 6 | Column | The board's real column (Stage 2 above) |
| 7 | **Due date, last** | It commits the card: a parked card that gets a date moves to the first column on its own (rule 2 in SKILL.md). Never asked before the others |

A field the user leaves open keeps the card **parked** (its date stays empty), and the row says which
field is missing. Never invent a value to get a card out.

### Exit style, by board

The board's profile decides what it shows, never how cards leave it. The exit style follows the
board's role, by name:

| Board | The board inbox is | Cards leave |
|---|---|---|
| 🔁 The domain's workflow board (` - wkflw`, bandit:audit rulebook S3) | A place for the unforeseen things a process must handle | **Daily sweep:** every parked card leaves today, all fields answered. Nothing waits for a better time |
| 🎯 Every other board | The **evaluation gate**, and the **idea list** | One question per card: does it make sense now? **Yes** → a chat about it, then `spec` on a Technical board (below) or the fields above · **Not yet** → stays parked, untouched (the board is the idea list: never a separate notes list) · **No** → archive the card (confirm) |

### 🛠️ Technical boards: clarify or spec

On a Technical board a parked item that passes the gate becomes a card through `spec`, never by
filling fields here. Per item, offer one of:

- **Fuzzy** (the outcome can't be stated in a sentence) → `/bandit:clarify` first; its Clarified
  Specification is `spec`'s input (`references/dev-workflow.md` → spec, Source: clarify)
- **Clear** → `/bandit:tasks spec` now, which places it in its area column and writes its Spec

## 🔀 Placement rules — memorise these

An `update_tasks` entry places a card the same way for one card or a hundred:

| You pass | Where it lands |
|---|---|
| `boardId` + `boardColumnId` | That column |
| `boardId`, no column, task **has no due date** | That board's Inbox — **parked** |
| `boardId`, no column, task **has a due date** | The board's **first column** |
| `boardId: null` | Untriaged |
| `boardColumnId: null` | Inside the board, unfiled |

🅿️ **A parked task can never hold a date.** Dating a parked task moves it into the first column automatically. This is the same rule from both directions — an `update_tasks` entry with only `dueDate` does it too.

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

- To split: `create_tasks` for the new pieces, then `delete_tasks` (kind `card`) or `manage_subtasks { action: "add" }` on the remainder
- To demote a task into a checklist line: `manage_subtasks { action: "add" }` on the keeper, `delete_tasks` (kind `card`) on the original — **confirm the delete**
- To promote a checklist line: `manage_subtasks { action: "promote" }` — it takes the parent's board and column and **nothing else**, and returns the new id

---

## 🚫 Not triage's job

| | Use |
|---|---|
| Setting execution state | `/bandit:tasks today` — Execution |
| Setting due dates in bulk as a planning act | `/bandit:tasks week` — Week |
| Creating tasks | `/bandit:tasks capture` |
| Creating or renaming columns | Design conversation. Outside the skill — except a WBS load (`/bandit:tasks load`) and the dev board shape's `PM` column (`references/dev.md`) |

🛠️ **Technical boards.** Triage run **from a project whose board is Technical** turns a parked item into a
card: the move into its area column stays here (`update_tasks` with `boardColumnId`), and `spec` (`references/dev-workflow.md`)
writes its lane tag, `stage/spec` and `Spec` section. Triage run from a workflow project is
unchanged: a dev item is filed into the dev project parked, and that project's `spec` picks it up.

🔀 **Moves live here and nowhere else.** If another surface needs a task moved, it says so explicitly and hands off.

---

## ⛔ Refusals

| Code path | Meaning |
|---|---|
| Completed task | Move refused. Reopen first (`reopen_tasks`), or leave it |
| Batch > 100 | **Whole call refused, nothing applied.** Split it yourself |
| Malformed set | Whole call refused, nothing applied |

Partial batches are **successes**. Nineteen applied and one refused is nineteen applied.
