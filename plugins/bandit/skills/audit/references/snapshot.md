# 📸 Snapshot: what the script scores

> The only step the script can't check for itself: copying tool output into files. Copy
> values as-is. Never fix, tidy, reorder or leave anything out: a wrong snapshot gives a report
> that looks right but isn't.

## 📂 Three input files (next to the script run: `.audit/` for `audit`, any scratch folder for `check`)

| File | From | How |
|---|---|---|
| `rules.yaml` | `references/structure-rules.yaml` (this skill) | Copied byte for byte |
| `rulebook.md` | `references/structure-rulebook.md` (this skill) | Copied byte for byte |
| `snapshot.json` | The reads below | Built to the schema below |

A read that fails → stop and say which. Don't build a partial snapshot: the script can't tell a
missing board from an empty one.

## 🧾 Schema (`schema: 8`)

Build schema 8. Its projects are the self-check stamps; nothing in it comes from a file storage.
The script loads no earlier schema: a saved snapshot of schema 1 to 7 was built from a storage that
is gone, so its report is superseded (`references/domain-audit.md` → Replay).

```json
{
  "schema": 8,
  "taken_at": "2026-11-22T19:18:00Z",
  "tags": ["deep-work", "lane/feature", "stage/spec"],
  "board": {
    "folders":  [{"name": "Acme", "parent": null}, {"name": "Clients", "parent": "Acme"}],
    "projects": [{"name": "Home Reno", "profile": "technical", "folder": "Acme",
                  "visibility": "household", "system_owner": null,
                  "lanes": [{"name": "Feature", "position": 0,
                             "matcher": {"field": "tag", "values": ["lane/feature"]}}]}],
    "sprint_cards": [{"id": "<uuid>", "short_id": "{PFX}-26", "sprints": ["Staging 1"]}]
  },
  "stamps": {
    "Acme/home-reno": {
      "surface": "claude-code",
      "name": null,
      "version": "2.0.0",
      "checked": "2026-11-22",
      "context": {"domain": "Acme", "project": "home-reno", "type": "product_service",
                  "board": "project \"Home Reno\"", "prefix": "hr", "dev": "true"},
      "guard": null,
      "workdir": null
    }
  },
  "notes": {
    "Acme": {
      "home-reno": {
        "board": "Home Reno",
        "notes": [{"id": "<note id>", "title": "home-reno-feature-tiles-2026-11-20", "kind": "brief",
                   "status": "active", "cards": ["{PFX}-26"], "tags": ["sprint-staging"]}]
      }
    }
  }
}
```

## 🔎 Where each field comes from

| Field | Tool | Rule |
|---|---|---|
| `taken_at` | clock | UTC, when the reads started |
| `board.folders` | `get_context → folders` (one `get_context` call serves every `board` and `tags` row) | Every folder, each top-level one and each child listed inside it; a child's `parent` is its parent's **name** |
| `board.projects` | `get_context → boards` (not archived: no `includeArchived`) | `name`, `profile` (`workflow` or `technical`, as-is), `folder` = `folder.name` (or `null`), `visibility`, `system_owner` = `systemOwner`. Every board, system ones included: the script exempts them |
| `….lanes` | `get_context → boards` (lanes come with the columns) | Every lane: `name`, `position`, `matcher.field` as-is, and `matcher.values` with **tag ids replaced by tag names** from `get_context → tags` (priority and state values as-is). No lanes → `[]` (a Workflow board always: the app hides its lanes) |
| `tags` | `get_context → tags` | Every tag **name**, as-is |
| `board.sprint_cards` | Real sprints: `get_sprints { boardId }` on each Technical board of the domain, then `get_sprints { sprintId }` for each one's cards. `MODULE_DISABLED` → stop and say Sprints is off; never write an empty list for it | One entry per card: `id`, `short_id` (`shortId`, or `null`), `sprints` = the **names** of the sprints holding it, as-is |
| `stamps` | The stamps note of each domain scored (`stamps.note_title`; found as `references/self-check.md` step 4 says), read with `notes_get` | One key per `## {project}` section, `{domain}/{project}`: the section's `json` block parsed, as-is. No note for a domain → no keys for it. A block that doesn't parse → stop and say which section: never skip it |
| `notes.{D}.{project}` | `notes_list` of the board the stamp's `board:` line names (its Inbox included, archived notes left out) | One key per stamped project of a scored domain. `board` = the board's name. `notes`: one row per note, `id`, `title`, `kind`, `status` as-is, `cards` = each linked card's `shortId` (its `id` when it has none). `board: none`, a board that doesn't resolve, or `notes: none` → `notes: []` |
| `….notes[].tags` | `notes_get` of **every** note of kind `brief` linked to a card | Its `tags`, as-is. Every other note: `null` (not read). The script refuses a brief linked to a card whose tags are `null` |

`audit {domain}` snapshots every domain's board, but reads the stamps note and the notes only for
the domains it scores. `audit all` reads them all, once. `check` reads its own project's notes only,
with every stamp of its domain's note.

## ▶️ Run

From Claude Code, in the folder the audit runs from (`references/domain-audit.md`). The
three input files are working files: write them in `.audit/` at that folder's root, then keep only
`snapshot.json`, renamed as the report's snapshot (`references/domain-audit.md` → Report).

```
python {skill folder}/scripts/check_structure.py --rules rules.yaml --rulebook rulebook.md \
    --snapshot snapshot.json [--domain D] --out out
```

Needs PyYAML (`pip install pyyaml` if missing). Exit codes: `0` scored · `2` an input broke its
contract (the message says which: fix the input, never score around it) · `3` replay mismatch.
