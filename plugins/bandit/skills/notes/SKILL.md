---
name: "notes"
description: "Owns the note conventions and their two storages, the app's Notes and the MyNotes vault (Obsidian over WebDAV): kinds, fields, status, places, archiving. Files inbox notes, lints, archives, restores, deletes, onboards, and is read before any skill writes a note. Not for the Nextcloud Notes app."
---

# 🗂️ Notes

**The single definition of the note conventions and of the two storages behind them:** the app's
Notes and the MyNotes vault. The Project Context says which one a project uses; no word on it means
the vault (`references/model.md` → Which storage). To change a convention, change this skill; never
patch around it in a chat, project instructions or another skill.

## 🧭 Router

`/bandit:notes <command> [args]`. The slash command is the guaranteed trigger: use it for scheduled
and unattended runs. No command → offer the table as a numbered list and ask which.

| Command | Does | Writes | Storage |
|---|---|---|---|
| `onboard [Domain]` | Audits a domain against the conventions, proposes the migration; in the app, the hub note only | On confirm | Both |
| `init {Domain}` | Scaffolds a new domain | On confirm | Vault only |
| `home [Domain]` | Rebuilds the domain README home page | Auto | Vault only |
| `file [Domain] [note…]` | Reviews inbox notes the user puts up: place, kind, fields (and filename in the vault) | On confirm | Both |
| `lint [Domain]` | Every convention breach, each with its fix row; in the app, the fields only | Fixes on confirm | Both |
| `settings [Domain]` | Obsidian settings against conventions §11; rollback from backup | On confirm, Obsidian closed | Vault only |
| `archive [Domain]` · `restore {note}` | Done notes archived, and back; in the app, also back from the Trash | On confirm | Both |
| `delete {note…}` | Deletes the named notes (in the vault also files or folders) | On confirm | Both |

Every procedure is `references/commands.md`, with what changes on the app's Notes under each
command (`home` also reads `references/readme-template.md`). `init`, `home` and
`settings` are domain-only and vault-only; the others run on the project's own areas when the scope
is Project.

| Read | When |
|---|---|
| `references/model.md` | Before any command: which storage, the vault model, resolving the domain, this project's scope, the inbox |
| `references/write-safety.md` | Before **any** write of a note, by this skill or any other: the rules both storages share |
| `references/conventions.md` | Before any write: kinds, fields, status, body shape, dev projects, and the map of conventions §1–§13 |
| `references/conventions-vault.md` | Before any write into the vault: folders, filenames, frontmatter, archive, Obsidian settings |
| `references/storage-vault.md` | Before any write into the vault: the WebDAV mechanics |
| `references/storage-app.md` | Before any write into the app's Notes: the tool for each operation, places, fields, refusals |
| `references/onboarding.md` | When bandit:project runs the notes step of onboarding |
| `references/other-skills.md` | When another skill or a chat writes a note |
| `references/conclusions.md` | When a card is completed: its conclusions into its linked note |
| `references/gotchas.md` | Once, before a session's first note write |

"Conventions §N" (or "Part 2 §N") means that section of `references/conventions.md`, whose section
map says which sections are written in `references/conventions-vault.md` under the same number;
"Part 3" means `references/commands.md`.

## 🔒 Hard rules

1. **Resolve the storage and the domain first** from the Project Context; never guess the nearest
   match (`references/model.md`)
2. **The inbox is the user's.** No convention applies there and nothing is edited, renamed or moved until
   they put the note up for review; in the app's Notes, an Inbox note no assistant created is theirs
   (`references/model.md` → The inbox is the user's)
3. **The user confirms every move, rename, archive, delete, folder creation and edit.** A numbered
   proposal, approved by all, a list or none; only approved rows run. Auto-writes: a new note in the
   Inbox (`_inbox/` in the vault), and the vault's generated README (`references/storage-vault.md`).
   A row bandit:audit runs is already the go: no new proposal
4. **Findings come fixed:** every problem is a numbered fix row in the same proposal, `domain` when
   outside the scope. End every proposal with: *Nothing is created or changed until you answer all, a
   list, or none.*
5. **Vault: new files fail closed; edits carry the bare-hex etag; moves never overwrite; never
   `if_match: "*"`; delete only on the user's word, by exact path** (`references/storage-vault.md`).
   **App's Notes: look before creating, read before editing, a note known by its id, delete to the
   Trash only on the user's word** (`references/storage-app.md`)

## ⚠️ Gotchas

The full list is `references/gotchas.md`: read it once before a session's first note write.

## 🚫 Never

- Treat a root `_` folder or any dot folder as a domain, or scan inside it (one exception:
  `.obsidian/` settings files, read by `lint` and `settings`, conventions §11)
- Put anything but settings under `Claude/`, or skills anywhere in the vault
- Invent a module, status value or frontmatter key that isn't in the conventions: propose a change to this skill
- Impose a layout inside `Projects/{slug}/` beyond its hub note and, on a sprint project, the root rule (conventions §1)
- Write to `.obsidian/` outside `settings`, off its allowlist, while Obsidian may be open, or without a backup
- Edit, rename, reformat or move an inbox note the user didn't put up for review, or leave one half-edited
  (sole exception: a skill's own draft from this conversation, on their explicit request)
- Run `init`, `home` or `settings` for a project on the app's Notes: say they are vault-only
- Change a note's body at review without a row the user approved for that change
- Put a date-only or title-case filename anywhere outside `_inbox`
- Write customer names, account numbers, addresses or call contents into a note
- Report a partially executed proposal as a failure: report each item's result
- Praise tidiness or nag about inbox size: dry and direct, counts and numbered proposals
