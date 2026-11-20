# Part 2 — Conventions

> What a note is, whichever storage holds it: its kind, its status, its one-line summary, its fields
> and its body. Where a note sits and how it is written down belong to the storage.

Two storages keep these conventions: the app's Notes (`references/storage-app.md`) and the MyNotes
vault (`references/storage-vault.md`, with the vault's own conventions in
`references/conventions-vault.md`). A helper follows this file for what a note holds, and the
storage's reference for where it goes and how it is saved.

Contents: Section map · Modules (§2) · Fields (§5) · Status (§6) · Note body shape (§12) ·
Dev projects (§13)

---

### Section map

The section numbers are fixed. "Conventions §N" names the same subject in every storage; this table
says where it is written.

| § | Subject | Written in |
|---|---|---|
| 1 | Where notes sit | The storage: `conventions-vault.md` §1 · `storage-app.md` → Places |
| 2 | Modules | Here. The vault's side: `conventions-vault.md` §2 |
| 3 | The settings area | Vault only: `conventions-vault.md` §3 |
| 4 | How a note is named | The storage: `conventions-vault.md` §4 · `storage-app.md` → Create without a duplicate |
| 5 | Fields | Here. How each is written: `conventions-vault.md` §5 · `storage-app.md` → Fields |
| 6 | Status | Here. Where each status lives: `conventions-vault.md` §6 · `storage-app.md` → Status and filing |
| 7 | Archive | The storage: `conventions-vault.md` §7 · `storage-app.md` → Archive, restore, delete |
| 8 to 11 | Other files, the ignore list, templates, Obsidian settings | Vault only: `conventions-vault.md` §8 to §11 |
| 12 | Note body shape | Here. The vault's link syntax: `conventions-vault.md` §12 |
| 13 | Dev projects | Here. The storage's side: `conventions-vault.md` §13 · `storage-app.md` → Dev projects |

---

### 2. Modules

Two optional sets of records, switched on per domain. Both are dated.

| Module | Kind | Holds |
|---|---|---|
| meetings | `minutes` | Every meeting's minutes or entry note, **including project meetings** |
| requests | `request` | Outstanding asks from other people: analyses and one-off work outside the daily routine |

- **Project meetings are minutes**, with the meeting value `project` and the project set. The
  minutes name the project, never the other way round, so no helper has to edit a project's own
  notes to list its meetings.
- A record that fits no kind and no module is never an invitation to invent one. It comes back as
  a fix row with the options, recommended first: map it to an existing module, put it with a
  project, or propose a new module (which means changing this file).

---

### 5. Fields

A helper adds missing fields and fixes malformed values; it **never removes a field value or a
tag the user added**. A note in the inbox is exempt until it is reviewed (`references/model.md`,
*The inbox is the user's*).

#### Every note

| Field | Values | Notes |
|---|---|---|
| Kind | `note` · `minutes` · `request` · `brief` · `reference` · `log` · `plan` | What the note is. Exactly these seven (`plan`: dev projects only, §13) |
| Status | `inbox` · `triaged` · `active` · `waiting` · `done` · `archived` | §6 |
| Summary | One sentence, ≤ 25 words | What the note covers, written so an agent can decide from the summary alone whether to open it. Not needed in the inbox; **required once reviewed** |
| Tags | Free words | The user's own. Untouched |
| Domain and project | The domain, and the project when the note is about one | Given by where the note sits (§1) |
| Created and updated | Dates | Kept by the storage |

#### When they apply

| Field | Values | Used by |
|---|---|---|
| Source | `chat` · `manual` · `meeting` · `email` · `migrated` | Where the content came from. `migrated` = moved in from another system (a repo, a wiki, another notes app, an older layout) by whichever step moves it; the original location goes in the body's first line |
| Card | One Bandit Brain card | The card that tracks the work. A plan or a brief belongs to exactly one card |
| Related notes | Other notes of the same domain | Each with its reason in the body's `## Related` (§12) |
| Lane | The repo's lane name; on a dev project the bare lane value (`feature`, not `lane/feature`) | Briefs and plans; bandit:tasks' vocabulary |
| Handler | `claude-code` · `claude-design` · `claude-ai` | Briefs; bandit:tasks' Handler vocabulary |
| Sprint | The sprint's name in the app | A sprint's records (§13) |

#### By kind

| Kind | Its own fields |
|---|---|
| `minutes` | Meeting: `supervisors` · `department` · `project` (nothing else) — meeting date — participants: the names mentioned — room: where it was held (free text, optional) |
| `request` | Requester: a **role**, not a name ("CS Director", "Billing team") — received: a date — due: a date or empty |
| `brief` | Lane, handler |
| `plan` | Lane, **left out on a sprint plan** (a sprint has no lane) — card: **required**; a sprint plan carries the sprint's name instead, or on an old-way sprint the sprint card — related notes |

The meeting field has **exactly three values**: `supervisors`, `department`, `project`. The user
has settled it: there is **no Ad-hoc and no Outstanding**. Never propose, add or suggest another
value ("ad-hoc", "other", "misc"…). "Outstanding" is the requests module, not a meeting. If a
meeting fits none of the three, ask the user which one it is; don't invent one.

---

### 6. Status

A note's lifecycle, **independent of the task board**. The board owns work state
(`backlog · assigned · next · doing · standby · done`); the note names its card and never mirrors
that state: two copies of one state drift the first time a card is ticked on the phone.

| Status | Means |
|---|---|
| `inbox` | The user's note in progress, in the inbox. What may be touched there: `references/model.md`, *The inbox is the user's* |
| `triaged` | Structured; nothing pending on it |
| `active` | Being worked on or referenced as current |
| `waiting` | Blocked on someone else |
| `done` | Finished: ready to be archived |
| `archived` | Kept, out of the way. Each storage says how it holds an archived note |

A helper's draft waiting for the user's review also sits in the inbox. Which status marks it is
the storage's: `conventions-vault.md` §6 · `storage-app.md` → Status and filing.

**A plan linked to its card follows that card** (§13): `active` while the card is open, `done`
once it is complete, and never its stage or execution state. No helper sets it: the storage keeps
it so. The app's Notes does it itself (`storage-app.md` → Status and filing); in the vault, `file`
and `lint` do (`references/commands.md`).

---

### 12. Note body shape (notes a skill or chat writes)

The user's own notes and templates keep their structure. Notes written by a skill or in a chat
(briefs, drafts, references, logs) use this shape, so any agent can take the slice it needs
without reading the whole note:

1. **One title**, saying what the note is.
2. **Summary line** directly under it: `> {same sentence as the summary}`.
3. **H2 sections**, short, H3 inside when needed. Tables over paragraphs for structured facts.
4. **Unambiguous dates** in the body: `YYYY-MM-DD` or a written month ("Sep 21"). Never
   `09/10/2026`.
5. **`## Related`** last, when the note names other notes: one line per note with the reason
   (`home-reno — project hub` · `department-minutes-2026-09-17 — decision source`). Every note
   named here is also among the note's related notes (or is its project).
6. **No customer data** (names, account numbers, addresses, call contents). Use placeholders
   (`[customer]`, `[account]`).

Minutes follow the bandit:minutes skill's layout, which already meets 1 and 3; they add the
summary line (2), `## Related` (5) when they name other notes, and rule 6 applies to them in full.

---

### 13. Dev projects (`dev: true`)

Written only from a project whose Project Context has `dev: true` (key owned by bandit:project).
Every other project keeps the rules above unchanged. Once written, a plan note carries its own
rules wherever `file` or `lint` meet it. The card workflow itself is bandit:tasks'
(`references/dev-workflow.md` there).

- **Plan notes** (kind `plan`, §5 fields, its status following its card, §6) hold a card's full technical plan:
  the plan itself and the landing/commit sequence for an L card (any WBS L4 lines: bandit-dev:sprint's
  rule). Body per §12. They're written **inbox-first** like any skill-written note; they are
  **not** part of the planning-docs exception.
  **Sprint plan:** one plan note shared by every card of a sprint, written straight in with the
  sprint's records, no lane, the sprint's name in place of the card (old way: the sprint card).
  Each card's `Technical plan` names it.
- **Card briefs** (kind `brief`, §5 fields) are the long form of one card's Spec: one brief per
  card, its card set, written when `/bandit:tasks spec` writes the card (the card names it).
  **Inbox-first** like any skill-written note. Body per §12, with these H2s in order: `## Summary` ·
  `## Scope` (**In scope** / **Out of scope** lists) · `## Requirements` (table: `#` · Requirement ·
  Priority `Must`/`Should`/`Could` · Notes) · `## Decisions` (dated) · `## Verified facts
  (YYYY-MM-DD)` (each with where it was checked: a file, a tool result) · `## Open questions` ·
  `## Change log` (optional: one dated line per change to the brief and why) · `## Conclusions`
  (on the app's Notes, written when its card is completed: `references/conclusions.md`) · `## Related`.
  **No card state in the body** (column, lane, stage): the card holds it, so a copy goes stale. A
  `Card: {short id}` line under the summary is fine; it stays as written even when the card later
  gets a new id, since a former id still finds the card (bandit:tasks `references/board.md` → Card IDs).
  A sprint's card briefs sit with that sprint's records.
- **A sprint's records** are its plan, execution prompt, ledger, handover report and review record,
  plus the briefs of its cards. Kinds: the plan is a `plan`; the execution prompt, the ledger and
  the report are `reference`; the review record is a `log`; each carries the sprint's name in place
  of a card. They are written straight in, like the planning documents
  (`references/other-skills.md`): they are worked on across many sessions while the sprint runs.
- **WBS card links.** A project's WBS note carries a `## 🔗 Card links` table (format owned by
  bandit:plan: WBS id · card id · card title at creation · created). A row is added when its card
  is created, or, for a card that already exists, when bandit:plan builds a WBS over it (sprint
  mode). Writer: the chat that ran `/bandit:tasks spec` or bandit:plan, through this skill, as an
  edit of an existing note: its own approval row, written by the storage's safe edit.
- **WBS levels:** the names are bandit:plan's; L3 = one card is bandit:tasks'
  (`references/dev-workflow.md`); where L4 lines go is bandit-dev:sprint's.

---
