# 🤝 Other skills and chats writing into MyNotes

> Read when another skill, or a chat, writes a note: who writes what, where, and the exceptions to the inbox rule.

## 🤝 Other skills and chats writing into MyNotes

Any note created by another skill or in a chat follows the same rules: it's created in
`{Domain}/_inbox/` as a **new** file, carries the standard frontmatter (including `summary`) with
`status: triaged`, follows the body shape in Part 2 §12, and may set `file-to:` so `/bandit:notes file`
(or the writing skill itself, after Leo confirms) can move it to its home in one step. Skills
create new notes in the inbox; they never edit an existing one there, except their own draft
from this conversation on Leo's explicit request (`references/model.md` → *The inbox is Leo's*).

- **bandit:project** owns the files inside `Claude/ai-{slug}/`. Those files start with an
  HTML metadata comment on line 1, so they are **exempt from frontmatter**; never add YAML to
  them. The folder path is derived from the Project Context: `MyNotes/{domain}/Claude/ai-{project}`.
  bandit:project also owns the **Claude Code twin** in `Claude/code-{slug}/`: its `CLAUDE.md`,
  `claude/settings.json` and `claude/hooks/workdir.py`, for any project without `dev: true`.
- **The working-folder manifest** (`Projects/{slug}/workdir-manifest.json`, structure rule S12) is
  written straight there by the twin's Claude Code session, asked by its `SessionStart` hook. Machine
  data for bandit:audit, not a note: no inbox, no frontmatter, create fail-closed, edit with the etag.
- **The dev mirror** is copied straight into `Claude/code-{slug}/` by the repo's `Stop` hook script,
  through the Nextcloud-synced folder (bandit:project `references/dev-mirror.md`). It's a settings
  copy, not a note: no inbox, no frontmatter, never edited by hand.
- **bandit:minutes** writes minutes to `_inbox` with `file-to: Meetings/`.
- **Sprint records** on dev projects (plan, execution prompt, ledger, report and the sprint's
  briefs) are written **straight into `Projects/{slug}/sprint-{name}/`** for the same reason as the
  planning documents below (Part 2 §1 → Sprint folders).
- **bandit:plan** (both modes) is the other exception to the inbox rule: it writes
  a project's planning documents (`{slug}-project-plan.md`, `{slug}-architecture.md`,
  `{slug}-wbs.md`) **straight into `Projects/{slug}/`**, or `Projects/{slug}/planning/` on a project
  with sprint folders (Part 2 §1 → Sprint project root), because they're worked on across many
  sessions. It asks this skill for the folder, still follow Part 2 (frontmatter, `status`, YAML
  style), create fail-closed and edit only with the etag. Drafts never go to `_inbox/`.
- **Leftovers.** A note used only to produce another (an inbox draft filed elsewhere, a superseded
  draft, an applied feedback note) is archived with the usual stamps (Part 2 §7), or deleted on
  Leo's word, **in the same step that consumed it**, and only on proof: the successor exists and was
  read. Never because a note looks done or its card is missing; unsure → it stays.
- **bandit:tasks** owns the task vocabulary. Frontmatter reuses it verbatim (`kind`, `handler`,
  `lane` as the bare value) and links tasks via `board-task`. This skill never writes to the board.
- **Dev projects** (`dev: true` in the Project Context): plan notes and the WBS card links exist
  **only** there (Part 2 §13). Without the flag nothing changes. Plan notes go **inbox-first**, like
  every skill-written note, except sprint records, which are written straight into the sprint
  folder. Because `type: plan` exists only on dev projects, `file` and `lint`
  apply the plan-note rules to any `type: plan` note, whichever project they run from (usually the
  domain workflow project).
- **Lookup for bandit:tasks.** bandit:tasks asks whether a plan-note **filename** is filed; this
  skill answers with `nc_webdav_find_by_name(pattern="{filename}", scope="MyNotes/{Domain}")` and
  checks the match sits in `Projects/{slug}/`, its `planning/` or one of its sprint folders. Vault paths stay here; bandit:tasks never restates them.
