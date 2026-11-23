# 📋 Project Instructions Reference Template

> Canonical definition of what well-formed project instructions contain, on either surface: a Claude.ai project's instructions, or a folder's `CLAUDE.md` in Claude Code.
> Drives both interview questions (new project mode) and audit criteria (existing project mode).
>
> **Reference Version:** 2.0 — 2.0 dropped the settings line, the settings folder and the second copy for another surface.

---

## 🗺️ Section Inventory

Every project instruction set addresses five concerns:

| Concern | Question It Answers |
|---------|---------------------|
| **Context** | What is this project? |
| **Role** | What should Claude do here? |
| **Behavior** | How should Claude operate? |
| **Guardrails** | What must Claude never/always do? |
| **Identity** | What's the tone and purpose? |

Sections are classified as **Required**, **Conditional**, or **Optional**.

---

## ✅ Required Sections

These appear in every project instruction set, regardless of project size or complexity.

### 1. Project Header

**Concern:** Context
**Purpose:** Version tracking and quick identification.

**Must contain:**
- Project name (on Claude.ai, the project's name there)
- Version number (semver)
- Last updated date

**Audit criteria:**
- Version exists and follows semver
- Last updated date is present
- Date older than 90 days triggers a staleness warning

**Length:** 3–5 lines.

**Example — Good:**
```markdown
## the user Claude Marketplace — Project Instructions
**Version:** 7.0.0
**Last Updated:** 2026-02-11
```

**Example — Bad:**
No version. Or a last-updated date from six months ago with no changes logged.

---

### 2. Project Overview

**Concern:** Context
**Purpose:** Orient a fresh Claude session with zero history. If Claude can't understand the project from this section alone, it's incomplete.

**Content scales with complexity:**

| Project Type | Content |
|-------------|---------|
| Single repo, single concern | 3–5 sentences: purpose, tech stack, audience |
| Single repo, multiple concerns | Above + directory sketch + domain boundaries |
| Multi-repo | Architecture table (repo / role / purpose) + dependency flow + interface contracts |

**Project classification** (always present in overview):

| Classification | Description |
|---------------|-------------|
| Product / Service | Delivering and maintaining a product or service |
| Workflow | Manages a specific workflow (task manager, automation pipeline, etc.) |
| Claude Marketplace | Claude tools built to support Claude interactions (skills, plugins, commands) |

State the project classification at the top of the overview. It shapes smart defaults and audit expectations.

**Content rules:**
- Lead with purpose, not technology. What it does before how it's built.
- Name the tech stack explicitly — include framework versions when they affect behavior
- Multi-repo: state dependency direction. Who produces, who consumes, what's the contract.
- Describe what exists, not aspirational architecture.

**Audit criteria:**
- A fresh session can understand the project scope from this section alone
- Tech stack is named explicitly, not implied
- Multi-repo: dependency direction is stated, not assumed
- No stale references (renamed repos, deprecated components, removed services)

**Length:** 50–150 words (single repo) · 100–300 words (multi-repo).

---

### 2b. Project Context

**Concern:** Context
**Purpose:** Tell every other skill which project this is: domain, slug, type, board scope and prefix.

**Must contain:** the five required keys (plus the optional `dev: true`, `finance:`, `design:` and `notes:` lines), in the fixed format defined in `references/project-context.md` (not restated here).

**Audit criteria:**
- Present, directly after Project Overview
- All five required keys, valid values; `domain` is a top-level board folder (or `none`); `board` resolves (or `none` / `pending`)
- `dev`, when present, is `true`; anything else → fix or remove the line. Absent is valid
- `notes`, when present, is `none` or the older `app`; anything else → remove the line. Absent is valid (the app's Notes)
- Missing → built from what the instructions say, as a fix row

**Length:** 5 lines (6 with `dev`) plus the 2 closing lines.

---

### 2c. Environment (Claude Code projects only)

**Concern:** Context
**Purpose:** Say where the project runs, so nothing is guessed at runtime.

**Heading:** exactly `## 🖥️ Environment`, directly after Project Context.

**Must contain:**
- The machine it runs on and the folder it runs from
- Where its reference doc is: the note `{slug}-reference` on its board (`references/output.md`); with `notes: none`, the file `REFERENCE.md` in the folder
- Notes go to the app's Notes on its board; working files (data, scripts, outputs) stay in the folder
- A workflow agent: the **Working folder** line from `references/workdir.md` (S12), with the project's real `prefix`

**Audit criteria:**
- Present in a `CLAUDE.md`; absent from Claude.ai instructions
- Names the reference doc's home; without it, detail moved to the reference doc is unreachable
- A workflow agent's has the Working folder line

**Length:** 3–7 lines.

---

### 3. Role Definition

**Concern:** Role
**Purpose:** The single highest-impact section per token. Defines what Claude does in this project and shapes every response.

**Must contain:**
- A clear role title or framing (e.g., "Architect-in-Residence", "Implementation Partner")
- Concrete activities Claude performs — named actions, not vague capabilities
- Decision authority boundary: what Claude decides vs. what the user decides

**Audit criteria:**
- Role is specific. "Helpful assistant" fails. Named activities pass.
- Activities are verbs: review, plan, implement, debug, audit, scaffold — not "help with"
- Decision authority is explicit: recommend-and-user-picks? Execute autonomously? Where's the line?

**Length:** 30–80 words.

**Example — Good:**
```
Architect-in-Residence: Architecture decisions (options + trade-offs + recommendation),
code quality review, implementation plans (Claude Code-ready), dependency tracking.
```

**Example — Bad:**
```
You are a helpful coding assistant for this project.
```

---

### 4. Hard Rules

**Concern:** Guardrails
**Purpose:** Non-negotiable constraints. The never/always lists.

**Content rules:**
- Split into **Never** and **Always** lists
- Every rule is actionable and self-checkable — Claude can verify whether it violated each one
- Include "why" only when the rule is counterintuitive. Obvious rules need no justification.
- Rules must be project-specific. Generic good practices ("write clean code") don't belong here.
- No duplicates with rules stated in other sections.

**Default rules injected into every project:**
These are always present, regardless of what the interview produces:

> **Always:** When making technical decisions, present options with trade-offs and a recommended action. Never make a technical choice silently.

This default can be customized (e.g., scoped to architecture-only decisions) but never removed.

**Dev projects (`dev: true`) also get:**

> **Always:** When a scope is agreed, propose the card and, on the user's yes, write it through `/bandit:tasks spec`. `/bandit:tasks stage … ready` (on their approval) and `/bandit:tasks pick-ready` write the board the same way. These need no separate standing instruction.

Any other Hard Rule that forbids board writes is scoped to exclude them ("…except the dev commands `spec`, `stage … ready` and `pick-ready`").

**Audit criteria:**
- Every rule passes the verifiability test: could Claude check whether it violated this?
- No vague aspirations (bad: "maintain high quality" — good: "never modify `/production` without approval")
- No duplicates with Area-Specific Rules or Conventions sections
- Rules are scoped to this project, not general Claude behavior
- The technical-decisions default rule is present
- `dev: true` → the dev-commands rule is present, and no other rule contradicts it

**Length:** 10–20 rules total. If exceeding 20, some rules belong in Area-Specific Rules instead.

**Example — Good:**
```
Never write to database from app-personal-portfolio.
```

**Example — Bad:**
```
Always write tests.
```

---

## 🔀 Conditional Sections

Each has a trigger condition. Presented as a multi-select during the interview with smart defaults.

### 5. Operational Modes

**Concern:** Behavior
**Trigger:** Claude behaves fundamentally differently depending on a keyword, flag, or context.

**Must contain per mode:**
- Mode name
- Trigger condition (keyword, context, explicit request)
- How behavior differs from default
- Pointer to reference material if the mode has its own spec (don't inline full specs)

**Audit criteria:**
- Each mode has an unambiguous trigger
- Modes don't overlap (no situation activating two modes)
- Reference material pointers are valid and accessible

**Length:** 30–80 words per mode. Reference material is external.

---

### 6. Area-Specific Rules

**Concern:** Guardrails
**Trigger:** The project has distinct areas (repos, directories, domains, services) where different rules apply.

**Must contain per area:**
- Area name and primary concern (what it does / owns)
- Rules scoped to that area only
- Table format preferred (Rule / Detail) for scannability

**Content rules:**
- Rules here must NOT duplicate Hard Rules. If it applies everywhere → Hard Rules.
- Areas must match actual project structure. No phantom areas.

**Audit criteria:**
- Every rule is scoped to its area, not duplicated from Hard Rules
- Areas reflect real project structure
- Rules are actionable within that area's context

**Length:** 30–80 words per area.

---

### 7. Change Workflows

**Concern:** Behavior
**Trigger:** A change in one area can break or affect another area.

**Must contain per workflow:**
- Change origin ("When X changes…")
- Sequential propagation steps
- Verification step at each stage

**Audit criteria:**
- Every cross-boundary dependency has a documented workflow
- Workflows are sequential, not circular
- Each workflow includes at least one verification step

**Length:** 30–60 words per workflow.

---

### 8. Conventions

**Concern:** Behavior
**Trigger:** The project has consistent patterns the user follows that Claude should match. Almost always applicable — depth varies.

**Content categories:** naming conventions, config hierarchy, branch strategy, output format preferences, communication patterns.

**Content rules:**
- State the pattern, not the rationale (unless counterintuitive)
- Group by concern: git, naming, formatting, communication

**Audit criteria:**
- Conventions are consistent (no internal contradictions)
- Specific enough to follow ("use `/<noun> <action>`" not "use good names")
- Don't duplicate Claude's default behavior

**Length:** 30–100 words.

---

## 💡 Optional Sections

### 9. Tool & Integration Rules

**Purpose:** Which tools to use, which to avoid, how external services are accessed.
**Include when:** The project has strong tooling opinions — preferred CLIs, MCP servers, substitution rules.

**Content format:** Substitution rules where applicable: "Instead of X → use Y."

**Audit criteria:**
- Tool references are current (no deprecated tools)
- Substitution rules don't conflict
- Access patterns are specific (tool names, command syntax)

**Length:** 30–100 words.

---

### 10. External References

**Purpose:** Pointers to searchable files/docs that keep the instructions lean.
**Include when:** The project offloads detail to project knowledge files, wikis, or searchable docs.

**Must contain per reference:**
- Resource name and purpose
- Trigger condition (when should Claude consult this?)

**Audit criteria:**
- Every reference points to something accessible
- Trigger conditions are clear

**Length:** 2–4 lines per reference.

---

### 11. Mission Statement

**Purpose:** North star for ambiguous situations. Closes the instructions with tone and purpose.
**Include when:** The project benefits from personality consistency or has a guiding principle.

**Content rules:**
- 1–3 sentences maximum
- Actionable, not corporate boilerplate
- Humor is fine if it serves clarity

**Audit criteria:**
- Specific to this project
- Not a generic platitude

**Example — Good:**
```
Build the most useful, well-architected Claude Code marketplace possible.
Challenge bad ideas. Praise good ones (briefly).
```

**Example — Bad:**
```
Strive for excellence in all we do.
```

**Length:** 1–3 sentences.

---

## 🏗️ Structural Rules

These govern how the reference is applied across all sections.

### Section Ordering

1. Project Header
2. Project Overview
3. Project Context
   - Environment (Claude Code projects only)
4. Role Definition
5. Hard Rules
6. *Conditional sections (by relevance to this project)*
7. *Optional sections*
8. Mission Statement

Most-referenced sections first. Tone-setting last.

### Token Budget Targets

| Project Complexity | Target Length | Max Sections |
|-------------------|--------------|--------------|
| Simple (single repo, one concern) | 200–400 words | 4–6 |
| Moderate (single repo multiple concerns, or 2–3 repos) | 400–700 words | 6–9 |
| Complex (multi-repo ecosystem, multiple modes) | 700–1000 words | 8–11 |

Exceeding the target triggers a warning with suggestions for what to offload to External References.

### Anti-Redundancy (Generation AND Audit)

A rule, convention, or constraint stated in one section must not appear in another. This applies during generation (never produce duplicates) and during audit (flag any found).

When there's ambiguity about where something belongs:
- Applies everywhere → Hard Rules
- Applies to one area → Area-Specific Rules
- Is a pattern to match → Conventions
- Is a tool preference → Tool & Integration Rules

### ND-Friendly Formatting

All generated instructions follow these principles:

- **Emoji-anchored section headers** — every H2 gets a semantic emoji that serves as a visual landmark for scanning
- **Tables over prose** for structured comparisons, rule sets, and inventories
- **Short sentences** — 1–2 lines max per bullet or rule
- **White space** — generous spacing between sections
- **Bold key terms** on first occurrence within a section for scanning
- **No walls of text** — if a paragraph exceeds 4 sentences, restructure into a list or split into subsections
- **Progressive structure** — high-level first, detail second; reader can stop at the depth they need

### Default Injected Rules

These are always present in generated instructions regardless of interview answers:

1. **Technical decisions:** "For technical decisions, present options with trade-offs and a recommended action."
2. **Formatting standard:** Generated instructions follow ND-friendly formatting (emoji anchors, tables, scannable structure).
3. **Anti-redundancy:** No repeated information across sections.

### No settings line

Generated instructions start at their header: no HTML comment on line 1. The project's identity is
the `## 🧭 Project Context` section (`references/project-context.md`); its version is the
`**Version:**` line. Instructions written before reference 2.0 start with a comment of the form
`<!-- …: {…} -->` holding storage fields: the audit flags it (⚠️ Legacy settings line) and its row
removes it, after taking a slug or prefix found only there into the Project Context.

**The Project Context `project:` and `prefix:` are set once** and reused on every version. The user
must explicitly request a change.
