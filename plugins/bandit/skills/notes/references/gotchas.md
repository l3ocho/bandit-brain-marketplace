# ⚠️ Gotchas

One line per real failure: what went wrong → what to do instead. Read once before a session's first note write.

- **2026-09-24 · "create it" ran past the proposal.** The user said "create it" to a 5-row proposal and
  the chat also created four things that were only listed as findings. → Execute only the approved
  rows. Every finding is a row of its own.
- **2026-09-29 · Findings were flagged and never fixed.** Onboarding and lint listed stray notes
  and breaches as "findings" or "for the workflow project", and nothing fixed them without another
  run. → Findings come fixed: every one is a numbered fix row in the same proposal (`domain` when
  outside the scope), approved with the rest.
- **2026-09-24 · A waiting proposal looked like a failure.** The user ran the command, got a proposal,
  and saw nothing created. → End every proposal with the "nothing happens until you answer" line.
- **2026-09-24 · Project onboarding was split across three skills.** → Onboarding runs from
  bandit:project, which runs this skill's *Onboarding rows*. Typed directly in a project chat,
  `onboard` says which command applies and why, and points to bandit:project for a new project.
- **2026-09-24 · A `domain: none` stop gave no fix.** → Name the setting and the fix:
  `/bandit:project audit` in that project sets `domain:`. This skill never edits project
  instructions.
- **2026-09-25 · the user asked to amend a draft a skill had just written.** The rules had no path for
  this, and the edit went ahead on their explicit ask. → A helper's own draft from this
  conversation can be edited on the user's explicit request (*The inbox is the user's*).
- **2026-09-30 · Content migrated from a repo had nowhere to say where it came from.** → Its first
  line says it: `Moved from {path} · created {date} · updated {date}` (`references/storage-app.md` →
  Fields).
- **2026-10-08 · Two notes were archived on a guess.** They looked done. → Archive a consumed note
  only on proof that its successor exists and was read (*Other skills* → Leftovers).
- **2026-11-21 · A brief's line on its card read "Brief: Brief: …".** The title carried a kind
  label. → A title is the name Part 2 §4 gives, never a label in front.
- **2026-11-22 · A sprint's papers went to a storage that was being closed.** The project's
  instructions lacked a line and the old default applied. → There is one storage; the only thing a
  Project Context can say about notes is `none`.
