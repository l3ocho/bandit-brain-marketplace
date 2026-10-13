---
name: "bandit-notes"
description: "Owns the MyNotes vault conventions in BanditCloud (Obsidian over WebDAV): folders, filenames, frontmatter, status, archiving, and each domain's README home page. Invoked as /bandit-notes followed by a command (onboard, init, home, file, lint, settings, archive, restore, delete). Also runs the vault step of project onboarding for project-settings. Also use for reviewing and filing inbox notes (\"file my inbox\"), moving or archiving notes, scaffolding a domain, applying Obsidian vault settings, or before any skill writes a note into MyNotes. Do NOT use for the Nextcloud Notes app, for MyNotes/_skills (the Skill Manager project owns it), or for tasks on the board (bandit-tasks)."
---

# 🗂️ Bandit Notes

This skill is **the single definition of the vault conventions**. If a convention needs to
change, change this skill — never patch around it in a chat, a project instruction or another
skill. A folder outside the scope defined here simply doesn't use this skill.

This file is Part 1, the overview. The rest lives in `references/`, and the rules in them are
the product:

| File | Read it |
|---|---|
| `references/conventions.md` — **Part 2 · Conventions** | Before **any** write into the vault |
| `references/commands.md` — **Part 3 · Commands** | Before running a command: follow its procedure |
| `references/readme-template.md` — **README template** | When running `home` or `init` |

"Part 2 §N" anywhere means that section of `references/conventions.md`.

---

## 🧭 Model in one screen

```
MyNotes/                         ← BanditCloud root of all domains
├── _skills/                     ← root "_" folder: NOT a domain, ignored by every scan
├── .templates/                  ← any dot folder: ignored
└── {Domain}/                    ← one domain = one Obsidian vault (has its own .obsidian/)
    ├── README.md                ← generated home page; frontmatter = domain config
    ├── _inbox/                  ← Leo's working space: no rules, no edits until he asks for review
    ├── _templates/              ← input structures
    ├── _archive/                ← done notes and old settings versions, original path mirrored
    ├── _attachments/            ← every image, PDF, audio file embedded by a note
    ├── Claude/                  ← SETTINGS ONLY (instructions + reference doc; no logs/notes/journals): {ai|code|design}-{slug}/
    ├── Projects/{slug}/         ← hub note {slug}.md; the rest of the layout belongs to the project
    ├── Meetings/                ← module
    └── Requests/                ← module
```

- **Domain** = a top-level folder of `MyNotes` whose name doesn't start with `_` or `.`.
- **`_` at root** means "not a domain". **`_` inside a domain** means "system folder this skill
  knows by name". Same prefix, different level — never confuse the two.
- **Each domain is its own Obsidian vault.** Wikilinks resolve inside the domain only, so never
  link across domains with `[[…]]`.

---

## 📍 Resolve the domain before anything else

1. **Project Context first.** Read the `## 🧭 Project Context` section: in the Claude.ai
   project instructions, or in the repo's `CLAUDE.md` on Claude Code. `domain:` names the
   domain and `project:` the project slug. The block's format is owned by project-settings.
   - `domain: none` → this project has no vault. Say so and stop.
   - **Legacy fallback:** no Project Context section → read `vault_domain` and `vault_project`
     from the `<!-- project-settings: {...} -->` metadata instead.
2. **Run by project-settings (onboarding).** The project's instructions aren't pasted yet, so take
   `domain`, `project` and `type` from project-settings instead. See *Onboarding* below.
3. **Explicit argument.** `/bandit-notes home Summitt` — the scheduled home refresh always passes it.
4. **Otherwise ask**, listing the live domains from `nc_webdav_list_directory("MyNotes")`.

Never guess the nearest match. If the named domain isn't in the listing, stop and say so.

---

## 🎯 Scope — what this project may see and change

**One project, one slug.** `project:` is the project's own name as a slug (`cs-notes`), not
the Claude.ai project's display name. The same slug names every folder of that project:

```
Projects/cs-notes/        ← the shared docs: one source, one set of rules, for both surfaces
Claude/ai-cs-notes/       ← Claude.ai settings (higher-level implementation discussion)
Claude/code-cs-notes/     ← Claude Code settings: the repo mirror (CLAUDE.md + claude/)
```

The Claude Code side reaches `Projects/{slug}/` through the same `## 🧭 Project Context` section,
placed in the repo's `CLAUDE.md`: with it, `/bandit-notes` gets the same project scope in Claude Code
as in Claude.ai. That file is configured in the repo, not by this skill.

**Scope comes from the Project Context `type:`** (legacy fallback: `project_type` in the
metadata), resolved together with the domain:

| Situation | Scope |
|---|---|
| `type: workflow` (e.g. Summitt Workflow) | **Domain**: the whole domain. Oversees every project, and like every project has its own `Claude/ai-{slug}/` and `Projects/{slug}/` with its hub note |
| `type: product_service` or `type: claude_marketplace`, with `project:` | **Project**: the table below |
| No Project Context and no project metadata (e.g. the scheduled `/bandit-notes home Summitt`) | **Domain** |

**Project scope:**

| Area | Read | Change (on approval) |
|---|---|---|
| `_inbox/` | All of it (Leo's inputs) | Create new notes; review (`file`) notes **only** into `Projects/{slug}/`, and only the ones Leo puts up for review |
| `Projects/{slug}/` | ✓ | ✓ |
| `Claude/ai-{slug}/`, `Claude/code-{slug}/` | ✓ | Create the folder only; the twin belongs to project-settings, the mirror to the repo's Stop hook |
| `_templates/` | ✓ | ✓ Edit templates directly, no need to switch to the workflow project |
| `_archive/Projects/{slug}/` | ✓ | Archive and restore its own notes |
| `Meetings/`, `Requests/` | Only notes with `project: "[[{slug}]]"` | ✗ read-only |
| Missing core structure of the domain | ✓ | **Onboarding only:** create the missing core folders, `_templates/new-note.md` and the README, as approved rows |
| Everything else | ✗ | ✗ |

Anything outside the scope (another project's folder, a domain-level rename, `init`, `home`,
`settings`) that Leo asks for: stop and say it's a domain-level action to run from the workflow
project. Never widen scope on your own. Two exceptions: onboarding's approved rows may create the
domain's missing core structure (and `home` then builds the README), and a **`domain` fix row**
(below) runs when Leo approves that row by number. His yes is the widening, for that row only.

---

## 📥 The inbox is Leo's

`_inbox/` is where Leo writes, pastes and thinks. **While a note is in `_inbox/`, no convention
applies to it** — any filename, any frontmatter or none, any structure, any date format. And **no
skill or chat edits, renames, reformats or moves a note there** unless Leo puts that note up for
review in the current conversation. Not `lint`, not `onboard`, not another skill tidying up, not
a chat that is using the note as input. Reading is always fine. Leo's yes to a row that archives
or deletes a consumed draft by name (*Other skills* → Leftovers) is putting that note up.

**Exception: a skill-written draft, changed on Leo's request.** A note in `_inbox/` with
`status: triaged` that was written by a skill **in the current conversation** may be edited in
place when Leo explicitly asks for that change. Conditions: etag-guarded write, `updated` bumped,
`status` and `file-to` unchanged, and the change summarised back to him. Leo's own notes (`inbox`
or no status) stay untouchable, and so does any skill-written note from an earlier conversation.

**The rules apply at review.** Review is `/bandit-notes file`: Leo runs it (for the whole inbox or for
named notes) when he wants a note processed. That is the only moment the conventions touch it,
and the note leaves the inbox in the same step. The status says which side of that line a note
is on:

| Status | Whose | Rules |
|---|---|---|
| `inbox` (or no status at all) | Leo's, in progress | None. Untouchable |
| `triaged` + `file-to`, in `_inbox/` | Written by a skill, waiting for Leo's review | The skill wrote it compliant; not edited again until review, except on Leo's explicit request in the conversation that wrote it (the exception above) |
| anything, outside `_inbox/` | Reviewed | All of Part 2 |

**Review is all or nothing per note.** Every question a note needs answered (which project,
which meeting type, what an ambiguous date means) is asked before its row is final. A row with
an open question is not executed, and **a note is never left half-edited in the inbox**: it is
either still exactly as Leo left it, or reviewed and in its home folder.

**Leo's words stay Leo's.** At review, the frontmatter is the skill's job. The body is not: any
body change (removing a duplicated block, rewriting a date, fixing structure) is its own row
showing before → after, and happens only if Leo approves that row.

---

## 🛡️ Write safety — the rules that protect Leo's files

**Leo confirms every move, rename, archive, delete, folder creation and edit of an existing note.**
Present a numbered proposal, let him approve all, some ("1, 3, 5") or none, and execute exactly
what was approved. There are only two exceptions, both because they can't destroy anything:

| Auto-write (no confirmation) | Why it's safe |
|---|---|
| Creating a **new** note in `{Domain}/_inbox/` | It's the drop zone; fail-closed create can't clobber |
| Regenerating `{Domain}/README.md` | Generated file; its config frontmatter and `## Notes` section are carried over |

**Approval covers the approved rows and nothing else.** Never create, edit, move or delete
anything that isn't in an approved row: not a core folder the conventions say should exist, not a
fix spotted along the way, and never anything in another project's folder. A short "yes" or
"create it" approves the rows on the table, nothing else.

**Findings come fixed.** Every problem found (a breach, a legacy folder, a stray file, a broken
link) comes back as a numbered **fix row in the same proposal**, with the exact action and target
and the recommended fix. Nothing is ever just listed. A finding outside this project's scope is
still a row, marked `domain`. A finding with two valid fixes is one row with both, recommended
first. One "all" fixes everything; only approved rows run.

**Say plainly that nothing happens until he answers.** End every proposal with one line: *Nothing
is created or changed until you answer all, a list, or none.*

WebDAV mechanics (verified against the BanditCloud MCP):

- **New file:** `nc_webdav_write_file` with `if_match` omitted. It fails if the path exists —
  that failure is the protection. Never retry with `if_match: "*"`.
- **Edit existing:** read → take the etag → **strip `W/` and every `"`** → write with that
  bare-hex `if_match`. The raw read etag is rejected as a false concurrent edit.
- **Move / rename:** `nc_webdav_move_resource` with `overwrite: false`. A 412 means the
  destination exists — stop and report, don't overwrite. A 409 means the parent folder is
  missing — it was not in the approved plan, so ask.
- **Archiving: edit, then move.** Stamp the frontmatter in place, then move. If the move fails,
  the note is still whole where it was. Settings files have no frontmatter: they are moved only,
  never stamped (Part 3 → *Settings versions*).
- **Filing (review): move, then edit.** Move the inbox note to its new path and name first, then
  edit it there. If the move fails, the inbox note is untouched; if the edit fails, the note sits
  in its home folder unedited and the row is reported as half-done — never the other way round.
- **Delete only on Leo's word.** `nc_webdav_delete_resource` runs only when Leo explicitly asked
  to delete that item, or approved a `delete` row naming its exact path. Rules:
  - One row per path, never a wildcard. A folder row lists what's inside it, so he sees what goes.
  - Ambiguous wording ("get rid of it", "clean this up") isn't a delete: offer **archive** or
    **delete** and let him pick.
  - Never in `home` or any scheduled/unattended run: there's nobody to approve.
  - Re-list right before deleting; if the path changed or vanished since the proposal, skip the
    row and say so.
  - Nextcloud usually keeps deleted files in its trash bin, but that's a server setting this skill
    can't check, so treat a delete as permanent when asking.
- **Excluded-tag errors** are deliberate exclusions. Report them; never work around them.
- **Never edit non-markdown files** (images, PDFs, audio, `.canvas`, `.excalidraw`). Move them
  only as part of an approved proposal.
- **`.obsidian/` is written only by `/bandit-notes settings`**, only the allowlisted files and keys
  in Part 2 §11, only on approval, only with Obsidian closed on every device, and always with a
  backup first. Every other command treats `.obsidian/` as read-only.

**Obsidian doesn't see WebDAV moves.** Its wikilinks survive because they resolve by filename —
which is why **filenames must be unique** (Part 2 §4) and the vault's link format must be
"Shortest path when possible" (Part 2 §11). A rename, unlike a move, breaks `[[old-name]]`
links: before renaming a note outside `_inbox`, find the notes linking to it and include their
link updates in the same proposal. An `aliases` entry for the old name does **not** fix this —
Obsidian never resolves a bare `[[alias]]` to a note.

---

## ⌨️ Commands

| Command | Does | Writes |
|---|---|---|
| `/bandit-notes onboard [Domain]` | Audits an existing domain against the conventions and proposes the migration | On confirm |
| `/bandit-notes init {Domain}` | Scaffolds a new domain: core folders, chosen modules, starter README | On confirm |
| `/bandit-notes home [Domain]` | Rebuilds the domain README home page | Auto |
| `/bandit-notes file [Domain] [note…]` | Reviews inbox notes Leo puts up: destination, filename, frontmatter; body changes only as separate rows | On confirm |
| `/bandit-notes lint [Domain]` | Reports every convention breach, each with its fix row | Fixes on confirm |
| `/bandit-notes settings [Domain]` | Checks the vault's Obsidian settings against Part 2 §11 and proposes the changes; can roll back from backup | On confirm, Obsidian closed |
| `/bandit-notes archive [Domain]` | Proposes moving `status: done` notes into `_archive`, and old settings versions named by a structure audit (S7) | On confirm |
| `/bandit-notes restore {note}` | Moves an archived note back to its `archived-from` path | On confirm |
| `/bandit-notes delete {path…}` | Deletes the named notes, files or folders | On confirm |

**Invocation:** `/bandit-notes <command> [args]` — the slash command is the guaranteed trigger, so it's
the documented form everywhere, including scheduled tasks. The first word after `/bandit-notes` is the
command; the rest are its arguments. `/bandit-notes` with no command → offer the command table as a
numbered list and ask which one. Plain language ("file my inbox") also reaches this skill, but
it depends on description matching, so never rely on it for scheduled or unattended runs.

Commands respect the scope above: `init`, `home` and `settings` are domain-only; the others run
on the project's own areas when the scope is Project. Procedures are in Part 3
(`references/commands.md`).

---

## 🚀 Onboarding — the vault step, run by project-settings

**Onboarding a project is one command, owned by project-settings.** It interviews Leo, then loads
this skill for the vault rows and bandit-tasks for the board rows, and shows **one** proposal.
This skill only produces the vault rows and executes the approved ones; it never shows its own
proposal or asks for its own approval when project-settings runs it. Procedure: *Onboarding rows*
in Part 3.

| Situation | Vault rows |
|---|---|
| The domain doesn't exist yet | `init` rows: the domain folder, core folders, chosen modules, starter templates |
| The domain exists | **Every missing core item** (`_inbox/`, `_templates/` + `new-note.md`, `_archive/`, `_attachments/`, `Claude/`, `Projects/`, `README.md`), plus this project's `Claude/ai-{slug}/` and `Projects/{slug}/` with its hub note `{slug}.md`, **for every project type, workflow included**; plus `Claude/code-{slug}/` for a `dev: true` project (dev mirror), or a project without `dev: true` that runs in Claude Code (Claude Code twin) |

The core rows only **create** missing standard folders and starter files. Anything that would
move, rename, edit or delete existing content (legacy layout, settings folders in the wrong place,
stray files) is still fixed in the same proposal: it comes back as a **fix row** marked `domain`,
built with the `onboard` Stage B/C procedure (Part 3), after the create rows.

---

## 🤝 Other skills and chats writing into MyNotes

Any note created by another skill or in a chat follows the same rules: it's created in
`{Domain}/_inbox/` as a **new** file, carries the standard frontmatter (including `summary`) with
`status: triaged`, follows the body shape in Part 2 §12, and may set `file-to:` so `/bandit-notes file`
(or the writing skill itself, after Leo confirms) can move it to its home in one step. Skills
create new notes in the inbox; they never edit an existing one there, except their own draft
from this conversation on Leo's explicit request (see *The inbox is Leo's*).

- **project-settings** owns the files inside `Claude/ai-{slug}/`. Those files start with an
  HTML metadata comment on line 1, so they are **exempt from frontmatter**; never add YAML to
  them. The folder path is derived from the Project Context: `MyNotes/{domain}/Claude/ai-{project}`.
  project-settings also owns the **Claude Code twin** in `Claude/code-{slug}/`: its `CLAUDE.md`,
  `claude/settings.json` and `claude/hooks/workdir.py`, for any project without `dev: true`.
- **The working-folder manifest** (`Projects/{slug}/workdir-manifest.json`, structure rule S12) is
  written straight there by the twin's Claude Code session, asked by its `SessionStart` hook. Machine
  data for bandit-audit, not a note: no inbox, no frontmatter, create fail-closed, edit with the etag.
- **The dev mirror** is copied straight into `Claude/code-{slug}/` by the repo's `Stop` hook script,
  through the Nextcloud-synced folder (project-settings `references/dev-mirror.md`). It's a settings
  copy, not a note: no inbox, no frontmatter, never edited by hand.
- **meeting-minutes** writes minutes to `_inbox` with `file-to: Meetings/`.
- **Sprint records** on dev projects (plan, execution prompt, ledger, report and the sprint's
  briefs) are written **straight into `Projects/{slug}/sprint-{name}/`** for the same reason as the
  planning documents below (Part 2 §1 → Sprint folders).
- **project-planner** and **wbs-generator** are the other exception to the inbox rule: they write
  a project's planning documents (`{slug}-project-plan.md`, `{slug}-architecture.md`,
  `{slug}-wbs.md`) **straight into `Projects/{slug}/`**, or `Projects/{slug}/planning/` on a project
  with sprint folders (Part 2 §1 → Sprint project root), because they're worked on across many
  sessions. They ask this skill for the folder, still follow Part 2 (frontmatter, `status`, YAML
  style), create fail-closed and edit only with the etag. Drafts never go to `_inbox/`.
- **Leftovers.** A note used only to produce another (an inbox draft filed elsewhere, a superseded
  draft, an applied feedback note) is archived with the usual stamps (Part 2 §7), or deleted on
  Leo's word, **in the same step that consumed it**, and only on proof: the successor exists and was
  read. Never because a note looks done or its card is missing; unsure → it stays.
- **bandit-tasks** owns the task vocabulary. Frontmatter reuses it verbatim (`kind`, `handler`,
  `lane` as the bare value) and links tasks via `board-task`. This skill never writes to the board.
- **Dev projects** (`dev: true` in the Project Context): plan notes and the WBS card links exist
  **only** there (Part 2 §13). Without the flag nothing changes. Plan notes go **inbox-first**, like
  every skill-written note, except sprint records, which are written straight into the sprint
  folder. Because `type: plan` exists only on dev projects, `file` and `lint`
  apply the plan-note rules to any `type: plan` note, whichever project they run from (usually the
  domain workflow project).
- **Lookup for bandit-tasks.** bandit-tasks asks whether a plan-note **filename** is filed; this
  skill answers with `nc_webdav_find_by_name(pattern="{filename}", scope="MyNotes/{Domain}")` and
  checks the match sits in `Projects/{slug}/`, its `planning/` or one of its sprint folders. Vault paths stay here; bandit-tasks never restates them.

---

## ⚠️ Gotchas

- **2026-09-24 · "create it" ran past the proposal.** Leo said "create it" to a 5-row proposal and
  the chat also created `_inbox/`, `_templates/`, `_archive/` and `_attachments/`, which were only
  listed as findings. → Execute only the approved rows. Every finding is a row of its own.
- **2026-09-24 · Onboarding left the domain half-built.** Onboarding the Personal workflow project
  created `Claude/ai-personal/` but not the missing `_templates/`, `_archive/`, `_attachments/` or
  README, because they were only listed as findings. → Missing core structure is always a row in
  onboarding (create only).
- **2026-09-29 · Findings were flagged and never fixed.** Onboarding and lint listed legacy
  folders, stray files and breaches as "findings" or "for the workflow project", and nothing
  fixed them without another run. → Findings come fixed: every one is a numbered fix row in the
  same proposal (`domain` when outside the scope), approved with the rest.
- **2026-09-24 · A waiting proposal looked like a failure.** Leo ran the command, got a proposal,
  and saw nothing created. → End every proposal with the "nothing happens until you answer" line.
- **2026-09-24 · Project onboarding was split across three skills.** `init` run from a project
  chat was silently swapped for a project onboard. → Onboarding runs from project-settings, which
  runs this skill's *Onboarding rows*. Typed directly in a project chat, `init` or `onboard` says
  which command applies and why, and points to project-settings for a new project.
- **2026-09-24 · A `domain: none` stop gave no fix.** → Name the setting and the fix: a
  project-settings targeted update in that project sets `domain:`. This skill never edits
  project instructions.
- **2026-09-25 · Leo asked to amend a draft a skill had just written.** The rules had no path for
  this, and the edit went ahead on his explicit ask. → A triaged, skill-written draft from this
  conversation can be edited on Leo's explicit request (*The inbox is Leo's*).
- **2026-09-25 · Workflow projects had no project folder.** The old rule gave `type: workflow`
  settings only, so a workflow project had nowhere to keep its own docs. → Every project, workflow
  included, gets both `Claude/ai-{slug}/` and `Projects/{slug}/` with its hub note.
- **2026-09-30 · Content migrated from a repo had no `source:` value to take.** → `migrated`, with
  the original location in the body's first line (conventions §5).
- **2026-10-07 · A colon in a `summary` broke a note.** Obsidian opened it with invalid
  properties. → Quote any value that YAML would misread (conventions §5 → YAML style).
- **2026-10-08 · Two notes were archived on a guess.** They looked done. → Archive a consumed note
  only on proof that its successor exists and was read (*Other skills* → Leftovers).

---

## 🚫 Never

- Treat a root `_` folder (`_skills`) or any dot folder as a domain, or scan inside it (the one
  exception: `.obsidian/` settings files, read by `lint` and `settings`, Part 2 §11)
- Put anything but settings under `Claude/` — no project logs, working notes, decision journals, discussion records, reports or drafts (those go to `Projects/{slug}/`) — or a general skill anywhere under a domain
- Invent a module, status value or frontmatter key that isn't in Part 2
  — propose a change to this skill instead
- Impose a layout inside `Projects/{slug}/` beyond its hub note `{slug}.md` and, on a project with
  sprint folders, the root rule (Part 2 §1) — the project's own settings decide the rest
- Write to `.obsidian/` outside `/bandit-notes settings`, touch a file or key not on its allowlist,
  write it while Obsidian may be open, or write it without a backup
- Edit, rename, reformat or move a note in `_inbox/` that Leo didn't put up for review in this
  conversation, or leave a reviewed note half-edited in the inbox (sole exception: a skill's own
  `triaged` draft from this conversation, edited on his explicit request — *The inbox is Leo's*)
- Change a note's body at review without a row Leo approved for that change
- Create, edit, move or delete anything outside the rows Leo approved — no bonus folders or
  fixes, and nothing in another project's folder
- Put a date-only or title-case filename anywhere outside `_inbox`
- Write customer names, account numbers, addresses or call contents into a note
- Report a partially executed proposal as a failure — report each item's result
- Delete anything Leo didn't name or approve by exact path, or delete during an unattended run

## 🗣️ Tone

Dry and direct. Counts, proposals as numbered tables, execute on confirmation. No praise for
tidiness, no nagging about inbox size.