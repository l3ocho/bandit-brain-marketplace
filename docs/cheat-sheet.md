---
type: reference
summary: Every command, mode and trigger of the bandit-brain skills (and two companion skills), grouped by skill, with modifiers and the reference files each one reads.
updated: 2026-10-20
---

# 🧭 Skills Cheat Sheet

> Every command, mode and trigger of the bandit-brain skills (and two companion skills), grouped by skill, with modifiers and the reference files each one reads.

> [!info] How to read this
>
> | Mark                        | Means                                                      |
> |-----------------------------|------------------------------------------------------------|
> | `/skill command`            | Slash command. The guaranteed way in. Plain words work too |
> | 💬                          | No command: say it in plain words and the skill triggers   |
> | `{value}` · `[value]` · `…` | Required · optional · can repeat                           |
> | ⚙️                          | Modifier: an option that changes what the command does     |
> | 📚                          | Reference file the skill reads, and when                   |
> | ✋ / ⚡ / 👀                  | Writes after you confirm · writes on its own · read only   |
>
> Kept in the bandit-brain-marketplace repo (`docs/cheat-sheet.md`) and changed in the same commit as the skills. Each skill's `SKILL.md` router is the source of truth; the repo gate fails when a skill command is missing from this page.

> [!important] Findings come fixed
> Every audit and review (bandit:audit, `/bandit:notes lint` and `onboard`, `/bandit:tasks audit`, `/bandit:project audit`, `/bandit-maker:skill lint`, `/data-tools review`) returns each finding as a numbered **fix row** in the same proposal, fix already built, recommended option first. Answer all, a list or none: one "all" fixes everything. Nothing runs without your yes, except bandit:audit, which runs every row on its own.

---

## 🗂️ At a glance

|     | Skill                                        | Start it with                 | Use it for                                                                       |
|-----|----------------------------------------------|-------------------------------|----------------------------------------------------------------------------------|
| 🗃️ | [[#🗃️ bandit:notes\|bandit:notes]]         | `/bandit:notes {command}`     | Vault rules, filing the inbox, domain home pages                                 |
| ✅   | [[#✅ bandit:tasks\|bandit:tasks]]           | `/bandit:tasks {command}`     | The Bandit Brain task board, plus the dev card workflow on Technical boards  |
| 🎙️ | [[#🎙️ bandit:minutes\|bandit:minutes]]   | `/bandit:minutes` + the audio | Meeting recording → minutes in the vault                                         |
| 💰  | [[#💰 bandit:finance\|bandit:finance]]      | `/bandit:finance {command}`   | The Finance module: log, import, sort, the budget month, bills, reconcile, review |
| 🛠️ | [[#🛠️ bandit:project\|bandit:project]] | `/bandit:project {command}`   | Onboarding (instructions + vault + board, one approval) and project instructions |
| 📐  | [[#📐 bandit:audit\|bandit:audit]]          | `/bandit:audit {command}`     | Domain and project structure: Claude.ai ↔ vault ↔ board                          |
| 🧭  | [[#🧭 bandit:plan\|bandit:plan]]            | `/bandit:plan {mode}`         | `project`: plan → architecture doc · `wbs`: docs or cards → work breakdown       |
| 🔍  | [[#🔍 bandit:clarify\|bandit:clarify]]      | `/bandit:clarify [idea]`      | A thought, no text yet → questions → clear spec                                  |
| ✨   | [[#✨ bandit:rewrite\|bandit:rewrite]]         | `/bandit:rewrite` + the text  | Text you already have → readable markdown, no questions                          |
| 💡  | [[#💡 prompt-engineer\|prompt-engineer]]    | 💬 "help me write the prompt" | Prompts for coding work                                                          |
| 🧪  | [[#🧪 bandit-maker:skill\|bandit-maker:skill]]    | `/bandit-maker:skill {command}` | Build, test, tune and lint skills                                              |
| 🧰  | [[#🧰 data-tools\|data-tools]]              | `/data-tools {command}`       | Databases, dbt, data audits, profiling, analysis, notebooks                      |
| 🏃  | [[#🏃 bandit-dev:sprint\|bandit-dev:sprint]] | `/bandit-dev:sprint {command}` | A dev project's sprint: plan, run its waves, debug, release, close             |
| 🌱  | [[#🌱 bandit-dev:testdata\|bandit-dev:testdata]] | `/bandit-dev:testdata {command}` | Made-up data in development, test and staging; each card's test data          |

> [!important] New project? Run **`/bandit:project onboard`** ("onboard this project"). It's the one onboarding command: it runs the vault step (bandit:notes) and the board step (bandit:tasks) and shows everything in one proposal.

---

## 📝 Notes & tasks

### 🗃️ bandit:notes

> [!abstract] Owns the MyNotes vault: folders, filenames, frontmatter, status, archiving, home pages
> `plugin` · [[bandit:notes/SKILL|open skill]] · domain comes from the Project Context `domain:`, from bandit:project during onboarding, or the command, or it asks

| Command                  | ⚙️ Modifiers           | Does                                                                                                                                                                                                                       |        |
|--------------------------|------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|
| `/bandit:notes`          | —                      | Lists the commands and asks which one                                                                                                                                                                                      | 👀     |
| `/bandit:notes onboard`  | `[Domain]`             | Audits a domain against the conventions, proposes the migration in stages A→D. New project → use `/bandit:project onboard`                                                                                                          | ✋      |
| `/bandit:notes init`     | `{Domain}`             | Scaffolds a new domain: core folders, modules, templates, README                                                                                                                                                           | ✋      |
| `/bandit:notes home`     | `[Domain]`             | Rebuilds the domain README home page. Safe to schedule                                                                                                                                                                     | ⚡      |
| `/bandit:notes file`     | `[Domain]` `[note…]`   | Reviews inbox notes you put up: destination, filename, frontmatter. Body edits only as separate rows. A plan note → `active`, linked from the hub's `## Docs`, and the report prompts `/bandit:tasks stage {card} planned`. A consumed inbox draft gets an archive row, on proof the filed copy exists | ✋      |
| `/bandit:notes lint`     | `[Domain]`             | Reports every convention breach, each as a numbered fix row (the report is the proposal). Plus plan-note checks: no `board-task`, card done but note not, card deleted. Plus frontmatter that doesn't parse, a filename also in `_inbox`, sprint briefs outside their sprint folder, a sprint project's root, triaged notes whose card is gone (asked, never acted on)                                                     | 👀 → ✋ |
| `/bandit:notes settings` | `[Domain]` · `restore` | Checks Obsidian settings and proposes changes. `restore` rolls back from backup. Obsidian closed on every device                                                                                                           | ✋      |
| `/bandit:notes archive`  | `[Domain]`             | Moves `status: done` notes into `_archive/`, a whole sprint folder at close, and old settings versions named by a structure audit (S7)                                                                                                                     | ✋      |
| `/bandit:notes restore`  | `{note}`               | Moves an archived note back to where it came from                                                                                                                                                                          | ✋      |
| `/bandit:notes delete`   | `{path…}`              | Deletes exactly the paths named                                                                                                                                                                                            | ✋      |

> [!tip] Scope
> `type: workflow` projects see the whole domain. Other projects see only their own `Projects/{slug}/`, inbox and settings. `init`, `home` and `settings` are domain-only. A finding outside the scope still comes as a fix row marked `domain`; your yes to that row by number runs it.

> [!warning] Only approved rows run
> "Yes" or "create it" approves the rows on the table, nothing else. Every finding is its own fix row in the same proposal, never a bare list.

> [!tip] Dev projects (`dev: true`, conventions §13)
> Plan notes: `type: plan`, named `{project}-{lane}-{slug}-plan.md`, written to `_inbox/` first, `board-task` = the card's id. The WBS doc gets a `## 🔗 Card links` table, one row per card created.
> Card briefs: one `type: brief` per card, `board-task` = the card's short id, H2s Summary · Scope · Requirements · Decisions · Verified facts · Open questions · Change log (optional) · Related. No card state (column, lane, stage) in the body; a `Card: {short id}` line is fine.
> Sprint folders: `Projects/{slug}/sprint-{name}/` holds `{project}-sprint-{name}-plan.md` (no `lane`, `board-task` = the sprint card), `-handover-prompt.md`, `-progress.md`, `-handover-report.md` and the sprint's briefs, written straight in. Once a project has one, its root holds only the hub, `sprint-*` and `planning/` (WBS, plan, architecture, notes not yet in a sprint). A closed sprint archives as one folder.

📚 **References:**

- `references/model.md`: before any command (the vault model, resolving the domain, the project's scope, the inbox)
- `references/write-safety.md`: before any write into the vault, by this skill or any other
- `references/conventions.md`: before any write (folders, filenames, frontmatter, status, archive: conventions §1–§13)
- `references/commands.md`: the procedure of the command being run, including *Onboarding rows* (run by bandit:project; it adds `Claude/code-{slug}/` for `dev: true` projects and for any other project that runs in Claude Code, and returns domain findings as `domain` fix rows)
- `references/onboarding.md`: when bandit:project runs the vault step of onboarding
- `references/other-skills.md`: when another skill or a chat writes a note
- `references/readme-template.md`: for `home` and `init`
- `references/gotchas.md`: once, before a session's first vault write

🔗 **Works with:** bandit:project (runs its onboarding rows) · bandit:minutes · bandit:tasks · bandit:clarify (saves its spec as a note) · bandit:plan (writes planning docs straight into `Projects/{slug}/`, or its `planning/` on a sprint project) · bandit:audit (runs its vault fix rows) · bandit-dev:sprint (sprint folders, archived at close)

---

### ✅ bandit:tasks

> [!abstract] Operates the Bandit Brain task board
> `plugin` · [[bandit:tasks/SKILL|open skill]] · home board first, reads and writes across the domain (the `domain:` board folder and its subfolders), nothing outside it except linked cards; Untriaged from the workflow project only (`none` or `pending` → read only, except `load` and `onboard`) · dev commands only with `dev: true`

| Command                                        | ⚙️ Modifiers                        | Does                                                                                                                                                                                                                                                                                                               |        | 📚 Reads             |
|------------------------------------------------|-------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|----------------------|
| `/bandit:tasks`                                | —                                   | Lists the commands and asks which one                                                                                                                                                                                                                                                                              | 👀     | —                    |
| `/bandit:tasks triage` · `/bandit:tasks inbox` | —                                   | Sorts the Inbox board: untriaged → board, parked → column. Counts first                                                                                                                                                                                                                                          | ✋      | `triage.md`          |
| `/bandit:tasks capture`                        | `{text or brain dump}`              | Creates tasks, subtasks, dependencies, repeat rules                                                                                                                                                                                                                                                                | ⚡      | `capture.md`         |
| `/bandit:tasks today`                          | —                                   | Reads Execution: Doing, Next, Assigned. Flags cap breach, overdue, stale Stand By (sprint cards exempt)                                                                                                                                                                                                                                 | 👀     | `execution.md`       |
| `/bandit:tasks doing`                          | `{task}`                            | Moves a task to Doing (a blocked card can be worked, not completed)                                                                                                                                                                                                                                                                     | ⚡      | `execution.md`       |
| `/bandit:tasks done`                           | `{task}`                            | Completes it. Recurring → reports the next date                                                                                                                                                                                                                                                                    | ⚡      | `execution.md`       |
| `/bandit:tasks bump`                           | `{task…}` `{date}`                  | Changes the due date. Recurring → offers a skip instead                                                                                                                                                                                                                                                            | ⚡      | `execution.md`       |
| `/bandit:tasks week`                           | —                                   | Reads the week, day by day. Projections marked                                                                                                                                                                                                                                                                     | 👀     | `week.md`            |
| `/bandit:tasks week`                           | `[board]`                           | Proposes dates for undated tasks                                                                                                                                                                                                                                                                                   | ✋      | `week.md`            |
| `/bandit:tasks review`                         | —                                   | Recaps the week from the event log, proposes resize or drop                                                                                                                                                                                                                                                        | 👀 → ✋ | `week.md`            |
| `/bandit:tasks audit`                          | —                                   | Eleven hygiene checks, every finding a numbered fix row with the exact call (unreadable repeat rules rebuilt from their history, marked unchecked; board-shape problems get a concrete change). Archive candidates. Dev boards add card checks V1–V6 (lane/stage tags, plan note filed, XL, duplicates, `Spec change needed:` comments, card complete); sprint cards are exempt from V1, V3 and V6, and from Stand By rot; `sprint/*` tags from the orphan and off-vocabulary checks | 👀 → ✋ | `audit.md`           |
| `/bandit:tasks email`                          | —                                   | Gmail → proposed tasks. Never writes                                                                                                                                                                                                                                                                               | 👀     | `email.md`           |
| `/bandit:tasks load`                           | `[WBS]`                             | WBS → a board (Workflow unless you say Technical): deliverables become columns, work packages undated tasks, dependencies wired. Resumes a half-done load. Refused on a Technical home board                                                                                                                                               | ✋      | `load.md`            |
| `/bandit:tasks onboard`                        | —                                   | The board step of onboarding, run by bandit:project: resolves the `board:` scope or creates one empty board (Backlog only). New board names follow rulebook S2/S3. `dev: true` → adds the dev board shape rows (tags + six lanes)                                                                              | ✋      | `onboard.md`         |
| `/bandit:tasks spec`                           | `[card]`                            | 🛠️ Dev: writes a complete card from the app's lane template: area column (the module or page; ask if unclear), `lane/*` + `stage/spec` + handler + energy tags, priority, complexity, effort, assignee, dependencies, plus its brief (bandit:notes). XL splits before anything is created. Merge check first. Incident: no stage, dated today | ✋      | `dev-workflow.md`    |
| `/bandit:tasks spec reconcile`                 | `{card…}`                           | 🛠️ Dev: brings locked Specs in line with decisions taken since. Applies them with the lock override, no question, reads back, reports old and new, comments each card | ⚡      | `dev-workflow.md`    |
| `/bandit:tasks scope`                          | `{card}`                            | 🛠️ Dev: settles what's open on one card. Writes everything already answered (chat, brief, plan note, comments) into the Spec, brief and plan note, no question; asks only what nobody wrote down, in one decision table | ⚡ → ✋ | `dev-workflow.md`    |
| `/bandit:tasks plan-tech`                      | —                                   | 🛠️ Dev, Claude Code only: drift check, lists `stage/spec` cards, writes the plan note (inbox) and the card's `Technical plan`                                                                                                                                                                                     | ✋      | `dev-workflow.md`    |
| `/bandit:tasks stage`                          | `{card}` `{spec · planned · ready}` | 🛠️ Dev: the only stage writer. `planned` needs the plan note filed (a shared sprint plan counts); `ready` only on your explicit approval, either surface | ✋      | `dev-workflow.md`    |
| `/bandit:tasks pick-ready`                     | —                                   | 🛠️ Dev: the week's dating (`/bandit:tasks week`) over `stage/ready` cards outside a sprint. Picks and dates work, never plans a sprint: that's `/bandit-dev:sprint plan` | ✋      | `dev-workflow.md` · `week.md` |

> [!example]- ⚙️ Repeat rules (`/bandit:tasks capture`): the whole vocabulary
>
> | Field            | Values                                                                                                                 |
> |------------------|------------------------------------------------------------------------------------------------------------------------|
> | `basis`          | `schedule` (calendar: rent, bills) · `completion` (N after done: plants)                                               |
> | `every` + `unit` | whole number ≥ 1 · `day` `week` `month` `year` (`year` not with `completion`)                                          |
> | `days`           | weekdays `1`=Mon … `7`=Sun, only with `unit: week`. Sun–Thu = `[7,1,2,3,4]` · every other Tuesday = `every: 2` + `[2]` |
> | `weekdaysOnly`   | Mon–Fri, only with `schedule` + every 1 day. Any other set of days → `unit: week` + `days`                             |
> | `ends`           | `never` · `on {date}` · `after {count}` (not with `completion`)                                                        |
>
> Not possible: the second Tuesday of the month · last Friday of the month · twice a month · every 3 weekdays. The tool's `rule` schema wins over this table.

> [!example]- 🏷️ Tags: three axes, plus the dev tags
> **Kind** `feature` `issue` `chore` · **Energy** `quick-win` `deep-work` `needs-research` · **Handler** `claude-code` `claude-design` `claude-ai`
> Technical boards: **Lane** `lane/incident` `lane/issue` `lane/feature` `lane/maintenance` `lane/content` `lane/tech-debt` · **Stage** `stage/spec` → `stage/planned` → `stage/ready` (kept after completion) · **Sprint** `sprint/{name}` (`list_tasks { view: "sprint" }`)

> [!note]- 🛠️ Dev surfaces
> Claude.ai = high-level: `spec`, `scope`, `stage … ready` (on your approval), `pick-ready`. Claude Code (Project Context from the repo `CLAUDE.md`) = the same plus `plan-tech`, every stage and incident `spec`. Cards stay thin: `Spec` + `Technical plan`, up to L; XL splits. Every field filled (`dev.md` → 🧾 Card fields). A written Spec is locked: changes go in a `Spec change needed:` comment. Project-management cards go in the `PM` column.
> **Sprint card:** PM column (the dev board shape adds it when missing), no lane, stage or Spec; the batch cards are its blockers and carry `sprint/{name}`; its sections and sub-tasks are bandit-dev:sprint's, and only its sprint plan dates the batch. An XL card splits and the new card stays in the sprint.
>
> 📚 `dev.md` = board rules (lanes, stages, card sections and fields, Spec lock, tag merging, sprint card, dev board shape) · `dev-workflow.md` = the dev commands, surfaces, card boundaries, record homes.

> [!note] 🚧 The dependency gate
> Only **completing** waits for blockers: `done` is refused while a blocker is incomplete (a blocker in Stand By is not complete). A blocked card can still move to Next, Doing or Stand By and be worked. Blockers and their dependents complete in one call when the blockers are listed first.

> [!note]- 🔧 The board tools
> Every command works the board through the app's 18 assistant tools: `get_context` (boards, columns, lanes, tags, members, sprints, in one call) · `list_tasks` (a `view`: `inbox`, `execution`, `week`, `workload`, `sprint`; or filters) · `get_task` · `create_tasks` · `update_tasks` (moves, fields, completing) · `reopen_tasks` · `delete_tasks` · `manage_subtasks` · `manage_recurrence` · `link_tasks` · `manage_boards` · `manage_columns_lanes` · `manage_tags` · `manage_folders` · `set_visibility` · `delete_board_items` · `add_comment` · `list_events`. The write tools take a list and answer each entry on its own.

📚 **Also reads:** `scope.md` before every read or write (home board, domain, filtering household-wide views) · `board.md` (board profile, sizing, tags and tag view, card descriptions, sub-tasks, safety) · `errors.md` when a call or one of its entries is refused · `gotchas.md` once at the start of a session that writes.

🔗 **Works with:** bandit:project (runs `onboard`, writes `board:` and `dev:`) · bandit:notes (shares Kind and Handler; plan notes and the plan-note lookup) · bandit:plan (`load` input; card links on dev projects) · bandit:clarify (its spec becomes a card through `capture` or `spec`) · bandit:audit (runs its board fix rows, including S9's dev board shape) · bandit-dev:sprint (plans and runs sprints over `stage/ready` cards)

---

### 🎙️ bandit:minutes

> [!abstract] Meeting recording → professional minutes, saved to the vault
> `plugin` · [[bandit:minutes/SKILL|open skill]] · `/bandit:minutes` with the recording attached, or 💬 attach the audio and ask for minutes

| Asks up front | ⚙️ Options                                                       | Default             |
|---------------|------------------------------------------------------------------|---------------------|
| Version       | `Both` · `Full only` · `Short only`                              | Both                |
| Location      | `{Domain} vault` · `Same folder as the audio` · `Another BanditCloud folder` | The vault |
| Meeting       | `Supervisors` · `Department` · `Project` (vault only)            | From the transcript |
| Speakers      | Separate voices, only if you ask                                 | Off                 |
| Model         | `small` · `medium` for poor audio (≈3× slower)                   | small               |

📚 **References:** `references/workflow.md` (setup, transcription, verify and save) · `references/scripts.md` (the scripts) · `references/formats.md` (the full and short formats) · `references/vault.md` (saving and filing).
📚 **Scripts:** `scripts/transcribe.py` · `scripts/diarize.py` · `scripts/merge.py`, copied to the working directory before running.
🔗 **Works with:** bandit:notes (its conventions; files to `_inbox/` with `file-to: Meetings/`)

---

## 💰 Money

### 💰 bandit:finance

> [!abstract] Works the Bandit Brain Finance module from chat
> `plugin` · [[bandit:finance/SKILL|open skill]] · a `finance: accounts "…"` line in the Project Context limits it to those accounts; no line, or a plain chat, means every account you can see · previews before every bulk write, every delete confirmed, never mixes currencies

| Command                       | ⚙️ Modifiers              | Does                                                                                                                         |        | 📚 Reads       |
|-------------------------------|---------------------------|------------------------------------------------------------------------------------------------------------------------------|--------|----------------|
| `/bandit:finance`             | —                         | Lists the commands and asks which one                                                                                        | 👀     | —              |
| `/bandit:finance setup`       | —                         | Accounts, category groups, categories, targets and first bills from a short talk, one approval table                         | ✋      | `setup.md`     |
| `/bandit:finance log`         | `{plain words}`           | One spend, income, transfer or split; payee and category matched by name, asks only when more than one fits                  | ⚡      | `log.md`       |
| `/bandit:finance import`      | the bank CSV              | Reads the first rows for the mapping (date format never guessed), previews new · duplicate · matched · ambiguous, commits only approved rows | ✋      | `import.md`    |
| `/bandit:finance sort`        | —                         | Uncategorised rows in batches (bulk edit preview, then apply), payee merges and defaults, the app's category suggestions, rules | ✋      | `sort.md`      |
| `/bandit:finance month`       | `[YYYY-MM]`               | The budget month: left to assign, overspent, behind on target; assign, move, hold, auto-assign (preview first)               | ✋      | `month.md`     |
| `/bandit:finance bills`       | —                         | Due and late bills and income; create, skip, amend, post, unmatch, archive. A bill you pay by hand gets the app's "needs action" task | ✋      | `bills.md`     |
| `/bandit:finance reconcile`   | `{account}`               | Statement in hand → the difference → lock (an adjustment only on your yes)                                                   | ✋      | `reconcile.md` |
| `/bandit:finance review`      | `[week · month · YYYY-MM]` | Balances, the forecast (below-zero dates first), spending by category, income against expense, one block per currency        | 👀     | `review.md`    |
| `/bandit:finance audit`       | —                         | Clean-up check: uncategorised, duplicate payees, late or never-matching bills, rules off, budget below zero, not reconciled; fix rows you approve | 👀 → ✋ | `audit.md`     |

> [!note]- 🔧 The Finance tools
> Every command works through the app's 17 Finance tools: `finance_get_context` (accounts, balances, categories, payees, in one call) · `finance_list_transactions` · `finance_get_budget` · `finance_list_schedules` · `finance_get_report` (`forecast`, `reports`) · `finance_list_rules` · `finance_get_account_history` · `finance_manage_accounts` · `finance_manage_transactions` · `finance_manage_budget` · `finance_manage_categories` · `finance_manage_payees` · `finance_manage_schedules` · `finance_import_transactions` · `finance_manage_reconciliation` · `finance_manage_rules` · `finance_delete_items`. Money is whole cents with its currency; some actions stay yours, in the app (who sees an account, deleting accounts and categories, undoing an import, unlocking a reconciled row).

📚 **Also reads:** `scope.md` before every read or write (which accounts) · `money.md` before any amount, date or currency · `errors.md` when a call is refused · `gotchas.md` once at the start of a session that writes.

🔗 **Works with:** bandit:project (writes the `finance:` line) · bandit:tasks (the board; bill reminders arrive there from the app, never from this skill) · bandit:notes (saving a review as a note)

---

## 🧱 Projects & planning

### 🛠️ bandit:project

> [!abstract] The one onboarding command, plus Claude.ai project instructions and the Project Context block
> `plugin` · [[bandit:project/SKILL|open skill]] · 💬 "onboard this project", "project settings", "audit these instructions"

| Command                            | ⚙️ Modifiers | Does                                                                                                                                                                                                                                  |        | 📚 Reads                                   |
|------------------------------------|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|--------------------------------------------|
| `/bandit:project`                  | —            | No command: picks the mode from the project's state (no instructions → new project, instructions → audit, another project named → vault update)                                                                                       | —      | `audit.md` → Mode Detection                |
| `/bandit:project onboard`          | —            | New or existing project: interview or audit, then **one proposal** of vault rows (bandit:notes), board rows (`/bandit:tasks onboard`) and settings files, plus a fix row for every finding. Only approved rows run; you get the instructions to paste | ✋      | `onboard.md` · `interview.md` (new)        |
| `/bandit:project audit`            | —            | Scores every section of this project's instructions against the template, flags old Project Context lines and board tool names that aren't current (on Claude.ai, the hand-over adds a line to check the Claude Code `CLAUDE.md` too), finds duplicates, builds the fixed version straight away and adds whatever the vault or board is missing, all as rows in one proposal. Naming, board and footprint → `/bandit:audit check` (skip for `domain: none`) | 👀 → ✋ | `audit.md`                                 |
| `/bandit:project update`           | `{project}`  | Targeted change to **another** project's instructions from its vault copy (bandit:audit settings rows use it): only that change → the next version in that project's vault folder; anything else noticed comes back as an extra fix row. You paste it there, then `/bandit:audit check` (skip for `domain: none`) | ✋      | `update.md`                                |
| `/bandit:project instructions`     | —            | Generates the instructions from the one-page template for the project's type (`workflow`, `product_service`, or `dev` for any `dev: true` project), as one proposal row                                                              | ✋      | `instructions.md`                          |
| `/bandit:project sync`             | —            | Saves the current instructions and reference doc to the vault settings folder                                                                                                                                                        | ✋      | `output.md` · `vault-storage.md`           |

> [!note]- 🔀 What `audit` asks first
> Before auditing it asks what changed and what you want: **Full audit** (above), **Targeted update** (you know the change: skips the audit, writes the next version) or **Just sync** (the same as `sync`).

> [!example]- ⚙️ Answers it records
>
> | Question                   | Options                                                                                                                             |
> |----------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
> | Project type → `type:`     | `product_service` · `workflow` · `claude_marketplace`                                                                               |
> | Dev workflow → `dev: true` | Yes · No. Asked only for `product_service` and `claude_marketplace`; No = no `dev` line                                             |
> | Claude Code surface        | Yes · No. Asked for every project without `dev: true`. Yes → `Claude/code-{slug}/` + the Claude Code twin. No Project Context key   |
> | Task board → `board:`      | existing `project "{name}"` in the domain's folder · a new board (created empty, in the domain's folder) · `none` · `pending` |
> | Output                     | Artifact · + vault folder · vault folder only                                                                                       |
> | Folder backend             | Domain (or custom path → `domain: none`) · project slug · prefix                                                                    |

> [!note] Audits flag and migrate legacy projects: Notes-app storage → vault folder, and old `lifecycle` blocks are dropped.

> [!tip] `dev: true` projects: onboarding adds the dev board shape, the instructions allow `/bandit:tasks spec`, and you get the exact Project Context block to put in the repo's `CLAUDE.md` for Claude Code.

> [!tip] Claude Code surfaces live in `Claude/code-{slug}/`, settings only. Any project without `dev: true` that also runs in Claude Code gets a **twin** `CLAUDE.md` (same core and version; only `## 🖥️ Environment` differs), plus an optional `claude/settings.json` for the agent's permission rules. The twin keeps its type's scope. A `dev: true` repo gets a **dev mirror**: a `Stop` hook has Claude copy `CLAUDE.md` + `.claude/` (stored as `claude/`) into the vault.

📚 **References** (besides each command's file in the table):

- `references/reference-template.md`: before anything else (the section standard, v1.4: every section, its audit criteria, the metadata block, the token budget)
- `references/project-context.md`: the Project Context block (keys, format, repo copy, dev mirror, Claude Code twin)
- `references/vault-storage.md`: before any write to, or audit of, the settings folder
- `references/dev-mirror.md`: onboarding or auditing a `dev: true` project (the Stop hook and mirror script; the sprint checker is `bandit-dev`'s own hook, not wired here)
- `references/workdir.md`: a Claude Code twin (onboarding, a twin version change, an S12 row)
- `references/gotchas.md`: once, before onboarding or an audit
- `assets/instructions/`: the one-page templates (`workflow.md` · `product_service.md` · `dev.md`)

🔗 **Works with:** bandit:notes and bandit:tasks (it runs their onboarding steps) · every `bandit` skill (reads its Project Context) · bandit:audit (runs its settings rows through `update`)

---

### 📐 bandit:audit

> [!abstract] Audits domain and project structure across Claude.ai, the vault and the board, against the structure rulebook. Scored by a script, never by hand
> `plugin` · [[bandit:audit/SKILL|open skill]] · 💬 "audit the BanditLabs domain", "audit all domains", "is this project in sync with the vault"

| Command               | ⚙️ Modifiers       | Does                                                                                                                                                                                                                    |        | 📚 Reads                          |
|-----------------------|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|-----------------------------------|
| `/bandit:audit`       | —                  | Lists the commands and asks which one                                                                                                                                                                                   | 👀     | —                                 |
| `/bandit:audit check` | —                  | Run inside the project: stamps its running instructions version, scores that project with the script, runs its fix rows. No question                                                                                    | ⚡      | `self-check.md`                   |
| `/bandit:audit audit` | `{domain}` · `all` | One snapshot of board + vault + stamps → `check_structure.py` → report with numbered fix rows, shown unedited, plus **Extra fix rows** below it for findings the rules don't cover. `all` = every domain, same snapshot. Runs every row, archives the old report, writes the new one. No question | ⚡      | `domain-audit.md` · `snapshot.md` |
| `/bandit:audit close` | `{domain}`         | Replays the report; valid → moves report + snapshot to `_archive/`                                                                                                                                                       | ⚡      | `domain-audit.md`                 |

> [!warning] Findings come fixed, through their owners
> Every finding is a fix row, never a bare note; S9 (dev lanes without `dev: true`) is one row with both options; the recommended one runs. It never changes anything with its own calls: every row runs through its owner, no question, in order: vault (bandit:notes) → settings (bandit:project) → board (bandit:tasks). A board rename always comes paired with its `board:` update.

📚 **Rules:** `structure-rulebook.md` + `structure-rules.yaml` (read-only): 16 rules. S9 = dev board shape (`dev: true` boards have the six dev lanes, others have none) · S10 = Claude Code twin of any project without `dev: true` · S11 = dev mirror (`code-{slug}/` has the Stop hook and script) · S12 = Claude Code working folder · S13–S16 = sprint projects' vault content (briefs in their sprint folder, no filename twice in `Projects/` and `_inbox/`, frontmatter parses, root holds only hub + `sprint-*` + `planning/`; bandit-dev:sprint's local checker enforces the same at write time). **Script:** `scripts/check_structure.py`, snapshot schema 5 (lanes + tags + surfaces + working-folder manifests + project files and frontmatter + sprint cards). **Ledger:** `paths.stamps` in the rules. Reports go to `{Domain}/Projects/{workflow-project}/`, never a settings folder.
📚 **Also reads:** `references/fix-rows.md` (building and running fix rows: owners, linked rows, order) · `references/gotchas.md` (once, before a `check` or an `audit`).
🔗 **Works with:** bandit:notes · bandit:tasks · bandit:project (they carry out its fix rows)
🚫 Auditing a skill → `/bandit-maker:skill lint` · board hygiene → `/bandit:tasks audit` · note lint → `/bandit:notes lint`.

---

### 🧭 bandit:plan

> [!abstract] Plans a project in two modes: `project` (idea → project plan → architecture document) and `wbs` (docs or a batch of cards → a numbered, gap-checked work breakdown structure)
> `plugin` · [[bandit:plan/SKILL|open skill]] · 💬 "plan a project", "architecture document", "create a WBS", "break down this project" · saves to the vault: `MyNotes/{domain}/Projects/{project}/` (`planning/` on a sprint project)

| Command               | ⚙️ Modifiers | Does                                                                                                                  |    | 📚 Reads     |
|-----------------------|--------------|-----------------------------------------------------------------------------------------------------------------------|----|--------------|
| `/bandit:plan`        | —            | Lists the two modes and asks which one                                                                                | 👀 | —            |
| `/bandit:plan project` | —           | Idea → Project Plan (Phase 1) → Architecture Document (Phase 2). The phase is read from the files, below             | ✋  | `project.md` |
| `/bandit:plan wbs`    | —            | Project docs → gap analysis → numbered WBS, in the fixed format `/bandit:tasks load` reads. Sprint and migration modes below | ✋ | `wbs.md`     |

The order is `project` → `wbs` → the board (`/bandit:tasks load`, or the dev route on `dev: true`).

> [!example]- 🧭 `project` mode: state comes from the files
>
> | 💬 Say                                              | Phase            | Output                                                 |
> |-----------------------------------------------------|------------------|--------------------------------------------------------|
> | "start a new project" · "plan a project"            | Phase 1 · New    | `{project}-project-plan.md`                            |
> | "continue planning" · "where are we on the project" | Phase 1 · Resume | Picks up at the first `_Pending_` section              |
> | "move to architecture" · "architecture document"    | Phase 2          | `{project}-architecture.md`                            |
> | (planning finished)                                 | Done             | Points you to `/bandit:plan wbs`, which offers the board step |
>
> The phase is read from each document's `status` (`active` / `triaged`); nothing is stored in the project instructions. Planning docs go straight into the project folder, not `_inbox/`.

> [!example]- 🏗️ `wbs` mode: five phases
>
> | Phase         | Does                                                                                                          |
> |---------------|---------------------------------------------------------------------------------------------------------------|
> | 1 · Ingest    | Reads your docs, or the plan + architecture from the project's vault folder                                   |
> | 2 · Analyze   | Gap analysis against a completeness checklist                                                                 |
> | 3 · Resolve   | Asks about the gaps: options + a recommendation                                                               |
> | 4 · Generate  | The WBS as ND-friendly markdown, in the fixed format `/bandit:tasks load` reads                               |
> | 5 · Reconcile | Backports findings into the source doc (the vault plan is edited in place), offers to save `{project}-wbs.md` |

⚙️ **Migration mode** (`wbs`): give it an existing WBS (e.g. a Gitea wiki page) → rewritten into this format, gaps listed, no Phase 5 · **Sprint mode** (`wbs`, run by `/bandit-dev:sprint plan`): a WBS over existing cards and their briefs, no Phase 5, no sizes, card links rows for those cards · `dev: true`**:** level glossary in the header, an empty `## 🔗 Card links` section, and it points to `/bandit:tasks spec` per work package, then `/bandit-dev:sprint plan`, instead of `load`. The WBS is saved only as the final file, in the folder bandit:notes names; drafts never go to `_inbox`.
📚 **References:** `references/project.md` (`project` mode) · `references/wbs.md` (`wbs` mode).
🔗 **Works with:** bandit:clarify and bandit:rewrite (before planning) · bandit:project (its Project Context) · bandit:notes (note format and folders) · `/bandit:tasks load` (output) · `/bandit:tasks spec` (dev projects, one card per work package) · bandit-dev:sprint (runs sprint mode)

---

## ✍️ Thinking & writing

> [!tip] Got text yet? No, just a thought → **bandit:clarify** asks you questions. Yes → **bandit:rewrite** rewrites it.

### 🔍 bandit:clarify

> [!abstract] A thought you can't put into words yet → questions → a clear, actionable spec, with the 4-D method
> `plugin` · [[bandit:clarify/SKILL|open skill]] · `/bandit:clarify [idea]`, or 💬 "clarify" (that word alone is enough), "help me think through this", "what do I need to decide"

| Phase                  | Does                                                                                 |
|------------------------|--------------------------------------------------------------------------------------|
| Deconstruct · Diagnose | Silent: breaks the request apart, finds what's missing, a 3–5 bullet summary with assumptions you can correct |
| Develop                | At most 2 questions a turn, each with options; a summary every 2–3 questions         |
| Verify                 | Checks cheap assumptions with one read-only call, each marked verified or unverified |
| Deliver                | A Clarified Specification: summary, scope, requirements, assumptions, open questions |

⚙️ Simplifies when it's getting too much · offers a deeper pass when it's bigger than it looked · offers a break after 4 or more questions · offers once where the spec goes: a spec that changes skills → a Marketplace card plus brief; dev-project work → `/bandit:tasks spec`; anything else → a note in the domain `_inbox` **and** a card, linked (say *note only* or *card only*; no domain → card only, no board → note only). Cards go through bandit:tasks, notes through bandit:notes.
📚 **References:** `references/method.md` (phases 1–3 and verify) · `references/deliver.md` (the spec and where it goes) · `references/pacing.md` and `references/gotchas.md` (once per clarification). 🔗 Other skills hand off to it with "use the 4-D method".
🚫 Pasted content that needs rewriting → bandit:rewrite · code, plans or WBS → hand the spec on.

---

### ✨ bandit:rewrite

> [!abstract] Text you already have (notes, brain dumps, transcripts) → clean, scannable ND-friendly markdown, in one pass, no questions asked
> `plugin` · [[bandit:rewrite/SKILL|open skill]] · `/bandit:rewrite` with the content pasted or attached, or 💬 "process this", "clean this up", "make this readable", "deduplicate this"

| Step               | Does                                      |
|--------------------|-------------------------------------------|
| 1 · Ingest & audit | Inventories the content, finds duplicates |
| 2 · Structure      | Designs emoji-anchored sections           |
| 3 · Write          | Rewrites into short, scannable blocks     |
| 4 · Final pass     | Checks nothing was lost                   |

⚙️ Nothing added, nothing dropped: gaps it finds go in an Open questions section at the end, with an offer to run `/bandit:clarify` on them. Code stays as written. Delivers the file (inline for short input); a vault save goes through bandit:notes.
📚 **References:** `references/rewrite.md` (all four steps).
🚫 A bare "clarify" with nothing to rewrite → bandit:clarify · recordings → bandit:minutes · filing into the vault → bandit:notes · code, data, slides.

---

### 💡 prompt-engineer

> [!abstract] Structured prompts for Claude Code and development work
> `plugin` · [[prompt-engineer/SKILL|open skill]] · 💬 "help me write the prompt for…", "write a prompt for Claude Code", "turn this into a prompt", "tighten this prompt"

| Framework                     | For                          |
|-------------------------------|------------------------------|
| 1 · New feature               | Building something new       |
| 2 · Architecture design       | System design and trade-offs |
| 3 · Code review & refactoring | Improving existing code      |
| 4 · Debugging                 | Finding and fixing a problem |

📚 **References:**

- `workflow-patterns.md`: multi-step processes
- `code-quality.md`: asking for clean, maintainable code
- `common-mistakes.md`: pitfalls to avoid

⚙️ Delivers the prompt in one copyable block and bakes in your standing conventions (modular packages, pinned versions, git flow, Compose V2).
🚫 Doing the task itself · vague idea → bandit:clarify · project instructions → bandit:project · skills → bandit-maker:skill.

---

## 🛠️ Claude tooling

### 🧪 bandit-maker:skill

> [!abstract] Create, test, benchmark, tune and lint the marketplace skills
> `plugin` · Claude Code, for maintainers · [[bandit-maker:skill/SKILL|open skill]] · 💬 "make a skill for…", "improve this skill", "run evals", "lint the skills", "make it house-standard"

| Command                         | ⚙️ Modifiers  | Does                                                                                                         | 📚 Reads                              |
|---------------------------------|---------------|--------------------------------------------------------------------------------------------------------------|---------------------------------------|
| `/bandit-maker:skill`           | —             | Works out where you are in the loop (draft, test, rewrite) and jumps in there                                | —                                     |
| `/bandit-maker:skill create`    | —             | Captures intent, interviews, writes the `SKILL.md` and its test prompts                                      | `create.md`                           |
| `/bandit-maker:skill eval`      | —             | Runs test prompts with and without the skill, grades them, opens the review viewer; benchmark with variance; blind A/B comparison ("which version is better?") | `eval.md`                             |
| `/bandit-maker:skill improve`   | —             | Rewrites the skill from your feedback on the eval results, then runs the next iteration                      | `eval.md`                             |
| `/bandit-maker:skill describe`  | —             | Optimizes the description's triggering against a train/test set of trigger evals                             | `description.md`                      |
| `/bandit-maker:skill lint`      | `[folder…]`   | The house gate (`house_lint.py`) over the skills named, or every skill in `plugins/*/skills/*`; plus `python3 scripts/check_repo.py` in the marketplace repo; every ❌ and ⚠️ a fix row, only approved rows written. A ❌ blocks the package or the card | `lint.md`                             |
| `/bandit-maker:skill package`   | —             | Builds a `.skill` file with `scripts/package_skill.py`, lint first                                           | `description.md` → Package and Present |


> [!tip] House standard
> Every skill built or edited here passes `references/rulebook.md` (R1–R15) plus the marketplace rules: description ≤ 300 characters, `SKILL.md` ≤ 150 lines with a router table and each procedure in its reference file, one home per rule, no project details, `## ⚠️ Gotchas` and `## 🚫 Never` sections, emoji H2s, and command names unique across every skill (R15).

📚 **References:**

- `references/rulebook.md`: before any draft (the house standard; it wins over the skill page)
- `references/surfaces.md`: on Claude.ai or in Cowork (no subagents or display)
- `references/schemas.md`: the eval and grading JSON formats
- `agents/grader.md` · `agents/comparator.md` · `agents/analyzer.md`: when it spawns that subagent
- `scripts/`: run_eval · run_loop · improve_description · aggregate_benchmark · generate_report · quick_validate · house_lint · package_skill

---

## 📊 Data

### 🧰 data-tools

> [!abstract] Databases, dbt, data audits, profiling, analysis and notebooks, for any project
> `plugin` · [[data-tools/SKILL|open skill]] · servers, databases and credentials come from the project's `CLAUDE.md` or `.env`, never from the skill

| Command                | ⚙️ Modifiers          | Does                                                                                                                                                                                  |                       | 📚 Reads                                                                                  |
|------------------------|-----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------|-------------------------------------------------------------------------------------------|
| `/data-tools`          | —                     | Picks the command from what you ask; asks when two fit                                                                                                                                | 👀                    | —                                                                                         |
| `/data-tools sources`  | `[engine]`            | Connects to SQL Server, PostgreSQL, SQLite, Access or files (DuckDB); catalog, dialects, copying data out                                                                             | 👀 (writes ✋)         | `sources.md` + `sqlserver.md` · `postgres.md` · `sqlite.md` · `access.md` · `dialects.md` |
| `/data-tools dbt`      | `[selector]`          | Build, test, explain, lineage, unit tests, contracts, slim CI, failed runs                                                                                                            | ⚡ dev target · ✋ prod | `dbt.md` · `dbt-adapters.md` · `dbt-lineage.md`                                           |
| `/data-tools review`   | `[path]` · `gate`     | Integrity audit (FAIL/WARN/INFO) with a fix row per FAIL and WARN; approved rows applied as file edits, then re-checked (never a direct database write). `gate` = read-only PASS/FAIL | 👀 → ✋ · `gate` 👀    | `review.md` · `postgis.md`                                                                |
| `/data-tools profile`  | `{table or file}`     | Grain, nulls, distincts, ranges, bad values, judged against what each column should hold                                                                                              | 👀                    | `profile.md`                                                                              |
| `/data-tools explore`  | `{question}` · `full` | Quick answer with tested evidence, or `full` for an open exploration                                                                                                                  | 👀                    | `explore.md` · `explore-method.md`                                                        |
| `/data-tools notebook` | `[topic]`             | Notebook structure, Plotly chart choice, light or dark theme, maps                                                                                                                    | ⚡                     | `notebook.md` · `notebook-charts.md` · `notebook-maps.md` · `notebook-theme.md`           |
| `/data-tools agent`    | —                     | Installs the read-only `data-reviewer` subagent in the current repo's `.claude/agents/`; asks before replacing one. It returns fix rows, never applies them                           | ✋                     | `agent.md`                                                                                |

> [!warning] Read-only by default
> Database writes happen only when you ask for a named target. An approved `review` fix row counts as that ask, for file edits only. Summaries come back to the chat, not raw personal data.

📚 **References:** every command reads its file in `references/` first (column above). `assets/data-reviewer.md` is the agent template.
🚫 Spreadsheet files → xlsx · charts in HTML artifacts → dataviz · vault notes → bandit:notes.

---

## 🏃 Delivery (Claude Code)

> [!tip] The `bandit-dev` plugin: the sprint pipeline from plan to close, plus the test data it runs on. Claude Code only, on `dev: true` projects. The stages, surfaces and gates are `docs/pipeline.md`; each project's recipe is its `bandit.yaml` (`docs/bandit-yaml.md`).

### 🏃 bandit-dev:sprint

> [!abstract] Turns a set of existing cards into one planned, approved sprint, then runs, debugs, releases and closes it. Every gate leaves evidence on the sprint card and in the sprint folder
> `plugin` · Claude Code only, from the repo · needs `dev: true`, a `board:` project and `prefix` in the repo `CLAUDE.md` Project Context · 💬 "plan a sprint", "run the waves", "debug the sprint", "close the sprint"

| Command                        | ⚙️ Modifiers                                          | Does                                                                                                                                                                                       |        | 📚 Reads      |
|--------------------------------|-------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|---------------|
| `/bandit-dev:sprint`           | —                                                     | Lists the commands and asks which one                                                                                                                                                      | 👀     | —             |
| `/bandit-dev:sprint plan`      | `[card…]`                                             | The 12-step plan cycle below. No list → every open High card not in a sprint, stated and started straight away (open Urgent cards listed as "not selected"). Ends committed: tag, dates, execution prompt, ledger, one sub-task per wave | ✋      | `plan.md` · `pace.md` |
| `/bandit-dev:sprint execute`   | `{sprint card}` `[wave N]`                            | One wave in this chat, in order (no number → the first open wave, said out loud). Refuses a batch card; moves the wave's cards on the Execution board; then stops: next wave, new chat     | ⚡      | `execute.md`  |
| `/bandit-dev:sprint run`       | `{sprint card…}` · `--paced [minutes]` (under `/loop`) | Every open wave of each sprint, one new subagent per wave, strictly in sequence; the orchestrator checks each wave on the board before the next; stops on a blocker. Refuses a sprint whose plan review isn't ticked or that an open sprint blocks. `--paced`: one wave per wake-up, 45 minutes apart by default | ⚡      | `run.md`      |
| `/bandit-dev:sprint debug`     | `{sprint card}`                                       | After the last wave, in a fresh chat: your adjustments → one decision table → verified fixes. New requirements are parked as cards outside the sprint                                       | ✋      | `debug.md`    |
| `/bandit-dev:sprint release`   | `{sprint card}` + your deploy word                    | Preconditions (every card tested, debug done, your "deploy"/"release"/"ship it" in this message, migration tail recorded, backup confirmed, recipe present), then the project's `bandit.yaml` release recipe; a plugin release for Marketplace cards; fills the production handover card the sprint commit created, for the CTO agent (its hook reads the prompt; the final push fills the staging one) | ✋      | `release.md`  |
| `/bandit-dev:sprint close`     | `{sprint card}` · "close without release"             | Refuses without a `Released:` line (unless you say "close without release"); completes the cards you approved in this chat, blockers first, then the sprint card; archives the sprint folder | ✋      | `close.md`    |

> [!example]- 📋 The plan cycle: the sprint card's 12 step sub-tasks
>
> | #  | Step                              | Done when                                                                                       |
> |----|-----------------------------------|-------------------------------------------------------------------------------------------------|
> | 1  | Select and freeze the batch       | Sprint card in PM, the cards block it, the previous open sprint card blocks it, none in another sprint |
> | 2  | Spec completeness, per card       | Every card read against its brief; gaps as fix rows                                             |
> | 3  | Close the open questions          | One interview answered and recorded                                                             |
> | 4  | Size and classify                 | Every card at most L (XL split), lane and boundaries checked                                    |
> | 5  | Cross-card analysis               | Migrations, shared files, hidden order, docs regeneration written down                          |
> | 6  | Sequence                          | Waves with reasons, split with the WBS (`/bandit:plan wbs`, sprint mode)                        |
> | 7  | Write the one technical plan      | Plan note filed; every card's Technical plan filled; each live check's data from `/bandit-dev:testdata make` |
> | 8  | Risk and rollback                 | Per card and for the sprint, in the plan                                                        |
> | 9  | Definition of ready, per card     | Each Spec reconciled; stage moved on; fix rows for failures                                     |
> | 10 | Approval gate                     | Your explicit approval, quoted on the card                                                      |
> | 11 | Independent plan review           | The `plan-reviewer` agent's record in the sprint folder; majors applied; no blocker open (the only stop) |
> | 12 | Commit the sprint                 | Tag, assignee, due date, size, execution prompt, ledger with `Committed:`; one sub-task per wave |

> [!warning] Gates
> **Gate 0** before any command: Claude Code only · Project Context with `dev: true` · a `PM` column (missing → one fix row) · repo state (work on the deploy branch is said out loud) · the board server, BanditCloud and a browser tool. **The checker is the proof:** `scripts/check_sprint.py` enforces the vault rules (SP1–SP7) at step 12, every wave end, `run` and `close`, and runs as the plugin's `Stop` hook. **The recipe** is read through `scripts/recipe.py` from `bandit.yaml`; a missing key refuses by name. Nothing reaches the deploy branch outside `release`, and only `close` completes cards.

📚 **Also reads:** `references/templates.md` (note and card shapes, filenames) · `references/homes.md` (homes, write rules, owners, before a step's first write) · `references/gotchas.md` (once at the start of any command). **Agent:** `plan-reviewer` (read-only, step 11). **Hook:** the sprint checker on `Stop`.
🔗 **Works with:** bandit:tasks (board rules, `spec reconcile` and the `plan-tech` card-write rules) · bandit:notes (the sprint folder, archived at close) · bandit:plan (`wbs` sprint mode) · bandit:project (the Project Context) · bandit-dev:testdata (each live check's data)
🚫 One card's Spec or plan → `/bandit:tasks spec`, `/bandit:tasks plan-tech` · picking ready work outside a sprint → `/bandit:tasks pick-ready`.

---

### 🌱 bandit-dev:testdata

> [!abstract] Made-up data for a dev project's development, test and staging databases, never the user's own
> `plugin` · Claude Code only, from the app repo · needs the `testdata` section of the app's `bandit.yaml` (contract: the sprint skill's `references/bandit-yaml.md`)

| Command                                     | ⚙️ Modifiers                      | Does                                                                                                                       |      | 📚 Reads    |
|---------------------------------------------|-----------------------------------|----------------------------------------------------------------------------------------------------------------------------|------|-------------|
| `/bandit-dev:testdata`                      | —                                 | Lists the commands and asks which one                                                                                      | 👀   | —           |
| `/bandit-dev:testdata map`                  | `[cards or sprint card]`          | Reads the schema, the live database's structure, the app's rules and what was built; which tables and rules each card touches | 👀   | `map.md`    |
| `/bandit-dev:testdata fill`                 | `{development, test or staging}`  | A lasting made-up set across the whole app, following its rules, kept until `clean`: a made-up user sees made-up data on every page | ⚡ · staging ✋ | `fill.md`   |
| `/bandit-dev:testdata make`                 | `{cards or sprint card}`          | The data each acceptance line needs, in states the rules allow, with the SQL; nothing written                              | 👀   | `make.md`   |
| `/bandit-dev:testdata create`               | `{db}`                            | Writes what `make` prepared and records every id                                                                           | ⚡ · staging ✋ | `create.md` |
| `/bandit-dev:testdata clean`                | `{db}` + a record, `card {label}` or `fill` | Removes exactly the rows a record names, checks none is left                                                     | ⚡ · staging ✋ | `create.md` |

`python3 scripts/dbguard.py records` (in the skill) lists the open run records.

> [!warning] The guard
> Every database call goes through `scripts/dbguard.py`: only development, test and staging; no address or password in `bandit.yaml` (env var names, or `psql` inside the database container); INSERTs only, each recorded; `clean` deletes only recorded ids; staging writes need your yes on every run. Records live in the app's git-ignored `.testdata/`.

📚 **Also reads:** `references/safety.md` once at the start of any command (made-up values, credentials, staging, what the guard enforces).
🔗 **Works with:** bandit-dev:sprint (planning runs `make` per live check; waves run `create` before the check and `clean` after it).

---

## 🔎 Full review prompts

> [!tip] How these run
> Paste one, with the `{…}` placeholder filled in. **Phase 1** runs every audit read-only. **Phase 2** asks every question once: your single answer approves every fix row. **Phase 3** runs everything with no more stops. What's left for you at the end: pasting instructions into Claude.ai, and running `/bandit:audit check` inside those projects.

### 📁 One project

Paste into that project's own chat.

```
Full setup review of this project: {Project name}. Work in three phases.

PHASE 1 — DISCOVERY (read-only, write nothing)
Run each of these with its own skill and procedure. No shortcuts, and no scoring by hand:
  a. /bandit:project audit, as a full audit ("audit these instructions"). It includes /bandit:audit check and the vault and board rows. Build the updated instructions version, but don't write it yet.
  b. /bandit:notes lint, limited to this project's folders.
  c. /bandit:tasks audit.
Collect every fix row from a–c into ONE numbered table: | # | Skill | Action | Target | Recommended option |.

PHASE 2 — ONE QUESTION ROUND
Show the table, then every decision any row needs (either/or choices, deletes, anything a skill would normally ask). Ask everything at once, as numbered questions, each with options and a recommendation. Also mark which rows depend on each other.
My single answer approves everything: "all", a list of row numbers, or "none", plus my answers to the questions. After that, ask me nothing.

PHASE 3 — AUTONOMOUS RUN (no more stops)
- Run exactly the approved rows, through their owner skills, in this order: vault (bandit:notes), then settings (bandit:project, which writes the new instructions version), then board (bandit:tasks).
- My Phase 2 answer is the approval each skill would normally ask for. Don't ask again.
- A row that depends on a declined or failed row is skipped, and the reason is recorded.
- If something new turns up during the run, don't act on it. Add it to the final report as a fix row.
- Never delete anything I didn't approve by exact path. Never pass if_match "*".

FINAL REPORT
One result line per row, then the fix rows for anything new, then my hand-off:
  1. The file name and the full instructions text to paste into this project.
  2. After the paste: run /bandit:audit check in this chat.
```

### 🌐 Whole domain

Paste into the domain's workflow project chat (e.g. Bandit Labs).

```
Full setup review of the {Domain} domain. Work in three phases.

PHASE 1 — DISCOVERY (read-only, write nothing)
Run each of these with its own skill and procedure. No shortcuts, and no scoring by hand:
  a. /bandit:audit audit {Domain}. Keep the script's report unedited, plus its extra fix rows. Don't write the report file yet.
  b. /bandit:notes lint {Domain}.
  c. /bandit:tasks audit.
Collect every fix row from a–c into ONE numbered table: | # | Skill | Project | Action | Target | Recommended option |. Pair linked rows (a board rename with its board: update) so they're approved or declined together.

PHASE 2 — ONE QUESTION ROUND
Show the table, then every decision any row needs (either/or choices such as S9 dev lanes, deletes, anything a skill would normally ask). Ask everything at once, as numbered questions, each with options and a recommendation.
My single answer approves everything: "all", a list of row numbers, or "none", plus my answers to the questions. After that, ask me nothing.

PHASE 3 — AUTONOMOUS RUN (no more stops)
- Write the audit report and its snapshot to the workflow project's folder.
- Run exactly the approved rows through their owner skills, in this order: vault (bandit:notes), then settings (bandit:project writes each project's new instructions version), then board (bandit:tasks).
- Then run /bandit:notes home {Domain}.
- My Phase 2 answer is the approval each skill would normally ask for. Don't ask again.
- A row that depends on a declined or failed row is skipped, and the reason is recorded. Half of a linked pair never runs alone.
- If something new turns up during the run, don't act on it. Add it to the final report as a fix row.
- Never delete anything I didn't approve by exact path. Never pass if_match "*".
- Don't run /bandit:audit close. Pastes and checks are still pending.

FINAL REPORT
One result line per row, then the fix rows for anything new, then my hand-off list:
  1. For each project with a new instructions version: the Claude.ai project name, the file name and the full text to paste.
  2. The projects where I run /bandit:audit check after pasting.
  3. The last step: /bandit:audit close {Domain} in this chat, once 1 and 2 are done.
```

### 🪞 Dev repo alignment (Claude Code)

Paste into Claude Code at the repo root of a `dev: true` project, as is: no placeholders. It reads the domain and project from the repo's own `CLAUDE.md`. It doesn't use the three phases above: read-only pre-flight, one approval, then the install and the first mirror. The hook and script come from bandit:project `references/dev-mirror.md`, read from the vault mirror, so this prompt never goes stale. Existing settings and permissions stay as they are: the only change to them is one added `Stop` hook.

```
# Align this repo with the dev mirror (bandit:project standard)

## Goal
Install the dev mirror so every Claude Code session mirrors this repo's Claude settings
(`CLAUDE.md` + everything under `.claude/`) into `MyNotes/{domain}/Claude/code-{project}/`.
Add to what exists. Existing settings and permissions stay exactly as they are.

## Source of truth
- Domain and project: the `## 🧭 Project Context` block in this repo's `CLAUDE.md`.
- Hook, `.gitignore` line and script: bandit:project `references/dev-mirror.md` (the installed
  `bandit` plugin, or the marketplace repo), section "📦 The repo change". Byte for byte. Never retype or "improve" it.
- Claude.ai side: the highest-numbered `{prefix}-instructions-v{N}.md` in `MyNotes/{domain}/Claude/ai-{project}/`.

## Pre-flight (read-only; any ❌ → stop and report, change nothing)
1. BanditCloud WebDAV tools are available in this session.
2. `CLAUDE.md` has a `## 🧭 Project Context` block (exact heading: the hook parses it) with `domain`,
   `project` and `dev: true`. No block or no `dev: true` → stop (no `dev: true` = a Claude Code twin, not this).
3. Compare that block with the Project Context block in the Claude.ai instructions file. Different →
   show both side by side and ask which one is right. Never edit it without my answer.
4. `MyNotes/{domain}/Claude/code-{project}/` exists. List it. Missing → stop: bandit:notes creates it.
5. Inventory the whole settings set: `CLAUDE.md` + every file under `.claude/` (settings.json, agents/,
   commands/, skills/, hooks/, anything else), with a sha256 each. Mark which ones the mirror will copy
   (everything except `settings.local.json` and the stamp). Also list any Claude files it won't copy
   (`CLAUDE.local.md`, `.mcp.json`, `CLAUDE.md` in subfolders): report them, don't change anything.
6. `.gitignore` doesn't ignore `.claude/` or `.claude/settings.json` wholesale. Report if it does; don't fix it.

Show the pre-flight table and the planned changes as rows `| # | File | Change |`. Wait for my approval.

## Changes (only the approved rows, nothing else)
1. `.claude/settings.json`: copy it to `.claude/settings.json.bak` first. Add the Stop hook entry to
   `hooks.Stop`. That is the only change: `permissions`, every other hook and every other key stay
   byte-identical. Skip it if a Stop hook already runs `mirror-check.py`. The file doesn't exist → create
   it with only the hook. Check that the result parses as JSON.
2. `.gitignore`: append `.claude/mirror-stamp.json` if it isn't there.
3. `.claude/hooks/mirror-check.py`: create it exactly as in the source.
4. `CLAUDE.md` Project Context: only if pre-flight 3 found a difference and I said which side is right.
   Replace that block only; the rest of the file stays as is.

## Never
- Change permissions, other hooks, agents, commands, skills or any settings file not in an approved row.
- Touch `.claude/settings.local.json`, or mirror it.
- Add `workdir.py` or the S12 working-folder hooks (twin-only; a dev repo keeps its own layout).
- Create, move or delete anything in the vault except the files the hook tells you to mirror.
- Pass `if_match: "*"`. New files: omit `if_match`. Existing: read, strip the etag to bare hex, send it.
- Commit or push without my yes.

## After the changes
- Prove nothing else moved: rerun the step-5 inventory. Every sha256 matches, except the approved files
  and the new ones. For `settings.json`, show the diff: only the one added Stop entry.
- Delete `.claude/settings.json.bak` only after I approve that diff.
- The first Stop hook fires with no stamp and lists every settings file. Mirror them all as the hook says
  (`.claude/` → `claude/`), then run the `--stamp` command it prints.
- Verify: list `MyNotes/{domain}/Claude/code-{project}/`. It matches the step-5 "mirrored" list.
- Report: pre-flight, the diffs, the vault listing, and anything skipped with the reason.
```

---

## 🔁 Keeping this page current

- Any marketplace change that adds, removes or changes a command, modifier, trigger phrase or reference file updates this page in the same commit.
- `house_lint.py --names docs/cheat-sheet.md` keeps its bare commands from clashing with skill commands (R15).
- `python3 scripts/check_repo.py` fails when a skill command is missing from this page (rule CS1).
- `python3 scripts/done_check.py` lists what changed since the last release and each place that must change with it, this page included (`docs/dependencies.md`).

## Related

- `README.md` (repo root): the three plugins and how to install them
- `docs/pipeline.md`: the ten stages from idea to closed release, and the command that owns each
- `docs/dependencies.md`: what changes together
- bandit-maker:skill `references/rulebook.md`: the house standard every skill is audited against