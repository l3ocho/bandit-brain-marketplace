# ⚠️ Gotchas

One line per real failure: what went wrong → what to do instead. Read once before a session's first vault write.

- **2026-09-24 · "create it" ran past the proposal.** The user said "create it" to a 5-row proposal and
  the chat also created `_inbox/`, `_templates/`, `_archive/` and `_attachments/`, which were only
  listed as findings. → Execute only the approved rows. Every finding is a row of its own.
- **2026-09-24 · Onboarding left the domain half-built.** Onboarding the Personal workflow project
  created `Claude/ai-personal/` but not the missing `_templates/`, `_archive/`, `_attachments/` or
  README, because they were only listed as findings. → Missing core structure is always a row in
  onboarding (create only).
- **2026-09-29 · Findings were flagged and never fixed.** Onboarding and lint listed legacy
  folders, stray files and breaches as "findings" or "for the workflow project", and nothing
  fixed them without another run. → Findings come fixed: every one is a numbered fix row in the
  same proposal (`domain` when outside the scope), approved with the rest.
- **2026-09-24 · A waiting proposal looked like a failure.** The user ran the command, got a proposal,
  and saw nothing created. → End every proposal with the "nothing happens until you answer" line.
- **2026-09-24 · Project onboarding was split across three skills.** `init` run from a project
  chat was silently swapped for a project onboard. → Onboarding runs from bandit:project, which
  runs this skill's *Onboarding rows*. Typed directly in a project chat, `init` or `onboard` says
  which command applies and why, and points to bandit:project for a new project.
- **2026-09-24 · A `domain: none` stop gave no fix.** → Name the setting and the fix: a
  bandit:project targeted update in that project sets `domain:`. This skill never edits
  project instructions.
- **2026-09-25 · the user asked to amend a draft a skill had just written.** The rules had no path for
  this, and the edit went ahead on their explicit ask. → A triaged, skill-written draft from this
  conversation can be edited on the user's explicit request (*The inbox is the user's*).
- **2026-09-25 · Workflow projects had no project folder.** The old rule gave `type: workflow`
  settings only, so a workflow project had nowhere to keep its own docs. → Every project, workflow
  included, gets both `Claude/ai-{slug}/` and `Projects/{slug}/` with its hub note.
- **2026-09-30 · Content migrated from a repo had no `source:` value to take.** → `migrated`, with
  the original location in the body's first line (conventions §5).
- **2026-10-07 · A colon in a `summary` broke a note.** Obsidian opened it with invalid
  properties. → Quote any value that YAML would misread (conventions §5 → YAML style).
- **2026-10-08 · Two notes were archived on a guess.** They looked done. → Archive a consumed note
  only on proof that its successor exists and was read (*Other skills* → Leftovers).
