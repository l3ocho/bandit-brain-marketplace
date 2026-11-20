# 🗄️ Storage: the MyNotes vault

> How a note is read and written in the MyNotes vault (Obsidian files on BanditCloud, over WebDAV). The rules every storage shares are `references/write-safety.md`; the vault's folders, filenames and frontmatter are `references/conventions-vault.md`.

Contents: The operations · Auto-writes · WebDAV mechanics · Obsidian and moves

## 🧰 The operations

Every storage answers the same seven operations. In the vault:

| Operation | Tool | How |
|---|---|---|
| Read | `nc_webdav_read_file` | Returns the text and the etag |
| Create if absent | `nc_webdav_write_file`, `if_match` omitted | Fails if the path exists: that failure is the protection |
| Edit if unchanged | `nc_webdav_write_file` with the bare-hex etag as `if_match` | Refused if the file changed since the read |
| Move without overwrite | `nc_webdav_move_resource`, `overwrite: false` | Refused if the destination exists |
| List | `nc_webdav_list_directory` | One folder |
| Find | `nc_webdav_find_by_name(pattern="{filename}", scope="MyNotes/{Domain}")` | By filename, inside the domain (the uniqueness check, `references/conventions-vault.md` §4) |
| Delete | `nc_webdav_delete_resource` | Only on the user's word, by exact path |

## ✍️ Auto-writes

Two writes need no confirmation, both because they can't destroy anything:

| Auto-write (no confirmation) | Why it's safe |
|---|---|
| Creating a **new** note in `{Domain}/_inbox/` | It's the drop zone; fail-closed create can't clobber |
| Regenerating `{Domain}/README.md` | Generated file; its config frontmatter and `## Notes` section are carried over |

Creating a folder is confirmed like every other change.

## 🔧 WebDAV mechanics

Verified against the BanditCloud MCP.

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
- **Delete only on the user's word** (`references/write-safety.md`). `nc_webdav_delete_resource`
  runs on one exact path a row. A folder row lists what's inside it. Never in `home`. Re-list
  right before deleting. Nextcloud usually keeps deleted files in its trash bin, but that's a
  server setting this skill can't check, so treat a delete as permanent when asking.
- **Excluded-tag errors** are deliberate exclusions. Report them; never work around them.
- **Never edit non-markdown files** (images, PDFs, audio, `.canvas`, `.excalidraw`). Move them
  only as part of an approved proposal.
- **`.obsidian/` is written only by `/bandit:notes settings`**, only the allowlisted files and keys
  in `references/conventions-vault.md` §11, only on approval, only with Obsidian closed on every
  device, and always with a backup first. Every other command treats `.obsidian/` as read-only.

## 🔗 Obsidian and moves

**Obsidian doesn't see WebDAV moves.** Its wikilinks survive because they resolve by filename —
which is why **filenames must be unique** (`references/conventions-vault.md` §4) and the vault's
link format must be "Shortest path when possible" (§11 there). A rename, unlike a move, breaks
`[[old-name]]` links: before renaming a note outside `_inbox`, find the notes linking to it and
include their link updates in the same proposal. An `aliases` entry for the old name does **not**
fix this — Obsidian never resolves a bare `[[alias]]` to a note.
