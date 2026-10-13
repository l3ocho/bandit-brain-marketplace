---
name: "project-settings"
description: "Bootstraps and maintains Claude.ai project instruction sets, and is the one command that onboards a project: interviews for new ones, audits existing ones, runs the vault step (bandit-notes) and the board step (bandit-tasks) in one approval, writes the Project Context block (domain, project, type, board, prefix, optional dev) that every other skill reads, resolves the BanditBrains board scope, and syncs the instructions and their reference doc to the project's vault folder, MyNotes/{Domain}/Claude/ai-{slug}. Use when the user says \"project settings\", \"onboard this project\", \"onboard a new project\", \"set up this project\", \"write the project instructions\", \"audit these instructions\", \"update the instructions\", \"sync the instructions\", \"fix the Project Context\", or pastes project instructions and asks for a review. Do NOT use for planning the project itself (project-planner), filing vault notes (bandit-notes) or working the task board (bandit-tasks)."
---

# 🛠️ Project Settings Manager

Bootstrap and maintain Claude.ai project instruction sets. Produces structured, ND-friendly
instructions aligned to a canonical reference standard, with optional sync to the project's
settings folder in the MyNotes vault over WebDAV.

**Before doing anything else:** read `references/reference-template.md`. It defines every
section, its purpose, content rules and audit criteria, and the metadata block. That template
is the backbone.

---

## 🚀 Onboarding — one command for the whole project

**This skill is the only way a project gets onboarded.** Leo runs it once; it does the
instructions, the vault and the board together. bandit-notes and bandit-tasks keep owning their
own rules: this skill loads them and runs their onboarding procedures, it never restates them.

| Step | What | Who |
|---|---|---|
| 1 | Interview (new project) or audit (existing project): the five Project Context values (+ optional `dev`), the hub-note summary, and the modules when the domain is new | This skill |
| 2 | **Vault rows:** load the `bandit-notes` skill and run its *Onboarding rows* (Part 3) with `domain`, `project`, `type`, `dev` (when set), whether the project has a Claude Code surface, the summary and the modules | bandit-notes |
| 3 | **Board rows:** load the `bandit-tasks` skill and run `references/onboard.md` with the board answer, project name, board type and folder, plus `dev: true` when set (onboard then adds its dev board shape rows to the same proposal) | bandit-tasks |
| 4 | **Settings rows:** the instructions and reference doc files in `Claude/ai-{slug}/` (see **Vault Folder**) | This skill |
| 5 | **One proposal** with every row from steps 2–4 and a fix row for every finding, then the closing line | This skill |
| 6 | Execute exactly the approved rows, in order: vault → board → settings files. Report per row | Each owner's procedure |
| 7 | Hand over the instructions to paste | This skill |

**The one proposal:**

```
| # | Step | Action | Target | Why |
|---|---|---|---|---|
| 1 | vault | create folder | MyNotes/BanditLabs/Projects/bandit-labs/ | project folder |
| 2 | vault | create note | …/Projects/bandit-labs/bandit-labs.md | hub note: summary below |
| 3 | vault | create folder | MyNotes/BanditLabs/Claude/ai-bandit-labs/ | settings folder |
| 4 | board | create board project | "Bandit Labs" · deliverable · folder "Bandit Labs" | board: project "Bandit Labs" |
| 5 | settings | create file | …/Claude/ai-bandit-labs/bl-instructions-v0.md | instructions |
| 6 | settings | create file | …/Claude/ai-bandit-labs/bl-prompt-reference-v0.md | reference doc |
```

**Findings come fixed.** Anything noticed along the way (a legacy folder elsewhere in the
domain, a stale `board:` line) is a **row in the same table**, step `fix`, with its owner's exact
action (vault fixes come from bandit-notes as `domain` rows). Never a bare list. Two valid fixes →
one row with both, recommended first. Then: *Nothing is created or changed until you answer all,
a list, or none.*

**Rules:**
- **Length gate first.** Before any interview, audit, targeted update or version write, count
  the instructions' words without the metadata comment (`sed 1d {file} | wc -w`), and both copies
  for a twin. Over the tier's target in **Token Budget Targets** (`references/reference-template.md`,
  never above 1,000) → the trim is built first and is row 1 of the same proposal: cut what the
  reference doc already holds, move detail there. Never write or hand over a version over the budget.
- **Step 3 is bandit-tasks' procedure, loaded and run.** Never swap it for a quick check of your
  own. Each board row cites the `list_projects` entry it came from.
- **Approval covers the approved rows and nothing else.** Every finding has its own row, so one
  "all" fixes everything; a row Leo didn't approve never runs. Nothing outside this project's own
  folders is touched except by a `fix` row he approved.
- A row that depends on a declined row is skipped and reported (the hub note without its folder,
  the settings files without `Claude/ai-{slug}/`).
- The Project Context written into the instructions reflects what was approved: `domain:` is the
  real domain whenever a vault is used (`none` only for a custom path or artifact-only), and
  `board:` is the line bandit-tasks returned.
- **Existing projects run the same flow.** Audit the instructions, then steps 2–7 propose only
  what's missing (a wrong `domain:`, a missing folder, no board scope). Nothing missing → say so.
- bandit-notes' `init`/`onboard` and bandit-tasks' `onboard`, typed directly in a project chat to
  set up a project, point back here.

---

## 🔍 Mode Detection

Determine which mode to operate in based on the current project state.

**Check the current project instructions** (they're visible as the system prompt in this conversation):

| Condition | Mode | Action |
|-----------|------|--------|
| No instructions, or only a project name / placeholder text | **New Project** | Run the interview flow |
| Substantive instructions already present | **Existing Project** | Run the audit flow |
| The change is for **another** project (bandit-audit runs a settings row, or Leo names a project that isn't this one) | **Vault update** | Run **🎯 Targeted update from the vault**. Never interview: this chat's own instructions aren't the target |

If ambiguous (e.g., a few lines that might be intentional or might be a stub), ask the user:
> "I see some brief instructions already in this project. Should I treat this as a fresh start
> and interview you for a complete set, or audit what's here and fill gaps?"

---

## 🆕 New Project Mode — Interview Flow

No instructions yet → read `references/interview.md` and follow it: four chunked phases
(context and stack, role and authority, conditional sections, optional sections and output),
then generation. It fills every Project Context key, and its board question hands off to
bandit-tasks exactly like **🚀 Onboarding** step 3.

---

## 🔄 Existing Project Mode — Audit Flow

Analyze current instructions against the reference template. Produce a gap report and an
updated instruction set.

### Step 0: Collect User Updates

Before auditing, ask the user what's changed or what they want to address. Use a combination
of open-ended and structured input:

1. **What's changed?** (open-ended) — "Anything new since these instructions were last updated?
   New repos, changed stack, shifted priorities, dropped features?"
2. **What do you want to do?** (single select via `ask_user_input`) — Options:
   - "Full audit — check everything against the reference standard"
   - "Targeted update — I know what I want to change"
   - "Just sync to the vault — instructions are fine, just save them"

If "Targeted update": ask what specifically they want to change, then skip to Step 5
(generate updated version) incorporating their changes without running the full audit. For
another project's instructions, use **🎯 Targeted update from the vault** instead.

If "Just sync to the vault": read `storage_backend` from the metadata. `"webdav"` → go to
**Vault Folder (WebDAV)**. `"notes"` → run the ⚠️ Legacy Notes backend migration first.
`null` or absent → ask the output target question first.

If "Full audit": incorporate any updates they shared into the analysis and continue below.

### Step 1: Read & Inventory

Read the current project instructions completely. Map each existing section to a reference
template section. Note:

- **Present sections** — which reference sections are covered?
- **Missing sections** — which required sections are absent?
- **Unmapped content** — any content that doesn't fit a reference section?
- **Metadata block** — is it present? What reference version was used?
- **Project Context** — is the `## 🧭 Project Context` section present, right after Project
  Overview, with all five required keys and valid values? A `dev:` line must say `true`; any
  other value → propose fixing or removing the line. No `dev:` line is never a finding. Check them live: `domain` is a folder in
  `MyNotes` (or `none`), `board` resolves via `list_projects` (or is `none` / `pending`).
  Naming, board type and footprint aren't judged here: run `/bandit-audit check` in this project
  and carry its rows into the proposal (skip it for `domain: none`: bandit-audit scores domain
  projects only).
  - **Missing (legacy instructions)** → flag ⚠️ **Legacy context** and build the block from what
    the old instructions carry: `vault_domain` → `domain` (`null` → `none`), `vault_project` →
    `project`, `project_type` → `type`, `note_prefix` → `prefix` (`null` → `none`), and the
    `scope:` line of a `## 🗺️ Task Board Scope` section (or a `taskops_scope` metadata field) →
    `board` (neither → `none`). Propose it as a fix, and on the updated version drop those
    five fields from the metadata comment and the old scope section.
- **Legacy lifecycle** — a `lifecycle` object in the metadata, or a `## 🔄 Project Lifecycle
  Workflow` section, is left over from the old project-planner. project-planner now keeps its
  plan, architecture and WBS in the vault's `Projects/{project}/` and reads its state from those
  files. Flag ⚠️ **Legacy lifecycle** and, on the updated version, drop both. Take `project_slug`
  and `prefix` into the Project Context `project:` / `prefix:` if those are still empty. Old
  lifecycle notes in the Notes app stay where they are; this skill never touches them.
- **Legacy Notes backend** — `storage_backend: "notes"`, or a `note_id` with no
  `storage_backend`. The Notes app is no longer a destination. Flag ⚠️ **Legacy Notes backend**
  and offer to migrate: ask the Phase 4 domain, slug and prefix questions (`references/interview.md`), then do a **First
  Write** into the vault folder (next version numbers after the ones in the metadata), and on
  the updated metadata set `storage_backend: "webdav"` and drop `note_id`, `ref_doc_note_id`
  and `note_category`. The old notes stay in the Notes app. Declined → artifact-only.

### Step 2: Audit Against Criteria

For each present section, evaluate against the audit criteria in the reference template.
Score each as:

| Rating | Meaning |
|--------|---------|
| ✅ **Pass** | Meets all audit criteria |
| ⚠️ **Needs attention** | Partially meets criteria, specific improvement identified |
| ❌ **Fail** | Missing required content or violates a criterion |

### Step 3: Redundancy Scan

Check for information repeated across sections. Flag every instance with the specific
duplicate content and which sections contain it.

### Step 4: Present Findings

Output the audit as a structured report:

```
## 📋 Audit Report

**Reference Version:** 1.0
**Instructions Version:** [from metadata or "none found"]
**Overall:** [X/Y sections pass] · [N redundancies found] · [Token count vs. target]

### Section Scores

| Section | Status | Notes |
|---------|--------|-------|
| Project Header | ✅ | Current |
| Project Overview | ⚠️ | Tech stack implied, not named |
| Role Definition | ❌ | Missing — generic "helpful assistant" |
| ... | ... | ... |

### 🔁 Redundancies Found
- [Rule X appears in both Hard Rules and Area-Specific Rules for repo Y]

### 🔧 Fix rows (each one is also a row in the proposal)
1. [Highest impact fix first]
2. [Next fix]
...
```

### Step 5: Generate Updated Version

Don't ask whether to fix. Build the updated version straight away and show it with the report;
its version files are rows in the one proposal, so Leo's answer to the proposal is the approval.

1. Preserve all existing content that passes audit
2. Fill gaps identified in the audit
3. Resolve redundancies (keep in the most specific section)
4. Apply ND-friendly formatting
5. Update metadata block (bump version, set ref_version to current)
6. Run steps 2–7 of **🚀 Onboarding**: propose whatever the vault and board are missing
   together with the new version files, in one proposal (artifact-only → board rows only)

If the existing instructions already have a vault destination (`webdav_folder`), default to a
version bump using the existing naming convention; the new version files are rows, never written before Leo's yes.

---

## 🎯 Targeted update from the vault

Updates **another** project's instructions from its vault copy, because only a project can see
its own instructions. bandit-audit runs this for its settings rows. Leo can run it too ("update
the Family instructions: board is now …").

**Inputs:** the settings folder (`MyNotes/{domain}/Claude/ai-{project}`), the production file
(the one matching the project's self-check stamp, given by the caller; not given → list the
folder and ask, never assume the highest `v{N}`), and the exact change.

1. **Read** the production instructions file raw, and keep its etag. Missing or unreadable → stop
   and report; nothing is written.
2. **Apply only the requested change** to this version. No audit, no reformatting. Anything else
   noticed goes back as an **extra fix row** (target + exact change) in the same hand-over, for
   the caller's proposal: never folded in silently, never just mentioned. Check the new value
   live, except a `board:` name that belongs to an approved rename not run yet: check that the old name still resolves, and say the new one is
   checked when the board row runs.
3. **Bump** the `**Version:**` and `**Last Updated:**` lines and the metadata, as Step 5 does.
4. **Write** the next instructions version with **Subsequent Writes** in
   `references/vault-storage.md`, as an approved row. The prompt-reference file is not bumped.
   **Project copy** is skipped: this chat's project is not the target.
5. **Hand over** the file name and the full text to paste, with the Claude.ai project it goes into.
   After the paste: `/bandit-audit check` in that project, unless it has `domain: none`
   (bandit-audit scores domain projects only).

---

## 🧾 Metadata Storage Fields

The metadata block carries the storage destination; the reference template documents the
other fields. The project's identity (domain, slug, type, board, prefix) is **not** here: it
lives in the **Project Context** section.

| Field | Type | Description |
|-------|------|-------------|
| `storage_backend` | `"webdav"` / `null` | `"webdav"` = the vault folder holds the files. `null` = artifact-only. Legacy `"notes"` → see the audit flow |
| `webdav_folder` | string/null | Full folder path, no leading slash (e.g., `MyNotes/Personal/Claude/ai-bandit-infra`). Derived from the Project Context `domain` + `project` unless the user chose a custom path. `null` when artifact-only |
| `instructions_etag` | string/null | Etag of the current instructions file, for drift detection. **Bare hex** — see Etag Drift Detection |
| `prompt_ref_etag` | string/null | Etag of the current prompt reference file. **Bare hex** |
| `instructions_version` | int/null | Integer version of the instruction set |
| `prompt_ref_version` | int/null | Integer version of the prompt reference doc |

With `storage_backend: null`, every storage field is `null`.

Example:

```json
{"storage_backend": "webdav", "webdav_folder": "MyNotes/Personal/Claude/ai-bandit-infra",
 "instructions_etag": "a1b2c3", "prompt_ref_etag": "d4e5f6",
 "instructions_version": 0, "prompt_ref_version": 0}
```

---

## 📤 Output Handling

Both modes produce **two deliverables**: the instruction set and the supporting project reference doc.
In audit mode, the reference doc is updated (or created if it doesn't exist yet).

### Output Target Selection

**New Project mode:** Phase 4 of `references/interview.md` asks the output target question (single select).

**Audit mode:** Read `storage_backend` from the metadata first, then:

| `storage_backend` | Behaviour |
|---|---|
| `"webdav"` with a `webdav_folder` | Default to a version bump using the existing convention. Confirm before creating new versions |
| `"notes"`, or a `note_id` with no `storage_backend` | ⚠️ Legacy Notes backend: offer the migration (audit flow, Step 1) |
| `null`, absent, or destination fields empty | Ask the output target question below, then the Phase 4 folder questions |

> "Where should I save the updated instructions?"

Options (single select via `ask_user_input`):
- "Artifact only" (default)
- "Artifact + vault folder (WebDAV)"
- "Vault folder (WebDAV) only"

### Artifact (Default)

Output the instruction set for pasting into the Claude.ai project settings. The reference doc
goes to the project (see **Project copy**).

After outputting, remind:
> "Copy the instruction set into your project's Custom Instructions field in Claude.ai.
> The `<!-- project-settings: ... -->` comment on line 1 is invisible in the UI but
> helps me track versions during future audits.
> The reference doc is saved in this project as `claude/{name}` — it's your project's living memory."

### Vault Folder (WebDAV)

**Backend: `"webdav"`.** Writes the two deliverables as plain `.md` files into the project's
settings folder. Tools: `nc_webdav_write_file`, `nc_webdav_read_file`, `nc_webdav_list_directory`,
`nc_webdav_create_directory`. No `nc_notes_*` call belongs anywhere in this skill.

**Read `references/vault-storage.md` before any write to the folder, and before auditing it.**
It holds the file naming and versioning rules, the Notes-app collision check, the folder
existence check, the first-write and version-bump procedures, etag drift detection, the
missing-file case and the audit folder checks. The limits that always apply are in
**What This Skill Never Does** below.

### Project copy

Every time this skill produces the reference doc, whatever the output target, it saves it into
the Claude.ai project with the Projects tool, instead of showing it in the chat:

1. Name: `claude/{prefix}-prompt-reference-v{N}.md`, the same name as the vault file. Artifact-only
   (`prefix: none`): `claude/{project}-prompt-reference-v{N}.md`, next N from the doc list.
2. Read the doc list with `project_info`. The name is already there → stop and ask.
   `project_write` replaces an existing path silently, so it never gets one.
3. `project_write` with that `path`, the full doc as `content`, `present_to_user: false`.
4. Confirm in one line: the file name and what changed. Show the doc only if Leo asks.

No Projects tool in the session → output the reference doc as an artifact, and say in one line
that it wasn't saved to the project.

---

## 🧭 Project Context Section

This skill **owns the Project Context**: the one block every skill reads to learn which project
it is in (`bandit-notes`, `meeting-minutes`, `bandit-tasks`, `project-planner`, `wbs-generator`). The same block works on every surface: in the
Claude.ai project instructions, and in a repo's `CLAUDE.md` on Claude Code. Other skills read it
and point here; they never restate its format.

Always insert it, **immediately after Project Overview** — the other skills read it before doing
anything, so it must be near the top.

```markdown
## 🧭 Project Context

domain: {domain}
project: {project}
type: {type}
board: {board}
prefix: {prefix}
{dev: true — this line only when the project opted in}

Read by bandit-notes, meeting-minutes, bandit-tasks, project-planner and wbs-generator.
**Read anywhere. Write inside `board` only.**
Names only: skills resolve IDs live via `list_projects`. No hardcoded IDs, ever.
```

| Key | Values | Filled from (phases: `references/interview.md`) |
|---|---|---|
| `domain` | MyNotes domain folder (e.g. `Summitt`), or `none` | Phase 4 Domain question. `none` for a custom path and artifact-only |
| `project` | The project's own slug (e.g. `cs-notes`) | Phase 4 slug question. When it wasn't asked, suggest a kebab-case slug from the project name and confirm it |
| `type` | `product_service` · `workflow` · `claude_marketplace` | Phase 1 question 1 |
| `board` | `project "{name}"` · `folder "{name}"` · `global` · `none` · `pending` | Phase 1 question 5. Names exactly as `list_projects` returns them, quoted |
| `prefix` | 2–3 character filename prefix, or `none` | Phase 4 prefix. `none` when artifact-only |
| `dev` *(optional)* | `true`, or the line is absent | Phase 1 dev question (`references/interview.md`). Only for technical development projects that use the dev card workflow (bandit-tasks, bandit-notes) and sprints (bandit-sprint, Claude Code) |

**Format rules** (other skills parse this, so it is fixed): the heading text is `Project
Context`; one `key: value` per line; these five required keys, lower-case, plus the optional
`dev: true` line right after `prefix` (written only when the project opted in; otherwise
omit the line, never `dev: false`); nothing else inside the block except the two closing lines. `board` is asymmetric on purpose — planning needs
cross-board reads, but work from this project must never land on another project's board.

**How readers treat it:** a missing required key → ask; a missing `dev` line → not a dev project
(never ask); a value that doesn't check out (the board name no
longer resolves, the domain isn't in `MyNotes`) → stop and say so, never guess at the nearest
match. `board: none` or `pending` → bandit-tasks reads anywhere and writes nothing (except
`/bandit-tasks load` on `pending`).

### Repo copy (Claude Code)

For a `dev: true` project, Claude Code reads the same block from the repo's `CLAUDE.md`. This
skill **produces the exact block text** (identical to the Claude.ai one) and hands it over as a
repo change for Claude Code to make; it never writes to the repo itself. Whenever an update changes
the Claude.ai block, the hand-over adds one line: *the repo `CLAUDE.md` Project Context needs the
same edit.*

**Dev mirror.** When onboarding or auditing a `dev: true` project, read `references/dev-mirror.md`
and hand over its repo change: the mirror-check script in `.claude/hooks/`, a `Stop` command hook
in `.claude/settings.json` that runs it, and the gitignored stamp. From then on the script itself
copies `CLAUDE.md` + `.claude/` into the synced `MyNotes/{Domain}/Claude/code-{slug}/` at each
turn's end (no model, no connector), `.claude/` stored as `claude/`, never `settings.local.json` or `.claude/worktrees/`.
Git stays the source. Hand over the installed reference's script, never the vault mirror's (it lags).

### Claude Code twin (projects without `dev: true`)

A project without `dev: true` (any `type:`) has a Claude Code surface when Leo answers yes to the
Claude Code question (`references/interview.md`, Phase 1) or `Claude/code-{slug}/` already exists.
It then runs as **twins**: the Claude.ai instructions and a Claude Code `CLAUDE.md`. The surface
never changes scope: `type:` decides it (a `product_service` twin still writes only inside its own
`board:`). A `dev: true` project gets the dev mirror instead, never a twin.

| Part | Rule |
|---|---|
| Core | Byte-identical in both: everything outside the Environment section, `**Version:**` included |
| `## 🖥️ Environment` | The one section that differs (`references/reference-template.md`): Claude.ai = planning, no local files; Claude Code = local working files, execution |
| Vault copy | `MyNotes/{Domain}/Claude/code-{slug}/CLAUDE.md`, as an approved row: created fail-closed, then edited with its bare-hex etag on each version. Old versions live in `ai-{slug}/` |
| Live file | Handed to Claude Code as a local change. This skill never writes the local folder |
| Reference doc | One copy only, the `{prefix}-prompt-reference-v{N}.md` in `ai-{slug}/`. Claude.ai reads its **Project copy**; the Claude Code `## 🖥️ Environment` names that vault path and reads it through BanditCloud when a rule points to it. Never copied into the local folder, never `@`-imported (that loads it every session) |
| Permissions | `code-{slug}/claude/settings.json`: the permission rules and hooks the Claude Code twin runs under. Same handling as the vault copy: an approved row, created fail-closed, edited with its bare-hex etag, handed to Claude Code as a local change. Never `settings.local.json` |
| Working folder (S12) | The layout guard: `code-{slug}/claude/hooks/workdir.py` (this skill's `scripts/workdir.py`, byte for byte), its two hooks and allow rules in `settings.json`, and one Environment line. Read `references/workdir.md` on onboarding, on every twin version change, and for an S12 row |

**Twin sync.** Any version change to either twin produces the matching change for the other in
the same output, and ends with one line: *apply both: paste the Claude.ai instructions, and have
Claude Code update its `CLAUDE.md`.*

---

## ⚠️ Gotchas

- **2026-09-24 · Onboarding was split across three skills.** Leo set up the bandit-labs project
  here, got `domain: none`, and then bandit-notes refused to create anything and the board was
  never set. → Onboarding is one run of this skill: vault, board and settings rows in one
  proposal (**🚀 Onboarding**). `domain:` is never `none` when a vault is used.
- **2026-09-25 · Workflow projects had no project folder.** Onboarding showed only the settings
  path for `type: workflow`, so those projects had nowhere to keep their own docs. → Every
  project gets both paths; the vault rows come from bandit-notes, which owns that rule.
- **2026-09-25 · The reference doc reached the project only sometimes, and was shown in full in
  the chat.** → Always save it with **Project copy** (`present_to_user: false`, one-line
  confirmation).
- **2026-09-27 · The Personal onboarding audit skipped the board step.** The chat ran its own
  `list_projects` check instead of loading bandit-tasks' onboard step, never opened the structure
  rulebook, and wrote "no board rows, scope is already correct". The board names were wrong. →
  Step 3 is loaded and run, never swapped for a quick check (**🚀 Onboarding** rules); structure is
  judged by `/bandit-audit check`.
- **2026-09-29 · Audits flagged problems and stopped.** Findings sat in a list below the proposal,
  and the audit asked "want me to generate an updated version?" instead of building it. → Findings
  come fixed: every finding is a row in the one proposal, and the updated version is built
  straight away (**🔄 Existing Project Mode**, Step 5).
- **2026-09-29 · The Claude Code twin had no way to reach the reference doc.** Only Claude.ai got a
  Project copy, so detail moved out of the instructions was lost on the Claude Code side. → The
  twin's Environment names the vault path of the reference doc (**Claude Code twin** table).
- **2026-09-29 · Bandit CTO reached the Claude Code onboarding at 1,389 words.** The budget was
  only a warning at the end, so a full run finished on instructions that were already over it. →
  The length gate runs first, and an over-budget trim is row 1 (**🚀 Onboarding** rules).
- **2026-09-29 · An update proposed archiving the live instructions.** The archive row came from the
  metadata's `instructions_version`, but the stamp said an older file was production. → S7 archive
  rows name production from the stamp ledger (`stamps.json`); no stamp → no archive row.
- **2026-09-30 · Onboarding installed the old dev-mirror script** from the lagging vault mirror and
  cheat-sheet prompt. → Hand over the installed `references/dev-mirror.md` (**Dev mirror**).

---

## 🚫 What This Skill Never Does

- **Leave a finding without a fix row**, or stop an audit at a question when the fix is known
- **Create, rename or restructure anything on a BanditBrains board** — except what bandit-tasks'
  onboard procedure proposes as approved rows: one empty project, and for `dev: true` its dev
  board shape (lane and stage tags, lanes). No folders, columns or tasks
- **Store an ID** — no project, folder, note or task IDs in metadata or instructions. Names
  and paths only, resolved live
- Write project instructions programmatically into Claude.ai — the user always pastes
- **Call `project_write` on a path already in the project's doc list, or call `project_delete`** —
  old versions stay, as in the vault
- Inject new opinions or content not gathered from the user during the interview
- Remove existing content the user explicitly wants to keep (in audit mode, always ask before cutting)
- Write or hand over instructions over the token budget (1,000 words max): the trim comes first
- Generate duplicate information across sections
- Change `webdav_folder` or the Project Context `prefix:` without explicit user request
- Reference a prompt-reference version that doesn't match the current version in metadata
- **Delete or overwrite a file in the vault folder** — old versions stay.
  `nc_webdav_delete_resource` and `nc_webdav_move_resource` have no part in this skill
- **Pass `if_match: "*"` to `nc_webdav_write_file`** — it force-overwrites unconditionally and
  would destroy a version. Omit `if_match` and let the write fail closed
- **Compare or send an etag without normalising it to bare hex** — the read tool's `W/"…` form
  produces false drift reports and false "concurrent edit" failures
- **Create a directory in Nextcloud outside an approved row** — folders come from bandit-notes'
  onboarding rows or an explicit yes, never on the side
- **Move or rename a settings folder** — migrating to the MyNotes convention is `bandit-notes
  onboard`'s job; this skill only updates the metadata once the folder is in place
- **Put anything but the two settings files into `Claude/ai-{slug}/`**, or add YAML frontmatter
  to them
- **Write to the Nextcloud Notes app** — legacy projects are migrated to the vault, never
  written to the Notes app
- **Add a lifecycle block or lifecycle section** — project-planner reads its state from the
  vault; this skill only removes the legacy ones on an approved update
- **Write past a file missing from the listing** — see *If an Expected File Is Missing* in
  `references/vault-storage.md`