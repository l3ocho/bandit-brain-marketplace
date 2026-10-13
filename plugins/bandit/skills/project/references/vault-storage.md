# 🗄️ Vault Folder (WebDAV) — Procedures

> How bandit:project writes, versions and audits its two files in the project's settings folder. Read before any write to `webdav_folder` and before auditing it.

## Folder Naming Convention

Files follow this pattern: `{webdav_folder}/{prefix}-{type}-v{N}.md`

| Component | Source | Example |
|-----------|--------|---------|
| `webdav_folder` | Derived in Phase 4: `MyNotes/{domain}/Claude/ai-{project}` (Project Context) | `MyNotes/Personal/Claude/ai-bandit-infra` |
| `prefix` | The Project Context `prefix:` (Phase 4) | `bi` |
| `type` | Fixed per file | `instructions` or `prompt-reference` |
| `v{N}` | Integer, no dots, starts at `v0` | `v0`, `v1`, `v2` |
| `.md` | Fixed | — |

Full example: `MyNotes/Personal/Claude/ai-bandit-infra/bi-instructions-v0.md`

These files start with the `<!-- bandit-project: ... -->` comment on line 1, so they carry no
YAML frontmatter. The `bandit:notes` skill exempts `Claude/ai-*` files from its frontmatter and
filename rules for exactly this reason — never add frontmatter to them.

**Version numbers are independent per file.** Instructions might be at `v3` while the prompt
reference is at `v1`. Each file tracks its own version in the metadata block.

**Cross-references:** the instruction set references the prompt-reference file by its **current
versioned name**. When the prompt-reference version bumps, the instruction set's reference must
also update (and the instruction set gets its own version bump to reflect the change).

**Version history lives in the folder.** Old versions are **kept**: write the new version as a
new file and leave the old one in place. The user cleans up old versions by hand if they choose.

## Notes-App Collision Check

Run this **once, before the first write to a new folder.** The Nextcloud Notes app stores its
notes as `.md` files on disk inside its own root folder. A folder path that sits inside that
root will be picked up and indexed as notes, which means files this skill wrote as plain
documents start appearing in the user's Notes app and can be edited or moved from there —
exactly the coupling the folder backend exists to avoid.

The Notes root is user-configurable and **no available tool exposes it**, so this check cannot
be fully automated. Do what can actually be verified, and ask about the rest:

1. **Check the default.** If `webdav_folder` equals `Notes` or begins with `Notes/`, it is
   almost certainly inside the Notes root. Warn and confirm before proceeding.
2. **Ask about a custom root.** For any other path, ask once: "Is your Nextcloud Notes app
   configured to use a folder other than `Notes/`? If it is, and `{webdav_folder}` sits inside
   it, these files will show up in your Notes app as well."
3. **Confirm before proceeding** if either check indicates a collision. State the consequence
   plainly rather than refusing — the user may well want this, and it is their Nextcloud.

Do not invent a metadata field to record the answer. This check belongs to folder setup, not to
every version bump.

## Folder Existence Check

Before the first write, call `nc_webdav_list_directory` on `webdav_folder`.

- **Folder exists** → proceed.
- **404 / not found** → during onboarding it's already a row: bandit:notes' onboarding rows
  include `Claude/ai-{slug}/` when it's missing, and the settings files depend on that row. Outside
  onboarding (a custom path), **ask before creating it**: create it at this path, re-enter the
  path, or switch to artifact-only. Never call `nc_webdav_create_directory` without an approved
  row or an explicit yes.
- **Some other error** → report it and stop. In particular, `nc_webdav_list_directory` raises
  an error when the path sits inside a folder carrying an excluded system tag. That is a
  deliberate exclusion, not a missing folder, and creating a directory is not the fix.

## First Write (no existing files)

1. Run the collision check and the existence check above.
2. Write the instruction set via `nc_webdav_write_file` with:
   - `path`: `{webdav_folder}/{prefix}-instructions-v0.md`
   - `content`: the full instruction set
   - `if_match`: **omitted**
3. Write the prompt reference doc the same way, at
   `{webdav_folder}/{prefix}-prompt-reference-v0.md`.
4. Capture the returned `etag` from each write into `instructions_etag` and `prompt_ref_etag`.
   The write result returns bare hex — store it exactly as returned.
5. Update metadata: `storage_backend: "webdav"`, `webdav_folder`, both etags,
   `instructions_version: 0`, `prompt_ref_version: 0`, `last_sync`.
6. Output the instruction set to paste, and write the reference doc to the project (SKILL.md,
   **Project copy**).
7. Confirm: "Files written to `{webdav_folder}`:
   - `{prefix}-instructions-v0.md`
   - `{prefix}-prompt-reference-v0.md`
   Paste the instructions into your project's Custom Instructions field in Claude.ai."

**Omitting `if_match` is the safety mechanism, not an oversight.** These writes are fail-closed:
with no `if_match`, the write creates a new file and errors if anything already exists at that
path. That error is the desired outcome — it means a file is already there and this write would
have destroyed it. Never retry such a failure by passing `if_match: "*"`, which force-overwrites
unconditionally. Stop, list the directory, and work out what is actually there.

The response also returns `created` — `true` for a newly created file, `false` for an overwrite.
On any write that is supposed to be new, `created: false` means something was clobbered despite
the above. Surface that immediately rather than reporting success.

## Subsequent Writes (version bump)

**The directory is the source of truth for version numbers.** Fail-closed writes make a directory scan safe: the worst
case is an error, never a silent overwrite. Metadata can fall behind when the user copies a file
in by hand, and trusting it blindly would aim the next write at a path that already exists.

1. Call `nc_webdav_list_directory` on `webdav_folder`.
2. For each file type independently, find the highest existing `v{N}` among files matching
   `{prefix}-{type}-v*.md`. Ignore anything that doesn't match the pattern.
3. Determine which file(s) changed: instructions only, prompt-reference only, both, or a
   cross-reference-forced instructions bump (see **Cross-references** above).
4. For each file being bumped, write `v{N+1}` as a **new file** with `if_match` omitted.
   Leave every old version in place. Never delete.
5. Capture each new `etag` (bare hex, as returned by the write) into metadata, replacing the
   previous value for that file.
6. Update the version integers and `last_sync`.
7. Output the instruction set to paste, and write the reference doc to the project (SKILL.md,
   **Project copy**).
8. Confirm: "Version bumped in `{webdav_folder}`:
   - `{prefix}-instructions-v{N}.md` (was v{N-1})
   - `{prefix}-prompt-reference-v{M}.md` (unchanged)
   Remember to paste the updated instructions into your project settings."

If the directory scan and the metadata versions disagree, say so and ask before writing. The
scan wins for choosing the next number, but a gap the user didn't expect is worth a sentence.

## Etag Drift Detection

The stored etags answer one question on each audit: has anyone edited these files outside this
skill? Get the file's current etag and compare it against `instructions_etag` /
`prompt_ref_etag`.

**Normalise before comparing — the tools disagree on format** (verified 2026-09-19):

| Source | Shape | Example |
|---|---|---|
| `nc_webdav_write_file` result, `nc_webdav_list_directory` | Bare hex | `184e673c3028c9d6d33a796dc67a63ab` |
| `nc_webdav_read_file` | Weak, malformed — `W/` prefix, one stray quote | `W/"184e673c3028c9d6d33a796dc67a63ab` |

Compared raw, these never match, and every audit would report drift that isn't there. So:

- **Store etags as bare hex only** — exactly as the write returns them.
- **Prefer the etag from `nc_webdav_list_directory`.** The audit already lists the folder, and
  the listing returns bare hex.
- **If the etag comes from `nc_webdav_read_file`, strip `W/` and every `"` first.**
- The same stripping applies anywhere an etag is sent as `if_match`: the raw read value is
  rejected as a false *"concurrent edit"* even when nothing changed. This skill's own writes omit
  `if_match`, so this only matters to flows that reuse the read → append → write pattern.

Then:

- **Match** → the file is as this skill last left it.
- **Differs** → someone edited it in the Nextcloud UI or another client. Flag it in the audit
  report and ask before bumping, since a blind bump would fork away from their edit.
- **Stored etag is `null`, or the tool returns no etag** → drift cannot be determined. Say that
  plainly and continue; a missing etag is a gap in knowledge, not evidence of a clean file.

## If an Expected File Is Missing (deleted externally)

Detected by listing the directory, never by fetching an ID.

- Inform the user: "The expected file `{webdav_folder}/{prefix}-{type}-v{N}.md` is not in the
  folder listing."
- Offer three options:
  - Write at the **same version number** (treat as a restore)
  - Write at the **next version number** (treat as a fresh bump)
  - Switch to artifact-only
- One caveat worth stating: `nc_webdav_list_directory` omits children carrying an excluded
  system tag. A file hidden that way is missing from the listing but still present on disk, so
  a same-version restore will fail fail-closed rather than overwrite it. That error is the
  system working correctly — report it instead of forcing the write.

## Audit Mode: Folder Checks

When auditing existing instructions with `storage_backend: "webdav"`, resolve the current state
by listing `webdav_folder` via `nc_webdav_list_directory`.

**MyNotes path check (webdav only).** If the Project Context `domain` is `none` but `webdav_folder`
sits in a MyNotes domain (settings written before the MyNotes convention), or `domain` isn't
`none` and `webdav_folder` doesn't equal `MyNotes/{domain}/Claude/ai-{project}`,
flag it in the audit report as ⚠️ **Legacy settings path**. The fix is two steps, and this skill
does only the second:
1. Moving the folder is `bandit:notes onboard`'s job (this skill never moves or renames files).
2. Once the folder exists at the derived path, set the Project Context `domain` and `project`
   and the metadata `webdav_folder` on the next write, and update any path the instructions
   mention (e.g. External References).

If the folder hasn't been moved yet, keep writing to the current `webdav_folder` and say so.

**Project folder check (webdav, every project type).** If `domain` isn't `none` and
`MyNotes/{domain}/Projects/{project}/` doesn't exist, flag it (workflow projects included)
as ⚠️ **No shared project folder**. The fix is the vault rows of **🚀 Onboarding** in the same
proposal as the version bump. Never create it outside an approved row.

Then:
- Default to the existing naming convention — do not re-ask the questions
- If a version bump is needed, follow that backend's Subsequent Writes flow
- If the user wants to change the category, folder path or prefix, they must explicitly request it
