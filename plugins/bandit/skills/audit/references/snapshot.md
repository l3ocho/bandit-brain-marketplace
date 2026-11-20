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
missing folder from an empty one.

## 🧾 Schema (`schema: 7`)

Build schema 7. It adds, under `vault.projects`, the notes of a project on the app's Notes
(`notes: app` in its Project Context), and drops `vault.inbox` (S14 is retired). The script still
reads older saved snapshots and scores the rules that stay as before: schema 6 has no app notes
(every project is read from the vault), schema 5 carries each board's old `type` where schema 6 has
its `profile` (S3 reads the type, S9 skips the profile), schema 4 has no project files (S13 scores
**unchecked**), schema 3 has no working-folder manifests either (S12 unchecked too), schema 2 has no
surfaces either (S10 and S11 unchecked too), schema 1 has no lanes either (S9 unchecked too).

```json
{
  "schema": 7,
  "taken_at": "2026-09-27T19:18:00Z",
  "tags": ["deep-work", "lane/feature", "stage/spec"],
  "board": {
    "folders":  [{"name": "Personal", "parent": null}, {"name": "Career", "parent": "Personal"}],
    "projects": [{"name": "Career Manager", "profile": "technical", "folder": "Career",
                  "visibility": "household", "system_owner": null,
                  "lanes": [{"name": "Feature", "position": 0,
                             "matcher": {"field": "tag", "values": ["lane/feature"]}}]}],
    "sprint_cards": [{"id": "<uuid>", "short_id": "{PFX}-26", "sprints": ["sprint/staging"]}]
  },
  "vault": {
    "domains": ["Acme", "Home", "Work"],
    "settings": {
      "Personal": {
        "ai-career-manager": {
          "entries": [{"name": "cm-instructions-v2.md", "dir": false, "modified": "2026-09-25"}],
          "instructions": {
            "cm-instructions-v2.md": {
              "version_line": "1.1.0",
              "context": {"domain": "Personal", "project": "career-manager", "type": "product_service",
                          "board": "project \"Career Manager\"", "prefix": "cm"},
              "text": "<the whole file, raw>"
            }
          }
        }
      }
    },
    "surfaces": {
      "Acme": {
        "code-home-reno": {
          "entries": [{"name": "CLAUDE.md", "dir": false, "modified": "2026-09-28"},
                      {"name": "claude", "dir": true, "modified": "2026-09-28"},
                      {"name": "claude/settings.json", "dir": false, "modified": "2026-09-28"}],
          "files": {"CLAUDE.md": "<raw>", "claude/settings.json": "<raw>"},
          "repo": null,
          "workdir": null
        }
      }
    },
    "projects": {
      "Acme": {
        "garden": {
          "storage": "vault",
          "entries": [{"name": "garden.md", "dir": false},
                      {"name": "sprint-staging", "dir": true},
                      {"name": "sprint-staging/garden-sprint-staging-plan.md", "dir": false}],
          "frontmatter": {"garden.md": "<raw YAML between the --- lines>",
                          "sprint-staging/garden-sprint-staging-plan.md": "<raw>"}
        },
        "home-reno": {
          "storage": "app",
          "board": "Home Reno",
          "notes": [{"id": "<uuid>", "title": "home-reno-tiles-brief", "kind": "brief", "status": "active",
                     "cards": ["{PFX}-26"], "tags": ["sprint-staging"]},
                    {"id": "<uuid>", "title": "home-reno-sprint-staging-plan", "kind": "plan", "status": "active",
                     "cards": [], "tags": null}]
        }
      }
    }
  },
  "stamps": { "Personal/career-manager": { "...": "the ledger entry, as-is" } }
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
| `vault.domains` | `nc_webdav_list_directory("MyNotes")` | Folders not starting with `_` or `.` |
| `settings.{D}` | list `MyNotes/{D}/Claude/` | One key per `ai-*` folder |
| `….entries` | list each `ai-*` folder, and every subfolder inside it | `name` = path relative to the `ai-*` folder (`sub/file.md`); `dir` true for folders; `modified` = `last_modified` as `YYYY-MM-DD` |
| `….instructions` | `nc_webdav_read_file` raw, **every** file whose name ends `-instructions-v{N}.md`, subfolders included | `version_line` = everything after `**Version:**` on that line, verbatim. `context` = the `key: value` lines inside `## 🧭 Project Context`, verbatim; `null` if the section is missing |
| `….instructions.{file}.text` | the same raw read | The whole file, verbatim. S10 hashes the text outside `## 🖥️ Environment` |
| `surfaces.{D}` | list `MyNotes/{D}/Claude/` | One key per `code-*` and `design-*` folder. `{}` when there are none |
| `….entries` (surfaces) | list the folder and every subfolder inside it | Same rule as settings entries |
| `….files` | `nc_webdav_read_file` raw | `CLAUDE.md`, `claude/settings.json` and `claude/hooks/workdir.py`, when listed, verbatim. Nothing else |
| `….repo` | nothing | Always `null`. S11 no longer dates the mirror (GitHub's last push lags the real remote); the key stays so older snapshots still load |
| `….workdir` | `nc_webdav_read_file` raw of `MyNotes/{D}/Projects/{slug}/workdir-manifest.json` (`{slug}` = the folder name after `code-`), parsed | `code-*` of a project **without** `dev: true` only: the JSON object as-is. Missing file, `design-*`, or dev → `null`. Never rebuilt or tidied: S12 reads it field by field |
| `stamps` | ``nc_webdav_read_file` of the stamp ledger (`paths.stamps` in `references/structure-rules.yaml`)` | Its `projects` object, as-is. Missing ledger → `{}` |
| `board.sprint_cards` | Real sprints: `get_sprints { boardId }` on each Technical board of the domain, then `get_sprints { sprintId }` for each one's cards. Old sprints, until the tags retire: `list_tasks(tagPrefix: "sprint/")`, open and completed (not archived). `MODULE_DISABLED` → stop and say Sprints is off; never write an empty list for it | One entry per card: `id`, `short_id` (`shortId`, or `null`), `sprints` = the **names** of the real sprints holding it, as-is, and its tag names starting `sprint/`, as-is |
| `vault.projects.{D}` | The production instructions' Project Context (`….instructions` above) says where each project's notes are: `notes: app` → the app's Notes, no line → the vault | One key per project: `storage` is `app` or `vault`. A project on the app's Notes is never read from the vault, even when an old `Projects/{slug}/` folder is still there |
| `….{slug}` (vault) | `nc_webdav_find_by_name(pattern="%", scope="MyNotes/{D}/Projects")` | One key per folder directly under `Projects/`, except the folder of a project with `notes: app`. `entries`: every file and folder inside it, `name` relative to that folder (`sprint-x/note.md`), `dir` as listed. Results must equal `total_found`; fewer → stop (a partial listing) |
| `….frontmatter` (vault) | `nc_webdav_read_file` raw of **every** `.md` in a project that has a `sprint-*` folder at its root; none for other projects (`{}`) | The text between the first two `---` lines, verbatim, without them. A file that doesn't start with `---` → `null`. The script refuses a sprint project with a note left unread |
| `….{slug}` (app) | `notes_list` of the project's board (`board:` in its Project Context; its Inbox included, archived notes left out) | `board` = the board's name. `notes`: one row per note, `id`, `title`, `kind`, `status` as-is, `cards` = each linked card's `shortId` (its `id` when it has none). `board: none` → `notes: []` (a sprint lives on a board) |
| `….notes[].tags` (app) | `notes_get` of **every** note of kind `brief` linked to a card | Its `tags`, as-is. Every other note: `null` (not read). The script refuses a brief linked to a card whose tags are `null` |

`audit {domain}` still snapshots every domain's board, but only reads settings and project notes for
the domains it scores. `audit all` reads them all, once.

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
