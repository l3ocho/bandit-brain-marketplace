# 🤝 Other skills and chats writing a note

> Read when another skill, or a chat, writes a note: who writes what, as kinds and places, and the exceptions to the inbox rule.

## 🤝 Other skills and chats writing a note

Any note created by another skill or in a chat follows the same rules, whichever storage the
project uses (`references/model.md` → Which storage). It asks this skill for the note's kind and
place and names no storage of its own. It is created as a **new** note in the Inbox (create without
a duplicate first), carries its kind, its `summary` and the kind's fields (Part 2 §5), follows the
body shape in Part 2 §12, and waits there for the user's review. Skills never edit an existing note
in the Inbox, except their own draft from this conversation on the user's explicit request
(`references/model.md` → *The inbox is the user's*).

How the same note is written in each storage:

| | App's Notes (`references/storage-app.md`) | Vault (`references/storage-vault.md`) |
|---|---|---|
| A draft for review | `notes_create` on its board, status `inbox` | A new file in `{Domain}/_inbox/`, `status: triaged`, with `file-to:` naming its home |
| Its place | A board, and a column of it (Places) | A folder (`references/conventions-vault.md` §1) |
| Written straight in | Filed with `notes_file` in the same step | Created in its folder |

**Who writes what:**

| Skill | Kind | Place |
|---|---|---|
| bandit:minutes | `minutes` | Inbox first, then the domain's meetings place: the domain's workflow board (app) or `Meetings/` (vault) |
| bandit:plan (both modes) | `reference`, or `plan` on a dev project | **Written straight in**, not to the Inbox, because they're worked on across many sessions: the project's board (app) or `Projects/{slug}/`, its `planning/` on a project with sprint folders (vault, Part 2 §1 → Sprint project root). Still Part 2: kind, status, summary; in the vault create fail-closed and edit only with the etag |
| bandit-dev:sprint | the sprint's records (plan, execution prompt, ledger, report, briefs) | **Written straight in**, for the same reason: the project's board with the tag `sprint-{name}` (app) or `Projects/{slug}/sprint-{name}/` (vault, Part 2 §1 → Sprint folders) |
| bandit:tasks (dev projects) | a card's `brief` and `plan` | Inbox-first, then its card: linked to it (app) or the project's folder with `board-task` (vault). Part 2 §13 |

- **Settings files stay in the vault**, whichever storage holds the notes. **bandit:project** owns
  the files inside `Claude/ai-{slug}/`. Those files start with an HTML metadata comment on line 1,
  so they are **exempt from frontmatter**; never add YAML to them. The folder path is derived from
  the Project Context: `MyNotes/{domain}/Claude/ai-{project}`. bandit:project also owns the
  **Claude Code twin** in `Claude/code-{slug}/`: its `CLAUDE.md`, `claude/settings.json` and
  `claude/hooks/workdir.py`, for any project without `dev: true`.
- **The working-folder manifest** (`Projects/{slug}/workdir-manifest.json`, structure rule S12) is
  written straight there by the twin's Claude Code session, asked by its `SessionStart` hook. Machine
  data for bandit:audit, not a note: no inbox, no frontmatter, create fail-closed, edit with the etag.
- **The dev mirror** is copied straight into `Claude/code-{slug}/` by the repo's `Stop` hook script,
  through the Nextcloud-synced folder (bandit:project `references/dev-mirror.md`). It's a settings
  copy, not a note: no inbox, no frontmatter, never edited by hand.
- **Leftovers.** A note used only to produce another (an inbox draft filed elsewhere, a superseded
  draft, an applied feedback note) is archived (Part 2 §7 in the vault, status `archived` in the
  app), or deleted on the user's word, **in the same step that consumed it**, and only on proof: the
  successor exists and was read. Never because a note looks done or its card is missing; unsure →
  it stays.
- **bandit:tasks** owns the task vocabulary. Notes reuse it verbatim (kind, handler, lane as the
  bare value) and name their card: the card link in the app, `board-task` in the vault. This skill
  never writes to the board.
- **Dev projects** (`dev: true` in the Project Context): plan notes and the WBS card links exist
  **only** there (Part 2 §13). Without the flag nothing changes. Plan notes go **inbox-first**, like
  every skill-written note, except sprint records, which are written straight in. Because a plan
  exists only on dev projects, `file` and `lint` apply the plan-note rules to any plan note,
  whichever project they run from (usually the domain workflow project).
- **Lookup for bandit:tasks: the notes linked to this card.** App: `notes_list` of the card's board;
  the notes whose `cards` hold the card are its notes, a plan and a brief one each. Vault: bandit:tasks
  asks whether a plan-note **filename** is filed; this skill answers with
  `nc_webdav_find_by_name(pattern="{filename}", scope="MyNotes/{Domain}")` and checks the match sits
  in `Projects/{slug}/`, its `planning/` or one of its sprint folders. Places and paths stay here;
  bandit:tasks never restates them.
