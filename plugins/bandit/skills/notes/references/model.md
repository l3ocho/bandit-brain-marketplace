# 🧭 Storage, domain and scope

> Read before any command: where a project's notes are, what a domain is, how this project's scope is resolved, and why the inbox is the user's.

## 🗄️ Where the notes are

A project's notes live in **the app's Notes** (`references/storage-app.md`), on the project's
board. That is the only storage: no helper keeps a copy of a note anywhere else.

The project's Project Context can say one thing about it (the key and its format are
bandit:project's):

| `notes:` line | Means |
|---|---|
| absent, or `app` | The notes are in the app's Notes |
| `none` | The helpers keep no notes for this project: its records are kept elsewhere, by its own rules. Asked to write, file, lint or archive a note for it, a helper says so in one line and stops; nothing is created, in the Inbox either |

Read it with the domain, before any command and before any other skill's note is written.

**What is not a note.** A project's instructions file and settings, its working files (data,
scripts, outputs) and any file that is not text are not notes. They stay with the project: in its
folder on the machine it runs on. The one exception is bandit:project's two reference notes, which
are notes like any other (`references/other-skills.md`).

---

## 📍 Resolve the domain before anything else

1. **Project Context first.** Read the `## 🧭 Project Context` section of the project's
   instructions: the Claude.ai project instructions, or the folder's `CLAUDE.md` in Claude Code.
   `domain:` names the domain and `project:` the project slug. The block's format is owned by
   bandit:project.
   - `domain: none` → the project has no board folder. Its notes are private notes with the tag
     `{slug}` (`references/storage-app.md` → Places).
2. **Run by bandit:project (onboarding).** The project's instructions aren't written yet, so take
   `domain`, `project` and `type` from bandit:project instead. See *Onboarding* below.
3. **Explicit argument.** `/bandit:notes lint Acme`.
4. **Otherwise ask**, listing the live top-level board folders from `get_context`.

The names are read live from `get_context`: the **domain** is the top-level board folder of that
name, with its subfolders; the **project** is its board (`board:` in the Project Context); an
**area** is a column of that board (`references/storage-app.md` → Places). Never guess the nearest
match. A board or folder that isn't there: stop and say so.

---

## 🎯 Scope — what this project may see and change

**One project, one slug.** `project:` is the project's own name as a slug (`home-reno`). The same
slug names its hub note and tags its private notes.

**Scope comes from the Project Context `type:`**, resolved together with the domain:

| Situation | Scope |
|---|---|
| `type: workflow` (e.g. Acme Workflow) | **Domain**: every board in the domain's folder. Oversees every project, and like every project has its own board and hub note |
| `type: product_service` or `type: claude_marketplace` | **Project**: the table below |
| No Project Context, a domain given as the argument | **Domain** |

**Project scope:**

| Area | Read | Change (on approval) |
|---|---|---|
| The project's board: its notes, its Inbox, its archived notes, its notes in the Trash | ✓ | ✓ |
| Minutes and requests on the domain's workflow board | Only the ones that name this project (related to its hub note) | ✗ read-only. A helper may create its new minutes or request drafts in that board's Inbox; filing them is the workflow project's |
| Every other board | ✗ | ✗ |

A `write:` line in the Project Context limits note writes the same way it limits card writes (bandit:tasks
`references/scope.md`): a note is created, filed or moved only on a board it names, and into that board's column when
it names one.

Anything outside the scope (another project's board, a note on the workflow board) that the user
asks for: stop and say it's a domain-level action to run from the workflow project. Never widen
scope on your own. One exception: a **`domain` fix row** runs when the user approves that row by
number. Their yes is the widening, for that row only.

---

## 📥 The inbox is the user's

The Inbox is where the user writes, pastes and thinks: a board's Inbox, or the private one. A note
in it has status `inbox`. **While a note is there, no convention applies to it** — any title, any
fields or none, any structure, any date format. And **no skill or chat edits, renames, reformats
or moves a note there** unless the user puts that note up for review in the current conversation.
Not `lint`, not `onboard`, not another skill tidying up, not a chat that is using the note as
input. Reading is always fine. The user's yes to a row that archives or deletes a consumed draft by
name (*Other skills* → Leftovers) is putting that note up.

Whose a note is reads from who created it:

| Note in status `inbox` | Whose | Rules |
|---|---|---|
| `createdViaAssistant` false | The user's, in progress | None. Untouchable until they put it up for review |
| `createdViaAssistant` true | A helper's draft, waiting for the user's review | The helper wrote it compliant (kind, summary, fields); not edited again until review, except on the user's explicit request in the conversation that wrote it. A plan linked to its card waits here with no summary until the review gives it one (`references/storage-app.md` → Status and filing) |
| any other status | Reviewed | All of the conventions |

A helper's own draft is one it created. It stays in the Inbox, status `inbox`, until the user
reviews it; nothing marks it but who created it. A draft from an earlier conversation is as
untouchable as the user's own.

**The rules apply at review.** Review is `/bandit:notes file`: the user runs it (for the whole
inbox or for named notes) when they want a note processed. That is the only moment the conventions
touch it, and the note leaves the Inbox in the same step.

**Review is all or nothing per note.** Every question a note needs answered (which project,
which meeting type, what an ambiguous date means) is asked before its row is final. A row with
an open question is not executed, and **a note is never left half-edited in the inbox**: it is
either still exactly as the user left it, or reviewed and in its place.

**The user's words stay the user's.** At review, the fields are the skill's job. The body is not: any
body change (removing a duplicated block, rewriting a date, fixing structure) is its own row
showing before → after, and happens only if the user approves that row.
