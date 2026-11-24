# 🆕 New Project Mode — Interview Flow

> Read when Mode Detection (`references/audit.md`) picks **New Project**: no instructions yet, or only a
> placeholder. Covers the four interview phases and the generation steps.

The interview gathers information to populate the reference template sections. It follows a
chunked pattern: 2–3 questions per phase, with multi-select where applicable.

## Phase 1: Context & Stack

Gather information for **Project Overview** and begin shaping **Role Definition**.

Ask the open-ended questions in prose, and use `ask_user_input` for structured choices.
Each phase may take 1–2 messages when mixing both question types — that's fine.

1. **Project type** (single select via `ask_user_input`) — Options:
   - "Product / Service" — delivering and maintaining a product or service
   - "Workflow" — manages a specific workflow (e.g., task manager, automation pipeline)
   - "Claude Marketplace" — Claude tooling built to support Claude interactions (skills,
     plugins, commands)
   This classification drives smart defaults in Phase 3 and is stored as the Project Context
   `type:` (`product_service`, `workflow` or `claude_marketplace`).
   - **Dev workflow** (only when the type is `product_service` or `claude_marketplace`; never for
     `workflow`) — *"Is this a technical development project that should use the dev card
     workflow (lanes, stages, plan notes)? 1. Yes 2. No (recommended unless there's a code
     repo)"*. Yes → the Project Context gets `dev: true`. No → no `dev` line at all.
   - **The surface is not asked.** It is the one this chat runs on (`references/surfaces.md`):
     the instructions go to the folder's `CLAUDE.md` in Claude Code, or are handed over to paste
     on Claude.ai. A `dev: true` project is a Claude Code project: asked for on Claude.ai, say
     that sprints run in Claude Code and that onboarding should be run from the repository.
   - **Notes** — *"Should the helpers keep this project's notes in the app? 1. Yes (recommended)
     2. No, its records are kept elsewhere"*. Yes → no `notes:` line. No → the Project Context
     gets `notes: none`.
   - **Finance accounts** (only when the user says this project works with money) — *"Should
     Finance in this project see only some accounts? Name them, or say all."* Names → the Project
     Context gets `finance: accounts "…"`, each checked live with `finance_get_context`. All → no
     `finance` line.
2. **What is this project?** (open-ended) — Purpose, domain, who it's for. Ask them to describe
   it like they'd explain it to a colleague in 2–3 sentences.
3. **Tech stack** (open-ended) — Languages, frameworks, databases, key libraries. Ask for versions
   only if they matter for behavior.
4. **Repository structure** (single select) — Options: "Single repo", "Monorepo with distinct areas",
   "Multiple repos", "Not a code project"
5. **Task board scope** (single select via `ask_user_input`) — Does this project's work live on
   a Bandit Brain board?

   Call `get_context` first. **Domain** (single select): its top-level board folders, plus "A new
   folder" (its name is asked; bandit:tasks' board step creates it) and "None" (`domain: none`).
   A project that should see and change only a subfolder (a client's folder inside a company's) gets that folder as a
   path, `domain: {top} / {sub}` (`references/project-context.md`).
   Then present the `boards` in the domain's folder. Options:
   - "One existing board" — pick from the domain's live board list
   - "New board" — ask its name and, optionally, a subfolder of the domain's folder. Its profile
     is not asked: `technical` with `dev: true` (the dev rules and the dev board shape go
     together), `workflow` otherwise
   - "Not board-backed"
   - "Decide later"

   The answer goes to bandit:tasks' board step (**🚀 Onboarding** (`references/onboard.md`), step 3). What each answer
   becomes, the `board:` line it returns and what it may create are bandit:tasks' rules
   (`references/onboard.md`), not this skill's. Write back the `board:` line it returns.

   **Slug and prefix.** Suggest a kebab-case slug from the project name for the Project Context
   `project:` (the project's own name, not a Claude.ai display name) and confirm it. Then the
   prefix: a 2–3 character abbreviation (e.g. `kf` for KeyForge), or `none` for a project with no
   working folder.

## Phase 2: Role & Decision Authority

Gather information for **Role Definition** and begin shaping **Hard Rules**.

1. **What should Claude do in this project?** (open-ended) — Ask for concrete activities, not
   capabilities. Prompt with examples: "review code, plan architecture, debug issues, write
   documentation, implement features, research options…"
2. **Decision authority** (single select) — Options:
   - "Present options, I decide" (advisory)
   - "Execute autonomously, flag only when uncertain" (autonomous)
   - "Mixed — depends on the type of decision" (hybrid)
   If hybrid, follow up: "Which decisions should Claude make autonomously vs. present options for?"
3. **Any absolute rules?** (open-ended) — Things Claude must never do or must always do in this
   project. Prompt: "Think about past mistakes or frustrations — what guardrails prevent those?"

## Phase 3: Conditional Sections

Present the four conditional sections as a **multi-select** with smart defaults based on
what was learned in Phases 1–2.

Set defaults based on prior answers:
- Repo structure is "Multiple repos" → pre-select Area-Specific Rules + Change Workflows
- Repo structure is "Monorepo with distinct areas" → pre-select Area-Specific Rules
- User described distinct interaction patterns → pre-select Operational Modes
- Default Conventions to selected for all projects
- **Project type "Product / Service"** → pre-select Change Workflows + Conventions
- **Project type "Workflow"** → pre-select Operational Modes + Conventions

Present:
> "Based on what you've described, I'd include these sections. Adjust if needed:"

Options (multi-select, pre-selected based on logic above):
1. **Operational Modes** — "Claude behaves differently based on keywords or context"
2. **Area-Specific Rules** — "Different rules apply to different parts of the project"
3. **Change Workflows** — "Changes in one area can break another"
4. **Conventions** — "Consistent patterns Claude should match (naming, git, formatting)"

For each selected conditional, ask a focused follow-up:
- **Operational Modes:** "Name each mode and what triggers it."
- **Area-Specific Rules:** "For each area, what rules are unique to it?"
- **Change Workflows:** "When area X changes, what needs to happen downstream?"
- **Conventions:** "What patterns do you follow consistently? (naming, branches, output format, etc.)"

## Phase 4: Optional Sections

Quick resolution of the optionals.

1. **Optional sections** (multi-select):
   - **Tool & Integration Rules** — "Strong opinions about which tools to use or avoid"
   - **External References** — "Project knowledge files or docs Claude should consult on-demand"
   - **Mission Statement** — "A north-star statement for tone and decision-making"

   **Project Context** is not offered here — it is always included (see `references/project-context.md`). Phase 1 question 5 fills its `board:` line, whatever the answer.

For each selected optional, ask its focused follow-up (same pattern as Phase 3).

## Generation

After the interview completes:

1. **Assemble** the instruction set following the section ordering from the reference template
2. **Inject default rules** — technical-decisions rule goes into Hard Rules
3. **Apply ND-friendly formatting** — emoji-anchored headers, tables, short sentences, white space
4. **Dedup check** — scan for any information repeated across sections. Merge or cut.
5. **Token budget check** — compare against the target for the project's complexity tier. If over,
   suggest what to offload to External References.
6. **No settings line.** The instructions start at their header (`references/output.md` → No
   settings line).
7. **Generate the Project Context** — always insert a `## 🧭 Project Context` section,
   immediately after Project Overview. See `references/project-context.md` for the exact
   format and how each key is filled.
8. **Generate supporting document** — create a project reference doc alongside the instruction set.
   This is a separate file that contains:
   - **Project type** (from Phase 1)
   - **Tech stack inventory** (frameworks, versions, key dependencies)
   - **Repository map** (repos, their roles, dependency direction — even if single repo)
   - **Decision log** (stub section — "No decisions logged yet")
   - **Change history** (initial entry: "v0 — Initial project settings created — {date}")
   - **Open questions** (anything flagged during interview that wasn't resolved)
   Even minimal projects get this document. It keeps a consistent structure from day one and
   gives future audits a baseline to compare against. Format as markdown with ND-friendly
   formatting. Title: "Project Reference — {project name}". It is saved as the note
   `{slug}-reference` (`references/output.md`).
9. **Onboarding proposal** — run steps 2–7 of **🚀 Onboarding** (`references/onboard.md`): the
   notes, board and settings rows in one proposal.
