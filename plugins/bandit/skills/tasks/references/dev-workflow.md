# 🛠️ Dev workflow — the card commands

**Commands:** `/bandit:tasks spec` `/bandit:tasks spec reconcile` `/bandit:tasks scope` `/bandit:tasks plan-tech`
`/bandit:tasks stage` `/bandit:tasks pick-ready`
**Owns:** surface roles · card boundaries · record homes · the dev card procedures
**Board rules** (lanes, stages, lane template headings, Spec lock, tag merging, card fields, the
sprint card, the dev board shape): `references/dev.md`. Read it first; its gate applies here too.

One card workflow shared by Claude.ai and Claude Code. The card is the record (Gitea issues are
retired; Gitea keeps PRs, the wiki, releases and CI). Project specifics (branch prefixes, gates,
how work lands, where records live) stay in the repo; its `lane-triage.md` points here. Repo
commands never reuse a command word of this skill (rulebook R15): a repo triage command is not
named after `/bandit:tasks triage`.

**Sprints are bandit-dev:sprint's** (Claude Code): its 12 planning steps, the sprint in the app (its
cards, run order, expected date and status), seeding the batch to Assigned, and the ledger's steps and
waves. A sprint gives its date only to cards with no due date, at commit; a card with its own date keeps it. It uses the `plan-tech` card-write rules (drift check, read
before writing, show old and new before replacing) from its own steps instead of restating them, and
edits no Spec or brief unless the user asks (`spec reconcile` runs only on the user's word).
`pick-ready` and `/bandit:tasks week` only pick and date ready work; neither plans a sprint.

---

## 🧭 Surface — who may do what

**Identify the surface by where the Project Context was read from, never by which tools exist.**

| Project Context source | Role |
|---|---|
| Claude.ai project instructions (also a Claude Code session bound to a Claude.ai project) | **Claude.ai** — high-level |
| Repo `CLAUDE.md` in the working directory | **Claude Code** — technical, a superset |
| Neither | No Dev commands |

| | Claude.ai | Claude Code |
|---|---|---|
| Commands | `spec`, `scope`, `stage … ready` (on the user's approval), `pick-ready` | `spec`, `scope`, `plan-tech`, `stage` (any), `pick-ready`, incident `spec` |
| Writes on a card | `Spec` only | `Spec` on cards it creates; `Technical plan` on any card |
| Refuses | `plan-tech`, plan notes, `stage … planned`, subtasks, branch / file / code detail on cards (effort only as a first estimate, `references/dev.md` → Card fields) | Rewriting the `Spec` of a card Claude.ai wrote |

Every Dev command checks the role **before acting**. Outside it → refuse and name the surface that
can do it (*"`plan-tech` runs in Claude Code, from the repo"*).

- **Claude.ai going technical:** write the point into `Spec` → *Open questions* as a plain item
  and move on. No branch names, file paths or code.
- **A spec problem on a card with a Spec** (Claude Code on a Claude.ai card, or any locked Spec):
  settled somewhere already → fix it through the Spec lock (`references/dev.md`), no question. Not
  settled anywhere → add a **card comment** starting `Spec change needed:` (the app's intended
  path). The card stays `stage/spec` until the user resolves it, on either surface.

---

## 📐 Card boundaries

| # | Rule |
|---|---|
| B1 | One card = one lane, one branch, one landing, one "done" signal, pickable into a sprint on its own. **Landing** is however the repo lands work (a merge, or a PR); an Incident's merge to `main` plus its back-merge counts as one |
| B2 | No WBS for simple work. A WBS only for work spanning more than one branch or more than one sprint |
| B3 | The WBS lives in the vault (bandit:plan). L1 and L2 never become cards |
| B4 | Lazy: the next L3 work package becomes a card only through `spec`, which cites its `WBS-X.Y.Z` |
| B5 | Thin card: `Spec` + `Technical plan`, each short. Everything else goes in the doc |
| B6 | Before creating: merge check (below). Skipped for Incident |
| B7 | Up to **L**. An L card's plan note lays out the landing/commit sequence. **XL splits** into 2+ cards, wherever the size is set: at `spec`, at `plan-tech` and at a sprint's sizing step. **Avoid** a card that is both high effort and high complexity (L and Complex): split it too. **No umbrella cards** that only group smaller ones: the smaller cards are the work, and a sprint takes them in its place. Each new card keeps the original's lane and stage and stays in the same sprint: added to its record (`manage_sprints { action: "add_cards" }`), or on an old-way sprint its `sprint/{name}` tag and a blocker of the sprint card |

**WBS on dev projects.** Level names are bandit:plan's. Here: **L3 work package = one card**,
created lazily through `spec` (B4). **A Technical home board is never loaded** (`/bandit:tasks load` refuses
it). Where L4 lines go is bandit-dev:sprint's.

---

## 🗂️ Record homes

The card is the work record. Every other record a lane produces has its home in the repo's
`lane-triage.md` **Record homes** table, never in this file (rulebook R13). A dev repo maps at least:

| Record | Lane |
|---|---|
| Plan note | Any lane with a `Technical plan` (the vault, through bandit:notes) |
| Postmortem | Incident |
| Maintenance log entry | Maintenance |
| Decision record | Feature, Tech Debt |
| Release notes | Any release |

A step that writes one of these reads its home from that table. No table, or the record isn't in
it → stop and ask the user; never pick a place.

**Recurring runbook cards.** A recurring card (it belongs to a series) that follows an existing
runbook needs no plan note: its `Technical plan` carries `Runbook: {repo path} §{section}` instead.
`stage … planned` and audit V2 accept that line in place of a filed plan note.

---

## ⚙️ Procedures

### `/bandit:tasks spec` — create or update one card

1. **Gate and role** (above). Resolve scope (`references/scope.md`).
   **Input.** A conversation, a parked card from triage, or a **Clarified Specification** from
   bandit:clarify. A Clarified Specification maps straight in: Summary → Outcome, In/Out of Scope →
   Scope in/out, Requirements (Must/Should) → Acceptance, verified Assumptions → Decisions,
   unverified ones and Open Questions → Open questions. The Spec's `Source` names it:
   `Source: clarify, {date}`, and the brief keeps the full specification.
   **Baseline.** The user's own words are the Spec. Read the repo, board and notes before asking; ask only what they cannot answer, in plain words, no codes. Add nothing the user did not ask for: anything that differs is shown as old and new before it is written.
2. **Place it** by the column rule (`references/dev.md` → Card fields), never parked. Lane from the
   agreed scope. A WBS exists for the project → cite the matching `WBS-X.Y.Z` (bandit:notes finds
   the doc).
3. **Merge check (B6):** `list_tasks { boardId, boardColumnId, tagId: {lane tag id}, completed: false }`
   (filters combine with AND). An open card with the same outcome → propose adding a subtask to it
   instead. Title match is a judgment call: show both, the user decides.
4. **Propose** the card: title, every Card fields value, and the description built from
   `get_context → laneTemplates` (`references/dev.md` → Card sections).
   Effort XL → propose the split into L-or-smaller cards before anything is created (B7).
5. **On yes:** one `create_tasks` entry with `boardId` and every Card fields value (subtasks and
   dependencies included); a screen-changing card gets `stage/spec` only through the Design step's gate. Read its result (refused → report `code`, `reason` and `field`), then `get_task` and check it.
   **Updating an existing card** (a merge match, or a parked item triage just moved into its
   column): `get_task` → fill missing fields → write `Spec` only where it's empty; a Spec with text
   is locked (`references/dev.md` → Spec lock): a settled change is written straight away and
   reported old and new → one `update_tasks` entry (fields and tags together). Claude Code never rewrites a `Spec` whose `Source` is Claude.ai (it adds a
   `Spec change needed:` comment instead). Tags per `references/dev.md` → Tag merging.
6. **Brief:** hand bandit:notes the card's brief (new, or updated when it exists), `board-task` =
   the card's short id; the Spec's `Brief:` line names its filename.
7. **WBS link:** the card cites a `WBS-X.Y.Z` → hand bandit:notes one approval row adding the
   Card links row to `{slug}-wbs.md` (bandit:notes owns the write and the path, bandit:plan the
   format).

### Design step — screen-changing cards, before `stage/spec`

Pipeline stage 4 (`docs/pipeline.md` in the marketplace): after `spec` writes the card, before `stage/spec`. Cards that change no screen skip it.

1. **Which cards.** A card changes a screen when its Outcome or Scope in changes what a page shows
   or how it looks. Read it from the card's own words; unclear → ask the user once, yes or no.
2. **Route: Claude Design inside Claude Code**, from the app repo, starting from the real page.
   **Once per project**, `/design-sync` loads the design system from the code; run it again when the
   theme changes. Then `/design` makes the card's design. The design system copies on the old
   standalone design site are not used (the site closes 2026-12-14); nothing there is deleted.
   **Closing step.** When the design changed the shared look (colours, fonts, spacing, shared
   components), the session ends by asking the user to run `/design-sync`, a Claude Design command the
   helpers cannot run, and writes the answer on the design card: `<p>Design sync run {date}</p>` or
   `<p>Design sync not needed: {reason}</p>` (on the build card when there is no design card).
3. **Trap check before linking.** Check the design against the project's recorded traps (its
   `CLAUDE.md` and the docs it names). A design that hits one is changed before it is linked.
4. **Link and approval.** The design page link (the Claude.ai page the user approves on, a full
   `https://` address) goes in the Spec's Source block, `<p>Design: {page link}</p>` beside `Brief:`,
   and where the handover files live goes beside it, `<p>Handover: {where the handover files live}</p>`.
   The agent that lands the handover and writes the card's Spec adds both. The user approves the page
   explicitly; record `Design approved {date}: {page link}` as a card comment. Neither is assumed.
5. **Gate.** On a screen-changing card, `spec` and `stage … spec` write `stage/spec` only when the
   `Design:` line and the approval comment are both there. Missing → the card keeps its lane with no
   stage, and the report names the design step as owed.

**Design card** (the project's Project Context has a `design:` line; bandit:project
`references/project-context.md` owns it). The design gets a card of its own, and its handover
unblocks the build:

1. **Create it with the Spec.** Right after `spec` writes a screen-changing card, one `create_tasks`
   call makes `Design: {build card title}` in the `design:` line's column (on the home board unless the
   line names a board), with `dependencies.blocks: [the build card]` so the dependency gate names the
   build card's gate line ("the design handover is linked and approved"). Its description: the build
   card's short id, its brief's filename and its Spec's Outcome, as the design's input. A link made
   later with `link_tasks` gets the gate's generic notice.
2. **The design session's result is its handover.** Steps 2 and 3 above run on the design card. Once
   the handover lands, the design card carries `<p>Design page: {page link}</p>` (the Claude.ai page
   the user approves on, a full `https://` address) and `<p>Handover: {where the handover files live}</p>`.
   The agent that lands the handover adds both, the user's approval goes on as the comment
   `Design approved {date}: {page link}`, and then the design card is completed. It is not completed
   without the page link. It is not completed either without one of the two design sync lines (the
   closing step of the Design step, item 2).
3. **The build card follows.** Its Spec's Source block gets `<p>Design: {page link}</p>`, the same full
   web address as the design card's (a first line in Source, no Spec override needed when the line is
   new), and its gate sub-task is ticked. The handover files are found through the design card's
   `Handover:` line, reached through the build card's `blockedBy`.
4. **Gate.** `stage/spec` on the build card only once its design card is complete. Open → the build
   card keeps its lane with no stage, and the report names the design card.

Without a `design:` line, steps 1 to 5 above run on the build card itself, as before: its Source
carries both `Design: {page link}` and `Handover: {where the handover files live}`, and the handover
files are found through that `Handover:` line.

### `/bandit:tasks spec reconcile {card…}` — bring locked Specs in line with decisions

For cards whose Spec is locked and has fallen behind decisions taken since (in comments, the brief,
the sprint's ledger or an old-way sprint card). Run only when the user asks; sprint planning never calls it.

1. **Gate and role** (above). Per card: `get_task` → current `Spec`, comments, linked brief.
2. Build the new `Spec` from the same template headings: answered questions move into Decisions,
   Open questions keep only what is still open, acceptance lines match the decisions. Nothing
   outside `Spec` changes.
3. **Apply**, no question: `update_tasks { items: [{ taskId, description, overrideSpecLock: true }, …] }`, one entry per card, with the new description, then read `results` and
   `get_task` each to check it. Only settled changes go in; anything still open stays in Open questions.
4. **Report** each card's old and new `Spec` side by side, changed lines marked, all cards together.
5. Add a comment on each changed card: `Spec reconciled {date}: {one line on what changed}`. The brief
   gets the same change and a Change log line through bandit:notes.

**Incident** (`/incident` in the repo → `spec` with `lane/incident`, Claude Code): no stage tag, no
merge check, `dueDate` today, created in its area column, then `update_tasks { items: [{ taskId, executionState: "assigned" }] }`
straight away. A card due today reaches Assigned on its own only at the next midnight run,
too late for an incident. The postmortem cites the card title and lives where the repo's Record homes
table says (**🗂️ Record homes**).

### `/bandit:tasks scope {card}` — settle what's still open on one card

1. **Gate and role** (above). `get_task` → Spec, comments; the brief (its Change log first) and the
   plan note through bandit:notes.
2. **Sort every gap:** an Open question already answered (in this chat, the brief, the plan note or
   a comment), an acceptance line the brief has and the card lacks, a decision not yet in Decisions.
   Settled → it goes in. Never bring back a limit the brief's Change log shows the user removed.
3. **Write** the settled ones straight away, as `spec reconcile` does, and make the same change in
   the brief (with a Change log line) and the plan note through bandit:notes.
4. **Ask only what is truly open**, one decision table: `Issue | Recommendation | Different from my
   request? | How`. On the answer, write it the same way.
5. **Report** in three lines: what changed, what is still open, the next stage step.

### `/bandit:tasks plan-tech` — Claude Code only

Steps 1 and 5 are the **card-write rules** bandit-dev:sprint calls for a sprint's cards.

1. **Drift check first.** Compare the repo `CLAUDE.md` Project Context with the **production**
   Claude.ai block: the instructions version matching the project's self-check stamp, read the way
   bandit:project reads its vault folder. Report any difference before anything else; don't fix it.
2. **List** the `stage/spec` cards (`list_tasks { boardId, tagId: {stage/spec tag id}, completed: false }`). Separately list the
   ones whose plan note is already filed (ask bandit:notes whether the filename in `Technical plan`
   exists in the project folder) and offer the `planned` flip for them.
3. The user picks a card → technical discussion.
4. **Plan note** through bandit:notes: a new `plan` note in `_inbox/` (type, filename and keys are
   bandit:notes' rules), `board-task` = this card's id.
5. **Card:** `get_task` → read the current `Technical plan` first (rulebook R14). Write only the
   lines that are missing (plan-note filename, branch, size, summary). A line already there with a
   different value (above all the branch, the merge commit or the PR URL) → show both and ask the user;
   never replace it silently. Every other line stays. → one `update_tasks` entry with the description and `effort` ≤ L (XL →
   propose the split, B7); a Claude.ai estimate that differs → show both and ask → the build steps
   as sub-tasks, ordered and read back (`references/board.md` → Sub-tasks).
6. **The card stays `stage/spec`.** It moves only after the user files the note (`/bandit:notes file`).

### `/bandit:tasks stage {card} {spec|planned|ready}` — the only stage writer

1. **Role:** `ready` is set only on the user's explicit approval, on either surface (or by the user by hand).
   Claude.ai sets nothing else. Claude Code sets `spec` and `planned` on its own judgement.
2. `get_task` → refuse on a `lane/incident` card. **`spec`** on a screen-changing card: refuse without its
   `Design:` line and approval comment (Design step, gate), and name the step owed; with a `design:`
   line in the Project Context, also refuse while its design card is open, and name that card.
3. **`planned`:** its plan note must be filed (bandit:notes lookup of the filename in `Technical
   plan`), or, on a recurring card, a `Runbook:` line must name the runbook (**🗂️ Record homes**).
   A **shared sprint plan** counts: one filed plan note whose filename sits in the `Technical plan`
   of several cards of the same sprint. Each card still needs its own plan lines (branch, size,
   summary).
   Neither → say so and stop. **`ready`** expects a `planned` card; from `spec`, say so
   and ask the user to confirm.
4. **Write the tags** per `references/dev.md` → Tag merging (one `stage/*`, every other tag kept),
   `update_tasks { items: [{ taskId, tagIds }] }` with the full merged set.

### `/bandit:tasks pick-ready` — Week `plan` over ready cards

Runs **Dating the week** (`/bandit:tasks week`, `references/week.md`) with its `stage/ready` filter, and adds nothing: a
weekly pick of approved cards, not sprint planning. Picked cards get due dates only; the midnight
job moves them into Assigned when due. A card picked for today → its `update_tasks` entry also carries
`executionState: "assigned"`, since the midnight run has already passed. Cards already in a sprint (a record or a `sprint/*` tag, `references/board.md` → Tags)
are the sprint's work: they are not candidates.

