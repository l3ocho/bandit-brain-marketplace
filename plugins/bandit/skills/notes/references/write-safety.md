# 🛡️ Write safety

> The rules that protect the user's notes, whichever storage holds them. This skill owns them: every other skill that writes a note follows this file and never restates it.

How a write is made safe in each storage is that storage's reference: `references/storage-app.md`
for the app's Notes, `references/storage-vault.md` for the MyNotes vault.

## 🛡️ Write safety — the rules that protect the user's notes

**The user confirms every move, rename, archive, delete and edit of an existing note**, and the
creation of any place a note goes into. Present a numbered proposal, let them approve all, some
("1, 3, 5") or none, and execute exactly what was approved. One thing is written without
confirmation in every storage, because it can't destroy anything:

| Auto-write (no confirmation) | Why it's safe |
|---|---|
| Creating a **new** note in the inbox | It's the drop zone; a create never replaces a note that exists |

A storage may name one more of its own (`references/storage-vault.md` → Auto-writes).

**Approval covers the approved rows and nothing else.** Never create, edit, move or delete
anything that isn't in an approved row: not a place the conventions say should exist, not a fix
spotted along the way, and never anything that belongs to another project. A short "yes" or
"create it" approves the rows on the table, nothing else.

**Findings come fixed.** Every problem found (a breach, a leftover, a stray note, a broken link)
comes back as a numbered **fix row in the same proposal**, with the exact action and target and the
recommended fix. Nothing is ever just listed. A finding outside this project's scope is still a
row, marked `domain`. A finding with two valid fixes is one row with both, recommended first. One
"all" fixes everything; only approved rows run.

**Say plainly that nothing happens until they answer.** End every proposal with one line: *Nothing
is created or changed until you answer all, a list, or none.*

**A create never makes a second copy.** Before creating a note, look for the one that is already
there, the way the storage's reference says. What happens when one is found is the storage's too.

**An edit starts from the note as it is now.** Read the note right before changing it, and change
only what the approved row names.

**Delete only on the user's word.** A delete runs only when the user explicitly asked to delete
that item, or approved a `delete` row naming exactly that item. Rules:

- One row per item, never a wildcard. A row that removes a group lists what's inside it, so they
  see what goes.
- Ambiguous wording ("get rid of it", "clean this up") isn't a delete: offer **archive** or
  **delete** and let them pick.
- Never in a scheduled or unattended run: there's nobody to approve.
- Look again right before deleting; if the item changed or vanished since the proposal, skip the
  row and say so.
- Whether a deleted note can be brought back is the storage's; say what that storage keeps when
  asking.

**A refusal is an answer.** When the storage refuses a write, stop that row, report what it said,
and never work around it.
