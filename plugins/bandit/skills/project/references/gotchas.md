# ⚠️ Gotchas

One line per real failure: what went wrong → what to do instead. Read once before onboarding or an audit.

- **2026-09-24 · Onboarding was split across three skills.** The user set up a project
  here, got `domain: none`, and then bandit:notes refused to create anything and the board was
  never set. → Onboarding is one run of this skill: notes, board and settings rows in one
  proposal (**🚀 Onboarding** (`references/onboard.md`)).
- **2026-09-27 · The Personal onboarding audit skipped the board step.** The chat ran its own
  `get_context` boards check instead of loading bandit:tasks' onboard step, never opened the structure
  rulebook, and wrote "no board rows, scope is already correct". The board names were wrong. →
  Step 3 is loaded and run, never swapped for a quick check (**🚀 Onboarding** (`references/onboard.md`) rules); structure is
  judged by `/bandit:audit check`.
- **2026-09-29 · Audits flagged problems and stopped.** Findings sat in a list below the proposal,
  and the audit asked "want me to generate an updated version?" instead of building it. → Findings
  come fixed: every finding is a row in the one proposal, and the updated version is built
  straight away (`references/audit.md`, Step 5).
- **2026-09-29 · A project in Claude Code had no way to reach its reference doc.** Detail moved out
  of the instructions was lost there. → The `## 🖥️ Environment` names the reference doc's home
  (`references/reference-template.md` → Environment).
- **2026-09-29 · An onboarding reached its last step at 1,389 words.** The budget was only a
  warning at the end, so a full run finished on instructions that were already over it. → The
  length gate runs first, and an over-budget trim is row 1 (**🚀 Onboarding** (`references/onboard.md`) rules).
- **2026-11-21 · Two copies of one project's settings drifted, and keeping them in step cost more
  than the work.** A project had Claude.ai instructions, a Claude Code copy and a settings folder
  holding both. → One configuration: a project runs on one surface and has one instructions file
  (`references/surfaces.md`).
- **2026-11-22 · A project's settings named a board that had been renamed, and nothing said so
  until a sprint filed its papers in the wrong place.** → The Project Context is checked live on
  every run: a `board:` or `domain:` that does not resolve is a row, never a guess.
