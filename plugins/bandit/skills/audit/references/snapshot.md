# 📸 Snapshot: what the script scores

> The only step the script can't check for itself: copying tool output into files. Copy
> values as-is. Never fix, tidy, reorder or leave anything out: a wrong snapshot gives a report
> that looks right but isn't.

## 📂 Three input files (in the sandbox, next to the script run)

| File | From | How |
|---|---|---|
| `rules.yaml` | `references/structure-rules.yaml` (this skill) | Copied byte for byte |
| `rulebook.md` | `references/structure-rulebook.md` (this skill) | Copied byte for byte |
| `snapshot.json` | The reads below | Built to the schema below |

A read that fails → stop and say which. Don't build a partial snapshot: the script can't tell a
missing folder from an empty one.

## 🧾 Schema (`schema: 5`)

Build schema 5. The script still reads older saved snapshots: schema 4 has no project files
(S13–S16 score **unchecked**), schema 3 has no working-folder manifests either (S12 unchecked too),
schema 2 has no surfaces either (S10 and S11 unchecked too), schema 1 has no lanes either (S9
unchecked too).

```json
{
  "schema": 5,
  "taken_at": "2026-09-27T19:18:00Z",
  "tags": ["deep-work", "lane/feature", "stage/spec"],
  "board": {
    "folders":  [{"name": "Personal", "parent": null}, {"name": "Career", "parent": "Personal"}],
    "projects": [{"name": "Career Manager", "type": "hybrid", "folder": "Career",
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
        "home-reno": {
          "entries": [{"name": "home-reno.md", "dir": false},
                      {"name": "sprint-staging", "dir": true},
                      {"name": "sprint-staging/home-reno-sprint-staging-plan.md", "dir": false}],
          "frontmatter": {"home-reno.md": "<raw YAML between the --- lines>",
                          "sprint-staging/home-reno-sprint-staging-plan.md": "<raw>"}
        }
      }
    },
    "inbox": {"Acme": ["Untitled 3.md", "home-reno-wbs.md"]}
  },
  "stamps": { "Personal/career-manager": { "...": "the ledger entry, as-is" } }
}
```

## 🔎 Where each field comes from

| Field | Tool | Rule |
|---|---|---|
| `taken_at` | clock | UTC, when the reads started |
| `board.folders` | `list_folders` | Every folder; a child's `parent` is its parent's **name** |
| `board.projects` | `list_projects` (not archived) | `name`, `type`, `folder` = `folder.name` (or `null`), `visibility`, `system_owner` = `systemOwner`. Every project, system ones included: the script exempts them |
| `….lanes` | `list_projects` (lanes come with the columns) | Every lane: `name`, `position`, `matcher.field` as-is, and `matcher.values` with **tag ids replaced by tag names** from `list_tags` (priority and state values as-is). No lanes → `[]` |
| `tags` | `list_tags` | Every tag **name**, as-is |
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
| `board.sprint_cards` | `list_tasks(tagPrefix: "sprint/")`, open and completed (not archived) | One entry per card: `id`, `short_id` (`shortId`, or `null`), `sprints` = its tag **names** starting `sprint/`, as-is |
| `vault.projects.{D}` | `nc_webdav_find_by_name(pattern="%", scope="MyNotes/{D}/Projects")` | One key per folder directly under `Projects/`. `entries`: every file and folder inside it, `name` relative to that folder (`sprint-x/note.md`), `dir` as listed. Results must equal `total_found`; fewer → stop (a partial listing) |
| `….frontmatter` | `nc_webdav_read_file` raw of **every** `.md` in a project that has a `sprint-*` folder at its root; none for other projects (`{}`) | The text between the first two `---` lines, verbatim, without them. A file that doesn't start with `---` → `null`. The script refuses a sprint project with a note left unread |
| `vault.inbox.{D}` | `nc_webdav_list_directory("MyNotes/{D}/_inbox")` | Filenames only, as-is. Never read: the inbox is the user's |

`audit {domain}` still snapshots every domain's board, but only reads settings, project files and
the inbox for the domains it scores. `audit all` reads them all, once.

## ▶️ Run

```
python {skill folder}/scripts/check_structure.py --rules rules.yaml --rulebook rulebook.md \
    --snapshot snapshot.json [--domain D] --out out
```

Needs PyYAML (`pip install pyyaml` if missing). Exit codes: `0` scored · `2` an input broke its
contract (the message says which: fix the input, never score around it) · `3` replay mismatch.
