# 📤 Deliverables

> Read before writing any deliverable: the instructions, the reference doc, and the two reference notes that hold their copies in the app.

## 📦 What a run produces

Both modes (new project, audit) produce **two deliverables**: the instructions and the supporting
reference doc. In audit mode the reference doc is updated, or created if it doesn't exist yet.

| Deliverable | Claude Code project | Claude.ai project |
|---|---|---|
| **Instructions** | The folder's `CLAUDE.md`, written by an approved row (`references/surfaces.md`) | Handed over in full for the user to paste into the project's instructions field |
| **Reference doc** | The note `{slug}-reference` | The note `{slug}-reference` |
| **Copy of the instructions** | None: the file in the folder is the one copy | The note `{slug}-instructions`, so the text the project runs on can be read outside that project |

After a paste hand-over, remind in one line: *paste it into the project's instructions in
Claude.ai, then run `/bandit:audit check` there.*

## 🗒️ The two reference notes

Written through bandit:notes (`references/other-skills.md` there → Who writes what), each as its
own row of the proposal:

| Note | Kind · title | Holds | Place |
|---|---|---|---|
| Reference doc | `reference` · `{slug}-reference` | The project's living memory: stack, inventories, decision log, change history, open questions (`references/interview.md` → Generation, step 8) | The project's board, in its hub note's column |
| Instructions copy (Claude.ai projects only) | `reference` · `{slug}-instructions` | The instructions exactly as handed over, in one code block, with their `**Version:**` line | The same place |

- **One note each, updated in place.** A new version replaces the text (bandit:notes' safe edit:
  read right before, then the whole text); the app keeps the text before every save as a version
  the user can restore. Never a second note per version, never a version number in the title.
- **Each carries its own version.** The reference doc's first lines hold `**Version:**` and
  `**Last Updated:**`, and name the instructions version it goes with.
- **Size.** The app refuses a note over 200 KB. A reference doc that would pass it → row 1 of the
  proposal trims it: closed history moves to a second note, `{slug}-reference-history`, related to
  the first. Nothing is cut silently.
- **`notes: none` in the Project Context** → no note is written. The reference doc is a file in
  the project's folder, `REFERENCE.md` beside `CLAUDE.md` (Claude Code), written by its own row; on
  Claude.ai it is handed over in the chat.
- **`board: none` or `pending`** → the notes are private, with the tag `{slug}` (bandit:notes
  Places), and move to the board when it exists.

## 🧾 No settings line

The instructions carry no metadata comment. Their identity is the Project Context; their version
is the `**Version:**` line. A first line of the form `<!-- …: {"storage_backend": …} -->`, left by
an earlier version of this skill, is a finding: its row removes the line
(`references/audit.md` → Legacy settings line).
