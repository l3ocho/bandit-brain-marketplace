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
   - **Claude Code surface** (whenever the project has no `dev: true`: every `workflow` project,
     and a `product_service` or `claude_marketplace` project that answered No to the dev question)
     — *"Will this project also run in Claude Code? 1. Yes 2. No"*. Yes → onboarding creates
     `Claude/code-{slug}/` (bandit:notes) and this skill produces the Claude Code twin (`references/project-context.md` → Claude Code twin). No → neither.
     No Project Context key: the answer goes to the onboarding hand-off only.
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

   Call `get_context` first and present its `boards` in the domain's folder (the domain not
   known yet → ask the Phase 4 Domain question now, once). Options:
   - "One existing board" — pick from the domain's live board list
   - "New board" — ask its name and, optionally, a subfolder of the domain's folder. Its profile
     is not asked: `technical` with `dev: true` (the dev rules and the dev board shape go
     together), `workflow` otherwise
   - "Not board-backed"
   - "Decide later"

   The answer goes to bandit:tasks' board step (**🚀 Onboarding** (`references/onboard.md`), step 3). What each answer
   becomes, the `board:` line it returns and what it may create are bandit:tasks' rules
   (`references/onboard.md`), not this skill's. Write back the `board:` line it returns.

   **Slug and prefix** are asked in Phase 4 (folder backend). When the output is artifact-only,
   suggest a kebab-case slug from the project name for the Project Context `project:` and
   confirm it; `prefix:` is then `none`.

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

## Phase 4: Optional Sections & Output

Quick resolution of optionals and output preference.

1. **Optional sections** (multi-select):
   - **Tool & Integration Rules** — "Strong opinions about which tools to use or avoid"
   - **External References** — "Project knowledge files or docs Claude should consult on-demand"
   - **Mission Statement** — "A north-star statement for tone and decision-making"

   **Project Context** is not offered here — it is always included (see `references/project-context.md`). Phase 1 question 5 fills its `board:` line, whatever the answer.

2. **Output target** (single select):
   - "Artifact only" (default)
   - "Artifact + vault folder (WebDAV)"
   - "Vault folder (WebDAV) only"

   Record it as `storage_backend`: `"webdav"` for either vault option, `null` for
   artifact-only. The Nextcloud Notes app is **not** a destination any more (see
   ⚠️ Legacy Notes backend in the audit flow).

3. **Folder, slug and prefix** — only when the output includes the vault folder. The folder is
   **derived, not typed**. Settings live in the project's settings folder of the MyNotes vault,
   as defined by the `bandit:notes` skill: `MyNotes/{domain}/Claude/ai-{project}`. Ask:
   - **Domain** (single select via `ask_user_input`) — list the live domains with
     `nc_webdav_list_directory("MyNotes")`: every folder whose name doesn't start with `_` or
     `.`. Add a last option, "Outside MyNotes (custom path)". Store the choice as the Project
     Context `domain:`.
   - **Project slug** (single select + free text) — the **project's own name** as a slug, not
     the Claude.ai project's display name: "Acme Notes Templates" in Claude.ai is the
     `home-reno` project. One slug names all of the project's folders in the vault, and the
     Claude Code settings reuse it, so both surfaces share the same docs. Offer the existing
     `Projects/` folders of the domain first (`nc_webdav_list_directory`), then a free-text
     option for a new one. Store it as the Project Context `project:`.
   - **File prefix** (open-ended) — a 2–3 character abbreviation (e.g. `kf` for KeyForge).
     Store it as the Project Context `prefix:`.

   Then show the derived paths and confirm, e.g. for a regular project:
   - Settings (this skill writes here): `MyNotes/Acme/Claude/ai-home-reno`
   - Shared project docs (read by Claude.ai and Claude Code): `MyNotes/Acme/Projects/home-reno`
   - Claude Code settings (configured in the repo): `MyNotes/Acme/Claude/code-home-reno`

   Every project type, **workflow included**, gets both folders (settings and shared project
   docs); which folders a project has is bandit:notes' rule, not this skill's. Show both paths.
   Store the settings path as `webdav_folder`. The `Projects/` and `Claude/` folders are **vault rows** from bandit:notes'
   onboarding procedure (see **🚀 Onboarding** (`references/onboard.md`)), never created outside the approved proposal.

   **"Outside MyNotes"** is the escape hatch for folders the vault conventions don't cover:
   ask for the full path (relative to the Nextcloud root, no leading slash), store it verbatim
   as `webdav_folder`, set the Project Context `domain: none`, and still ask the project slug
   for `project:`.

   Derived filenames (**`.md` extension** — these are real files and want to open as markdown):
   - Instructions: `{prefix}-instructions-v{N}.md` (e.g., `bi-instructions-v0.md`)
   - Prompt reference: `{prefix}-prompt-reference-v{N}.md` (e.g., `bi-prompt-reference-v0.md`)

   Version numbers are integers appended without dots. Initial version is always `v0`. See
   **Vault Folder (WebDAV)** in `references/output.md` for the full rules.

For each selected optional, ask its focused follow-up (same pattern as Phase 3).

## Generation

After the interview completes:

1. **Assemble** the instruction set following the section ordering from the reference template
2. **Inject default rules** — technical-decisions rule goes into Hard Rules
3. **Apply ND-friendly formatting** — emoji-anchored headers, tables, short sentences, white space
4. **Dedup check** — scan for any information repeated across sections. Merge or cut.
5. **Token budget check** — compare against the target for the project's complexity tier. If over,
   suggest what to offload to External References.
6. **Add metadata block** — `<!-- bandit-project: {...} -->` as first line, in the shape the
   reference template defines. Always set `storage_backend`; with vault output, populate the
   storage fields (see **Metadata Storage Fields** in `references/output.md`).
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
   formatting. Title: "Project Reference — {project name}". With vault output, the file name is
   the versioned one (e.g., `bi-prompt-reference-v0.md`).
9. **Onboarding proposal** — with a vault target, run steps 2–7 of **🚀 Onboarding** (`references/onboard.md`): the vault
   and board rows plus the two settings files, in one proposal. Artifact-only → just the board
   rows (if any), then output the two files (see **Output Handling** in `references/output.md`).
