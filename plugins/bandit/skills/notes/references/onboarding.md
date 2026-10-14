# 🚀 Onboarding: the vault step

> Read when bandit:project runs the vault step of onboarding. The procedure itself is `references/commands.md` → Onboarding rows.

## 🚀 Onboarding — the vault step, run by bandit:project

**Onboarding a project is one command, owned by bandit:project.** It interviews the user, then loads
this skill for the vault rows and bandit:tasks for the board rows, and shows **one** proposal.
This skill only produces the vault rows and executes the approved ones; it never shows its own
proposal or asks for its own approval when bandit:project runs it. Procedure: *Onboarding rows*
in Part 3.

| Situation | Vault rows |
|---|---|
| The domain doesn't exist yet | `init` rows: the domain folder, core folders, chosen modules, starter templates |
| The domain exists | **Every missing core item** (`_inbox/`, `_templates/` + `new-note.md`, `_archive/`, `_attachments/`, `Claude/`, `Projects/`, `README.md`), plus this project's `Claude/ai-{slug}/` and `Projects/{slug}/` with its hub note `{slug}.md`, **for every project type, workflow included**; plus `Claude/code-{slug}/` for a `dev: true` project (dev mirror), or a project without `dev: true` that runs in Claude Code (Claude Code twin) |

The core rows only **create** missing standard folders and starter files. Anything that would
move, rename, edit or delete existing content (legacy layout, settings folders in the wrong place,
stray files) is still fixed in the same proposal: it comes back as a **fix row** marked `domain`,
built with the `onboard` Stage B/C procedure (Part 3), after the create rows.
