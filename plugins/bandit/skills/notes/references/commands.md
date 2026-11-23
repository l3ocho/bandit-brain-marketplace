# Part 3 — Commands

Every procedure starts by resolving the project and the domain (`references/model.md`) and reading
Part 2 (`references/conventions.md`). A project whose Project Context says `notes: none` gets one
line saying so, and nothing runs. The tools are `references/storage-app.md`'s.

**Proposal format** used by every command that writes on confirmation:

```
| # | Action | From | To | Why |
|---|---|---|---|---|
| 1 | file | Home Reno · Inbox · "Untitled" | Acme - wkflw · Requests · billing-dispute-report-2026-09-23 | request from CS Director |
| 2 | fields | Home Reno · Docs · queue-map | — | add the summary |
| 3 | delete | Home Reno · Inbox · "Untitled 7" | — | empty capture, the user asked to remove |
```

From and To name the note by its title and its place (board · column, or board · Inbox), never by
its id. The user answers "all", a list ("1, 3"), or "none". Execute only the approved rows, in
order, and report per row: done / refused (with its code and reason, `references/storage-app.md` →
Refusals). A refused row doesn't undo the others.

---

### `/bandit:notes onboard [Domain]`

Checks that every project in scope has its hub note (`references/storage-app.md` → The hub note).
Project scope: this project's board. Domain scope: every project board in the domain's folder.

1. Look for the hub note on each board (Create without a duplicate): a `reference` note titled with
   the project's slug.
2. Missing → one create row naming **one** column, with the summary drafted in the row for the user
   to edit: the column of the area the hub is about, or the board's first column when no area
   fits. The row never leaves the place open ("this column or that", "or left in its Inbox").
3. Found without a summary → one `fields` row with the drafted summary.
4. Present the proposal. On approval, create it with `notes_create` and file it with `notes_file`
   into the row's column, then read it back and report per row.

A new project is onboarded by bandit:project, which runs *Onboarding rows* below; typed in a
project chat to set one up, `onboard` says so and points there.

---

### Onboarding rows (run by bandit:project)

The notes step of project onboarding. bandit:project passes `domain`, `project` (slug), `type`,
`dev` and `notes` (when set) and the hub-note summary drafted in its interview. This procedure
returns rows; bandit:project puts them in its one combined proposal.

1. `notes: none` → return no row and say so in one line.
2. Otherwise return one create row for the hub note on the project's board, built as `onboard`
   does (above). The board may not exist yet: the row runs after bandit:tasks' board rows. A new
   board's columns are the ones its board rows create.
3. Anything found on the way that breaks a convention (a second hub note, a hub note in the Inbox)
   comes back as a fix row in the same list, marked `domain` when it is outside the project's
   board.
4. Execute the approved rows once the board exists: `notes_create`, `notes_file`, read back.
   Report per row.

---

### `/bandit:notes file [Domain] [note…]`

The review: takes inbox notes the user puts up and files them in their places, compliant. With note
names, reviews only those; without, the whole inbox. This is the command the user uses most — keep
it fast.

1. `notes_list` of the scope's board (Project scope: the project's board; Domain scope: each board
   in the domain's folder) and read each Inbox note in scope with `notes_get`. **Named notes:** only
   those. **No names:** rows only for helpers' drafts (`createdViaAssistant` true); the user's own
   Inbox notes are listed in one line by title and get a row only once the user names them
   (`references/model.md` → The inbox is the user's). Nothing is written in this step or the next.
   **Project scope:** only notes for this project's board get a row. Minutes, requests and notes
   for another project stay in their Inbox for the workflow project; list those in one line.
2. Per note, work out the row:
   - its place: the project's board and the column of the area it is about; a meeting or a request,
     the domain's workflow board; a card's brief or plan, its card, linked by the card workflow
   - its kind, its title per Part 2 §4 (looked for first, Create without a duplicate), a drafted
     summary shown in the row so the user can edit it, the kind's fields, its tags with the user's
     kept, and `active` or `waiting` when the content says so
   - **body:** untouched by default. Anything worth changing (a duplicated block, an ambiguous
     date like `09/10/2026`, customer data, broken structure) becomes a **separate body row**
     showing before → after, which the user approves or skips on its own
   - **open questions** (which project, which meeting type, what a date means): ask them now,
     all at once, before the proposal is final
   - a note too thin to classify stays in the Inbox untouched; say why in one line
   - **Consumed draft.** When the note filed is a rewrite, a brief or a WBS made from another inbox
     note (related to it, or named in its body's first line), add a separate **archive row** for
     that source note (status `archived`). Proof first: the filed note exists in its place and was
     read in this run. No proof, or the source isn't named → no row; the source stays
     (`references/other-skills.md` → Leftovers)
3. Present the proposal, rows ordered by place. A note with an unanswered question has no
   executable row yet — say so, and leave it alone.
4. On approval, per note: `notes_set_fields` (kind, summary, tags, the kind's fields) →
   `notes_update` when its title changes (read right before) → `notes_move` when its board changes
   → `notes_file` into its column (it leaves the Inbox, `triaged`) → `notes_set_status` when the
   row says `active` or `waiting` → any approved body row (`notes_get` right before, then
   `notes_update_section`). A card's brief: `notes_set_fields`, then `notes_link_card` when it is
   not linked yet, then `notes_file` into its card's column. A plan is linked by the card workflow
   when it is written: here its row gives it its summary and fields (`notes_set_fields`), which
   takes it out of the Inbox with its card's state; no `notes_file` and no status are set for it
   (`references/storage-app.md` → Status and filing). A plan with no card link gets no row: say
   which card it seems to belong to and leave it to `/bandit:tasks plan-tech`. A refused step stops
   that note's row; what ran is reported, and the note is read back.
5. **Read back** each note with `notes_get` after its last step; the note a write tool returned is
   not a read-back. Report per row, from that read, with each note's kind, summary, status and
   place; say "read back" only after that call. The read gives the place as ids: the board and
   column names come from `get_context`, and a brief's card from `notes_list` (`cards`). Suggest a
   `/bandit:tasks capture` for notes that describe work with no card — suggest only; bandit:tasks
   does the capture.

A plan's link to its card is its inbound link; the report names the card and the prompt
`/bandit:tasks stage {card} planned`. This skill never writes the board.

---

### `/bandit:notes lint [Domain]`

Read-only report whose rows are the fixes. Nothing is written until the user answers. Lint reads
the notes of the scope's boards (`notes_list`, then `archived: true`) and checks each note:

| Check | Breach |
|---|---|
| Scope | **The Inbox is skipped entirely**: the user's notes and helpers' drafts are not linted before review |
| Summary | A note out of the Inbox with none |
| Name | A title that breaks Part 2 §4 (a kind label in front, a date in the middle, a `.md` ending); two notes with one title in one place |
| Kind's fields | Minutes without `meeting` or `meetingDate`; a request without `requester` or `receivedOn` (Part 2 §5) |
| Status | `done` and not archived (fix: `archive`), except a plan linked to its card, which follows the card; `inbox` out of the Inbox |
| Card | A brief or plan with no card link and no `sprint-{name}` tag; a card link to a card that no longer resolves (read live, read-only) |
| Tags | A `sprint-{name}` tag whose sprint does not resolve through `get_sprints` |
| Hub note | A project board with no hub note, or with two (fix: `onboard`) |
| Customer data | Names, account numbers, addresses or call contents in a note's text (fix: a body row with placeholders, Part 2 §12) |

Each row is fixed with `notes_set_fields`, `notes_set_status`, `notes_link_card` or, for a title or
a body row, `notes_update` / `notes_update_section` after a read, as the row says.

---

### `/bandit:notes delete {note…}`

1. Resolve each named note: `search` with its title, then `notes_list` of its place (and
   `archived: true`). The match is a note with exactly that title in the scope. Zero or several →
   ask; never pick one.
2. Propose one `delete` row per note, with its place and status.
3. Say that a deleted note goes to the Trash with its text, versions and links, can be brought back
   with `restore` for 30 days, and is then gone for good; offer `archive` for anything that isn't
   junk.
4. On approval: `notes_get` each approved note again (it is still there and still the one named),
   then `notes_delete`; report per row with the days the Trash keeps it, read from
   `notes_list_trash` (`daysLeft`).

---

### `/bandit:notes archive [Domain]` · `/bandit:notes restore {note}`

The app keeps an archived note in its place and the status says it is archived
(`references/storage-app.md` → Archive, restore, delete).

- **Archive:** find the scope's notes with status `done` (`notes_list`). Propose one row per note
  setting `archived`. On approval, `notes_set_status` → `archived`, read back. A plan linked to its
  card follows the card and is not archived by hand (`PLAN_FOLLOWS_CARD`): it gets no row. A
  sprint's records are archived by bandit-dev:sprint's close, not by a row here.
- **Restore:** find the named note in the place's archived notes (`notes_list` with
  `archived: true`), then in the Trash (`notes_list_trash`, the whole account's: match the title
  and the place, a row's `boardId`). Exactly one match, or ask.
  From the archive: propose `triaged`, or the status the user names, since the app does not keep the
  one it had; on approval `notes_set_status`. From the Trash: propose bringing it back as it was,
  with the days left; on approval `notes_restore`. Read the note back with `notes_get` and report
  its status and place.
