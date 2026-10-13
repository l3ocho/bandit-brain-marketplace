# ⚠️ Gotchas

One line per real failure: what went wrong → what to do instead. Read once at the start of a session that writes to the board.

- **2026-09-24 · Commands were bangs (`!triage`).** They're now `/bandit:tasks triage`, the same
  form as every other skill. → A `!command` typed from habit means the same command: run it.
- **2026-09-27 · Said a Sun–Thu repeat wasn't possible.** `capture.md` listed the rule vocabulary
  without `days`, which the tool supports on weekly rules. → Check the tool's `rule` schema before
  calling a rule impossible; the schema wins over this skill's table (`references/capture.md`).
- **2026-09-29 · Audit flagged problems and left them.** Unreadable rules were "flag, do not
  rewrite", and shape problems were reported with no fix. → Findings come fixed: every audit
  finding is a numbered fix row with the exact call, approved in one answer (`references/audit.md`).
- **2026-09-30 · Onboarding a real dev repo found `dev.md` out of step with it.** B1 said "one PR"
  where the repo lands by merge, an incident waited for the midnight run to reach Assigned, no
  record had a home, and `plan-tech` could overwrite a recorded branch. → Landing, not PR (B1);
  Assigned set explicitly; homes read from the repo (`references/dev-workflow.md` → Record homes);
  `plan-tech` reads first.
- **2026-10-05 · Card descriptions came out unreadable.** Three cards held escaped
  `&lt;br/&gt;`, shown as literal text; the skill only said "simple HTML". → Write only the tags in
  **📝 Card descriptions**, and read every description back after the write.
- **2026-10-06 · Dev cards drifted from the app's lane template.** The skill allowed only `<h2>`
  and said *Open questions for Claude Code*; the template uses `<h3>` and *Open questions*, and the
  column rule never said module or page. → Start every card from `get_lane_template`, fill
  Card fields in full, place it by the column rule (`references/dev.md`).
- **2026-10-06 · A tag write dropped tags.** `set_task_tags` replaces the whole set, so writing one
  tag wiped the rest. → `get_task` first and send the full merged set, every time (**🏷️ Tags**).
- **2026-10-06 · Sub-tasks came out in reverse order.** They were added with parallel
  `add_subtask` calls, and later landed at the top, reversed, even one at a time. → After any
  sub-task write, `reorder_subtasks` with the full order and read it back (**☑️ Sub-tasks**).
- **2026-10-06 · Two cards still showed raw tags.** They opened with a bare `<b>`; the app
  reads a description as rich text only when it opens and closes with a block tag, so it showed
  every tag as text. The 10-05 rule allowed a top-level `<b>` and its read-back never tested the
  ends. → Every description opens and closes with a block tag; the read-back checks both ends.
- **2026-10-08 · Wave 2 cards were refused Doing.** Their blockers sat in Stand By awaiting Leo's
  test, and the skill said only "complete"; the board refused with `BLOCKED_BY_INCOMPLETE_TASK`. →
  Stand By is not complete: the Doing gate holds until the app lets Stand By count (`references/execution.md`).
- **2026-10-06 · `spec` parked obvious questions and skipped the brief.** A card (per-user theme) left
  two Open questions with obvious answers (keep or reset the current theme; do other settings share
  the bug) and ended "no brief written, want one?". → A point with a sensible default is decided
  and written under Decisions (the check for other settings goes in Scope in). Open questions hold
  only real forks that change scope, each with options and a recommendation, or `None`. Every
  `spec` step runs, the brief (step 6) included: never skip a required step and offer it after.
