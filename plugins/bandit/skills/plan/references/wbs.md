# 🏗️ WBS Generator

Transform project documentation into a structured, numbered Work Breakdown Structure with gap analysis, dependency mapping, and ND-friendly formatting.

## 🗺️ Process Overview

The workflow has five phases. Do them in order — each depends on the previous one.

```
Phase 1: INGEST    → Read and inventory the project documentation
Phase 2: ANALYZE   → Gap analysis — find what's missing or ambiguous
Phase 3: RESOLVE   → Ask the user to fill gaps (multi-choice + recommendation)
Phase 4: GENERATE  → Produce the structured WBS markdown artifact
Phase 5: RECONCILE → Backport findings into the source document and deliver updated version
```

---

## 📥 Phase 1: Ingest the Documentation

### Vault Document Source (Check First)

When the chat has a `## 🧭 Project Context` with `domain` and `project`, look in the project's
planning folder before asking for uploads: `MyNotes/{domain}/Projects/{project}/`, or its
`planning/` on a project with sprint folders (bandit:notes conventions §1 names the folder):

| Found | Do |
|---|---|
| `{project}-project-plan.md` **and** `{project}-architecture.md` | Offer: *"This project has a plan and architecture in the vault. Read those, or do you have newer versions to upload?"* |
| The plan only | Read it. Tell the user the WBS will be thinner on technical work without the architecture |
| Neither, or no Project Context | Ask for uploaded docs as usual |

**Dev projects.** A Project Context with `dev: true` (key owned by bandit:project) switches on
the dev variant: the level glossary in the header, the empty `## 🔗 Card links` section, and the
dev closing offer. Nothing else in the format changes. How cards map onto the levels is
bandit:tasks' (`references/dev-workflow.md` → WBS on dev projects).

### Sprint mode (a batch of existing cards)

Run by bandit-dev:sprint's planning (its step 6) on a `dev: true` project, before it splits waves.

| | Sprint mode |
|---|---|
| Input | A set of existing cards (`get_task`, read-only) and their briefs (through bandit:notes) |
| Output | The same `{slug}-wbs.md`, same format. The sprint plan note links it; nothing is embedded |
| Phases | 1–4 as usual. **Phase 5 is skipped**, as in migration mode: it would edit the briefs, which aren't this skill's |
| Card links | One row per card the WBS maps (below) |
| Sizes | None. The WBS carries no sizes; sprint sizing is bandit-dev:sprint's step 4 |

### Migration mode (an existing WBS)

When the input is an existing breakdown rather than project docs (e.g. the Gitea wiki page
`WBS: Home Reno Templates`), rewrite it into the Output Format below instead of generating from
scratch: map its levels onto L1 phase · L2 deliverable · L3 work package · L4 sub-step, keep its
IDs' meaning, and list everything that didn't map under **⚠️ Assumptions & Gaps** as a gap.
Skip Phase 5 (the source isn't a file this skill edits). Save `{slug}-wbs.md` as below; the old page becomes a pointer, changed wherever it lives (Claude Code for a repo wiki).

### Ingest Process

Read the uploaded project document(s) completely before doing anything else. During this read, extract and inventory:

1. **Project identity** — name, goal/objective, sponsor, target audience
2. **Scope boundaries** — what's explicitly in scope and out of scope
3. **Deliverables** — tangible outputs mentioned (a website, a report, a product, an event)
4. **Constraints** — budget, timeline, technology choices, team size, regulatory requirements
5. **Stakeholders** — who's involved, who approves, who's affected
6. **Dependencies** — anything that must happen first, external systems, third-party vendors
7. **Quality criteria** — acceptance criteria, definition of done, success metrics
8. **Risks** — anything flagged as uncertain, risky, or conditional

If the user uploaded a file, use the appropriate file-reading approach for the file type. If the project info is in the chat context (pasted text, prior conversation), gather it from there.

After ingesting, produce a brief **Project Snapshot** summary (5–8 lines) and share it with the user to confirm you understood the project correctly. This prevents building a WBS from a misunderstanding.

---

## 🔍 Phase 2: Gap Analysis

Compare what you extracted against the **completeness checklist** below. Every WBS needs these answered, either explicitly in the doc or inferrable from context. Flag anything missing or ambiguous.

### Completeness Checklist

| # | Question | Why It Matters |
|---|----------|---------------|
| 1 | Is the project goal specific and measurable? | Vague goals → vague scope → scope creep |
| 2 | Are all major deliverables listed? | Missing deliverables = missing entire branches of work |
| 3 | Are scope boundaries defined (in/out)? | Without boundaries, scope grows invisibly |
| 4 | Is there a timeline or deadline? | Affects how deep to decompose and how to phase work |
| 5 | Is there a budget or resource constraint? | Determines whether to include budget-tracking tasks |
| 6 | Are technology/platform choices stated? | Different stacks = different work packages |
| 7 | Are stakeholders and approvers identified? | Every approval gate is a task in the WBS |
| 8 | Are external dependencies mentioned? | Third-party work is a risk; needs tracking tasks |
| 9 | Are quality/acceptance criteria defined? | Drives testing and validation work packages |
| 10 | Are there known risks or assumptions? | Risks may need mitigation tasks in the WBS |

### Classifying Gaps

For each gap, classify it:

- **🔴 Blocker** — Cannot build a meaningful WBS without this. Must ask the user.
- **🟡 Important** — WBS will be weaker without it, but you can make a reasonable assumption. Ask the user to confirm or override your assumption.
- **🟢 Nice-to-have** — Would improve the WBS but you can infer a sensible default. Mention it but don't block on it.

---

## ❓ Phase 3: Resolve Gaps

If Phase 2 found any 🔴 Blocker or 🟡 Important gaps, present them to the user **before** generating the WBS. This is critical — a WBS built on wrong assumptions is worse than no WBS.

### How to Ask

Use the `ask_user_input` tool when possible (for bounded choices). Group related gaps into a single interaction to minimize back-and-forth. For each gap:

1. **State the gap clearly** — what's missing and why it matters (one sentence)
2. **Offer 2–4 concrete options** — not vague categories, but specific choices the user can pick from
3. **Mark your recommendation** — indicate which option you'd pick and why (briefly)

#### Example Gap Resolution

> **Gap: No technology stack specified for the website project.**
> This determines whether we need front-end, back-end, CMS, or static-site work packages.
>
> Options:
> 1. Static site (HTML/CSS, hosted on Netlify/Vercel) — simplest
> 2. CMS-based (WordPress, Webflow) — content team can self-serve
> 3. Custom full-stack (React + Node/Python API) — most flexible
> 4. I'll specify something else
>
> **Recommendation:** Option 2 (CMS-based) — best balance of flexibility and maintainability for most business websites.

If the user's answer introduces new scope or changes the project fundamentally, loop back to Phase 1 and re-inventory. Otherwise, record their answers and proceed.

For **🟢 Nice-to-have** gaps, state your assumption inline in the WBS output (e.g., "Assuming 2-week testing phase based on project size") rather than asking.

---

## 🧱 Phase 4: Generate the WBS

Now build the actual WBS. Follow these rules precisely — they're the difference between a useful WBS and a useless one.

### Structural Rules

1. **Level 0** — The project itself. One line. Format: `WBS-0: [Project Name]`
2. **Level 1 (Phases)** — 3–7 major work categories. These are the big buckets. Format: `WBS-X`
3. **Level 2 (Deliverables)** — Break each phase into tangible outputs. Format: `WBS-X.Y`
4. **Level 3 (Work Packages)** — The actual assignable tasks. Format: `WBS-X.Y.Z`
5. **Level 4** (rare) — Only if a work package genuinely has sub-steps that different people would do. Format: `WBS-X.Y.Z.W`

**The 100% Rule:** The children of any parent MUST capture 100% of the parent's scope. No gaps, no extras. Cross-check every level.

**The 8/80 Rule for Work Packages:** Each work package should represent between 8 hours (1 day) and 80 hours (2 weeks) of effort. Smaller = micromanagement. Larger = too vague to estimate.

**Deliverable-oriented, not action-oriented:** Name items as things (nouns/deliverables), not actions (verbs). "Approved wireframes" not "Design wireframes." The WBS captures WHAT, not HOW.

### ID System

Every item gets a structured ID with the prefix `WBS-`:

```
WBS-0          → Project level
WBS-1          → Phase 1
WBS-1.1        → First deliverable under Phase 1
WBS-1.1.1      → First work package under that deliverable
WBS-1.1.1.1    → Sub-task (Level 4, use sparingly)
```

These IDs are used for:
- **Internal dependency references** — e.g., "Depends on: WBS-2.3.1"
- **Deliverable traceability** — linking a work package to the deliverable it produces
- **Communication** — "Let's discuss WBS-3.2" is unambiguous

### Dependency Mapping

For each work package (Level 3), identify:
- **Depends on:** Which other WBS items must complete before this one can start?
- **Blocks:** Which other WBS items are waiting on this one?

Use WBS IDs for references. Only map direct dependencies — if A→B→C, item C depends on B, not A.

### Output Format

Deliver the WBS as a **markdown file** presented to the user.

Use this exact structure. It is fixed on purpose: **`/bandit:tasks load` parses it** (the
`WBS-0` heading, the `#### WBS-X.Y:` deliverable headings, the work-package tables and the
dictionary). Changing the headings or table columns breaks the load. The optional
`## 🔗 Card links` section is last, after everything load parses, and load ignores it. Its card
id is the link; the title is for reading and may go stale after a rename.

```markdown
# 🏗️ [Project Name] — Work Breakdown Structure

> 📋 **Generated from:** [source document name]
> 📅 **Date:** [generation date]
> 🎯 **Project Goal:** [one-sentence goal from Phase 1]
> 🧭 **Levels (dev projects only):** L1 phase · L2 deliverable · L3 work package · L4 sub-step

---

## 🗺️ WBS Overview

[2-3 sentence summary of the project scope and what this WBS covers]

### 📊 Structure Summary

| Metric | Count |
|--------|-------|
| Phases (L1) | X |
| Deliverables (L2) | X |
| Work Packages (L3) | X |
| Total Items | X |

---

## 🎯 WBS-0: [Project Name]

### 📦 WBS-1: [Phase Name]

> [One-sentence description of what this phase covers]

#### WBS-1.1: [Deliverable Name]

| ID | Work Package | Dependencies | Blocks |
|----|-------------|-------------|--------|
| WBS-1.1.1 | [Package name] | — | WBS-X.Y.Z |
| WBS-1.1.2 | [Package name] | WBS-1.1.1 | WBS-X.Y.Z |

#### WBS-1.2: [Deliverable Name]
...

[Repeat for all phases]

---

## 🔗 Dependency Map

[Summary table showing critical path items and key dependency chains]

---

## 📝 WBS Dictionary (Key Packages)

For each critical-path or high-risk work package, include a dictionary entry:

| Field | Detail |
|-------|--------|
| **ID** | WBS-X.Y.Z |
| **Name** | [Package name] |
| **Description** | [What needs to be done — 1-2 sentences] |
| **Owner** | [Role or person, if known; otherwise "TBD"] |
| **Done When** | [Acceptance criteria] |
| **Dependencies** | [WBS IDs this depends on] |

---

## ⚠️ Assumptions & Gaps

[List any 🟢 Nice-to-have assumptions made, and any unresolved ambiguities]

---

## 💡 Notes

[Any recommendations, risks, or observations from the analysis]

---

## 🔗 Card links

<!-- dev projects only: omit this section entirely without `dev: true`. Empty at generation,
     except in sprint mode. A row is added (through bandit:notes) when a work package's card is
     created, or, in sprint mode, for each existing card the WBS maps. -->

| WBS id | Card id | Card title (at creation) | Created |
|---|---|---|---|
```

### ND-Friendly Formatting Rules

These aren't optional — they're core to making the output actually usable:

- **Emoji anchors on every H2 and H3** — creates visual landmarks for scanning. Pick semantically meaningful emojis (see emoji guide below).
- **Tables for structured data** — work packages, dependencies, dictionary entries all go in tables. Never bury structured info in prose paragraphs.
- **Generous whitespace** — horizontal rules between major sections. Blank lines between table and next heading.
- **Bold key terms** — bold WBS IDs and package names on first reference in prose.
- **Short prose** — no paragraph longer than 3 sentences. If it's longer, convert to a list or table.
- **Progressive disclosure** — Overview → Structure Summary → Detail. Reader can stop at any depth.
- **Consistent patterns** — every phase looks the same. Every deliverable section looks the same. Predictability reduces cognitive load.

### Emoji Guide for WBS Sections

| Section Type | Suggested Emoji |
|-------------|----------------|
| Project (L0) | 🎯 |
| Planning/Requirements phase | 📋 |
| Design phase | 🎨 |
| Development/Build phase | 🔧 |
| Content/Data phase | ✏️ |
| Testing/QA phase | 🧪 |
| Launch/Deployment phase | 🚀 |
| Training/Handover phase | 📚 |
| Admin/Logistics phase | 📁 |
| Budget/Finance phase | 💰 |
| Travel/Transport phase | ✈️ |
| Documentation phase | 📝 |
| Dependency map | 🔗 |
| WBS Dictionary | 📝 |
| Assumptions | ⚠️ |
| Notes/Tips | 💡 |
| Overview | 🗺️ |
| Structure summary | 📊 |
| Phase (generic) | 📦 |

---

## 🔁 Phase 5: Reconcile the Source Document

The WBS process almost always reveals information that the original project document was missing, ambiguous about, or inconsistent on. Phase 5 closes that loop — ALWAYS update the source document with what was learned during Phases 2–4 and deliver the improved version back to the user.

This is not optional. Every WBS generation run produces insights that belong back in the source. Skip this only if the source was a chat-pasted brain dump with no file to update.

### What to Backport

After the WBS is finalized, review the source document against these categories:

| Category | What to Look For | How to Update |
|----------|-----------------|---------------|
| **Gap resolutions** | Answers the user provided in Phase 3 that aren't in the original doc | Add them to the relevant section (scope, requirements, constraints, etc.) |
| **Scope clarifications** | In/out-of-scope boundaries that were implicit or missing | Add an explicit Scope section or update the existing one |
| **Assumptions surfaced** | 🟢 Nice-to-have defaults you assumed during generation | Add an Assumptions section or append to existing one |
| **Missing deliverables** | Deliverables the WBS identified that the doc never mentioned | Add to the deliverables/objectives section |
| **Dependency discoveries** | External dependencies or prerequisites found during decomposition | Add to a Dependencies or Risks section |
| **Contradictions resolved** | Conflicting info in the doc that you resolved with the user | Fix the contradicting passages to be consistent |
| **Terminology alignment** | Terms the WBS standardized (e.g., doc says "website" and "portal" interchangeably) | Pick one term and make the doc consistent |

### How to Update

1. **Read the original file** from its upload path. Use the appropriate file-reading method for the file type.
2. **Identify every modification** needed from the categories above. Build a mental changelog.
3. **Apply modifications** — preserve the original document's structure, style, and formatting. Insert new content where it logically belongs. Do not rearrange or rewrite sections that don't need changes.
4. **Add a changelog block** at the end of the document (or as a comment if the format supports it):

   ```markdown
   ---
   ## 📋 WBS Reconciliation Log
   
   > The following updates were applied based on WBS generation and gap analysis.
   
   | # | Section Modified | Change Description |
   |---|-----------------|-------------------|
   | 1 | Scope | Added explicit in/out-of-scope boundaries |
   | 2 | Requirements | Added technology stack decision (React + Node) |
   | 3 | Assumptions | New section — listed 3 assumptions from WBS |
   ```

5. **Save the updated file** as an output file using the original filename (preserving extension). If the original was `project-brief.md`, the output is `project-brief.md` — not `project-brief-updated.md`. The user gets back their own document, improved.
6. **Present both files** to the user: the WBS artifact first, then the updated source document. Briefly summarize what changed in the source (3–5 bullet points max, not the full changelog — that's in the document itself).

### When the Source is Not a File

- **Chat-pasted text**: Generate a new markdown file containing the original content plus the backported updates. Name it `[project-name]-project-brief.md`.
- **Multiple source files**: Update each file that needs changes. If changes span files, note cross-file dependencies in the changelog.
- **Binary/complex formats** (DOCX, PDF, PPTX): Read content, produce the updated version in markdown. Note in the output that the user may want to port changes back to their original format manually, or offer to produce the updated file in the original format if the appropriate skill is available.

### Vault Source (Project Plan in the Vault)

When the source was `{project}-project-plan.md` from the vault, don't produce a copy. Show the
backport as a short list of changes; on confirmation, edit the plan **in place**: read it for
its etag, write with `if_match` = that bare-hex etag, never `"*"`. A 412 means it changed since
you read it: re-read, say so, ask. The plan's format belongs to `project` mode and bandit:notes;
change content only.

---

## 💾 Saving the WBS to the Vault

**Ask bandit:notes for the folder**, never hard-code it: `Projects/{slug}/`, or
`Projects/{slug}/planning/` on a project with sprint folders (its conventions §1). When that folder
exists, offer: *"Save this WBS as `{project}-wbs.md` in {folder}?"*

**Only the final file is saved.** Drafts stay in the chat: never written to `_inbox/` or anywhere
else in the vault.

| Case | Write |
|---|---|
| No `{project}-wbs.md` yet | Create it with **no `if_match`** (fails closed if it appeared meanwhile: stop and ask) |
| It exists | Show that it will be replaced, then on confirmation read its etag and write with `if_match` = that etag. **Carry its `## 🔗 Card links` rows over unchanged** |

Frontmatter follows the bandit:notes conventions (`type: reference`, `status: triaged`, `project`
linking the hub note). No version numbers, no copies, no stored IDs (the one exception: card ids
in `## 🔗 Card links` on dev projects), never delete.

**Card links rows for cards that already exist** (sprint mode): this chat writes them, through
bandit:notes, as its own approval row on the saved file (an etag-guarded edit, `updated` bumped).
The row format is this skill's; the write is bandit:notes'.

Next step to offer: *"Want it on the board? `/bandit:tasks load` builds the project from it."*
When the project's home board is Technical, offer the dev route instead: `/bandit:tasks spec` per work package, then
`/bandit-dev:sprint plan` in Claude Code (bandit:tasks `references/dev-workflow.md`); in sprint mode,
hand back to bandit-dev:sprint.

---

## 🧩 Edge Cases

- **Very small project** (< 10 work packages): Still follow the full structure but collapse Levels — you may only need L0 → L1 → L2 (no L3). Mention this in the output. **Not on dev projects:** there L3 always exists (bandit:tasks `references/dev-workflow.md` → WBS on dev projects).
- **Very large project** (> 100 work packages): Suggest splitting into sub-projects or program-level WBS. Offer to generate one phase at a time.
- **No uploaded document — just a chat description**: Treat the chat context as the "document." Phase 2 gap analysis will likely surface more gaps, which is expected.
- **Multiple documents**: Ingest all of them. Cross-reference for contradictions and flag any.
- **Document is a brain dump / messy notes**: That's fine — the skill is designed for this. Extract what you can, gap-analyze the rest.
- **User wants to iterate**: After generating, the user may say "add X" or "remove Y" or "break down WBS-3.2 further." Update the artifact in place, preserving all IDs (don't renumber existing items — append new sub-IDs).
- **User asks for estimates**: The WBS itself does NOT include time or cost estimates (WHAT, not WHEN or HOW MUCH). If asked, offer to add an "Estimated Effort" column to the work package tables as a separate pass, but note this is supplementary. **In sprint mode, never:** the WBS carries no sizes; sizing is bandit-dev:sprint's step 4.

---

## ✅ Quality Checklist (Self-Review Before Output)

Before presenting the final WBS, verify:

- [ ] Every Level 1 phase passes the 100% rule (children cover all parent scope)
- [ ] Every Level 2 deliverable passes the 100% rule
- [ ] All work packages are between 8–80 hours of effort (conceptually)
- [ ] All WBS IDs are sequential and correctly nested
- [ ] Dependencies use valid WBS IDs that exist in the document
- [ ] No circular dependencies
- [ ] Emoji anchors on all H2 and H3 headings
- [ ] All structured data is in tables, not prose
- [ ] No prose paragraph exceeds 3 sentences
- [ ] Assumptions section lists everything inferred (not stated by user/doc)
- [ ] The overview section alone gives a reader the full picture at high level
- [ ] Source document has been updated with all gap resolutions from Phase 3 (not in migration or sprint mode)
- [ ] Source document changelog lists every modification made
- [ ] Updated source preserves original structure and formatting
- [ ] Both files (WBS + updated source) are presented, or the vault plan was edited in place
