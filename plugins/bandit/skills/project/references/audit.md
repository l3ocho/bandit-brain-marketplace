# 🔄 Audit and mode detection

> Read for `/bandit:project audit`, and at the start of `onboard` to pick the mode.

## 🔍 Mode Detection

Determine which mode to operate in based on the current project state.

**Check the current project instructions** (they're visible as the system prompt in this conversation):

| Condition | Mode | Action |
|-----------|------|--------|
| No instructions, or only a project name / placeholder text | **New Project** | Run the interview flow |
| Substantive instructions already present | **Existing Project** | Run the audit flow |
| The change is for **another** project (bandit:audit runs a settings row, or the user names a project that isn't this one) | **Vault update** | Run **🎯 Targeted update from the vault** (`references/update.md`). Never interview: this chat's own instructions aren't the target |

If ambiguous (e.g., a few lines that might be intentional or might be a stub), ask the user:
> "I see some brief instructions already in this project. Should I treat this as a fresh start
> and interview you for a complete set, or audit what's here and fill gaps?"

---

## 🆕 New Project Mode — Interview Flow

No instructions yet → read `references/interview.md` and follow it: four chunked phases
(context and stack, role and authority, conditional sections, optional sections and output),
then generation. It fills every Project Context key, and its board question hands off to
bandit:tasks exactly like **🚀 Onboarding** (`references/onboard.md`) step 3.

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
another project's instructions, use **🎯 Targeted update from the vault** (`references/update.md`) instead.

If "Just sync to the vault": read `storage_backend` from the metadata. `"webdav"` → go to
**Vault Folder (WebDAV)** (`references/output.md`). `"notes"` → run the ⚠️ Legacy Notes backend migration first.
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
  other value → propose fixing or removing the line. No `dev:` line is never a finding. A
  `finance:` line must read `accounts "…"` with each name an account `finance_get_context` returns;
  a name that doesn't resolve → propose the fix. No `finance:` line is never a finding. Check them live: `domain` is a folder in
  `MyNotes` (or `none`), `board` resolves via `get_context → projects` (or is `none` / `pending`).
  Naming, board type and footprint aren't judged here: run `/bandit:audit check` in this project
  and carry its rows into the proposal (skip it for `domain: none`: bandit:audit scores domain
  projects only).
  - **Missing (legacy instructions)** → flag ⚠️ **Legacy context** and build the block from what
    the old instructions carry: `vault_domain` → `domain` (`null` → `none`), `vault_project` →
    `project`, `project_type` → `type`, `note_prefix` → `prefix` (`null` → `none`), and the
    `scope:` line of a `## 🗺️ Task Board Scope` section (or a `taskops_scope` metadata field) →
    `board` (neither → `none`). Propose it as a fix, and on the updated version drop those
    five fields from the metadata comment and the old scope section.
- **Project Context lines** — the three lines under the keys must read word for word as the block in
  `references/project-context.md` (who reads it, the scope line, the names-only line). Any other
  wording (old skill names, an old scope line, an old lookup tool) → ⚠️ **Legacy context lines**:
  the updated version carries the current three lines.
- **Legacy tool names** — every Bandit Brain tool the instructions name, anywhere, must be a current
  one: `get_context`, `list_tasks`, `get_task`, `add_comment`, `list_events`, `create_tasks`,
  `update_tasks`, `reopen_tasks`, `delete_tasks`, `manage_subtasks`, `manage_recurrence`,
  `link_tasks`, `manage_projects`, `manage_columns_lanes`, `manage_tags`, `manage_folders`,
  `set_visibility`, `delete_board_items`, and the Finance tools `finance_get_context`,
  `finance_list_transactions`, `finance_get_budget`, `finance_list_schedules`, `finance_get_report`,
  `finance_list_rules`, `finance_get_account_history`, `finance_manage_accounts`,
  `finance_manage_transactions`, `finance_manage_budget`, `finance_manage_categories`,
  `finance_manage_payees`, `finance_manage_schedules`, `finance_import_transactions`,
  `finance_manage_reconciliation`, `finance_manage_rules`, `finance_delete_items`. Any other board
  tool name → ⚠️ **Legacy tool name**: the
  updated version names the current call (bandit:tasks references give the shape). On Claude Code,
  check the twin or repo `CLAUDE.md` the same way and list each hit in the hand-over; on Claude.ai,
  the hand-over adds one line: *check the Claude Code `CLAUDE.md` for board tool names that aren't current.*
- **Legacy lifecycle** — a `lifecycle` object in the metadata, or a `## 🔄 Project Lifecycle
  Workflow` section, is left over from the old planning skill. `/bandit:plan project` now keeps its
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
its version files are rows in the one proposal, so the user's answer to the proposal is the approval.

1. Preserve all existing content that passes audit
2. Fill gaps identified in the audit
3. Resolve redundancies (keep in the most specific section)
4. Apply ND-friendly formatting
5. Update metadata block (bump version, set ref_version to current)
6. Run steps 2–7 of **🚀 Onboarding** (`references/onboard.md`): propose whatever the vault and board are missing
   together with the new version files, in one proposal (artifact-only → board rows only)

If the existing instructions already have a vault destination (`webdav_folder`), default to a
version bump using the existing naming convention; the new version files are rows, never written before the user's yes.
