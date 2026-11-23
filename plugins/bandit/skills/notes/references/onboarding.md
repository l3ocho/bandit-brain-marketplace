# 🚀 Onboarding: the notes step

> Read when bandit:project runs the notes step of onboarding. The procedure itself is `references/commands.md` → Onboarding rows.

## 🚀 Onboarding — the notes step, run by bandit:project

**Onboarding a project is one command, owned by bandit:project.** It interviews the user, then loads
this skill for the notes rows and bandit:tasks for the board rows, and shows **one** proposal.
This skill only produces the notes rows and executes the approved ones; it never shows its own
proposal or asks for its own approval when bandit:project runs it. Procedure: *Onboarding rows*
in Part 3.

| Situation | Notes rows |
|---|---|
| The project's notes are in the app's Notes (no `notes:` line, or `app`) | The hub note on the project's board, after its board row |
| `notes: none` | None. One line says the helpers keep no notes for this project |
| A project with `board: none` | The hub note as a private note, with the tag `{slug}` |

The row only **creates** the missing hub note. Anything that would move, rename, edit or delete an
existing note is still fixed in the same proposal: it comes back as a **fix row**, marked `domain`
when it is outside the project's board.
