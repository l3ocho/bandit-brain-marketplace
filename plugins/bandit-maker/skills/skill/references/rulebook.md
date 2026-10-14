---
type: reference
summary: House standard for the user's own skills. Audits score against these 15 rules; Curate and Portfolio review apply them.
updated: 2026-10-13

---
# 📏 Skill Rulebook

> House standard for the user's own skills. Audits score against these 15 rules; Curate and Portfolio review apply them.

## 🗺️ Overview

- **9 musts** (R1–R5, R12–R15): a break is ❌ and the skill gets a fix proposal.
- **6 shoulds** (R6–R11): a break is ⚠️, fixed when the skill is touched anyway or when the user asks.
- A rule that doesn't apply to a skill scores **—** (e.g. R5 for a skill that never writes, R12 for a skill that never audits or reviews).
- **Score line:** `musts 9/9 · shoulds 4/6 · 2026-09-30`.
- **Sources:** the skill-authoring article (Tahir), `bandit-maker:skill` (which builds these skills), and conventions the existing skills already share.
- **The gate is code.** `scripts/house_lint.py` (in `bandit-maker:skill`) checks R1, R3, R7, R10, R11 and R15 before any change ships: `package_skill.py` runs it and refuses to build on a ❌, and the marketplace repo's `scripts/check_repo.py` runs it over every skill before each commit. Judgment rules (R2, R4, R6, R8, R12, R13, R14) stay with review in `bandit-maker:skill`.

---

## ❌ Musts

### R1 · Frontmatter

- `name`: kebab-case, identical to the folder name.
- **Short names; the plugin is the brand.** Skills ship as plugins of the `bandit-brain` marketplace, so the plugin namespace carries the brand (`bandit:tasks`, `bandit-dev:sprint`). A skill's own name never repeats it (2026-10-13, replacing the old `bandit-` prefix rule).
- `description`: **≤ 1024 characters**, the hard limit for saving a skill.
- **Check:** both keys present, names match, length counted. Anything above 1000 characters is ⚠️, because the next edit will break the limit.

### R2 · The description is a trigger

The description is what Claude scans to decide whether a skill applies. It isn't a summary for humans.

- Says **when** to use it (the situations and the phrases the user actually uses) as well as what it does.
- Leans a little **pushy**: Claude tends to under-trigger skills (`bandit-maker:skill`).
- Names **what it's not for**, and which skill handles that, whenever a neighbouring skill could steal the trigger (e.g. `clarify` ↔ `bandit:rewrite`).
- **Check:** could Claude pick this skill from the description alone, and turn it down for the neighbour's job? A pure "does X" description fails.

### R3 · Gotchas section

The highest-signal content a skill has: real failures, captured one at a time.

- `## ⚠️ Gotchas` in SKILL.md, one line per failure: **what went wrong → what to do instead**.
- A new skill starts with `None logged yet.`
- Past ~15 lines, move the list to `references/gotchas.md` and leave a pointer saying when to read it.
- **Check:** the section exists and every line has both halves.

### R4 · One owner per convention

A convention lives in exactly one skill. Other skills name that owner and never restate the rule.

| Convention | Owner |
|---|---|
| MyNotes vault: folders, filenames, frontmatter, inbox | `bandit:notes` |
| BanditBrains task vocabulary and board rules | `bandit:tasks` |
| Claude.ai project instructions and metadata | `bandit:project` |
| Project Context block (`## 🧭 Project Context`: keys and format, on Claude.ai and in `CLAUDE.md`) | `bandit:project` |

- **Check:** no copied rule blocks from an owner. A copy drifts the first time the owner changes.

### R5 · Safe writes

Applies to any skill that writes outside the chat (BanditCloud, boards, mail).

- **New files fail closed** (no overwrite). **Edits** carry the etag from the read. **Never force-overwrite.**
- **Delete** only what the user named or approved by exact path; never in an unattended run.
- **Resolve names live**; never store IDs.
- **Check:** each write path in the skill states which of these it uses.

### R12 · Findings come fixed

Applies to any skill that audits, reviews, lints or checks something. Added 2026-09-29, after the same failure turned up in five skills: problems were flagged as "findings" and left unfixed.

- Every finding comes back as a **numbered fix row in the same proposal**: the exact action, the target, the owner that runs it, and the recommended fix. Never a bare list, a "Notes" section or "for another run".
- A finding with two valid fixes is **one row with both options**, recommended first, settled at the same approval.
- Approval still gates every write: one "all" fixes everything, and only approved rows run. A read-only gate or subagent that CI or another tool reads returns the fix rows without applying them.
- Pure context that needs no fix (a denominator change, a count) is a one-line note, never a finding.
- **Check:** find every place the skill reports a problem. Each one has a fix row, and nothing says "flag", "report only", "do not fix" or "finding, never a row".

### R13 · Named homes and values

Applies to any skill that creates a record (a note, log, report, file, card section) or writes a field value. Added 2026-09-30, after onboarding shipped postmortems and a maintenance log with no home (bandit:tasks) and migrated notes with no `source:` value (bandit:notes).

- Every record type a skill creates names its **home**: the exact folder or filename pattern, taken from the owner's table (R4). A new record type is added to the owner first, in the same proposal.
- Every field value a skill writes is in the owner's **list of allowed values**. A new value is added to the owner's list in the same proposal.
- **Check:** every create step names its path pattern, and every value it writes appears in the owner's list.

### R14 · Read before overwrite

Applies to any skill that edits an existing record, section, line or field. Added 2026-09-30, after `plan-tech` could replace a branch line already recorded in a card's `Technical plan`.

- Read the current value first. Missing or empty → write it. The same → leave it. **Non-empty and different → show both and ask**; never replace it silently.
- An "add or replace" step names what it may replace and what it keeps.
- **Check:** each edit step reads first and says what happens to a non-empty value.

### R15 · Unique command names

Applies to any skill that defines or installs a slash command (a repo command such as `/incident`, a Claude Code command). Added 2026-09-30, after a repo triage command shared its name with `/bandit:tasks triage`.

- A bare `/name` command never reuses a command word of any in-scope skill, or the cheat sheet's.
- A skill's own name alone (`/bandit:clarify`) is an invocation, not a new command.
- **Check:** `house_lint.py` compares every bare `` `/name` `` in the skill's text with the `/skill command` words of every skill in the marketplace repo's `plugins/*/skills/`, plus any file passed with `--names` (e.g. the cheat sheet). A clash is ❌.

---

## ⚠️ Shoulds

### R6 · Don't state the obvious

Every section either moves Claude off a default or holds a the user-specific fact (paths, tools, conventions, preferences).

- **Check:** delete the section in your head. If Claude would behave the same without it, cut it.

### R7 · Progressive disclosure

- SKILL.md **under 500 lines** (`bandit-maker:skill`). Above that, move detail into `references/{topic}.md`.
- SKILL.md keeps the router: modes or commands, hard limits, gotchas, and pointers. Each pointer says **when** to read the file.
- The same content never lives in both SKILL.md and a reference file.
- **Gate at build:** no change ships with SKILL.md over 500 lines. `house_lint.py` blocks it like a must. An audit of an already-installed skill still scores it ⚠️.
- **Check:** line count; duplicated blocks between SKILL.md and `references/`.

### R8 · Don't railroad

- Fix what must be fixed: inputs, safety, hand-offs to other skills.
- Leave format and wording to context, **unless** the output feeds another skill or tool. Then a fixed format is justified, and the skill says so.
- **Check:** every rigid template has a stated consumer.

### R9 · Scripts for exact work

- Exact, repeated procedures (API payloads, parsing, validation, file conversion) go in `scripts/`, and SKILL.md says when to run them.
- Claude composes the pieces; it doesn't reconstruct them from prose each time.
- **Check:** long step-by-step exact procedures in prose are candidates for a script.

### R10 · Settings and state live outside the skill

- Skill folders are **read-only** in Claude.ai. Nothing the skill learns or stores goes inside them.
- **User-specific values** (domain, project slug, type, board scope, prefix) come from the `## 🧭 Project Context` section, owned by `bandit:project`; other paths from a clearly marked section. If one is missing, **ask**. Never guess.
- **Persistent state** goes to BanditCloud, in a location the skill names.
- **Check:** no instruction writes into the skill folder; no hardcoded ID.

### R11 · House format

- ND-friendly: an **emoji-anchored H2** per section, tables for structured facts, short lines, no walls of text.
- Somewhere near the top: what the skill is for and its modes or commands. Somewhere: a **Never / limits** section, and the gotchas (R3).
- Section order is otherwise free.
- **Forked upstream skills** (`bandit-maker:skill`) keep the upstream body format so upstream updates merge as a diff. They need only the house layer: Gotchas, a Never section, and any house-specific sections, each with an emoji H2.
- **Check:** scan the H2s alone. They should tell the skill's story. For a fork, check only the house layer.

---

## 🧭 Claude Code-only rules from the article

These don't apply to Claude.ai skills. They apply only to a plugin skill used inside Claude Code:

| Article rule | Why it's excluded here |
|---|---|
| `config.json` inside the skill folder | Skill folders are read-only in Claude.ai. R10 covers settings instead |
| Plugin data folder for memory | Claude Code plugin feature. R10 sends state to BanditCloud |
| On-demand hooks | Hooks don't exist in Claude.ai |

---

## 🔄 Changing this rulebook

- Changes follow the usual proposal flow, and the user approves them.
- After a change, the next Portfolio review re-scores every skill against the new version.
- A rule gets added when the same gotcha turns up in **two or more skills**. That's the signal it's a house rule, not a one-skill quirk.
- A rule the lint checks changes in `house_lint.py` in the same proposal.
- **2026-10-13 · Moved into the bandit-brain-marketplace repo** (sprint marketplace-v1): skill names follow the plugin namespaces, the R1 prefix rule became the short-name rule, and the gate also runs in the repo checker.
