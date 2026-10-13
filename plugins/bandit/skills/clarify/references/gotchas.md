# ⚠️ Gotchas

One line per real failure: what went wrong → what to do instead. Read once per clarification.

- Fires when the user pastes notes and says "clarify this" → that's a rewrite: hand off to bandit:rewrite.
- Rapid-fires a wall of questions → one block of 1–2 questions, then wait.
- Asks open-ended questions with no options → every question gets 2–4 options plus "Other".
- Delivers the spec before the user confirms the assumptions → echo back and let them correct first.
- **2026-09-25 · Spec shipped on a guess about a connector.** "Probably can't auto-refresh" went
  into the spec untested, and the spec was revised twice. → Test capability assumptions with one
  call before Phase 4.
- **2026-09-25 · "See attached" with nothing attached.** The skill didn't check, lost a tool call,
  then guessed which feature was meant. → Check references in Phase 1; name a missing one as an
  assumption.
- **2026-09-28 · Skill spec saved to Acme/_inbox.** The save offer always pointed at the domain
  inbox, so a spec changing bandit:tasks and bandit:notes landed in a vault. → The destination
  follows the subject: skill changes go to a Marketplace card plus brief, everything else to the domain `_inbox`.
- **2026-10-07 · Inbox note with no card.** The offer was note-only, so specs sat in `_inbox` with
  nothing on the board pointing at them, and got lost or binned. → Offer note **and** card by
  default, linked via `board-task`; Leo drops one by saying so.
