# Part 3 — Commands

Every procedure starts by resolving the storage and the domain (`references/model.md`) and reading
Part 2 (`references/conventions.md`, and for the vault `references/conventions-vault.md`).

**Two storages.** Each command's steps below are the vault's; its **On the app's Notes** block says
what replaces them for a project whose notes are in the app, with the tools of
`references/storage-app.md`. `init`, `home` and `settings` are vault-only: run for a project on the
app's Notes, say so in one line and stop. A project with no word on its storage is a vault project,
and its commands run exactly as written here.

**Proposal format** used by every command that writes on confirmation:

```
| # | Action | From | To | Why |
|---|---|---|---|---|
| 1 | move | _inbox/Untitled 3.md | Requests/billing-dispute-report-2026-09-23.md | request from CS Director |
| 2 | frontmatter | Meetings/x.md | — | add type, status, domain |
| 3 | delete | _inbox/Untitled 7.md | — | empty capture, the user asked to remove |
```

The user answers "all", a list ("1, 3"), or "none". Execute only the approved rows, in order, and
report per row: done / refused (with reason). A refused row doesn't undo the others.

On the app's Notes, From and To name the note by its title and its place (`BanditBrain · Inbox` →
`BanditBrain · Docs`), never by its id; a refusal is reported with its code and reason
(`references/storage-app.md` → Refusals).

---

### `/bandit:notes onboard [Domain]`

Brings an existing domain in line with the conventions. It runs in **stages**, each proposed and
confirmed separately, because a structure change should be settled before hundreds of file edits
are planned against it.

**Stage A — Structure.** List the domain root and `Claude/`. Propose:
- Missing core folders (`_archive/`, `_attachments/`, `Claude/`, `Projects/`) — create
- A missing hub note `Projects/{slug}/{slug}.md` for each project folder — create
- Run with a Project Context (a workflow project): this project's own `Claude/ai-{slug}/`,
  `Projects/{slug}/` and hub note `{slug}.md`, whichever is missing — create
- Attachments outside `_attachments/` — move (with any rename per Part 2 §4 and its embed edits)
- Legacy folders → standard names. Common mappings:

  | Found | Proposed |
  |---|---|
  | `Department/`, `Minutes/`, `Meetings notes/` | `Meetings/` + `meetings` module |
  | `Outstanding/`, `Asks/` | `Requests/` + `requests` module |
  | `Agents/` | `Claude/` |
  | `Claude/claude-ai-settings/`, `Agents/{Project}/claude-ai-settings/` | `Claude/ai-{slug}/` (slug from the Project Context `project:`, or ask) |
  | `Claude/claude-ai-skills/`, `Claude.ai-Skills/`, any skills folder | `_archive/` (skill sources live in the bandit-brain-marketplace repo) |

- Folders that fit nothing (e.g. `Career/`, `Apps/`): offer map-to-module, move under
  `Projects/`, or "propose a new module" (a change to this skill — stop and say so).
- Anything in `Claude/` that isn't settings → its proper folder.

After Stage A moves a settings folder, **the project instructions still point to the old path.**
Say so and tell the user to run bandit:project (targeted update) to set the Project Context
`domain:` and `project:` and the derived `webdav_folder`. Don't edit instructions from here.

**Stage B — Templates.** Read every file in `_templates/`. Propose the frontmatter
standardisation (pre-fill and legacy key map in Part 2 §10). Show each template's before/after
frontmatter; the body stays untouched. Also propose **creating any missing standard template**
(Part 2 §10: `new-note.md` always, a meeting template when `meetings` is on, `request.md` when
`requests` is on).

**Stage C — Notes.** Walk every content folder. **Skip `_inbox/` entirely** — it's the user's; review
happens through `file`. For each
`.md`: missing or legacy frontmatter keys (a missing `summary` gets a drafted sentence in the
row, for the user to approve or edit; a note moved in from another system gets `source: migrated`), YAML
style and key order (Part 2 §5), customer data in the
body, wrong `status` for its location, filename breaches
(including date-first names like `2026-09-23-csnotes-feature-x.md` → date-last). Renames outside
`_inbox` need a backlink search (read the domain's `.md` files for `[[old-name` and include those
link edits as rows). If Stage C would exceed ~40 rows, propose it folder by folder.

**Stage D — Home and settings.** Run `home`. Record `mynotes-version: 2` and the modules in the
README frontmatter. Then run the `settings` check and offer its proposal (applied only once the user
confirms Obsidian is closed everywhere); if they'd rather change them in the app, give them the
table instead.

**Upgrading a v1 domain** is `onboard` again: Stage A adds `_attachments/` and hub notes, Stage B
pre-fills templates, Stage C adds `summary`, converts `project` to a link and fixes YAML style,
Stage D bumps the version.

**Project scope** runs a smaller onboard instead of Stages A–D: check that `Projects/{slug}/`,
its hub note `{slug}.md` and `Claude/ai-{slug}/` exist (propose creating whichever is missing),
then run Stage C on
`Projects/{slug}/` only. Domain-level findings (legacy folder names, other projects) come as
fix rows marked `domain`, built with Stage B/C, after this project's rows. They run only when the user
approves them by number (`references/model.md` → Scope).

**On the app's Notes: the hub note only.** Folders, templates, frontmatter style and Obsidian
settings have no counterpart in the app, so Stages A to D do not run. Project scope: look for the
project's hub note on its board. The storage reference has no hub note yet, so it is defined here:
a `reference` note titled with the project's slug, with its summary, in the column of the area it
is about (`references/storage-app.md` → Places). Look for it first (Create without a duplicate).
Missing → one create row naming its column, the summary drafted in the row for the user to edit;
the column is asked when no area fits. Found without a summary → one `notes_set_fields` row.
Domain scope: the same for every project board in the domain's folder. On approval, create it with
`notes_create` and file it with `notes_file` into the row's column, then read it back. The
settings folders `Claude/ai-{slug}/` and `Claude/code-{slug}/` stay vault rows (`references/model.md`
→ Which storage).

---

### Onboarding rows (run by bandit:project)

The notes step of project onboarding. bandit:project passes `domain`, `project` (slug), `type`,
`dev` (when set), `notes` (when set), whether the project has a Claude Code surface (item 8 decides on these two),
the hub-note summary drafted in its interview, and, for a new domain, the chosen modules. This
procedure returns rows; bandit:project puts them in its one combined proposal.

1. `nc_webdav_list_directory("MyNotes")`. The domain isn't there → return the `init` rows (step
   3 of `init` below, with the modules bandit:project passed) and stop here.
2. List the domain root, `_templates/`, `Projects/` and `Claude/`. Return a row for **every
   missing item** of the domain's core structure (Part 2 §1: every domain has all of them) and of
   this project, in this order, whatever the project type:

   | # | Item | When |
   |---|---|---|
   | 1 | `_inbox/` | missing |
   | 2 | `_templates/` | missing |
   | 3 | `_templates/new-note.md` (Part 2 §10: standard keys, `status: inbox`, the domain written in) | missing |
   | 4 | `_archive/` | missing |
   | 5 | `_attachments/` | missing |
   | 6 | `Claude/` | missing |
   | 7 | `Claude/ai-{slug}/` | missing |
   | 8 | `Claude/code-{slug}/` | missing, and `dev: true`, or a project without `dev: true` that runs in Claude Code (twin) |
   | 9 | `Projects/` | missing |
   | 10 | `Projects/{slug}/` | missing (every type, workflow included) |
   | 11 | `Projects/{slug}/{slug}.md` hub note (Part 2 §1: `type: reference`, the drafted `summary`, a `## Docs` list) | missing (every type, workflow included) |
   | 12 | `README.md` (generated by `home`) | missing |

   These are **creates only**, of empty standard folders and starter files. They never move,
   rename, edit or delete anything that exists.
3. Everything else at domain level comes back as **fix rows** marked `domain`, after the core
   rows: legacy folder names, a settings folder outside `Claude/`, attachments outside
   `_attachments/`, files that fit no folder, module folders (modules are opt-in: propose adding
   the module or moving the folder, recommended first). Build each with the `onboard` Stage B/C
   procedure (renames carry their backlink rows).
4. Execute only the approved rows, in order: folders with `nc_webdav_create_directory`, the
   template and hub note as new files (`if_match` omitted), then the README by running `home`.
   A row whose parent folder row was declined is skipped. Report per row.
5. If the README already existed and any row ran, run `home` afterwards to refresh it (an
   auto-write, `references/storage-vault.md`).

**On the app's Notes** (`notes: app`): no domain scaffold and no folder for notes.
1. List `MyNotes` and the domain's `Claude/`. Return create rows only for the settings, which stay
   in the vault: the domain folder and `Claude/` when missing, item 7 `Claude/ai-{slug}/`, and item
   8 `Claude/code-{slug}/` under the same condition as above. A project without `dev: true` that
   runs in Claude Code (a twin) also gets items 9 and 10, `Projects/` and `Projects/{slug}/`, when
   missing: they hold its working-folder manifest (bandit:project `references/workdir.md`), not its
   notes, so no hub note goes there. No `init`, other core-folder, template or README rows.
2. Return one create row for the hub note on the project's board, built as `onboard` does on the
   app's Notes (above). The board may not exist yet: the row runs after bandit:tasks' board rows.
3. Domain-level fix rows as in step 3 above, for the settings folders only.
4. Execute the approved rows: the folders with `nc_webdav_create_directory`, then, once the board
   exists, the hub note with `notes_create` and `notes_file`, read back. Report per row.

---

### `/bandit:notes init {Domain}`

For a new domain — a new job, a new business area. **Vault only.** On the app's Notes a domain is
a board folder, made with the board step of onboarding (bandit:tasks), not here.

1. Check `MyNotes/{Domain}` doesn't exist. If it does, stop and offer `onboard` instead. Typed
   in a project chat to set up a new project: say that's bandit:project' onboarding and stop.
2. Ask which modules to enable (multi-select from the Part 2 §2 list).
3. Propose: the domain folder, core folders, module folders, pre-filled starter
   `_templates/new-note.md` (and `meeting-entry.md` / `request.md` when those modules are on),
   and the README.
4. On confirmation, create them in that order, then run `home`.
5. Obsidian creates `.obsidian/` the first time the user opens the folder as a vault. Tell them to do
   that, close it again, and then run `/bandit:notes settings {Domain}` to apply Part 2 §11.

---

### `/bandit:notes home [Domain]`

Rebuilds `{Domain}/README.md` from the **README template** in `references/readme-template.md`. Runs unattended from a
scheduled task, so it **never asks** and writes only the README. **Vault only:** the app lists a
board's notes itself, so a project on the app's Notes has no home page to build.

1. Read the existing README if there is one: keep its frontmatter (update `generated`) and the
   whole `## Notes` section verbatim. No README → start from the template with
   `modules` inferred from which module folders exist.
2. List the domain (skip the ignore list). Gather:
   - Folder map: each core and module folder with its file count
   - Projects: each `Projects/{slug}/`, its hub note's `summary` (read the hub's frontmatter),
     its `Claude/*-{slug}` settings folders, and its meetings (files in `Meetings/` starting with
     `{slug}-minutes-`, newest 5)
   - Recent meetings: the newest 10 files in `Meetings/` of **every** meeting type, grouped by
     the filename prefix (`supervisors`, `department`, `{project}`); `-short` versions listed
     beside their full version, not as separate rows. Read each one's `summary`
   - Reference notes: every `type: reference` note outside `Projects/` (found by reading the
     frontmatter of evergreen-named files) with its `summary`
   - Inbox: count and the oldest item's date
   - Requests: read frontmatter of each note in `Requests/`; list `active` and `waiting` ones
     with `requester`, `due`
   - Pending archive: notes with `status: done` found while reading (Requests, plus any file
     already read). Don't open every note in the vault for this — that's `lint`'s job
   - Conflict copies spotted in listings
3. Write it: read → strip the etag to bare hex → `if_match`. A 412 means the user edited it in the
   meantime: re-read once, re-merge the `## Notes` section, write again. A second 412 → stop
   and report.
4. **Links:** Obsidian can't link to a folder, so folders are shown as `` `path/` `` and notes as
   `[[note-name]]`. Never link across domains. Every note the README lists carries its
   `summary` beside the link; a note with no `summary` shows `—` and counts under Needs attention.

When run by a schedule, the only output that matters is the file. Finish with one line: what
changed (counts), or "no changes".

---

### `/bandit:notes file [Domain] [note…]`

The review: takes inbox notes the user puts up and moves them to their homes, compliant. With note
names, reviews only those; without, the whole inbox. This is the command the user uses most — keep
it fast.

1. List `{Domain}/_inbox/`. **Read** each note in scope; for each non-markdown file plan a
   sidecar. Notes that already carry `file-to` were structured by another skill: propose their
   move as-is. Nothing is written in this step or the next.
2. Per note, work out the row:
   - `type` and destination: `file-to` if set; otherwise from content (meeting → `Meetings/`,
     someone asking for something → `Requests/`, about a project → `Projects/{slug}/`,
     settings → `Claude/{prefix}-{slug}/`)
   - **Project scope:** only notes for this project get a row (destination `Projects/{slug}/`, or
     its `planning/` or a sprint folder on a project with sprint folders: Part 2 §1).
     Everything else stays in `_inbox` for the workflow project; list those in one line
   - **Destination not onboarded yet:** `file-to: Projects/{slug}/` and that folder doesn't
     exist → stop that row and point to bandit:project onboarding first (the note stays in
     `_inbox` untouched). Once the hub exists, filing adds `project: "[[{slug}]]"` (Part 2 §5)
   - filename per Part 2 §4, checked for uniqueness
   - frontmatter: add the missing keys, remove `file-to` (its job is done), `status: triaged`
     (or `active` / `waiting` if the content says so), `updated: today`, a drafted `summary`
     (shown in the row so the user can edit it), `project: "[[{slug}]]"` when it's about a project,
     a picked body value copied into its key (Part 2 §10), YAML style and key order per
     Part 2 §5
   - attachments: embedded files not yet in `_attachments/` move there; pasted-image names get
     renamed per Part 2 §4 with the embed updated in the same row
   - **body:** untouched by default. Anything worth changing (a duplicated block, an ambiguous
     date like `09/10/2026`, customer data, broken structure) becomes a **separate body row**
     showing before → after, which the user approves or skips on its own
   - **open questions** (which project, which meeting type, what a date means): ask them now,
     all at once, before the proposal is final
   - If a note is too thin to classify, leave it in `_inbox` untouched and say why in one line
   - **Consumed draft.** When the note filed is a rewrite, a brief or a WBS made from another inbox
     note (named in its `related`, or its body's first line), add a separate **archive row** for
     that source note (Part 2 §7 stamps, `status: done`, to `_archive/_inbox/`). Proof first: the
     filed copy exists at its destination and was read in this run. No proof, or the source isn't
     named → no row; the source stays (`references/other-skills.md` → Leftovers). A source with the
     same filename as the filed copy gets one row with both options: **delete** (recommended: an
     archived twin breaks uniqueness, Part 2 §4) or archive under a more specific name
3. Present the proposal. Order the rows by destination so similar items group. A note with an
   unanswered question has no executable row yet — say so, and leave it alone.
4. On approval, per note: **move** to the new path with the new name → **edit** the frontmatter
   there (bare-hex `if_match`) → apply any approved body rows → move or rename the attachments
   listed in the row. A failed move leaves the inbox note untouched; a failed edit leaves the
   note in its home folder unedited, reported as half-done.
5. Report per row. Suggest a `/bandit:tasks capture` for notes that describe work with no
   `board-task` — suggest only; bandit:tasks does the capture.

**Plan notes (dev projects, Part 2 §13).** Filing a `type: plan` note:
- sets `status: active` (not `triaged`);
- adds a **separate row**: one line in the hub note's `## Docs` list linking the plan note
  (`- [[{plan-note}]] — plan: {card title}`), edited with its etag. This is the plan note's inbound
  link; skipping the row leaves it an orphan;
- its report resolves `board-task` to the card's **current** title live (`get_task`, read-only) and
  adds: *card {title} can move to `stage/planned`: run `/bandit:tasks stage {card} planned`*. This
  skill never writes the board.

**On the app's Notes.**
1. `notes_list` of the scope's board (Project scope: the project's board; Domain scope: each board
   in the domain's folder) and read each Inbox note in scope with `notes_get`. **Named notes:** only
   those. **No names:** rows only for helpers' drafts (`createdViaAssistant` true); the user's own
   Inbox notes are listed in one line by title and get a row only once the user names them
   (`references/model.md` → The inbox is the user's). Nothing is written in this step or the next.
   **Project scope:** only notes for this project's board get a row. Minutes, requests and notes
   for another project stay in their Inbox for the workflow project; list those in one line.
2. Per note, work out the row: its place (the project's board and the column of the area it is
   about; a meeting or a request, the domain's workflow board; a card's brief, its card; a plan, left
   to the card workflow),
   its kind, a drafted summary shown in the row, the kind's fields, its tags with the user's kept,
   and `active` or `waiting` when the content says so. Body changes, open questions, notes too thin
   to classify and consumed drafts are handled as in the vault steps above, with an archive row
   that sets `archived` (`references/storage-app.md` → Archive, restore, delete).
3. Present the proposal, rows ordered by place.
4. On approval, per note: `notes_set_fields` (kind, summary, tags, the kind's fields) →
   `notes_move` when its board changes → `notes_file` into its column (it leaves the Inbox,
   `triaged`) → `notes_set_status` when the row says `active` or `waiting` → any approved body row
   (`notes_get` right before, then `notes_update_section`). A card's brief is linked with
   `notes_link_card`, then filed with `notes_file` into its card's column. A plan is not linked
   here: when a plan is linked is the card workflow's (bandit:tasks), and a linked plan follows its
   card (`references/storage-app.md` → Status and filing). A refused step stops that note's row;
   what ran is reported, and the note is read back.
5. Report per row, with each note's kind, summary, status and place.

A plan on the app's Notes needs no hub `## Docs` line: its link to its card is its inbound link. The
report names the card and the same `/bandit:tasks stage {card} planned` prompt, where the card
workflow links the plan.

---

### `/bandit:notes lint [Domain]`

Read-only report whose rows are the fixes. Nothing is written until the user answers.

Checks (each row: file, breach, proposed fix):

| Check | Breach |
|---|---|
| Scope | **`_inbox/` is skipped entirely** — only its count and its filenames are read (for Uniqueness). The user's notes aren't linted before review |
| Location | A folder that's neither core nor an enabled module; non-settings content in `Claude/`; a skill folder inside a domain; a non-markdown file outside `_attachments/` (except `.canvas`/`.base`, §8) |
| Claude subfolders | Name not `{ai\|code\|design}-{slug}` |
| Project pairing | A settings folder whose slug has no `Projects/{slug}/` (every project type, workflow included); a project folder without its hub note `{slug}.md` |
| Filenames | Not kebab-case; dated type without date suffix; date-first; spaces; reserved link characters; unrenamed `Pasted image …` attachments |
| Uniqueness | Same filename twice in the domain, `_inbox/` included (an inbox note whose name exists elsewhere is usually a consumed draft: fix row = archive it on proof, Leftovers; otherwise rename one). `README.md` is exempt (Part 2 §4) |
| Frontmatter parses | The block doesn't parse as YAML. The row names the key on the failing line and proposes the quoted value (Part 2 §5 → YAML style) |
| Sprint briefs | A `brief` whose `board-task` card is in sprint `{name}`: a real sprint, or an older `sprint/{name}` tag (resolved live, read-only, as bandit:tasks' `references/board.md` → Tags reads sprints) and sits outside `Projects/{slug}/sprint-{name}/`. Fix: move it there (Part 2 §1) |
| Sprint project root | A project with sprint folders holding anything at its root but the hub, `sprint-*` and `planning/`. Fix: move it into `planning/` (or its card's sprint folder) |
| Orphaned triaged notes | A filed `triaged` note whose `board-task` card no longer exists (resolved live, read-only). A question row for the user: keep, archive, or relink. Never acted on without their pick |
| Frontmatter | Missing required keys (`summary` once filed); legacy keys; unknown keys (fix row: map to the known key it means, recommended; removing it only if the user picks that); invalid enum value; `project` not a link; `request` missing `requester`/`received` |
| YAML style | Flow lists `[a, b]`; unquoted `[[links]]`; `#` in tags; keys out of order |
| Templates | Values that should be pre-filled are empty (§10); a missing standard template for an enabled module |
| Status vs place | `inbox` outside `_inbox`; `file-to` left on a reviewed note; `done` outside `_archive`; not `done` inside `_archive` (archived settings versions in `_archive/Claude/` are exempt: they have no status) |
| Links | Markdown path links (`[x](path/x.md)`) that a move will break; `[[links]]` to notes that don't exist |
| Orphans | A filed note with **no inbound link** from any other note, the README included (outbound links don't count). Fix: link it from its hub, a related note or the README's lists — or archive it |
| Customer data | Account-number patterns, customer names or addresses in any note body (report the line, propose a placeholder) |
| Ambiguous dates | `NN/NN/YYYY` in a body where both parts are ≤ 12 |
| Obsidian settings | Each row of the §11 table, read from `.obsidian/*.json`; property types per §5. Fix → `/bandit:notes settings` |
| Conflicts | Sync-conflict copies |
| Version | README `mynotes-version` older than the current convention version → suggest `onboard` |
| Plan notes (dev projects only) | Resolving each `board-task` id live, read-only: a `plan` note with neither `board-task` nor `sprint` (a sprint plan's `sprint` resolves through `get_sprints`) · a plan note whose card is complete, or whose sprint is `closed` (`get_sprints`), but the note isn't `done` (propose `done` + archive) · a plan note whose task id no longer resolves (card deleted). A renamed card still resolves: never report it as deleted |

Group the report by check, counts first. **Every breach is a numbered fix row** (file, breach,
fix), so the report is the proposal: the user answers all, a list or none. A breach whose fix belongs
to another command (`settings`, `archive`) is still a row, run through that command's procedure.
In project scope, lint only the project's own areas.

**On the app's Notes: the fields only.** The app holds folders, filenames and frontmatter for
itself, so lint reads the notes of the scope's boards (`notes_list`, then `archived: true`) and checks
each note's fields:

| Check | Breach |
|---|---|
| Scope | **The Inbox is skipped entirely**: the user's notes and helpers' drafts are not linted before review |
| Summary | A note out of the Inbox with none |
| Kind's fields | Minutes without `meeting` or `meetingDate`; a request without `requester` or `receivedOn` (conventions §5) |
| Status | `done` and not archived (fix: `archive`), except a plan linked to its card, which follows the card; `inbox` out of the Inbox |
| Card | A brief or plan with no card link and no `sprint-{name}` tag; a card link to a card that no longer resolves (read live, read-only) |
| Tags | A `sprint-{name}` tag whose sprint does not resolve through `get_sprints` |

Each row is fixed with `notes_set_fields`, `notes_set_status` or `notes_link_card`, as the row says.

---

### `/bandit:notes settings [Domain]`

Aligns the vault's Obsidian settings with Part 2 §11. Domain scope only. Never unattended. **Vault
only:** the app has no Obsidian settings.

1. Read the allowlisted files from `{Domain}/.obsidian/` (a missing file is "not set"). If one
   doesn't parse as JSON, report it and leave that file out of the proposal.
2. Build a proposal, one row per key that differs from §11:

   | # | File | Key | Now | New | Why |
   |---|---|---|---|---|---|
   | 1 | app.json | attachmentFolderPath | `"./"` | `"_attachments"` | §8 attachments folder |
   | 2 | core-plugins.json | sync | `true` | `false` | Needs the user's confirmation: no Obsidian Sync on this vault |

   Rows that need a fact from the user (Sync, Daily notes off vs. folder) say so in Why.
3. Ask for the approval **and** the closed-everywhere confirmation in the same message:
   "Approve all / a list / none — and confirm Obsidian is closed on every device."
4. On approval: per file, in order — backup → read (etag) → merge approved keys → validate →
   write (`if_match`) → re-read and verify. Report per row: done / skipped (with reason).
5. Finish with the after-run steps from §11 (wait for sync, open desktop first, check the UI).

**Roll back:** `/bandit:notes settings {Domain} restore` lists the backups in
`.obsidian/mynotes-backup/` newest first. The user picks one per file; with Obsidian closed
everywhere: back up the current live file first (so a restore can itself be undone), read its
etag, then `nc_webdav_copy_resource(source=backup, destination=live, overwrite: true,
if_destination_match: {bare-hex etag})` — the etag guard stops the copy if the file changed
since the read. Re-read and confirm it parses.

---

### `/bandit:notes delete {note…}`

1. Resolve each argument (a path, or a note's name) to an exact path (`nc_webdav_find_by_name`
   for a bare note name). Zero or several matches → ask; never pick one.
2. Propose one `delete` row per path. For a folder, list its contents in the row.
3. Say plainly that a delete may not be recoverable, and offer archive as the alternative for
   anything that isn't junk.
4. On approval: re-list, delete each approved path, report per row.

Other commands can also add `delete` rows to their proposals (empty inbox notes the user put up for
review, losing conflict copies, duplicates), but only when the user asked for cleanup, and each row
still needs their approval.

**On the app's Notes.**
1. Resolve each named note: `search` with its title, then `notes_list` of its place (and
   `archived: true`). The match is a note with exactly that title in the scope. Zero or several →
   ask; never pick one.
2. Propose one `delete` row per note, with its place and status.
3. Say that a deleted note goes to the Trash with its text, versions and links, can be brought back
   with `restore` for 30 days, and is then gone for good; offer `archive` for anything that isn't
   junk.
4. On approval: `notes_get` each approved note again (it is still there and still the one named),
   then `notes_delete`; report per row with the days the Trash keeps it.

---

### `/bandit:notes archive [Domain]` · `/bandit:notes restore {note}`

**Archive**
1. Find notes with `status: done` outside `_archive/` (read frontmatter folder by folder).
2. Propose each move to `_archive/{original path}`, plus any mirror folders to create.
3. On approval: stamp `archived-from` + `archived` (edit in place) → create missing mirror
   folders → move.

**A sprint folder** (Part 2 §1 → Archiving a sprint), named by the user or by bandit-dev:sprint's close:
one row per note setting `status: done` on the plan, execution prompt, ledger and report, one row
stamping every note in the folder, the mirror folders under `_archive/Projects/{slug}/` as rows,
then one move row for the folder itself. Stamp all, then move once; a failed stamp stops the move.

**Settings versions** (structure rulebook S7)

Old `{prefix}-instructions-v{N}.md` and `{prefix}-prompt-reference-v{N}.md` files leave
`Claude/ai-{slug}/` for `_archive/Claude/ai-{slug}/`. bandit:project owns the files but never
moves them; this skill does the move.

1. **Input:** the exact file paths, from an approved bandit:audit S7 row or named by the user. This
   skill doesn't decide which version is in production: that comes from the self-check stamp,
   which bandit:audit reads. No list given → ask for one; never pick "everything but the highest".
2. **Refuse** a path that isn't a settings file in `Claude/ai-{slug}/`, and any file of a project
   whose S5 is unchecked.
3. **Propose** one row per file, plus any missing `_archive/Claude/ai-{slug}/` mirror folder as
   its own row.
4. **On approval:** create missing mirror folders → move with `overwrite: false`. **No stamp:**
   settings files carry an HTML metadata comment, never frontmatter, so nothing is edited. The
   mirrored path is the only record of where a file came from.
5. **Report** per row. Run from a product project, this is outside its scope: it runs from the
   workflow project or as a bandit:audit row.

**Restore**
1. Locate the note in `_archive/` with `nc_webdav_find_by_name`.
2. Target = `archived-from`; if absent, the mirrored path. A settings version has no stamp: its
   target is always the mirrored path, and it is moved back without any edit.
3. Propose: move back, set `status: active`, remove `archived-from` and `archived`. Along with
   `file-to` at filing, these are the only keys this skill removes — they're its own stamps.

**On the app's Notes.** No folder moves and no stamps: the app keeps the note in its place and the
status says it is archived (`references/storage-app.md` → Archive, restore, delete).

- **Archive:** find the scope's notes with status `done` (`notes_list`). Propose one row per note
  setting `archived`. On approval, `notes_set_status` → `archived`, read back. A plan linked to its
  card follows the card and is not archived by hand (`PLAN_FOLLOWS_CARD`): it gets no row. Settings
  versions stay a vault procedure. A sprint on the app's Notes has no folder: its records are
  archived by bandit-dev:sprint's close, not by a sprint row here.
- **Restore:** find the named note in the place's archived notes (`notes_list` with
  `archived: true`), then in the Trash (`notes_list_trash`). Exactly one match by title, or ask.
  From the archive: propose `triaged`, or the status the user names, since the app does not keep the
  one it had; on approval `notes_set_status`. From the Trash: propose bringing it back as it was,
  with the days left; on approval `notes_restore`. Read the note back with `notes_get` and report
  its status and place.

---
