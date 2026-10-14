# 🛡️ Write safety

> The rules that protect the user's files. This skill owns them: every other skill that writes to the vault follows this file and never restates it.

## 🛡️ Write safety — the rules that protect the user's files

**The user confirms every move, rename, archive, delete, folder creation and edit of an existing note.**
Present a numbered proposal, let them approve all, some ("1, 3, 5") or none, and execute exactly
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

**Say plainly that nothing happens until they answer.** End every proposal with one line: *Nothing
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
- **Delete only on the user's word.** `nc_webdav_delete_resource` runs only when the user explicitly asked
  to delete that item, or approved a `delete` row naming its exact path. Rules:
  - One row per path, never a wildcard. A folder row lists what's inside it, so they see what goes.
  - Ambiguous wording ("get rid of it", "clean this up") isn't a delete: offer **archive** or
    **delete** and let them pick.
  - Never in `home` or any scheduled/unattended run: there's nobody to approve.
  - Re-list right before deleting; if the path changed or vanished since the proposal, skip the
    row and say so.
  - Nextcloud usually keeps deleted files in its trash bin, but that's a server setting this skill
    can't check, so treat a delete as permanent when asking.
- **Excluded-tag errors** are deliberate exclusions. Report them; never work around them.
- **Never edit non-markdown files** (images, PDFs, audio, `.canvas`, `.excalidraw`). Move them
  only as part of an approved proposal.
- **`.obsidian/` is written only by `/bandit:notes settings`**, only the allowlisted files and keys
  in Part 2 §11, only on approval, only with Obsidian closed on every device, and always with a
  backup first. Every other command treats `.obsidian/` as read-only.

**Obsidian doesn't see WebDAV moves.** Its wikilinks survive because they resolve by filename —
which is why **filenames must be unique** (Part 2 §4) and the vault's link format must be
"Shortest path when possible" (Part 2 §11). A rename, unlike a move, breaks `[[old-name]]`
links: before renaming a note outside `_inbox`, find the notes linking to it and include their
link updates in the same proposal. An `aliases` entry for the old name does **not** fix this —
Obsidian never resolves a bare `[[alias]]` to a note.
