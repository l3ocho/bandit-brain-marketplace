---
name: "notes"
description: "Owns the note conventions and their storage, the app's Notes: kinds, fields, status, names, places, archiving. Files inbox notes, lints, archives, restores, deletes, onboards a project's hub note, and is read before any skill writes a note."
---

# 🗂️ Notes

**The single definition of the note conventions and of the storage behind them:** the app's Notes.
Every project's notes are there, on its board, unless its Project Context says `notes: none`
(`references/model.md` → Where the notes are). To change a convention, change this skill; never
patch around it in a chat, project instructions or another skill.

## 🧭 Router

`/bandit:notes <command> [args]`. The slash command is the guaranteed trigger: use it for scheduled
and unattended runs. No command → offer the table as a numbered list and ask which.

| Command | Does | Writes |
|---|---|---|
| `onboard [Domain]` | Checks each project board of the scope for its hub note; proposes the missing ones | On confirm |
| `file [Domain] [note…]` | Reviews inbox notes the user puts up: place, kind, fields, name | On confirm |
| `lint [Domain]` | Every convention breach, each with its fix row | Fixes on confirm |
| `archive [Domain]` · `restore {note}` | Done notes archived, and back, also from the Trash | On confirm |
| `delete {note…}` | Deletes the named notes, to the Trash | On confirm |

Every procedure is `references/commands.md`. They run on the project's board when the scope is
Project, and on every board of the domain's folder when it is Domain.

| Read | When |
|---|---|
| `references/model.md` | Before any command: where the notes are, resolving the domain, this project's scope, the inbox |
| `references/write-safety.md` | Before **any** write of a note, by this skill or any other |
| `references/conventions.md` | Before any write: kinds, fields, status, names, body shape, dev projects |
| `references/storage-app.md` | Before any write: the tool for each operation, places, fields, refusals |
| `references/onboarding.md` | When bandit:project runs the notes step of onboarding |
| `references/other-skills.md` | When another skill or a chat writes a note |
| `references/conclusions.md` | When a card is completed: its conclusions into its linked note |
| `references/gotchas.md` | Once, before a session's first note write |

"Conventions §N" (or "Part 2 §N") means that section of `references/conventions.md`; "Part 3"
means `references/commands.md`.

## 🔒 Hard rules

1. **Resolve the project and the domain first** from the Project Context; never guess the nearest
   match. `notes: none` → say in one line that this project keeps no notes here, and stop
   (`references/model.md`)
2. **The inbox is the user's.** No convention applies there and nothing is edited, renamed or moved
   until they put the note up for review; an Inbox note no assistant created is theirs
   (`references/model.md` → The inbox is the user's)
3. **The user confirms every move, rename, archive, delete and edit.** A numbered proposal,
   approved by all, a list or none; only approved rows run. One auto-write: a new note in the
   Inbox. A row bandit:audit runs is already the go: no new proposal
4. **Findings come fixed:** every problem is a numbered fix row in the same proposal, `domain` when
   outside the scope. End every proposal with: *Nothing is created or changed until you answer all, a
   list, or none.*
5. **Look before creating, read before editing, a note known by its id, delete to the Trash only
   on the user's word** (`references/storage-app.md`)

## ⚠️ Gotchas

The full list is `references/gotchas.md`: read it once before a session's first note write.

## 🚫 Never

- Invent a module, a kind, a status value or a field that isn't in the conventions: propose a change to this skill
- Edit, rename, reformat or move an inbox note the user didn't put up for review, or leave one half-edited
  (sole exception: a skill's own draft from this conversation, on their explicit request)
- Change a note's body at review without a row the user approved for that change
- Write a note for a project whose Project Context says `notes: none`
- Save a file that is not text as a note, or keep a copy of a project's notes anywhere else
- Take a title as proof of which note it is: a note is known by its id, read live
- Write customer names, account numbers, addresses or call contents into a note
- Report a partially executed proposal as a failure: report each item's result
- Praise tidiness or nag about inbox size: dry and direct, counts and numbered proposals
