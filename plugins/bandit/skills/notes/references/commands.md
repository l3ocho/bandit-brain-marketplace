# Part 3 — Commands

Every procedure starts by resolving the domain (Part 1, SKILL.md) and reading Part 2
(`references/conventions.md`).

**Proposal format** used by every command that writes on confirmation:

```
| # | Action | From | To | Why |
|---|---|---|---|---|
| 1 | move | _inbox/Untitled 3.md | Requests/billing-dispute-report-2026-09-23.md | request from CS Director |
| 2 | frontmatter | Meetings/x.md | — | add type, status, domain |
| 3 | delete | _inbox/Untitled 7.md | — | empty capture, Leo asked to remove |
```

Leo answers "all", a list ("1, 3"), or "none". Execute only the approved rows, in order, and
report per row: done / refused (with reason). A refused row doesn't undo the others.

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
Say so and tell Leo to run bandit:project (targeted update) to set the Project Context
`domain:` and `project:` and the derived `webdav_folder`. Don't edit instructions from here.

**Stage B — Templates.** Read every file in `_templates/`. Propose the frontmatter
standardisation (pre-fill and legacy key map in Part 2 §10). Show each template's before/after
frontmatter; the body stays untouched. Also propose **creating any missing standard template**
(Part 2 §10: `new-note.md` always, a meeting template when `meetings` is on, `request.md` when
`requests` is on).

**Stage C — Notes.** Walk every content folder. **Skip `_inbox/` entirely** — it's Leo's; review
happens through `file`. For each
`.md`: missing or legacy frontmatter keys (a missing `summary` gets a drafted sentence in the
row, for Leo to approve or edit; a note moved in from another system gets `source: migrated`), YAML
style and key order (Part 2 §5), customer data in the
body, wrong `status` for its location, filename breaches
(including date-first names like `2026-09-23-csnotes-feature-x.md` → date-last). Renames outside
`_inbox` need a backlink search (read the domain's `.md` files for `[[old-name` and include those
link edits as rows). If Stage C would exceed ~40 rows, propose it folder by folder.

**Stage D — Home and settings.** Run `home`. Record `mynotes-version: 2` and the modules in the
README frontmatter. Then run the `settings` check and offer its proposal (applied only once Leo
confirms Obsidian is closed everywhere); if he'd rather change them in the app, give him the
table instead.

**Upgrading a v1 domain** is `onboard` again: Stage A adds `_attachments/` and hub notes, Stage B
pre-fills templates, Stage C adds `summary`, converts `project` to a link and fixes YAML style,
Stage D bumps the version.

**Project scope** runs a smaller onboard instead of Stages A–D: check that `Projects/{slug}/`,
its hub note `{slug}.md` and `Claude/ai-{slug}/` exist (propose creating whichever is missing),
then run Stage C on
`Projects/{slug}/` only. Domain-level findings (legacy folder names, other projects) come as
fix rows marked `domain`, built with Stage B/C, after this project's rows. They run only when Leo
approves them by number (Part 1 → scope exceptions).

---

### Onboarding rows (run by bandit:project)

The vault step of project onboarding. bandit:project passes `domain`, `project` (slug), `type`,
`dev` (when set), whether the project has a Claude Code surface (item 8 decides on these two),
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
   auto-write, Part 1).

---

### `/bandit:notes init {Domain}`

For a new domain — a new job, a new business area.

1. Check `MyNotes/{Domain}` doesn't exist. If it does, stop and offer `onboard` instead. Typed
   in a project chat to set up a new project: say that's bandit:project' onboarding and stop.
2. Ask which modules to enable (multi-select from the Part 2 §2 list).
3. Propose: the domain folder, core folders, module folders, pre-filled starter
   `_templates/new-note.md` (and `meeting-entry.md` / `request.md` when those modules are on),
   and the README.
4. On confirmation, create them in that order, then run `home`.
5. Obsidian creates `.obsidian/` the first time Leo opens the folder as a vault. Tell him to do
   that, close it again, and then run `/bandit:notes settings {Domain}` to apply Part 2 §11.

---

### `/bandit:notes home [Domain]`

Rebuilds `{Domain}/README.md` from the **README template** in `references/readme-template.md`. Runs unattended from a
scheduled task, so it **never asks** and writes only the README.

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
3. Write it: read → strip the etag to bare hex → `if_match`. A 412 means Leo edited it in the
   meantime: re-read once, re-merge the `## Notes` section, write again. A second 412 → stop
   and report.
4. **Links:** Obsidian can't link to a folder, so folders are shown as `` `path/` `` and notes as
   `[[note-name]]`. Never link across domains. Every note the README lists carries its
   `summary` beside the link; a note with no `summary` shows `—` and counts under Needs attention.

When run by a schedule, the only output that matters is the file. Finish with one line: what
changed (counts), or "no changes".

---

### `/bandit:notes file [Domain] [note…]`

The review: takes inbox notes Leo puts up and moves them to their homes, compliant. With note
names, reviews only those; without, the whole inbox. This is the command Leo uses most — keep
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
     (shown in the row so Leo can edit it), `project: "[[{slug}]]"` when it's about a project,
     a picked body value copied into its key (Part 2 §10), YAML style and key order per
     Part 2 §5
   - attachments: embedded files not yet in `_attachments/` move there; pasted-image names get
     renamed per Part 2 §4 with the embed updated in the same row
   - **body:** untouched by default. Anything worth changing (a duplicated block, an ambiguous
     date like `09/10/2026`, customer data, broken structure) becomes a **separate body row**
     showing before → after, which Leo approves or skips on its own
   - **open questions** (which project, which meeting type, what a date means): ask them now,
     all at once, before the proposal is final
   - If a note is too thin to classify, leave it in `_inbox` untouched and say why in one line
   - **Consumed draft.** When the note filed is a rewrite, a brief or a WBS made from another inbox
     note (named in its `related`, or its body's first line), add a separate **archive row** for
     that source note (Part 2 §7 stamps, `status: done`, to `_archive/_inbox/`). Proof first: the
     filed copy exists at its destination and was read in this run. No proof, or the source isn't
     named → no row; the source stays (SKILL.md → *Other skills* → Leftovers). A source with the
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

---

### `/bandit:notes lint [Domain]`

Read-only report whose rows are the fixes. Nothing is written until Leo answers.

Checks (each row: file, breach, proposed fix):

| Check | Breach |
|---|---|
| Scope | **`_inbox/` is skipped entirely** — only its count and its filenames are read (for Uniqueness). Leo's notes aren't linted before review |
| Location | A folder that's neither core nor an enabled module; non-settings content in `Claude/`; a skill folder inside a domain; a non-markdown file outside `_attachments/` (except `.canvas`/`.base`, §8) |
| Claude subfolders | Name not `{ai\|code\|design}-{slug}` |
| Project pairing | A settings folder whose slug has no `Projects/{slug}/` (every project type, workflow included); a project folder without its hub note `{slug}.md` |
| Filenames | Not kebab-case; dated type without date suffix; date-first; spaces; reserved link characters; unrenamed `Pasted image …` attachments |
| Uniqueness | Same filename twice in the domain, `_inbox/` included (an inbox note whose name exists elsewhere is usually a consumed draft: fix row = archive it on proof, Leftovers; otherwise rename one). `README.md` is exempt (Part 2 §4) |
| Frontmatter parses | The block doesn't parse as YAML. The row names the key on the failing line and proposes the quoted value (Part 2 §5 → YAML style) |
| Sprint briefs | A `brief` whose `board-task` card carries a `sprint/{name}` tag (resolved live, read-only) and sits outside `Projects/{slug}/sprint-{name}/`. Fix: move it there (Part 2 §1) |
| Sprint project root | A project with sprint folders holding anything at its root but the hub, `sprint-*` and `planning/`. Fix: move it into `planning/` (or its card's sprint folder) |
| Orphaned triaged notes | A filed `triaged` note whose `board-task` card no longer exists (resolved live, read-only). A question row for Leo: keep, archive, or relink. Never acted on without his pick |
| Frontmatter | Missing required keys (`summary` once filed); legacy keys; unknown keys (fix row: map to the known key it means, recommended; removing it only if Leo picks that); invalid enum value; `project` not a link; `request` missing `requester`/`received` |
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
| Plan notes (dev projects only) | Resolving each `board-task` id live, read-only: a `plan` note with no `board-task` · a plan note whose card is complete but the note isn't `done` (propose `done` + archive) · a plan note whose task id no longer resolves (card deleted). A renamed card still resolves: never report it as deleted |

Group the report by check, counts first. **Every breach is a numbered fix row** (file, breach,
fix), so the report is the proposal: Leo answers all, a list or none. A breach whose fix belongs
to another command (`settings`, `archive`) is still a row, run through that command's procedure.
In project scope, lint only the project's own areas.

---

### `/bandit:notes settings [Domain]`

Aligns the vault's Obsidian settings with Part 2 §11. Domain scope only. Never unattended.

1. Read the allowlisted files from `{Domain}/.obsidian/` (a missing file is "not set"). If one
   doesn't parse as JSON, report it and leave that file out of the proposal.
2. Build a proposal, one row per key that differs from §11:

   | # | File | Key | Now | New | Why |
   |---|---|---|---|---|---|
   | 1 | app.json | attachmentFolderPath | `"./"` | `"_attachments"` | §8 attachments folder |
   | 2 | core-plugins.json | sync | `true` | `false` | Needs Leo's confirmation: no Obsidian Sync on this vault |

   Rows that need a fact from Leo (Sync, Daily notes off vs. folder) say so in Why.
3. Ask for the approval **and** the closed-everywhere confirmation in the same message:
   "Approve all / a list / none — and confirm Obsidian is closed on every device."
4. On approval: per file, in order — backup → read (etag) → merge approved keys → validate →
   write (`if_match`) → re-read and verify. Report per row: done / skipped (with reason).
5. Finish with the after-run steps from §11 (wait for sync, open desktop first, check the UI).

**Roll back:** `/bandit:notes settings {Domain} restore` lists the backups in
`.obsidian/mynotes-backup/` newest first. Leo picks one per file; with Obsidian closed
everywhere: back up the current live file first (so a restore can itself be undone), read its
etag, then `nc_webdav_copy_resource(source=backup, destination=live, overwrite: true,
if_destination_match: {bare-hex etag})` — the etag guard stops the copy if the file changed
since the read. Re-read and confirm it parses.

---

### `/bandit:notes delete {path…}`

1. Resolve each argument to an exact path (`nc_webdav_find_by_name` for a bare note name). Zero
   or several matches → ask; never pick one.
2. Propose one `delete` row per path. For a folder, list its contents in the row.
3. Say plainly that a delete may not be recoverable, and offer archive as the alternative for
   anything that isn't junk.
4. On approval: re-list, delete each approved path, report per row.

Other commands can also add `delete` rows to their proposals (empty inbox notes Leo put up for
review, losing conflict copies, duplicates), but only when Leo asked for cleanup, and each row
still needs his approval.

---

### `/bandit:notes archive [Domain]` · `/bandit:notes restore {note}`

**Archive**
1. Find notes with `status: done` outside `_archive/` (read frontmatter folder by folder).
2. Propose each move to `_archive/{original path}`, plus any mirror folders to create.
3. On approval: stamp `archived-from` + `archived` (edit in place) → create missing mirror
   folders → move.

**A sprint folder** (Part 2 §1 → Archiving a sprint), named by Leo or by bandit-dev:sprint's close:
one row per note setting `status: done` on the plan, execution prompt, ledger and report, one row
stamping every note in the folder, the mirror folders under `_archive/Projects/{slug}/` as rows,
then one move row for the folder itself. Stamp all, then move once; a failed stamp stops the move.

**Settings versions** (structure rulebook S7)

Old `{prefix}-instructions-v{N}.md` and `{prefix}-prompt-reference-v{N}.md` files leave
`Claude/ai-{slug}/` for `_archive/Claude/ai-{slug}/`. bandit:project owns the files but never
moves them; this skill does the move.

1. **Input:** the exact file paths, from an approved bandit:audit S7 row or named by Leo. This
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

---
