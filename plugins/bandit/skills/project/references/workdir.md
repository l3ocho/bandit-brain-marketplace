# 📁 Working folder — the S12 guard for a workflow agent in Claude Code

> Read when onboarding or auditing a project that runs in Claude Code without `dev: true` (a
> workflow agent, `references/surfaces.md`), and for a bandit:audit S12 row. Holds the layout, the
> guard (`scripts/workdir.py` in this skill), its settings, the Environment line, and the rollout.
> The rule itself is S12 in bandit:audit `references/structure-rulebook.md`. Hook format checked
> against the Claude Code hooks docs (https://code.claude.com/docs/en/hooks) on 2026-09-29.

## 🗂️ Layout

The project's working folder is the folder Claude Code runs from (`$CLAUDE_PROJECT_DIR`).

| Path | Holds |
|---|---|
| `CLAUDE.md`, `.claude/` | Instructions and settings, written by this skill's approved rows |
| `repos/` | Read-only clones |
| `work/{prefix}-{task}/` | One folder per board task: drafts, SQL, scripts, analyses |
| `data/{prefix}-{task}/` | That task's data files. Purged on close, never archived |
| `scratch/` | Throwaway. Deleted after 7 days, as an approved row |
| `_closed/{prefix}-{task}/` | Closed work, moved there by `/bandit:tasks done`. Deleted after 30 days, as an approved row |
| `_backup/` | Settings rollback copies only, flat: `CLAUDE.md.{version}`, `settings.json.{version}`, `workdir.py.{version}`. No clock; deleted only by an approved row. A changelog's undo path points here |
| `{folder}/` with its own `CLAUDE.md` | A hosted project: its own settings apply, the guard leaves it alone |

- `{prefix}` is the Project Context `prefix:`. `{task}` is the board task's title in kebab-case
  (`sw-churn-report`). No task IDs.
- **Data files** (`.csv .tsv .xls .xlsx .xlsm .parquet .feather .jsonl .ndjson .db .sqlite
  .sqlite3 .duckdb`) go only in `data/{prefix}-{task}/`. `.json` isn't one: config files are.
- **Superseded work** stays in its task folder, `work/{prefix}-{task}/superseded/`, and leaves with
  it at close. Never `_backup/`. A delete the user asks for runs on their word.
- Nothing else at the root. Files outside this folder (a host changelog, `~/.ssh/config`) aren't
  the guard's business: the project's own rules cover them.

## 🧭 How the guard works

| Piece | Does |
|---|---|
| `PreToolUse` hook on `Write\|Edit\|NotebookEdit` → `workdir.py guard` | Exit 2 blocks a write outside the layout, a badly named task folder, or a data file outside `data/`, with the reason Claude sees. Settings (`CLAUDE.md`, `.claude/`) and hosted projects pass |
| `\|\| exit 2` after the command | `python3` missing or the script failing → the write is refused, never waved through |
| `SessionStart` hook → `workdir.py manifest` | Writes `.claude/workdir-manifest.json` (paths, dates, counts; never contents, never a file name under `data/`), and prints a one-line count. The manifest stays on the machine; bandit:audit reads it there |
| `permissions.allow` | `Edit(/work/**)`, `Edit(/data/**)`, `Edit(/scratch/**)`: allowed writes don't prompt. They never widen the guard: exit 2 wins over allow rules |

**What it can't catch:** a script that writes files itself, or Bash (`mv`, `>`, `tee`). The
manifest shows those, and bandit:audit S12 turns them into fix rows. Content isn't scanned:
customer names pasted into a `.md` draft stay a prose rule.

## 📦 The change (rows of the proposal, written into the folder on approval)

**1. `.claude/hooks/workdir.py`** — this skill's `scripts/workdir.py`, byte for byte.
Never edited per project: `domain`, `project` and `prefix` come from the folder's `CLAUDE.md`.
bandit:audit compares its hash with `s12.hook_sha12` in `structure-rules.yaml`.

**2. `.claude/settings.json`** — add to what's there (keep every existing `permissions` rule
and hook):

```json
{
  "permissions": {
    "allow": ["Edit(/work/**)", "Edit(/data/**)", "Edit(/scratch/**)"]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|NotebookEdit",
        "hooks": [
          {"type": "command",
           "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/workdir.py\" guard || exit 2"}
        ]
      }
    ],
    "SessionStart": [
      {
        "hooks": [
          {"type": "command",
           "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/workdir.py\" manifest"}
        ]
      }
    ]
  }
}
```

**3. The `## 🖥️ Environment`** of `CLAUDE.md` gets this line:

```
- **Working folder** (S12, enforced by `.claude/hooks/workdir.py`): `work/{prefix}-{task}/` per board task, data files only in `data/{prefix}-{task}/`, throwaway in `scratch/`. `/bandit:tasks done` closes a task's folders.
```

Written with the project's real `prefix`.

**4. The layout folders:** `work/`, `data/`, `scratch/`, `_closed/`, `_backup/`, one row. Then
existing loose files move into task folders (the first manifest lists them), each move a row, and
the project's notes are searched for every old path moved (through bandit:notes), proposing the
note edits.

Every item is a row of one proposal, with the instructions' version bump. The length gate
(`references/onboard.md` rules) runs first: the Environment line counts toward the budget.

## 🔁 Rollout to an existing project

A targeted update with the change above. The first `SessionStart` after it writes the manifest;
the next `/bandit:audit check` in that folder scores S12 from it. Until a manifest exists, S12 is
**unchecked** for that project.
