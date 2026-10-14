# 📤 Output and metadata

> Read before writing any deliverable: where the instructions and reference doc go, and the metadata fields that track them. Folder mechanics: `references/vault-storage.md`.

## 🧾 Metadata Storage Fields

The metadata block carries the storage destination; the reference template documents the
other fields. The project's identity (domain, slug, type, board, prefix) is **not** here: it
lives in the **Project Context** section.

| Field | Type | Description |
|-------|------|-------------|
| `storage_backend` | `"webdav"` / `null` | `"webdav"` = the vault folder holds the files. `null` = artifact-only. Legacy `"notes"` → see the audit flow |
| `webdav_folder` | string/null | Full folder path, no leading slash (e.g., `MyNotes/Personal/Claude/ai-bandit-infra`). Derived from the Project Context `domain` + `project` unless the user chose a custom path. `null` when artifact-only |
| `instructions_etag` | string/null | Etag of the current instructions file, for drift detection. **Bare hex** — see Etag Drift Detection |
| `prompt_ref_etag` | string/null | Etag of the current prompt reference file. **Bare hex** |
| `instructions_version` | int/null | Integer version of the instruction set |
| `prompt_ref_version` | int/null | Integer version of the prompt reference doc |

With `storage_backend: null`, every storage field is `null`.

Example:

```json
{"storage_backend": "webdav", "webdav_folder": "MyNotes/Personal/Claude/ai-bandit-infra",
 "instructions_etag": "a1b2c3", "prompt_ref_etag": "d4e5f6",
 "instructions_version": 0, "prompt_ref_version": 0}
```

---

## 📤 Output Handling

Both modes produce **two deliverables**: the instruction set and the supporting project reference doc.
In audit mode, the reference doc is updated (or created if it doesn't exist yet).

### Output Target Selection

**New Project mode:** Phase 4 of `references/interview.md` asks the output target question (single select).

**Audit mode:** Read `storage_backend` from the metadata first, then:

| `storage_backend` | Behaviour |
|---|---|
| `"webdav"` with a `webdav_folder` | Default to a version bump using the existing convention. Confirm before creating new versions |
| `"notes"`, or a `note_id` with no `storage_backend` | ⚠️ Legacy Notes backend: offer the migration (audit flow, Step 1) |
| `null`, absent, or destination fields empty | Ask the output target question below, then the Phase 4 folder questions |

> "Where should I save the updated instructions?"

Options (single select via `ask_user_input`):
- "Artifact only" (default)
- "Artifact + vault folder (WebDAV)"
- "Vault folder (WebDAV) only"

### Artifact (Default)

Output the instruction set for pasting into the Claude.ai project settings. The reference doc
goes to the project (see **Project copy** (`references/output.md`)).

After outputting, remind:
> "Copy the instruction set into your project's Custom Instructions field in Claude.ai.
> The `<!-- bandit-project: ... -->` comment on line 1 is invisible in the UI but
> helps me track versions during future audits.
> The reference doc is saved in this project as `claude/{name}` — it's your project's living memory."

### Vault Folder (WebDAV)

**Backend: `"webdav"`.** Writes the two deliverables as plain `.md` files into the project's
settings folder. Tools: `nc_webdav_write_file`, `nc_webdav_read_file`, `nc_webdav_list_directory`,
`nc_webdav_create_directory`. No `nc_notes_*` call belongs anywhere in this skill.

**Read `references/vault-storage.md` before any write to the folder, and before auditing it.**
It holds the file naming and versioning rules, the Notes-app collision check, the folder
existence check, the first-write and version-bump procedures, etag drift detection, the
missing-file case and the audit folder checks. The limits that always apply are in
**What This Skill Never Does** below.

### Project copy

Every time this skill produces the reference doc, whatever the output target, it saves it into
the Claude.ai project with the Projects tool, instead of showing it in the chat:

1. Name: `claude/{prefix}-prompt-reference-v{N}.md`, the same name as the vault file. Artifact-only
   (`prefix: none`): `claude/{project}-prompt-reference-v{N}.md`, next N from the doc list.
2. Read the doc list with `project_info`. The name is already there → stop and ask.
   `project_write` replaces an existing path silently, so it never gets one.
3. `project_write` with that `path`, the full doc as `content`, `present_to_user: false`.
4. Confirm in one line: the file name and what changed. Show the doc only if the user asks.

No Projects tool in the session → output the reference doc as an artifact, and say in one line
that it wasn't saved to the project.
