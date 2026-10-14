# 🧭 Project Planner

Takes a solo operator from raw idea through two phases — **Idealization** (Project Plan) and
**Architecture** (Architecture Document) — then hands off to the skills that break the work
down and put it on the board.

## 🔗 Delegation map

This skill does NOT do these. It tells the user when to invoke them:

| Skill | When |
|---|---|
| **clarify** | The user is stuck articulating something (4-D method) |
| **bandit:rewrite** | The user starts with a messy brain dump: clean it first |
| **`/bandit:plan wbs`** | After Phase 2: breaks the plan and architecture into a WBS |
| **bandit:tasks** | After the WBS: the board step `wbs` mode offers (`/bandit:tasks load`, or the dev route on `dev: true`) |
| **bandit:project** | Project instructions and the Project Context block |
| **Claude Design** (not a skill) | Phase 2 § 5, when an architecture diagram or screen mockup helps |

---

## 🗂️ Where the documents live

| What | Where |
|---|---|
| Folder | `MyNotes/{domain}/Projects/{project}/`, or its `planning/` once the project has sprint folders (bandit:notes conventions §1 names it), with `domain` and `project` from the `## 🧭 Project Context` section (owned by bandit:project). Missing, or `domain: none` → ask for the folder once. Never guess |
| Project plan | `{project}-project-plan.md` |
| Architecture | `{project}-architecture.md` |
| WBS | `{project}-wbs.md`, written by `wbs` mode (`references/wbs.md`), not this mode |
| Note format | Frontmatter, keys and YAML style follow the **bandit:notes** conventions. Read that skill before the first write. `type: reference`, `project` links the hub note |

Planning documents go straight into that folder, not through `_inbox/`: they are worked on
across many sessions, and the inbox is the user's. If the hub note `{project}.md` is
missing, say so and point to `/bandit:notes onboard`; don't create it here.

### 🧾 State comes from the files

No metadata block, no stored IDs. Read the folder at session start:

| Plan | Architecture | Mode |
|---|---|---|
| missing | — | **Phase 1 · New** |
| `status: active` | — | **Phase 1 · Resume** at the first section still holding `_Pending_` |
| `status: triaged` | missing or `status: active` | **Phase 2** (new or resume the same way) |
| `status: triaged` | `status: triaged` | **Done**: point to `/bandit:plan wbs`; it offers the board step |
| unclear | | **Ask**: "Are we starting a new project plan or working on the architecture?" |

`active` = being worked on. `triaged` = settled, nothing pending (the bandit:notes meaning).
Sections not confirmed yet hold the single line `_Pending_`.

When resuming, greet with the state:
> "Welcome back. Phase 1, Section 7 (Deliverables) is next."

### ✍️ Writing safely

- **First save:** create the file with no `if_match`. The write fails if the file exists:
  stop and ask, never overwrite.
- **Every later save:** read the file for its etag, write with `if_match` = that bare-hex
  etag. A 412 means someone edited it (often the user in Obsidian): re-read, say what changed, ask.
- Never pass `if_match: "*"`. Never delete. No version numbers or copies: the file is
  edited in place.
- Save after every 2–3 confirmed sections.

---

## 📝 Phase 1: Idealization (Project Plan)

### Entry Point

Ask the user:
> "Starting a new project plan. Do you want to brain dump everything and I'll draft from
> it, or go section by section?"

- **Brain dump path:** Let them dump freely. Parse the dump and pre-fill as many sections
  as possible. Then walk through each section to confirm/adjust. If the dump is messy,
  suggest running bandit:rewrite first.
- **Section-by-section path:** Walk through sections in order, one at a time.

### Interview Sections

For each section: draft an answer if ANY context exists (from brain dump, prior answers,
or inference). Present the draft for confirmation. If no context, ask a focused question
with concrete options. Use `ask_user_input` for bounded choices. Confirm before moving on.

#### § 1: Project Identity
- Project name, lead (pre-fill as user), date (auto-fill today), version (auto-fill v1.0)
- Confirm in one shot — low friction

#### § 2: Project Summary
- 1-2 paragraphs: what is this and why does it matter?
- Draft from brain dump if available; otherwise ask: "Describe this project like you'd
  explain it to a colleague in 2-3 sentences."

#### § 3: Problem / Opportunity
- What specific problem does this solve or opportunity does it capture?
- Separate from § 2 — this is the "why" not the "what"

#### § 4: Goals & Objectives
- 1-3 goals (broad outcomes), each with 1-3 SMART objectives
- These become functional requirements in Phase 2
- Draft goals from summary if possible; ask user to validate or adjust

#### § 5: Scope — In-Scope
- Explicit list of what the project includes, each item concrete and verifiable
- Draft from goals/deliverables if inferable

#### § 6: Scope — Out-of-Scope
- Explicit list of exclusions — critical for solo operators to prevent scope creep
- Suggest common exclusions based on project type (e.g., "no mobile app" for a web tool)

#### § 7: Key Deliverables
- Numbered list of tangible outputs the project produces
- Each deliverable maps to a system component in Phase 2

#### § 8: Technical Context
- Target stack: frontend, backend, database, deployment, hosting
- Known constraints (must use X, can't use Y, limited to Z)
- Existing systems this integrates with
- Pre-populates architecture document stack decisions
- Default to the user's standard stack patterns unless specified otherwise

#### § 9: Timeline & Milestones
- Phase names and sequence (not hard dates unless the user wants them)
- Solo = sequential phases, not parallel
- Suggest phases based on deliverables from § 7

#### § 10: Risks & Mitigation
- 2-4 risks with probability × impact scoring (P: 1-3, I: 1-3, Score = P × I)
- Always pre-fill: "Solo operator = single point of failure" (P:3, I:3, Score:9,
  Mitigation: document everything so future-you or Claude can pick it up)

#### § 11: Success Metrics
- 2-3 measurable criteria for project success
- These become performance requirements in Phase 2

#### § 12: Who Is This For?
- Solo-operator replacement for formal stakeholder/communication plans
- Who benefits from the output? Who needs to know it exists?
- No communication frequency tables

### Phase 1 Output

After all sections are confirmed:
1. Save the plan with no `_Pending_` left and `status: triaged`
2. Summary to user: "Project plan saved. X sections complete. Ready for architecture
   when you are."

### Phase Gate: Idealization → Architecture

Before Phase 2, validate:
- §§ 1-7 all filled (required)
- § 8 has at least stack preferences (required)
- The plan is saved with `status: triaged`

If gaps: list them and ask user to fill before proceeding.

---

## 🏛️ Phase 2: Architecture (Architecture Document)

### Entry Point

Read `{project}-project-plan.md` from the project folder.
> "I've read your project plan. I'll auto-draft the architecture document from it.
> Let's walk through — I'll show what I generated and you confirm or adjust."

### Auto-Draft Strategy

Phase 2 is **draft-first**. Generate a complete first draft of every section from the
project plan, then walk through each for confirmation. The user is reviewing and adjusting,
not answering from scratch.

### Architecture Sections

For each section, show the auto-drafted content and ask: "Confirm, adjust, or skip for now?"
Save progress every 3-4 sections.

#### § 1: System Identity
- Auto-draft from: Plan § 1 — system name, version, date, status: Draft

#### § 2: Purpose
- Auto-draft from: Plan §§ 2-3 — why this document exists, what it supports

#### § 3: High-Level Overview
- Auto-draft from: Plan §§ 2, 4, 5, 8 — what the system does, architecture style
- Include Core Stack table (frontend, backend, db, deployment, hosting) from § 8

#### § 4: System Components
- Auto-draft from: Plan § 7 — each deliverable becomes a component row
- Table: Component | Description | Technologies Used

#### § 5: System Architecture
- Cannot fully auto-draft — needs design decisions
- Draft text description based on components and stack
- Suggest architecture pattern based on project type
- Offer an architecture diagram or screen mockup in Claude Design
- For decisions where the user is uncertain, use clarify's 4-D approach

#### § 6: Data Flow
- Partially auto-draft from components — numbered steps showing data movement
- Confirm or adjust

#### § 7: API Structure (if applicable)
- Skip if not API-based
- Table: Method | Endpoint | Description | Inputs | Outputs

#### § 8: Database Schema (if applicable)
- Skip if stateless
- Table: Field | Type | Description

#### § 9: Security
- Auto-draft from: Plan § 10 + standard patterns for the deployment type
- Table: Feature | Description

#### § 10: Config & Environment Variables
- Standard env vars for chosen stack
- Table: Variable | Description | Example Value

#### § 11: Deployment & Hosting
- Auto-draft from: Plan § 8
- Docker Compose V2 example if Docker in stack (no version field)
- Cloudflare Tunnels if VPS hosting
- 3-branch git strategy (main ← staging ← development). **`dev: true`:** the repo's own branch
  rules instead (ask the user where they're written); never the default

#### § 12: Maintenance & Scaling
- Auto-draft based on stack: Python version, dependency lock, testing, scaling notes

#### § 13: Development Standards
- Auto-draft defaults: PEP8/Black/isort (Python), 3-branch git (`dev: true`: the repo's branch
  rules, as § 11), snake_case Python, kebab-case files, markdown docs in /docs

#### § 14: Appendix
- Links, diagram refs, onboarding notes
- "Onboarding" for solo = "how future-me picks this back up after 3 months"


### Phase 2 Output

After all sections are confirmed:
1. Save the architecture with no `_Pending_` left and `status: triaged`
2. Check whether Phase 2 changed the plan: new scope items, technical constraints that
   change deliverables, new risks
3. If so: show the changes, and on confirmation edit the plan in place (etag rules above)
4. Summary: "Architecture saved. Project plan updated (added X, Y). Next: `/bandit:plan wbs` to
   break this into a WBS; it offers the board step." The route after the WBS is `wbs` mode's.

---

## 📱 Phone-First Design

Every interaction must work on mobile:

- **One interaction = one section or one decision.** State comes from the files, so any
  session can pick up.
- **Draft first, confirm second:** never present a blank prompt when context exists.
- **Summaries are 3-5 bullets, not paragraphs:** "Section 4 done. 2 goals, 5 objectives.
  Moving to Scope. Ready?"
- **Use `ask_user_input`** for bounded choices wherever possible.
- **Don't dump the full document** into conversation — show only the current section.

---

## 🧠 ND-Friendly Patterns

- Maximum 4 options per question, always include an "Other" escape hatch
- 1-2 questions at a time
- Micro-summary after every 2-3 sections
- Offer a session break after extended questioning
- "Good enough for now" is always a valid option
