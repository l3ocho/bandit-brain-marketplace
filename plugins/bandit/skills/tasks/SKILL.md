---
name: "bandit-tasks"
description: "Operates the BanditBrains task board: inbox triage, daily execution, week planning, capture, recurring rules, hygiene audits, email → proposed tasks, WBS load, the board step of onboarding, and on dev projects the card workflow (spec, plan-tech, stage, pick-ready). Invoked as /bandit-tasks + a command (triage, inbox, today, doing, done, bump, week, plan, review, capture, audit, email, load, onboard, spec, plan-tech, stage, pick-ready). Also trigger on \"what's in my inbox\", \"what should I do now\", \"what does my week look like\", \"add a task\", \"remind me to\", \"make this repeat\", \"mark that done\", \"push that to tomorrow\", \"what's blocked\", \"am I overloaded\", \"clean up the board\", \"this project is finished\", \"anything in my email to act on\", \"load the WBS\", \"write the card\", \"move it to ready\", and any request to file, schedule, complete, defer or review tasks. Do NOT use to write the WBS (wbs-generator), plan notes (bandit-notes), plan a sprint (bandit-sprint) or design a board freehand."
---

# 🗂️ Bandit Tasks

One skill, nine surfaces. Everything shared lives here; each surface has its own reference file.

> **The purpose — the sleep test.** Go to bed knowing everything has been *addressed*. Not
> done — captured, sized correctly, and sitting somewhere it will surface on its own. Nothing
> floating in your head as the only copy.

---

## 🧭 Router

**Invocation:** `/bandit-tasks <command> [args]`, the same form as `/bandit-notes`. The first word
after `/bandit-tasks` is the command. `/bandit-tasks` with no command → offer this table as a
numbered list and ask which one.

Read the matching reference file **before acting**. Do not work from this page alone.

| Surface | Commands | Reference | Owns |
|---|---|---|---|
| 📥 **Triage** | `triage` `inbox` | `references/triage.md` | Inbox board. **The only holder of `move_task` and `bulk_move_tasks`**. Right-sizing during review |
| ▶️ **Execution** | `today` `doing` `done` `bump` | `references/execution.md` | The six Execution columns, dependency gates, the five-item cap |
| 📅 **Week** | `week` `plan` `review` | `references/week.md` | Week board, workload, projections, `skip_occurrence` |
| ✍️ **Capture** | `capture` | `references/capture.md` | Task creation, brain dumps, **the whole repeat-rule lifecycle** |
| 🧹 **Audit** | `audit` | `references/audit.md` | Hygiene checks, `archive_project` |
| 📧 **Email** | `email` | `references/email.md` | Gmail → **proposals only, zero writes** |
| 🏗️ **Load** | `load` | `references/load.md` | WBS → a new Deliverable project: columns, tasks, subtasks, dependencies |
| 🚀 **Onboard** | `onboard` | `references/onboard.md` | The board step of project onboarding, **run by project-settings**: resolve the board scope, or create one **empty** project |
| 🛠️ **Dev** | `spec` `plan-tech` `stage` `pick-ready` | `references/dev.md` (board rules) · `references/dev-workflow.md` (the commands) | **Dev projects only.** Lanes, stages, card sections and fields, the dev board shape · surface roles, card boundaries, the card procedures. `sprint` = old name of `pick-ready`, one release |

**Only Load and Onboard create projects.** Only Load, and the dev board shape's `PM` step, create columns.

🚦 **Dev gate.** The Dev surface, the `lane/*` / `stage/*` tag rules, the card boundaries and the
dev audit checks apply **only** when the current Project Context has `dev: true`. Without it every
command behaves exactly as it always has, and a Dev command says the project isn't a dev project
and stops. **Surface roles** (Claude.ai high-level, Claude Code technical) are decided by where the
Project Context was read from: `references/dev-workflow.md` → Surface. Every Dev command checks it first.

**Commands are shortcuts. Natural language always works.** When a request spans two surfaces, read
both files — the point of merging was to make that free.

---

## 🗺️ Scope — resolve before every write

Read the `board:` line of the `## 🧭 Project Context` section — in the Claude.ai project
instructions, or in the repo's `CLAUDE.md` on Claude Code. The block's format is owned by
project-settings.

```
board: project "App: BanditBrains"
board: folder "Bandit Labs"
board: global
board: none
board: pending
```

| `board:` | Behaviour |
|---|---|
| `project` / `folder` / `global` | Call `list_projects` to resolve that **name** to an ID, then read anywhere, write inside it |
| `none` | Not board-backed. Read anywhere, **write nothing**. Say the project has no board |
| `pending` | The board isn't designed yet. Read anywhere, **write nothing** — except `/bandit-tasks load`, which *is* the design step for a WBS-backed project, and `/bandit-tasks onboard`, which sets the scope. Otherwise say: design the board, then update the `board:` line |
| Neither a Project Context nor a legacy scope section (a plain chat, no project) | Unchanged: behave as before this section existed |

**Legacy fallback:** no Project Context but a `## 🗺️ Task Board Scope` section with a
`scope: …` line → read that line exactly as if it were the `board:` line.

🔴 **No hardcoded IDs, ever.** `list_projects` returns every folder, project and column with IDs
in one call — that *is* the scope table. Discovery is correct here. A stored ID is a stale ID.

**Read anywhere. Write inside declared scope only.** Asymmetric on purpose: planning needs
cross-board reads, but work from one project must never land on another's board.

If the declared name no longer resolves, **stop and say so.** Never guess at the nearest match.

---

## 🔒 The five hard rules

1. 📅 **Date is king.** A due date is the single strongest signal on a task
2. 🅿️ **Parked ≠ dated.** A parked task given a due date is automatically moved into the
   project's first column. A parked task can therefore never hold a date
3. 🔀 **Move is triage-only.** `move_task` belongs to Inbox review. It is not a general verb
4. 👻 **Projections aren't rows.** Week-board items may be recurring projections with no task
   record. They cannot be acted on by ID
5. 🗣️ **Never say bare "backlog."** Say **project Backlog** or **Execution Backlog**. The word
   means two different things and confusing them moves work to the wrong place

---

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
| 🏁 **Sprint** (dev boards) | `sprint/{name}`, one per sprint, created with it (bandit-sprint) |

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
splits, and bandit-sprint's sprint card.

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
once more. Still wrong after that → tell Leo which card; never leave it.

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
- **`/bandit-tasks load`:** a WBS maps onto a Deliverable project mechanically (deliverables →
  columns, work packages → tasks). It builds only what the WBS says. Anything beyond the mapping
  is back to the design conversation.
- **`/bandit-tasks onboard`:** creates one empty project (the protected Backlog column only) as an
  approved row of project-settings' onboarding proposal. Columns and lanes come later, from a
  load or the design conversation (with `dev: true`, onboard adds the dev board shape rows).
- **Dev board shape** (`references/dev.md`): creates the missing `lane/*` / `stage/*` tags, sets
  the six dev lanes and adds the `PM` column, as approved rows — from `onboard` with `dev: true`, a
  bandit-audit S9 fix row, or (the `PM` column only) a sprint plan. Nothing else.

`archive_project` is the other exception, and it lives in audit because audit is what discovers the
need for it.

---

## ⚠️ Gotchas

- **2026-09-24 · Commands were bangs (`!triage`).** They're now `/bandit-tasks triage`, the same
  form as every other skill. → A `!command` typed from habit means the same command: run it.
- **2026-09-27 · Said a Sun–Thu repeat wasn't possible.** `capture.md` listed the rule vocabulary
  without `days`, which the tool supports on weekly rules. → Check the tool's `rule` schema before
  calling a rule impossible; the schema wins over this skill's table (`references/capture.md`).
- **2026-09-29 · Audit flagged problems and left them.** Unreadable rules were "flag, do not
  rewrite", and shape problems were reported with no fix. → Findings come fixed: every audit
  finding is a numbered fix row with the exact call, approved in one answer (`references/audit.md`).
- **2026-09-30 · Onboarding a real dev repo found `dev.md` out of step with it.** B1 said "one PR"
  where the repo lands by merge, an incident waited for the midnight run to reach Assigned, no
  record had a home, and `plan-tech` could overwrite a recorded branch. → Landing, not PR (B1);
  Assigned set explicitly; homes read from the repo (`references/dev-workflow.md` → Record homes);
  `plan-tech` reads first.
- **2026-10-05 · Card descriptions came out unreadable.** FW-3, FW-5 and FW-21 held escaped
  `&lt;br/&gt;`, shown as literal text; the skill only said "simple HTML". → Write only the tags in
  **📝 Card descriptions**, and read every description back after the write.
- **2026-10-06 · Dev cards drifted from the app's lane template.** The skill allowed only `<h2>`
  and said *Open questions for Claude Code*; the template uses `<h3>` and *Open questions*, and the
  column rule never said module or page. → Start every card from `get_lane_template`, fill
  Card fields in full, place it by the column rule (`references/dev.md`).
- **2026-10-06 · A tag write dropped tags.** `set_task_tags` replaces the whole set, so writing one
  tag wiped the rest. → `get_task` first and send the full merged set, every time (**🏷️ Tags**).
- **2026-10-06 · Sub-tasks came out in reverse order.** They were added with parallel
  `add_subtask` calls, and later landed at the top, reversed, even one at a time. → After any
  sub-task write, `reorder_subtasks` with the full order and read it back (**☑️ Sub-tasks**).
- **2026-10-06 · FW-2 and PW-34 still showed raw tags.** They opened with a bare `<b>`; the app
  reads a description as rich text only when it opens and closes with a block tag, so it showed
  every tag as text. The 10-05 rule allowed a top-level `<b>` and its read-back never tested the
  ends. → Every description opens and closes with a block tag; the read-back checks both ends.
- **2026-10-08 · Wave 2 cards were refused Doing.** Their blockers sat in Stand By awaiting Leo's
  test, and the skill said only "complete"; the board refused with `BLOCKED_BY_INCOMPLETE_TASK`. →
  Stand By is not complete: the Doing gate holds until BB-94 ships (`references/execution.md`).
- **2026-10-06 · `spec` parked obvious questions and skipped the brief.** BB-65 (per-user theme) left
  two Open questions with obvious answers (keep or reset the current theme; do other settings share
  the bug) and ended "no brief written, want one?". → A point with a sensible default is decided
  and written under Decisions (the check for other settings goes in Scope in). Open questions hold
  only real forks that change scope, each with options and a recommendation, or `None`. Every
  `spec` step runs, the brief (step 6) included: never skip a required step and offer it after.

---

## 🗾 Tone

Dry and direct. Report counts, propose actions, execute on confirmation.

No praise for capturing things, no encouragement, no streak-keeping, no urgency theatre.
Corrected → correct it and move on.