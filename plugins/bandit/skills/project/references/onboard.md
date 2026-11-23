# 🚀 Onboarding: one command for the whole project

> Read for `/bandit:project onboard`. New projects also read `references/interview.md`; existing ones run `references/audit.md` first. `references/surfaces.md` comes before both.

## 🚀 Onboarding — one command for the whole project

**This skill is the only way a project gets onboarded.** The user runs it once; it does the
instructions, the notes, the board and the settings together. bandit:notes and bandit:tasks keep owning their
own rules: this skill loads them and runs their onboarding procedures, it never restates them.

| Step | What | Who |
|---|---|---|
| 1 | The surface and the kind of agent (`references/surfaces.md`), then the interview (new project) or the audit (existing project): the five Project Context values (+ optional `dev`, `finance` and `notes`) and the hub-note summary | This skill |
| 2 | **Notes rows:** load the `bandit:notes` skill and run its *Onboarding rows* (Part 3) with `domain`, `project`, `type`, `dev` and `notes` (when set) and the summary | bandit:notes |
| 3 | **Board rows:** load the `bandit:tasks` skill and run `references/onboard.md` with the board answer, project name, board profile and folder, plus `dev: true` when set (onboard then adds its dev board shape rows to the same proposal) | bandit:tasks |
| 4 | **Settings rows.** Claude Code: `CLAUDE.md`, `.claude/settings.json`, and for a workflow agent the working-folder guard and its folders (`references/surfaces.md`, `references/workdir.md`). Both surfaces: the reference notes (`references/output.md`) | This skill |
| 5 | **One proposal** with every row from steps 2–4 and a fix row for every finding, then the closing line | This skill |
| 6 | Execute exactly the approved rows, in order: board → hub note (it needs its board) → files in the folder → reference notes. Report per row, each file read back | Each owner's procedure |
| 7 | Claude.ai only: hand over the instructions to paste | This skill |

**The one proposal** (a workflow agent in Claude Code):

```
| # | Step | Action | Target | Why |
|---|---|---|---|---|
| 1 | board | create board | "Home Reno" · workflow · folder "Acme" | board: project "Home Reno" |
| 2 | notes | create note | "Home Reno" · Docs · home-reno | hub note: summary below |
| 3 | settings | create file | CLAUDE.md | instructions v1.0.0, from the product_service template (text below) |
| 4 | settings | add keys | .claude/settings.json | the working-folder guard: 2 hooks, 3 allow rules (listed below) |
| 5 | settings | copy file | .claude/hooks/workdir.py | the guard script |
| 6 | settings | create folders | work/ data/ scratch/ _closed/ _backup/ | the layout |
| 7 | notes | create note | "Home Reno" · Docs · home-reno-reference | reference doc |
```

On Claude.ai, rows 3 to 6 do not exist; a row for the note `{slug}-instructions` is added, and the
instructions are handed over after the proposal runs.

**Findings come fixed.** Anything noticed along the way (a stale `board:` line, a settings line
left at the top of the instructions, a second hub note) is a **row in the same table**, step
`fix`, with its owner's exact action. Never a bare list. Two valid fixes → one row with both,
recommended first. Then: *Nothing is created or changed until you answer all, a list, or none.*

**Rules:**
- **Length gate first.** Before any interview, audit or write, count the instructions' words
  (`wc -w`). Over the tier's target in **Token Budget Targets** (`references/reference-template.md`,
  never above 1,000) → the trim is built first and is row 1 of the same proposal: cut what the
  reference doc already holds, move detail there. Never write or hand over a version over the budget.
- **Step 3 is bandit:tasks' procedure, loaded and run.** Never swap it for a quick check of your
  own. Each board row cites the `get_context → boards` entry it came from.
- **Approval covers the approved rows and nothing else.** Every finding has its own row, so one
  "all" fixes everything; a row the user didn't approve never runs. Nothing outside this project's
  own folder and board is touched except by a `fix` row they approved.
- A row that depends on a declined row is skipped and reported (the hub note without its board;
  the guard script without its settings keys).
- The Project Context written into the instructions reflects what was approved: `domain:` is the
  board folder's real name (`none` only for a project with no board folder), `board:` is the line
  bandit:tasks returned, and a `notes:` line is written only when the answer was `none`.
- **Existing projects run the same flow.** Audit the instructions, then steps 2–7 propose only
  what's missing (a wrong `domain:`, a missing hub note, no board scope, no guard). Nothing
  missing → say so.
- bandit:notes' `onboard` and bandit:tasks' `onboard`, typed directly in a project chat to set up
  a project, point back here.
