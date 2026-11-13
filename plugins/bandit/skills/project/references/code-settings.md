# 🔁 Claude Code settings → Claude.ai settings

> Read for a full audit or a targeted update of a `dev: true` project's Claude.ai instructions
> (`references/audit.md` Step 1, `references/update.md`). It brings over the tool and architecture
> changes made on the Claude Code side that matter to Claude.ai's job, and nothing else.

The two surfaces have different purposes, so the two settings are never made to match: Claude.ai
captures, clarifies, triages, writes Specs and keeps the overview; Claude Code plans sprints,
builds, tests, releases and deploys.

## 📥 What to read

1. **The Claude Code copy** in the vault: `MyNotes/{domain}/Claude/code-{slug}/CLAUDE.md`, plus
   the listing of its `claude/` folder (the repo's `.claude/`, copied by the dev mirror,
   `references/dev-mirror.md`). Read through WebDAV; note the file's last-modified date.
2. **The production Claude.ai instructions** (the version the self-check stamp names) and their
   `**Last Updated:**` date.
3. Say in the report, in one line: "Read the Claude Code settings copy from {date}."
   **No copy** (the folder or its `CLAUDE.md` is missing) → one line, "No Claude Code settings copy
   in the vault: nothing brought over", and the review carries on without this step.

A Claude Code change counts as **new** when the copy's date is later than the Claude.ai
instructions' `Last Updated` date. Older content was already reviewed: compare it only when the
two settings say different things (Conflicts, below).

## 🗂️ What comes across

Sort each section or rule of the Claude Code `CLAUDE.md` by what it is about:

| Brings over, worded for Claude.ai | Pointer at most, never copied |
|---|---|
| Board and vault tools: names, arguments, what a call does or refuses | Sprint planning, waves, gates, the ledger |
| Connectors and what each is used for | Build, test and verify commands |
| The app's modules, layout and where its records live | Releases, deploys, branches, the recipe (`bandit.yaml`) |
| The skills and plugins Claude.ai uses, by name | Hooks, agents, aliases, permissions, guardrails, settings files |
| Project Context keys and their values | Anything only Claude Code runs (scripts, the dev mirror, worktrees) |

- **A row per change.** Each new change in the left column becomes one row in the same proposal
  as the rest of the audit: the target section of the Claude.ai instructions, and the exact text
  to add or change, written for what Claude.ai does with it (what to call, what to capture or
  check), never a copy of the Claude Code wording.
- **The right column gets no row.** If Claude.ai needs to know such a thing exists, one pointer
  line ("sprints run in Claude Code: `bandit-dev:sprint`"), only when the instructions lack one.
- **Unsure which column:** ask what Claude.ai would do differently with it. Nothing → right column.

## ⚖️ Conflicts

Where the two settings say different things about the same tool or part of the architecture,
show both in the proposal row, quoted with their source, and say which should win and why:

| Topic | Wins |
|---|---|
| How a tool or the code works as built (names, arguments, modules, record homes) | The Claude Code side: it sits next to the code |
| Capture, clarify, triage and Spec behaviour, and how the user is spoken to | The Claude.ai side: that is its job |

The losing side's fix is a row too: for the Claude.ai instructions, in this proposal; for the
Claude Code `CLAUDE.md`, a hand-over line for Claude Code in the project (this skill never writes
the repo).
