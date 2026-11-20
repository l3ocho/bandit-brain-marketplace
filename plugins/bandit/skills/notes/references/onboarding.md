# 🚀 Onboarding: the notes step

> Read when bandit:project runs the notes step of onboarding. The procedure itself is `references/commands.md` → Onboarding rows.

## 🚀 Onboarding — the notes step, run by bandit:project

**Onboarding a project is one command, owned by bandit:project.** It interviews the user, then loads
this skill for the notes rows and bandit:tasks for the board rows, and shows **one** proposal.
Which storage the project's notes use is read from the Project Context
(`references/model.md` → Which storage). This skill only produces the notes rows and executes the
approved ones; it never shows its own
proposal or asks for its own approval when bandit:project runs it. Procedure: *Onboarding rows*
in Part 3.

| Situation | Notes rows |
|---|---|
| Vault project, the domain doesn't exist yet | `init` rows: the domain folder, core folders, chosen modules, starter templates |
| Vault project, the domain exists | **Every missing core item** (`_inbox/`, `_templates/` + `new-note.md`, `_archive/`, `_attachments/`, `Claude/`, `Projects/`, `README.md`), plus this project's `Claude/ai-{slug}/` and `Projects/{slug}/` with its hub note `{slug}.md`, **for every project type, workflow included**; plus `Claude/code-{slug}/` for a `dev: true` project (dev mirror), or a project without `dev: true` that runs in Claude Code (Claude Code twin) |
| The project's notes are in the app's Notes (`notes: app`) | The hub note on the project's board, after its board row; in the vault only the settings folders: the domain folder and `Claude/` when missing, `Claude/ai-{slug}/`, and `Claude/code-{slug}/` when the row above would add it; for a Claude Code twin also `Projects/{slug}/`, which holds its working-folder manifest, not notes. No `_inbox/`, `_templates/`, `_archive/`, `_attachments/`, README or `init` rows |

The core rows only **create** missing standard folders and starter files. Anything that would
move, rename, edit or delete existing content (legacy layout, settings folders in the wrong place,
stray files) is still fixed in the same proposal: it comes back as a **fix row** marked `domain`,
built with the `onboard` Stage B/C procedure (Part 3), after the create rows.
