# 🔧 Fix rows: owners and execution

> Read when building fix rows and before running them: who owns each fix, and how linked rows run.

## 🔧 Who fixes what

The report assigns every fix row to an owner. This skill doesn't do the fix; it names the owner and
the exact target.

| Fix | Owner | In reach of |
|---|---|---|
| Rename a board, switch its profile (its creator only), rename a board folder | `bandit:tasks` | Any chat |
| Missing dev lanes or `lane/*` / `stage/*` tags (S9) | `bandit:tasks` **dev board shape** procedure | Any chat |
| Dev lanes on a board without `dev: true` (S9) | One row, two options, recommended first: remove the lanes (`bandit:tasks`) or onboard the project as dev (`bandit:project`, in the project). The recommended one runs; the report names the other | Any chat (the first option) |
| A sprint brief without the tag `sprint-{name}` (S13) | `bandit:notes`, a field fix as its `lint` rows make (`notes_set_fields`, the brief's other tags kept; owner key `brief_tag`) | Any chat |
| Project Context keys or values (S4), a `board:` line (S3, S4) | `bandit:project`, by `/bandit:project audit` in that project | That project's chat only |
| Working-folder guard missing or outdated (S12) | `bandit:project` (`references/workdir.md` there), by `/bandit:project audit` in that project | That project's chat only |
| Working-folder layout rows (S12): move, rename, delete in its folder | That project's Claude Code session: the rows are handed over, targets `{slug}:{path}` | That project's chat only |
| Rename a Claude.ai project (S1, S2) | The user, by hand | The user |

Retired rules (rulebook → Retired) make no rows.

**The local checker stays separate.** bandit-dev:sprint's `scripts/check_sprint.py` checks a
sprint's papers at write time, as a `Stop` hook, from the project's notes file: by title, tag and
status (its SP2 is that file's form of S13). This skill's script needs a snapshot and can't run
from a hook, so it never absorbs that checker; it scores S13 at audit time.

---

## ▶️ Running the rows

Every row in reach runs in the same turn, no approval asked; this skill runs them **through their
owners**, and the owner doesn't ask again. It loads the owner skill and follows that skill's own
procedure for the row. It never renames, moves, switches profiles or writes instructions with its
own calls. Its own writes are the report, the snapshot and the stamp, nothing else.

**In reach.** `check` runs inside the project, so every row of that project is in reach. `audit`
runs from one folder for a whole domain: board and notes rows are in reach; a row that changes
another project's instructions or folder is not, and becomes a close-out line.

**Linked rows.** A board or board-folder rename breaks every Project Context whose `board:` line
names the old name: readers stop when the name no longer resolves. So when building fix rows,
search every stamp's `board:` line for the old name. Each match gets a second row right after
the rename: that project's `board:` → the new name.

- A pair runs together, or not at all: a rename whose second row is out of reach is **not run**
  from `audit`. It is handed over with its pair: the project's chat fixes its `board:` line and
  renames the board in the same run.
- **Order:** notes rows (`bandit:notes`) → settings rows (`bandit:project`) → board rows
  (`bandit:tasks`). The new instructions exist before the old board name stops resolving.
- A row whose owner refuses or fails → skip the rows that depend on it, and report both.
- **S12 layout rows** run in the project's Claude Code session, as one block after the other rows.
  The block says it runs as written, deletes included, with no question; it re-lists each folder
  first and skips any path that changed. It ends by searching the project's notes (through
  bandit:notes) for every path it moved and making the note edits.

**Close the run** with one result line per row, then what is still owed, per project:
*in {project}: run `/bandit:project audit` for {the change}, then `/bandit:audit check`. Until
then {what stays broken}.* On Claude.ai the same line ends with the paste: *paste the new
instructions, then run `/bandit:audit check` there.*
