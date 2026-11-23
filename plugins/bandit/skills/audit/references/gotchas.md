# ⚠️ Gotchas

One line per real failure: what went wrong → what to do instead. Read once before a `check` or an `audit`.

- **2026-09-27 · An audit skipped the board step and scored against the template.** The
  chat ran its own quick `get_context` boards check instead of bandit:tasks' onboard step, never opened
  the rulebook, and wrote "scope is already correct". → Scoring is the script's: build the
  snapshot, run `check_structure.py`, show its output. A report without a snapshot hash in its
  footer is invalid.
- **2026-09-27 · An audit left a project half-renamed.** The user approved the rows, and the
  chat renamed the board with its own calls. The Project Context still named the old board, so
  bandit:tasks stopped in that project, and the fix was left for "later". → Rows run through
  their owners, and a rename is linked to its `board:` update (**▶️ Running the rows**).
- **2026-09-29 · Audits flagged problems and left them unfixed.** Anything the script didn't
  cover went into a Notes list with no fix, and S9 came back as "the user decides", so every audit
  needed another run. → Findings come fixed: every finding is a numbered fix row with its owner
  and exact target, run with the rest (`references/domain-audit.md` → Extra fix rows).
- **2026-10-15 · An audit asked for a yes three times.** It asked which rows to run, then
  ran `check`, found one more row and asked again, for changes anyone can undo. → `check` and
  `audit` run every row in reach in the same turn, no question; an either/or runs the recommended option.
- **2026-09-29 · `check` said the rules were missing after they'd been written.** It reused the
  files it had read earlier in the chat and refused to score, twice. → Every run re-reads
  `rules.yaml`, `rulebook.md` (this skill's `references/`) and the snapshot inputs from their
  sources (the app, the board, the folder), never from earlier in the chat.
- **2026-11-22 · The audit knew a project only by a folder kept somewhere else.** When that place
  closed, it could score nothing. → A project is known by what it says about itself: its stamp,
  written from inside it. A board no stamp names is unchecked, and says which project to check in.
