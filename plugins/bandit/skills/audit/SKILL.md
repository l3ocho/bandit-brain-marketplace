---
name: "audit"
description: "Audits Leo's domain and project structure across Claude.ai, the MyNotes vault and the BanditBrains board against the structure rulebook (references/structure-rulebook.md), scored by a script, never by hand. Invoked as /bandit:audit followed by a command: check (run inside a Claude.ai project: stamps its running instructions version and scores that project), audit {domain} or audit all (one snapshot of board, vault and stamps, scored by scripts/check_structure.py into a replayable report per domain with numbered fix rows, run through their owner skills on approval) and close (replays, then archives a finished report). Use when Leo says \"audit the BanditLabs domain\", \"audit all domains\", \"check my project structure\", \"is this project in sync with the vault\", \"domain audit\", \"do my projects follow the pattern\". Do NOT use for auditing a skill (bandit-maker:skill), rewriting one project's instructions (bandit:project), board hygiene (bandit:tasks audit) or note lint (bandit:notes lint)."
---

# 🧱 Bandit Audit

Keeps Leo's domains running on one pattern. It checks, scores and **fixes**. Every finding comes
back as a numbered fix row in the same report, and the approved rows run through the skill that owns
that thing. It never makes a change with its own calls.

**Findings come fixed.** A problem found and left without a fix row is a failed audit. Only a real
either/or (two valid fixes) goes back as a question, inside the same proposal, recommended option first.

**The standard lives in `references/structure-rulebook.md`** (this skill), and as data in
`references/structure-rules.yaml` next to it. This skill holds the procedure, not the rules.

**Scoring is the script's.** `scripts/check_structure.py` scores S1–S16 from one snapshot of the
board, the vault (settings, surfaces, project files and their frontmatter), the stamps and the
Claude Code working-folder manifests. Never score, count or reword a result by hand. No script run → no
report. The model's jobs: build the snapshot (`references/snapshot.md`), run the script, show its
output as printed, and run approved rows through their owners.

---

## 🧭 Router

`/bandit:audit <command>`. No command → offer the table as a numbered list and ask.

| Command | Run from | Does | Reference |
|---|---|---|---|
| `check` | Inside the project being checked | Reads this project's running `**Version:**` and Project Context, compares with the vault, proposes one stamp row, then scores this project with the script | `references/self-check.md` |
| `audit {domain}` · `audit all` | Anywhere | Builds one snapshot, runs the script, shows its report unedited; writes report + snapshot on approval. `all` = every domain from the same snapshot | `references/domain-audit.md`, `references/snapshot.md` |
| `close {domain}` | Anywhere | Replays the live report; valid and its fixes done → moves it and its snapshot to the domain `_archive/` | `references/domain-audit.md` → Close |

Read the reference **before acting**. Natural language works too: "is this project in sync" → `check`.

---

## 🗄️ Where things live

| Thing | Path | Written by |
|---|---|---|
| Rulebook | `references/structure-rulebook.md` (this skill) | The bandit-brain-marketplace repo. Read-only here |
| Rules as data | `references/structure-rules.yaml` (this skill) | The bandit-brain-marketplace repo, with the rulebook. Read-only here |
| Scorer | `scripts/check_structure.py` (this skill) | The bandit-brain-marketplace repo |
| Stamp ledger | `MyNotes/BanditLabs/Projects/bandit-brain-marketplace/.audit/stamps.json` | `check`, on approval |
| Domain report + its snapshot | `MyNotes/{Domain}/Projects/{workflow-project}/audit-{YYYY-MM-DD}.md` and `.snapshot.json` | `audit`, on approval |
| Archived report + snapshot | `MyNotes/{Domain}/_archive/Projects/{workflow-project}/` | `close`, on approval |

**Settings means settings.** `Claude/ai-*` folders hold only a project's instructions and reference doc — never project logs, working notes, decision journals, discussion records, reports, briefs, plans or drafts. All of those are work output. A report lives in the workflow project's own folder, `Projects/{workflow-project}/` (`{workflow-project}` = the `project:` key of the domain's workflow project).

**Repos are scored through the vault.** A repo's `CLAUDE.md` + `.claude/` are scored through its
mirror in `code-{slug}/`, not the lagging GitHub copy. Comparing a repo's Project Context with Claude.ai
stays in Claude Code.

**Why a stamp ledger:** from outside a project, nothing can read what Claude.ai is actually running.
Only the project itself can see its own instructions. So each project stamps its version with
`check`, and `audit` compares stamps with the vault. No stamp means **unchecked**, never a guess.

---

## 🔧 Who fixes what

The report assigns every fix row to an owner. This skill doesn't do the fix; it names the owner and
the exact target.

| Fix | Owner |
|---|---|
| Rename or retype a board, rename a board folder | `bandit:tasks` |
| Missing dev lanes or `lane/*` / `stage/*` tags (S9) | `bandit:tasks` **dev board shape** procedure |
| Dev lanes on a board without `dev: true` (S9) | One row, two options, recommended first: remove the lanes (`bandit:tasks`) or onboard the project as dev (`bandit:project`). Leo picks at the same approval |
| An invalid `dev:` value (S4) | `bandit:project` targeted update |
| Move old settings versions into `_archive/Claude/ai-{slug}/` (S7) | `bandit:notes archive` |
| Create a missing folder | `bandit:notes` |
| Project Context keys, instructions version, re-paste into Claude.ai | `bandit:project` targeted update (paste: Leo) |
| Rename a Claude.ai project | Leo, by hand |
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

## ▶️ Executing approved rows

Leo approves rows; this skill runs them **through their owners**. It loads the owner skill and
follows that skill's own procedure for the row. It never renames, moves, retypes or writes
instructions with its own calls. Its own writes are the report and the ledger, nothing else.

**Linked rows.** A board or board-folder rename breaks every Project Context whose `board:` line
names the old name: readers stop when the name no longer resolves. So when building fix rows,
search every project's `board:` line for the old name. Each match gets a second row right after
the rename: `bandit:project` targeted update of that project, `board:` → the new name.

- A pair is approved together. Leo approves one row of a pair and not the other → ask before
  running either.
- **Order:** vault rows (`bandit:notes`) → settings rows (`bandit:project`) → board rows
  (`bandit:tasks`). The new instructions version exists before the old board name stops
  resolving.
- A row whose owner refuses or fails → skip the rows that depend on it, and report both.
- **S12 layout rows** live on the Claude Code machine, out of reach here. Hand the approved ones
  over as one block for that project's Claude Code session, after the other rows; nothing is
  deleted there without the approval they already carry. The block ends by searching
  `Projects/{slug}/` for every path it moved and proposing the note edits.

**Close the run** with one result line per row, then what Leo still owes, per project:
*paste `{prefix}-instructions-v{N}` into {Claude.ai name}, then run `/bandit:audit check` there.
Until the paste, bandit:tasks stops in that project.*

---

## ✍️ Safe writes

- **New files omit `if_match`** (fail closed). **Edits send the bare-hex etag** from the read (strip
  `W/`, `"` and `-gzip`). Never `if_match: "*"`.
- **Resolve names live** (`list_projects`, `list_folders`, directory listings). No stored IDs.
- **Write only what Leo approved, by exact path.** Nothing on the side, even if the rulebook says it
  should exist.
- Nothing is deleted, ever. `close` moves; it never deletes.

---

## ⚠️ Gotchas

- **2026-09-27 · The Personal audit skipped the board step and scored against the template.** The
  chat ran its own quick `list_projects` check instead of bandit:tasks' onboard step, never opened
  the rulebook, and wrote "scope is already correct". → Scoring is the script's: build the
  snapshot, run `check_structure.py`, show its output. A report without a snapshot hash in its
  footer is invalid.
- **2026-09-27 · The Family audit left the project half-renamed.** Leo approved the rows, and the
  chat renamed the board `Familyflow` → `Family - wkflw` and created the report folder with its
  own calls. The Project Context still said `board: Familyflow`, so bandit:tasks stopped in that
  project, and the fix was left as "run `/bandit:project` later". → Approved rows run through
  their owners, and a rename is linked to its `board:` update (**▶️ Executing approved rows**).
- **2026-09-29 · Audits flagged problems and left them unfixed.** Anything the script didn't
  cover went into a Notes list with no fix, and S9 came back as "Leo decides", so every audit
  needed another run. → Findings come fixed: every finding is a numbered fix row with its owner
  and exact target, approved with the rest (`references/domain-audit.md` → Extra fix rows).
- **2026-09-29 · `check` said the rules were missing after they'd been written.** It reused the
  files it had read earlier in the chat and refused to score, twice. → Every run re-reads
  `rules.yaml`, `rulebook.md` (this skill's `references/`) and the snapshot inputs from the vault, never from earlier in the chat.
- **2026-09-30 · S11 dated the CS Notes mirror from GitHub, which lagged the repo by a month.** →
  S11 scores the hook, the script and the files only; the snapshot's `repo` is always `null`.

---

## 🚫 Never

- Leave a finding without a fix row, or list a problem as a note and walk away.
- Fix anything with its own calls: rename, move, retype, edit instructions or tasks. An approved
  row runs only through its owner's procedure (**▶️ Executing approved rows**).
- Run half of a linked pair, or run a board rename before its settings row.
- Guess a Claude.ai name or version. No stamp → **unchecked**.
- Restate the rulebook's rules. Read the file; quote rule numbers.
- Score, count or edit a result by hand, or write a report the script didn't print byte for byte.
- Act on a report that fails replay.
- Audit task placement, or boards with a `systemOwner`: the rulebook exempts both.
- Move a version file while S5 is **unchecked** for that project.
- Write anything into a `Claude/ai-*` settings folder: settings folders hold settings only — never project logs, working notes, decision journals, discussion records, reports, briefs, plans or drafts.
- Write to `.obsidian/`, a skill mirror folder, or anywhere outside the paths above.
