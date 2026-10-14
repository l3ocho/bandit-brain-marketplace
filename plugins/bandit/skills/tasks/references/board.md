# 📋 Board rules

> Read before any write that the command's own reference doesn't cover: the shared vocabulary of every `/bandit:tasks` command.

## 📦 Project taxonomy

Three types. **A real enum field on the project**, read via `list_projects` — never inferred
from the column names.

| | 🎯 **Deliverable** | 🔁 **Workflow** | 🔀 **Hybrid** |
|---|---|---|---|
| Lifespan | Temporary | Continuous | Continuous |
| Columns | One per deliverable | Process lines | Both, separated by lanes |
| Primary entry | Planning decomposition | Inbox | Both |
| Due dates | Absent while planning | Implicit, SLA-driven | Depends on lane |

⚠️ **Type is a label, not a rule.** The app keys no behaviour off it. Changing it moves,
re-dates and re-files nothing. Every behavioural difference is yours.

---

## ✂️ Right-sizing

| It's a **task** if it needs | It's a **subtask** if |
|---|---|
| Its own due date | It only needs ticking off in sequence |
| Its own execution state | It happens inside one sitting |
| To appear on a board by itself | It has no meaning outside its parent |
| To block or be blocked by something | Its order is obvious from the list |

**Over-splitting is as wrong as under-splitting.** Three cards that were always one sitting is
three cards of noise on Execution, three dates to maintain, two dependency links to justify.

**Propose. Never resize silently in either direction.**

`promote_subtask` converts a subtask to a task — it inherits the parent's project and column,
everything else starts unset, and it returns the new task id.

---

## 📊 The three planning variables

They are **instruments**, not decoration.

| Variable | Means | Behaviour |
|---|---|---|
| 🧩 **Complexity** | How tangled the work is | High is normal in early planning. Drive it down before execution |
| ⏱️ **Effort** | Time range | Too large triggers a split |
| 🔺 **Priority** | Urgency **only** | Drives sort order. Independent of the other two — a Complex XL task can be top priority |

---

## 🏷️ Tags — three axes, plus the dev tags

| Axis | Tags |
|---|---|
| 🔖 **Kind** | `feature` · `issue` · `chore` |
| ⚡ **Energy** | `quick-win` · `deep-work` · `needs-research` |
| 🤖 **Handler** | `claude-code` · `claude-design` · `claude-ai` |
| 🏊 **Lane** (dev boards) | `lane/incident` · `lane/issue` · `lane/feature` · `lane/maintenance` · `lane/content` · `lane/tech-debt` |
| 🪜 **Stage** (dev boards) | `stage/spec` · `stage/planned` · `stage/ready` |
| 🏁 **Sprint** (dev boards) | `sprint/{name}`, one per sprint, created with it (bandit-dev:sprint) |

A sprint has no entity of its own: it is its tag. `list_sprints` lists every `sprint/*` tag with
open, completed and total counts and the earliest and latest due date; `list_tasks(tagName:
"sprint/{name}")` gives one sprint's cards, `list_tasks(tagPrefix: "sprint/")` every sprint card.

Tags are account-wide, so the vocabulary is the **union** of all six rows. On dev boards Kind is
expressed by the `lane/*` tag; `feature · issue · chore` stay valid everywhere else.

🔴 **`set_task_tags` and `bulk_set_task_tags` REPLACE the whole set.**

Always `get_task` first, merge, then write. Applying one tag without reading silently wipes the
rest. `bulk_set_task_tags` takes a full list **per task** for exactly this reason — there is no
shared-set shortcut, on purpose.

---

## 📦 Bulk write

Many tasks, one action, one call. Cap is **100** — above it the whole call is refused, so split
it yourself.

`bulk_move_tasks` · `bulk_set_due_date` · `bulk_set_task_tags` · `bulk_set_execution_state` ·
`bulk_complete_tasks`

**Results come back per task.** A refusal on one **does not undo the others**. Report refusals
by task name with the reason. Never report a partial batch as a failure — nineteen moved and one
refused is a success.

There is no bulk create and no bulk delete.

---

## 📝 Card descriptions

`description` is **HTML**, shown in the app's rich-text editor. 🔴 The app reads it as rich text
**only when the whole value opens with a block tag and closes with one**: `<p>`, `<h1>`–`<h6>`,
`<ul>`, `<ol>` or `<blockquote>` (app code: `rich-text.ts` → `looksLikeHtml`). Anything else, a
value starting with `<b>` or bare text included, is shown as plain text: every tag appears as
literal characters. Applies to every surface that writes one: capture, email, load, dev, triage
splits, and bandit-dev:sprint's sprint card.

| Tag | For |
|---|---|
| `<p>…</p>` | Every paragraph or line of text, plain text included |
| `<h2>…</h2>` | Section headings (dev cards: `references/dev.md` → Card sections) |
| `<h3>…</h3>` | Headings inside a section. The app's lane templates (`get_lane_template`) use them; keep them as the template writes them |
| `<ul>` / `<ol>` + `<li><p>…</p></li>` | Lists |
| `<b>…</b>` · `<code>…</code>` | Bold, inline code: **only inside** a `<p>`, `<li>` or heading, never at the top level |

🚫 **Never:** a value that starts or ends outside a block tag · `<br>` / `<br/>` (a new line is a
new `<p>`) · escaped markup (`&lt;br/&gt;`, `&lt;p&gt;`) · markdown (`**`, `- `, `#`,
`[text](url)`) · any other tag. A real `<`, `>` or `&` in the text is written `&lt;` `&gt;` `&amp;`,
as normal HTML. Text that arrives as markdown (a WBS dictionary entry, an email, a note) is
converted to these tags before the write, never passed through.

🔁 **Read it back.** After any `create_task` or `update_task` that sets `description`: `get_task`
and check three things. **1** it opens with `<p`, `<h1-6`, `<ul`, `<ol` or `<blockquote` and closes
with `</p>`, `</h1-6>`, `</ul>`, `</ol>` or `</blockquote>` · **2** no escaped markup
(`&lt;` followed by `br`, `p`, `b`, `ul`, `ol`, `li` or `h1-6`) · **3** no `**`, and no line
starting `- ` or `#`. Any fails → rewrite the same content in the tags above and `update_task`
once more. Still wrong after that → tell the user which card; never leave it.

---

## ☑️ Sub-tasks

Order is set, never trusted: after any sub-task write, `reorder_subtasks` with the **full** order,
then `get_task` to read it back (`references/capture.md` → Subtasks).

---

## 🛡️ Safety

**Write freely. Confirm destructive.**

🔴 Confirm before calling: `delete_task` · `delete_project` · `delete_folder` · `delete_tag` ·
`delete_project_column` · `delete_subtask` · `delete_series` · `delete_series_occurrence`

- `delete_project` destroys every task inside it
- `delete_tag` strips it from every task carrying it — **retag first, confirm zero, then delete**
- `delete_series` destroys every occurrence, past and future

**None are recoverable. Archive before you delete** — almost every "get rid of this" is an
archive, and `restore_project` puts it back exactly as it was.

The `Backlog` column at position 0 is protected. Delete and rename are refused with
`PROTECTED_COLUMN`. That is correct — do not work around it.

---

## ⛔ Refusals to expect

Act on `code`, show `reason`, name the related task when `relatedId` is present. Never retry a
variant to get past one. **Every code, where it comes from and what to do: `references/errors.md`**
(dependency gates, tag rules, the Spec lock, recurring occurrences, protected columns, roles).

⛔ **A rule outside the vocabulary is refused, never rounded to the nearest thing that fits.**
Report it. Do not substitute an approximation.

---

## 🚫 Outside this skill

🏗️ **Board structure.** Creating projects, naming columns, configuring lanes — a design
conversation with raw tools, every time. There is no repeated procedure to encode, and an
interview answer produces a bad board.

**Three exceptions are procedures:**
- **`/bandit:tasks load`:** a WBS maps onto a Deliverable project mechanically (deliverables →
  columns, work packages → tasks). It builds only what the WBS says. Anything beyond the mapping
  is back to the design conversation.
- **`/bandit:tasks onboard`:** creates one empty project (the protected Backlog column only) as an
  approved row of bandit:project' onboarding proposal. Columns and lanes come later, from a
  load or the design conversation (with `dev: true`, onboard adds the dev board shape rows).
- **Dev board shape** (`references/dev.md`): creates the missing `lane/*` / `stage/*` tags, sets
  the six dev lanes and adds the `PM` column, as approved rows — from `onboard` with `dev: true`, a
  bandit:audit S9 fix row, or (the `PM` column only) a sprint plan. Nothing else.

`archive_project` is the other exception, and it lives in audit because audit is what discovers the
need for it.

---

## 🗾 Tone

Dry and direct. Report counts, propose actions, execute on confirmation.

No praise for capturing things, no encouragement, no streak-keeping, no urgency theatre.
Corrected → correct it and move on.
