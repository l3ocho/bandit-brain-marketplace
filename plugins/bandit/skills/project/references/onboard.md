# 🚀 Onboarding: one command for the whole project

> Read for `/bandit:project onboard`. New projects also read `references/interview.md`; existing ones run `references/audit.md` first.

## 🚀 Onboarding — one command for the whole project

**This skill is the only way a project gets onboarded.** The user runs it once; it does the
instructions, the vault and the board together. bandit:notes and bandit:tasks keep owning their
own rules: this skill loads them and runs their onboarding procedures, it never restates them.

| Step | What | Who |
|---|---|---|
| 1 | Interview (new project) or audit (existing project): the five Project Context values (+ optional `dev`), the hub-note summary, and the modules when the domain is new | This skill |
| 2 | **Vault rows:** load the `bandit:notes` skill and run its *Onboarding rows* (Part 3) with `domain`, `project`, `type`, `dev` (when set), whether the project has a Claude Code surface, the summary and the modules | bandit:notes |
| 3 | **Board rows:** load the `bandit:tasks` skill and run `references/onboard.md` with the board answer, project name, board type and folder, plus `dev: true` when set (onboard then adds its dev board shape rows to the same proposal) | bandit:tasks |
| 4 | **Settings rows:** the instructions and reference doc files in `Claude/ai-{slug}/` (see **Vault Folder**) | This skill |
| 5 | **One proposal** with every row from steps 2–4 and a fix row for every finding, then the closing line | This skill |
| 6 | Execute exactly the approved rows, in order: vault → board → settings files. Report per row | Each owner's procedure |
| 7 | Hand over the instructions to paste | This skill |

**The one proposal:**

```
| # | Step | Action | Target | Why |
|---|---|---|---|---|
| 1 | vault | create folder | MyNotes/Acme/Projects/home-reno/ | project folder |
| 2 | vault | create note | …/Projects/home-reno/home-reno.md | hub note: summary below |
| 3 | vault | create folder | MyNotes/Acme/Claude/ai-home-reno/ | settings folder |
| 4 | board | create board project | "Home Reno" · deliverable · folder "Acme" | board: project "Home Reno" |
| 5 | settings | create file | …/Claude/ai-home-reno/hr-instructions-v0.md | instructions |
| 6 | settings | create file | …/Claude/ai-home-reno/hr-prompt-reference-v0.md | reference doc |
```

**Findings come fixed.** Anything noticed along the way (a legacy folder elsewhere in the
domain, a stale `board:` line) is a **row in the same table**, step `fix`, with its owner's exact
action (vault fixes come from bandit:notes as `domain` rows). Never a bare list. Two valid fixes →
one row with both, recommended first. Then: *Nothing is created or changed until you answer all,
a list, or none.*

**Rules:**
- **Length gate first.** Before any interview, audit, targeted update or version write, count
  the instructions' words without the metadata comment (`sed 1d {file} | wc -w`), and both copies
  for a twin. Over the tier's target in **Token Budget Targets** (`references/reference-template.md`,
  never above 1,000) → the trim is built first and is row 1 of the same proposal: cut what the
  reference doc already holds, move detail there. Never write or hand over a version over the budget.
- **Step 3 is bandit:tasks' procedure, loaded and run.** Never swap it for a quick check of your
  own. Each board row cites the `list_projects` entry it came from.
- **Approval covers the approved rows and nothing else.** Every finding has its own row, so one
  "all" fixes everything; a row the user didn't approve never runs. Nothing outside this project's own
  folders is touched except by a `fix` row they approved.
- A row that depends on a declined row is skipped and reported (the hub note without its folder,
  the settings files without `Claude/ai-{slug}/`).
- The Project Context written into the instructions reflects what was approved: `domain:` is the
  real domain whenever a vault is used (`none` only for a custom path or artifact-only), and
  `board:` is the line bandit:tasks returned.
- **Existing projects run the same flow.** Audit the instructions, then steps 2–7 propose only
  what's missing (a wrong `domain:`, a missing folder, no board scope). Nothing missing → say so.
- bandit:notes' `init`/`onboard` and bandit:tasks' `onboard`, typed directly in a project chat to
  set up a project, point back here.
