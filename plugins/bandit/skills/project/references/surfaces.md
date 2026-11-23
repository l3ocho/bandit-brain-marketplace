# 🖥️ Surfaces: where a project runs, and what this skill may write

> Read first, on every run. A project has one configuration: this file says where it is, how the skill tells which surface it is on, what kind of agent the project is, and which files a row may touch.

## 🧭 Which surface

Decided by where the instructions were read from, never by which tools exist:

| The instructions are | Surface | Instructions file | Settings |
|---|---|---|---|
| A `CLAUDE.md` at the root of the folder the session runs from | **Claude Code** | That `CLAUDE.md` | `.claude/settings.json` (and `.claude/hooks/`) in the same folder |
| The project instructions shown as this chat's system prompt, with no such file | **Claude.ai** | The project's instructions field, which only the user can write | None this skill can reach |

No instructions on either → a new project: `references/interview.md`, on the surface this chat
is on.

**One configuration.** A project lives on one surface. This skill never builds a second copy of
the instructions for the other surface, never keeps two in step, and never asks which surface a
project "also" runs on. A user who wants a project on both runs this skill on each, as two
projects with two slugs.

## 🧩 Which kind of agent (Claude Code)

Read from the Project Context and the board, never asked twice:

| Kind | How it is told | What its folder needs |
|---|---|---|
| **Technical** | `dev: true`; its home board has profile Technical; the folder is a code repository | `CLAUDE.md` from the `dev` template; `.claude/settings.json` present; sprints and their gates come from `bandit-dev`, which the user installs. No working-folder guard: the repository's own layout rules apply |
| **Workflow agent** | No `dev` line (any `type:`); the folder holds working files, not a product's code | `CLAUDE.md` from the `workflow` or `product_service` template; `.claude/settings.json` with the working-folder guard's two hooks and three allow rules; `.claude/hooks/workdir.py`; the layout folders (`references/workdir.md`) |

A mismatch is a finding with its fix row: `dev: true` on a folder that is no repository, a
Technical home board with no `dev` line, a workflow agent with no guard. Say which kind the
project is in the first line of the report.

**Ready for Bandit Brain** (both kinds), each a row when it fails:

| Check | Row when it fails |
|---|---|
| `CLAUDE.md` exists at the root and carries the header lines (`**Version:**`, `**Last Updated:**`) and the Project Context | Create it, or add what is missing |
| The Project Context checks out live: `domain` is a board folder, `board` resolves (`get_context`) | The fix to the line, or bandit:tasks' board row |
| `.claude/settings.json` exists and parses | Create it with `{}` plus what the kind needs |
| The session reaches the board: `get_context` answers | No row this skill can run: say the Bandit Brain connector is not connected in this folder, and stop |
| No second instructions file for the same project (a leftover copy for another surface, a settings line at the top of `CLAUDE.md` naming another storage) | Remove the line; name the leftover copy for the user to retire |

## ✍️ What a row may write

| Surface | A row may | Never |
|---|---|---|
| Claude Code | Create or edit `CLAUDE.md`; create `.claude/settings.json` or **add** keys to it (hooks, allow rules), keeping every key it has; copy `.claude/hooks/workdir.py` from this skill; create the layout folders | Anything outside the folder; `settings.local.json`; the user's `~/.claude/`; removing or loosening what is there; a commit or a push |
| Claude.ai | Write the two reference notes on the project's board (`references/output.md`) | Write the instructions field: the full text is handed over and the user pastes it |

**Each row shows the change.** For an edit: the lines that go and the lines that come, or the
whole new text when most of it changes. For a settings merge: the keys added. The answer to the
proposal is the approval; a file is written only for an approved row, and read back after.

**A way back before every edit** of an existing file: a workflow agent's file is first copied to
`_backup/{name}.{version}` (`references/workdir.md` → Layout); a technical project's change is
left uncommitted in its repository, where git is the way back, and the report lists the changed
files for the project's own commit.
