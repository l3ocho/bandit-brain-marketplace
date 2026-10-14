# ⚠️ Gotchas

One line per real failure: what went wrong → what to do instead. Read once before a `check` or an `audit`.

- **2026-09-27 · The Personal audit skipped the board step and scored against the template.** The
  chat ran its own quick `list_projects` check instead of bandit:tasks' onboard step, never opened
  the rulebook, and wrote "scope is already correct". → Scoring is the script's: build the
  snapshot, run `check_structure.py`, show its output. A report without a snapshot hash in its
  footer is invalid.
- **2026-09-27 · The Family audit left the project half-renamed.** The user approved the rows, and the
  chat renamed the board `Familyflow` → `Family - wkflw` and created the report folder with its
  own calls. The Project Context still said `board: Familyflow`, so bandit:tasks stopped in that
  project, and the fix was left as "run `/bandit:project` later". → Approved rows run through
  their owners, and a rename is linked to its `board:` update (**▶️ Executing approved rows**).
- **2026-09-29 · Audits flagged problems and left them unfixed.** Anything the script didn't
  cover went into a Notes list with no fix, and S9 came back as "the user decides", so every audit
  needed another run. → Findings come fixed: every finding is a numbered fix row with its owner
  and exact target, approved with the rest (`references/domain-audit.md` → Extra fix rows).
- **2026-09-29 · `check` said the rules were missing after they'd been written.** It reused the
  files it had read earlier in the chat and refused to score, twice. → Every run re-reads
  `rules.yaml`, `rulebook.md` (this skill's `references/`) and the snapshot inputs from the vault, never from earlier in the chat.
- **2026-09-30 · S11 dated the Home Reno mirror from GitHub, which lagged the repo by a month.** →
  S11 scores the hook, the script and the files only; the snapshot's `repo` is always `null`.
