# 🛠️ Dev — board rules for technical development boards

**Read with:** `references/dev-workflow.md` (the commands `spec`, `spec reconcile`, `plan-tech`,
`stage`, `pick-ready`, surface roles, card boundaries, record homes)
**Owns:** the generic app-dev lanes and stage tags · the lane template headings · the Spec lock ·
tag merging · card fields · the sprint card's board shape · the **dev board shape** procedure

This file holds what the board itself enforces or expects. How work moves through it is
`references/dev-workflow.md`. Planning a sprint is `bandit-dev:sprint`'s (Claude Code): it calls the
rules here and never restates them.

---

## 🚦 Gate — Technical boards only

Everything in this file and in `references/dev-workflow.md` applies **only** when the current
project's home board (its `board:` line) has profile **Technical** (`get_context → boards →
profile`; `references/board.md` → Board profile). A Workflow board, or `board: none` or `pending`
→ every other command behaves as it always has, and a Dev command says *"this project's board
isn't Technical (its profile is Workflow)"* and stops. Family, Personal and the domain workflow
boards are never touched.

The Project Context `dev: true` line (owned by bandit:project) no longer gates these rules: it
marks a project for sprints (bandit-dev:sprint) and onboarding's dev board shape rows. A `dev: true`
project whose board is Workflow is a bandit:audit finding (S9), fixed by the dev board shape below.

---

## 🏊 Lanes and stages

**Six lanes**, top to bottom. Each lane matches one tag. Kind on dev boards is the `lane/*` tag.

| Lane | Tag | Holds |
|---|---|---|
| Incident | `lane/incident` | Something broken in production, now. No stage, no merge check |
| Issue | `lane/issue` | A defect or wrong behaviour to fix |
| Feature | `lane/feature` | New capability |
| Maintenance | `lane/maintenance` | Upgrades, dependencies, config, ops |
| Content | `lane/content` | Templates, copy, data the app ships |
| Tech Debt | `lane/tech-debt` | Refactors and cleanup with no visible change |

**Three stages**, one tag at a time (none on Incident). The app enforces both: a set with two
`stage/*` tags, or `lane/incident` with any `stage/*`, is refused whole (`TAG_RULE_VIOLATION`).

| Stage | Means | Set by |
|---|---|---|
| `stage/spec` | Scope agreed, `Spec` written | `spec` |
| `stage/planned` | Plan note reviewed and filed by the user | `stage … planned`, after `/bandit:notes file` |
| `stage/ready` | The user approved; a sprint candidate | `stage … ready`, or the user by hand |

**Stage tags stay after a card is completed.** Completion clears nothing (38 completed BanditBrain
cards still carried theirs, checked 2026-10-09). A done card's stage is its last stage, never a
finding.

**No age check on any stage.** How long a card has sat anywhere is never a finding.

---

## 🃏 Card sections

**Start from the app's lane template**, never from memory: `get_context → laneTemplates` (incident, standard). Its
headings are the contract (`audit`, `plan-tech` and the app's Spec lock look for them): `<h2>` for
the sections, `<h3>` inside them, names kept word for word. A `create_tasks` entry with a `lane/*` tag and
no description pre-fills the same text.

**Standard lanes** (every lane but Incident). `<h2>Spec</h2>` holds these `<h3>` sections, in order:

| `<h3>` | Holds | From the template? |
|---|---|---|
| Source | `<p>Claude.ai</p>` or `<p>Claude Code</p>`, then `<p>Brief: {filename}</p>`: filename only, never a folder | Added |
| Outcome | What is true when done, one or two sentences | ✅ |
| Lane | The `lane/*` value | ✅ |
| Problem | **`lane/issue` only:** the wrong behaviour and where it comes from | Added |
| Scope in · Scope out | `<ul>` lists | ✅ |
| Acceptance | `<ul>`, each line checkable | ✅ |
| Decisions | `<ul>`, settled choices | Added |
| Open questions | `<ul>`, anything undecided (Claude.ai's technical points go here) | ✅ |
| `WBS-X.Y.Z` | A `<p>` line, when one fits | Added |

`<h2>Technical plan</h2>` keeps the template's placeholder until `plan-tech` (Claude Code) writes:
plan note **filename** (never a path), or a `Runbook:` line on a recurring card
(`references/dev-workflow.md` → Record homes) · branch · size · short summary. The repo's close-out
may add the landing (merge commit, PR URL): `plan-tech` never removes it. Spec changes are card
comments (`references/dev-workflow.md` → Surface), not lines here.

**Incident:** its own template (`<h2>` Impact · Timeline · Root cause · Fix · Follow-ups), no Spec.

Subtasks carry the plan's steps. Everything longer lives in the plan note.

---

## 🔒 Spec lock (the app's)

Once `<h2>Spec</h2>` holds text, `update_tasks` refuses any change to it with `SPEC_LOCKED`. Pass
`overrideSpecLock: true`, without asking, when the change only writes in what is already settled:
the user's words in this chat, the brief, the plan note, or decisions in the card's comments. Read
the current Spec first (rulebook R14), write, read back, and report old and new after. A change
nobody wrote down is an open question for the user, never an override. Never to get past the refusal. Other sections (`Technical plan`) and
adding a Spec to a card with none are never refused.

---

## 🏷️ Tag merging on dev cards

`tagIds` in `update_tasks` replaces the whole set (`references/board.md` → Tags), so every dev tag write is: `get_task` →
merge → write the full set.

- **Stage change:** replace any `stage/*` tag with the new one, or **add** it when the card has
  none. Keep every other tag, the `lane/*` and `sprint/*` tags above all.
- **Lane and stage on an untagged card:** merge the `lane/*` tag + `stage/spec` into its current
  tags. A card that already has them keeps its tags.
- Refuse before writing if the result wouldn't carry exactly one `stage/*` tag (none on Incident);
  the app would refuse it anyway (`TAG_RULE_VIOLATION`).

---

## 🧾 Card fields

Every dev card is written **complete**, in one `create_tasks` entry, then read back (`get_task`).

| Field | Value |
|---|---|
| `boardColumnId` | The **area column**: the module or page the change touches. `App` only when the change is shell-wide. Spans two, or no column fits → ask the user. Never create a column for it (columns come from `load`, the design conversation, or the PM step of **🏗️ Dev board shape**). **Project-management cards** (sprint planning, a sprint card, umbrella cards, planning checklists, process work) go in the `PM` column instead |
| `tagIds` | `lane/*` + `stage/spec` (none on Incident) + one Handler tag + one Energy tag (`references/board.md` → Tags), ids resolved live |
| `priority` | Always set: urgency only |
| `complexity` | Always set |
| `effort` | Always set. Claude.ai's is a first estimate; `plan-tech` confirms it. Max L (B7, `references/dev-workflow.md`) |
| `assignedTo` | The user: the signed-in member, resolved live (`get_context → members`), never a stored id |
| `dueDate` | Empty. Only `pick-ready` and a sprint plan date cards; **only the sprint plan sets a sprint batch's due date** (bandit-dev:sprint). Incident: today |
| Execution state | Left as created. The midnight run moves it when due; `pick-ready` sets Assigned for a card picked for today; a sprint plan may seed its whole batch to Assigned. Incident: `assigned` straight away |
| `dependencies` | `blockedBy` / `blocks` for every known link, in the same entry |
| `subtasks` | Claude Code only: the build steps, when it writes the card or at `plan-tech`. Claude.ai writes none. Order as `references/board.md` → Sub-tasks |
| `description` | **🃏 Card sections**, written per `references/board.md` → Card descriptions |
| Brief | One `brief` note per card through bandit:notes, `board-task` = the card's short id. Its body is bandit:notes' rule |

---

## 🏁 Sprint card — board shape

A sprint runs on one **sprint card**, the umbrella for a batch of cards. Its sections and sub-tasks
(the planning steps, one per wave) are bandit-dev:sprint's (`templates.md` there); this file holds only
what the board sees.

| Part | Value |
|---|---|
| Column | `PM` (**🧾 Card fields** column rule) |
| Tags | No `lane/*`, no `stage/*`: it isn't a lane card. Exempt from audit V1, V3 and V6 |
| Description | No Spec. Written per `references/board.md` → Card descriptions |
| Batch | Every card in the sprint is a **blocker** of the sprint card (`link_tasks { blockerTaskId: card, blockedTaskId: sprint card }`). The live blockers are the source of truth |
| Sprint tag | `sprint/{name}` on each batch card, never on the sprint card. `list_tasks { view: "sprint" }` lists every sprint tag with open, completed and total counts; `list_tasks { tagName: "sprint/{name}" }` gives its cards |
| Effort | Its own size as the umbrella; B7 applies to the batch cards, not to it |
| Records | Plan, execution prompt, ledger, report and the batch's briefs, in the sprint folder (bandit:notes owns the names and the folder) |

---

## 🏗️ Dev board shape — procedure

Run from `onboard` (approved rows) or as a fix row for bandit:audit S9; the PM step also from a
sprint plan. The one lane and column procedure in this skill; any other lane or column design is
still a design conversation. **Never silently:** every step is an approved row.

Read `get_context` once (tags, boards), then work by id.

1. `get_context → tags` → the tags `lane/incident · lane/issue · lane/feature · lane/maintenance
   · lane/content · lane/tech-debt · stage/spec · stage/planned · stage/ready`, scope `system`. The
   app provides them and refuses to create them (`TAG_NAME_RESERVED`): one missing → stop and
   report it as an app problem, no row.
2. `get_context → boards` → the board's `profile`. Workflow → one row first:
   `manage_boards { action: "update", boardId, profile: "technical" }` (lanes are refused on a
   Workflow board, `NEEDS_TECHNICAL_BOARD`). Only the board's creator may run it: anyone else
   gets `REQUIRES_ADMIN` → name the creator (`createdBy`, `members`), add no lane row. A new board from
   `onboard` is created Technical, so it needs no row.
3. `get_context → boards` → the board's current lanes. One row: `manage_columns_lanes { action: "set_lanes", boardId, lanes }` with the **complete**
   list, in the lane table's order, each matcher `{field: "tag", values: [that lane tag's id]}`,
   ids resolved live after step 1 runs. The call replaces every lane, so existing lanes not in the
   list are named in the row.
4. **PM column** (from `onboard` with `dev: true`, or from a sprint plan when the board has none).
   `get_context → boards` → no `PM` column → one row with two calls: `manage_columns_lanes { action: "add", boardId, name: "PM" }`
   (it lands last), then `manage_columns_lanes { action: "reorder", columns }` with **every** column, Backlog at 0 and `PM` at
   1, the rest in their current order. A board that already has `PM` gets no row.
5. Execute only approved rows: the profile, then lanes, then the column. Report per row.
