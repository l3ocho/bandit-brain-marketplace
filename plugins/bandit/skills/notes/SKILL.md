---
name: "notes"
description: "Owns the MyNotes vault conventions (Obsidian over WebDAV): folders, filenames, frontmatter, status, archiving and each domain's README. Files inbox notes, lints, archives, scaffolds domains, runs onboarding's vault step, and is read before any skill writes a note. Not for the Nextcloud Notes app."
---

# 🗂️ Notes

**The single definition of the vault conventions.** To change a convention, change this skill;
never patch around it in a chat, project instructions or another skill.

## 🧭 Router

`/bandit:notes <command> [args]`. The slash command is the guaranteed trigger: use it for scheduled
and unattended runs. No command → offer the table as a numbered list and ask which.

| Command | Does | Writes | Procedure |
|---|---|---|---|
| `onboard [Domain]` | Audits a domain against the conventions, proposes the migration | On confirm | `references/commands.md` |
| `init {Domain}` | Scaffolds a new domain | On confirm | `references/commands.md` |
| `home [Domain]` | Rebuilds the domain README home page | Auto | `references/commands.md` · `references/readme-template.md` |
| `file [Domain] [note…]` | Reviews inbox notes the user puts up: destination, filename, frontmatter | On confirm | `references/commands.md` |
| `lint [Domain]` | Every convention breach, each with its fix row | Fixes on confirm | `references/commands.md` |
| `settings [Domain]` | Obsidian settings against conventions §11; rollback from backup | On confirm, Obsidian closed | `references/commands.md` |
| `archive [Domain]` · `restore {note}` | `status: done` notes into `_archive`, and back | On confirm | `references/commands.md` |
| `delete {path…}` | Deletes the named notes, files or folders | On confirm | `references/commands.md` |

`init`, `home` and `settings` are domain-only; the others run on the project's own areas when the
scope is Project.

| Read | When |
|---|---|
| `references/model.md` | Before any command: the vault model, resolving the domain, this project's scope, the inbox |
| `references/write-safety.md` | Before **any** write into the vault, by this skill or any other |
| `references/conventions.md` | Before any write: folders, filenames, frontmatter, status, archive (conventions §1–§13) |
| `references/onboarding.md` | When bandit:project runs the vault step of onboarding |
| `references/other-skills.md` | When another skill or a chat writes a note |
| `references/gotchas.md` | Once, before a session's first vault write |

"Conventions §N" (or "Part 2 §N") means that section of `references/conventions.md`; "Part 3" means
`references/commands.md`.

## 🔒 Hard rules

1. **Resolve the domain first** from the Project Context (`domain:`, `project:`, `type:`); never
   guess the nearest match (`references/model.md`)
2. **The inbox is the user's.** No convention applies there and nothing is edited, renamed or moved until
   they put the note up for review (`references/model.md` → The inbox is the user's)
3. **The user confirms every move, rename, archive, delete, folder creation and edit.** A numbered
   proposal, approved by all, a list or none; only approved rows run. Two auto-writes: a new note in
   `_inbox/`, and the generated README (`references/write-safety.md`). A row bandit:audit runs is
   already the go: no new proposal
4. **Findings come fixed:** every problem is a numbered fix row in the same proposal, `domain` when
   outside the scope. End every proposal with: *Nothing is created or changed until you answer all, a
   list, or none.*
5. **New files fail closed; edits carry the bare-hex etag; moves never overwrite; never `if_match: "*"`;
   delete only on the user's word, by exact path** (`references/write-safety.md`)

## ⚠️ Gotchas

The full list is `references/gotchas.md`: read it once before a session's first vault write.

## 🚫 Never

- Treat a root `_` folder or any dot folder as a domain, or scan inside it (one exception:
  `.obsidian/` settings files, read by `lint` and `settings`, conventions §11)
- Put anything but settings under `Claude/`, or skills anywhere in the vault
- Invent a module, status value or frontmatter key that isn't in the conventions: propose a change to this skill
- Impose a layout inside `Projects/{slug}/` beyond its hub note and, on a sprint project, the root rule (conventions §1)
- Write to `.obsidian/` outside `settings`, off its allowlist, while Obsidian may be open, or without a backup
- Edit, rename, reformat or move an inbox note the user didn't put up for review, or leave one half-edited
  (sole exception: a skill's own `triaged` draft from this conversation, on their explicit request)
- Change a note's body at review without a row the user approved for that change
- Put a date-only or title-case filename anywhere outside `_inbox`
- Write customer names, account numbers, addresses or call contents into a note
- Report a partially executed proposal as a failure: report each item's result
- Praise tidiness or nag about inbox size: dry and direct, counts and numbered proposals
