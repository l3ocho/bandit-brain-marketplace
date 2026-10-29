# ⚠️ Gotchas

One line per real failure: what went wrong → what to do instead. Read once before onboarding or an audit.

- **2026-09-24 · Onboarding was split across three skills.** The user set up a project
  here, got `domain: none`, and then bandit:notes refused to create anything and the board was
  never set. → Onboarding is one run of this skill: vault, board and settings rows in one
  proposal (**🚀 Onboarding** (`references/onboard.md`)). `domain:` is never `none` when a vault is used.
- **2026-09-25 · Workflow projects had no project folder.** Onboarding showed only the settings
  path for `type: workflow`, so those projects had nowhere to keep their own docs. → Every
  project gets both paths; the vault rows come from bandit:notes, which owns that rule.
- **2026-09-25 · The reference doc reached the project only sometimes, and was shown in full in
  the chat.** → Always save it with **Project copy** (`references/output.md`) (`present_to_user: false`, one-line
  confirmation).
- **2026-09-27 · The Personal onboarding audit skipped the board step.** The chat ran its own
  `get_context` boards check instead of loading bandit:tasks' onboard step, never opened the structure
  rulebook, and wrote "no board rows, scope is already correct". The board names were wrong. →
  Step 3 is loaded and run, never swapped for a quick check (**🚀 Onboarding** (`references/onboard.md`) rules); structure is
  judged by `/bandit:audit check`.
- **2026-09-29 · Audits flagged problems and stopped.** Findings sat in a list below the proposal,
  and the audit asked "want me to generate an updated version?" instead of building it. → Findings
  come fixed: every finding is a row in the one proposal, and the updated version is built
  straight away (`references/audit.md`, Step 5).
- **2026-09-29 · The Claude Code twin had no way to reach the reference doc.** Only Claude.ai got a
  Project copy, so detail moved out of the instructions was lost on the Claude Code side. → The
  twin's Environment names the vault path of the reference doc (`references/project-context.md` → Claude Code twin).
- **2026-09-29 · Bandit CTO reached the Claude Code onboarding at 1,389 words.** The budget was
  only a warning at the end, so a full run finished on instructions that were already over it. →
  The length gate runs first, and an over-budget trim is row 1 (**🚀 Onboarding** (`references/onboard.md`) rules).
- **2026-09-29 · An update proposed archiving the live instructions.** The archive row came from the
  metadata's `instructions_version`, but the stamp said an older file was production. → S7 archive
  rows name production from the stamp ledger (`stamps.json`); no stamp → no archive row.
- **2026-09-30 · Onboarding installed the old dev-mirror script** from the lagging vault mirror and
  cheat-sheet prompt. → Hand over the installed `references/dev-mirror.md` (`references/project-context.md` → Dev mirror).
