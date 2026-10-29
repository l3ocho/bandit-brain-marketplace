# 🔧 Fix rows: owners and execution

> Read when building fix rows and before running them: who owns each fix, and how linked rows run.

## 🔧 Who fixes what

The report assigns every fix row to an owner. This skill doesn't do the fix; it names the owner and
the exact target.

| Fix | Owner |
|---|---|
| Rename a board, switch its profile (its creator only), rename a board folder | `bandit:tasks` |
| Missing dev lanes or `lane/*` / `stage/*` tags (S9) | `bandit:tasks` **dev board shape** procedure |
| Dev lanes on a board without `dev: true` (S9) | One row, two options, recommended first: remove the lanes (`bandit:tasks`) or onboard the project as dev (`bandit:project`). The recommended one runs; the report names the other |
| An invalid `dev:` value (S4) | `bandit:project` targeted update |
| Move old settings versions into `_archive/Claude/ai-{slug}/` (S7) | `bandit:notes archive` |
| Create a missing folder | `bandit:notes` |
| Project Context keys, instructions version, re-paste into Claude.ai | `bandit:project` targeted update (paste: the user) |
| Rename a Claude.ai project | The user, by hand |
| Claude Code twin (any project without `dev: true`) missing, behind or its core differs (S10) | `bandit:project` (Claude Code twin) |
| Dev mirror: hook or script missing (S11) | `bandit:project` (dev mirror) |
| `code-{slug}/` folder missing (S11) | `bandit:notes` |
| Working-folder guard missing or outdated (S12) | `bandit:project` (`references/workdir.md`) |
| Working-folder layout rows (S12): move, rename, delete on the Claude Code machine | That project's Claude Code session: the rows are handed over, targets `{slug}:{path}` |
| A sprint brief outside its sprint folder (S13), a sprint project's root (S16) | `bandit:notes` (a move) |
| A filename twice in `Projects/` and `_inbox/` (S14) | `bandit:notes`: archive the consumed copy on proof (its Leftovers rule), or rename one |
| Frontmatter that doesn't parse (S15) | `bandit:notes` (quote the value, its YAML style) |

**The local checker stays.** bandit-dev:sprint's `scripts/check_sprint.py` enforces the same vault
rules at write time, as a `Stop` hook (rules SP2–SP5, citing S13–S16). This skill's script needs a
snapshot and can't run from a hook, so it never absorbs that checker; it scores the same rules at
audit time.

---

## ▶️ Running the rows

Every row runs in the same turn, no approval asked; this skill runs them **through their owners**,
and the owner doesn't ask again. It loads the owner skill and
follows that skill's own procedure for the row. It never renames, moves, switches profiles or writes
instructions with its own calls. Its own writes are the report and the ledger, nothing else.

**Linked rows.** A board or board-folder rename breaks every Project Context whose `board:` line
names the old name: readers stop when the name no longer resolves. So when building fix rows,
search every project's `board:` line for the old name. Each match gets a second row right after
the rename: `bandit:project` targeted update of that project, `board:` → the new name.

- A pair runs together, or not at all.
- **Order:** vault rows (`bandit:notes`) → settings rows (`bandit:project`) → board rows
  (`bandit:tasks`). The new instructions version exists before the old board name stops
  resolving.
- A row whose owner refuses or fails → skip the rows that depend on it, and report both.
- **S12 layout rows** live on the Claude Code machine, out of reach here. Hand them over as one
  block for that project's Claude Code session, after the other rows. The block says it runs as
  written, deletes included, with no question; it re-lists each folder first and skips any path
  that changed. It ends by searching `Projects/{slug}/` for every path it moved and making the
  note edits.

**Close the run** with one result line per row, then what the user still owes, per project:
*paste `{prefix}-instructions-v{N}` into {Claude.ai name}, then run `/bandit:audit check` there.
Until the paste, bandit:tasks stops in that project.*
