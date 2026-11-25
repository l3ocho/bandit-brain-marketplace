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
| 🗃️ | [[#🗃️ bandit:notes\|bandit:notes]]         | `/bandit:notes {command}`     | Note conventions, filing the inbox, lint, archive                                |
| ✅   | [[#✅ bandit:tasks\|bandit:tasks]]           | `/bandit:tasks {command}`     | The Bandit Brain task board, plus the dev card workflow on Technical boards  |
| 🎙️ | [[#🎙️ bandit:minutes\|bandit:minutes]]   | `/bandit:minutes [transcript]` | Meeting transcript → two minutes notes (a recording: the fallback)              |
| 💰  | [[#💰 bandit:finance\|bandit:finance]]      | `/bandit:finance {command}`   | The Finance module: log, import, sort, the budget month, bills, reconcile, review, investments |
| 🛠️ | [[#🛠️ bandit:project\|bandit:project]] | `/bandit:project {command}`   | Onboarding (instructions + notes + board, one approval) and project instructions |
| 📐  | [[#📐 bandit:audit\|bandit:audit]]          | `/bandit:audit {command}`     | Domain and project structure: each project's stamp ↔ the boards                  |
| 🧭  | [[#🧭 bandit:plan\|bandit:plan]]            | `/bandit:plan {mode}`         | `project`: plan → architecture doc · `wbs`: docs or cards → work breakdown       |
| 🔍  | [[#🔍 bandit:clarify\|bandit:clarify]]      | `/bandit:clarify [idea]`      | A thought, no text yet → questions → clear spec                                  |
| ✨   | [[#✨ bandit:rewrite\|bandit:rewrite]]         | `/bandit:rewrite` + the text  | Text you already have → readable markdown, no questions                          |
| 💡  | [[#💡 prompt-engineer\|prompt-engineer]]    | 💬 "help me write the prompt" | Prompts for coding work                                                          |
| 🧪  | [[#🧪 bandit-maker:skill\|bandit-maker:skill]]    | `/bandit-maker:skill {command}` | Build, test, tune and lint skills                                              |
| 🧰  | [[#🧰 data-tools\|data-tools]]              | `/data-tools {command}`       | Databases, dbt, data audits, profiling, analysis, notebooks                      |
| 🏃  | [[#🏃 bandit-dev:sprint\|bandit-dev:sprint]] | `/bandit-dev:sprint {command}` | A dev project's sprint: plan, run its waves, debug, release, close             |
| 🌱  | [[#🌱 bandit-dev:testdata\|bandit-dev:testdata]] | `/bandit-dev:testdata {command}` | Made-up data in development, test and staging; each card's test data          |

> [!important] New project? Run **`/bandit:project onboard`** ("onboard this project"). It's the one onboarding command: it runs the notes step (bandit:notes) and the board step (bandit:tasks) and shows everything in one proposal.

---

## 📝 Notes & tasks

### 🗃️ bandit:notes

> [!abstract] Owns the note conventions and their storage, the app's Notes: kinds, fields, status, names, places, archiving
> `plugin` · [[bandit:notes/SKILL|open skill]] · every project's notes are on its board, unless its Project Context says `notes: none` (then no helper writes a note for it) · the domain comes from the Project Context `domain:` (a top-level board folder, or a path down to a subfolder), and a `write:` line limits where it writes, from bandit:project during onboarding, or the command, or it asks

| Command                  | ⚙️ Modifiers           | Does                                                                                                                                                                                                                       |        |
|--------------------------|------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|
| `/bandit:notes`          | —                      | Lists the commands and asks which one                                                                                                                                                                                      | 👀     |
| `/bandit:notes onboard`  | `[Domain]`             | Checks each project board of the scope for its hub note and proposes the missing ones, each filed in one named column. New project → use `/bandit:project onboard`                                                        | ✋      |
| `/bandit:notes file`     | `[Domain]` `[note…]`   | Reviews inbox notes you put up: place, kind, name, summary and fields, then filed into its column. Body edits only as separate rows. A card's plan is already linked: its summary takes it out of the Inbox with its card's state, and the report prompts `/bandit:tasks stage {card} planned`. A consumed inbox draft gets an archive row, on proof the filed note exists. With no notes named, only helpers' drafts get rows and your own Inbox notes are listed until you name them | ✋      |
| `/bandit:notes lint`     | `[Domain]`             | Reports every convention breach, each as a numbered fix row (the report is the proposal): summary, name, the kind's fields, status, card link, sprint tag, the hub note, customer data. The Inbox is skipped                 | 👀 → ✋ |
| `/bandit:notes archive`  | `[Domain]`             | Sets done notes to archived, where they are. A plan linked to its card follows the card; a sprint's records are archived by the sprint's close                                                                              | ✋      |
| `/bandit:notes restore`  | `{note}`               | Brings a note back from the archive (status `triaged` or the one you name) or from the Trash (as it was)                                                                                                                    | ✋      |
| `/bandit:notes delete`   | `{note…}`              | Deletes exactly the notes named: to the Trash for 30 days, `restore` brings it back                                                                                                                                         | ✋      |

> [!tip] Scope
> `type: workflow` projects see every board of the domain's folder. Other projects see only their own board and its Inbox. A finding outside the scope still comes as a fix row marked `domain`; your yes to that row by number runs it.

> [!warning] Only approved rows run
> "Yes" or "create it" approves the rows on the table, nothing else. Every finding is its own fix row in the same proposal, never a bare list.

> [!tip] Names (conventions §4)
> A note's name is its title, lowercase kebab-case: dated `{slug}-YYYY-MM-DD` (minutes, requests, briefs, logs), evergreen `{slug}` (notes, references, plans). A brief `{project}-{lane}-{slug}-YYYY-MM-DD`, a plan `{project}-{lane}-{slug}-plan`, a sprint record `{project}-sprint-{name}-{record}`. Never a kind label in front, never a `-2` counter.

> [!tip] Dev projects (`dev: true`, conventions §13)
> Plan notes: kind `plan`, linked to their card from the start and waiting in the Inbox for review (linked with no summary; its status then follows its card). The WBS note gets a `## 🔗 Card links` table, one row per card created.
> Card briefs: one `brief` per card, linked to it, H2s Summary · Scope · Requirements · Decisions · Verified facts · Open questions · Change log (optional) · Conclusions (written at close) · Related. No card state (column, lane, stage) in the body; a `Card: {short id}` line is fine.
> A sprint's records: notes on the project's board with the tag `sprint-{name}` (the plan a `plan` with no card link, the review record a `log`, the rest `reference`); the sprint data file in `.sprint/` at the root of the repository the helper runs from.

📚 **References:**

- `references/model.md`: before any command (where the notes are, `notes: none`, resolving the domain, the project's scope, the inbox)
- `references/write-safety.md`: before any write of a note, by this skill or any other
- `references/conventions.md`: before any write (kinds, fields, status, names, body shape, dev projects)
- `references/storage-app.md`: before any write (the tool for each operation, places, the hub note, fields, refusals)
- `references/commands.md`: the procedure of the command being run, including *Onboarding rows* (run by bandit:project)
- `references/onboarding.md`: when bandit:project runs the notes step of onboarding
- `references/other-skills.md`: when another skill or a chat writes a note
- `references/conclusions.md`: when a card is completed (`/bandit:tasks done`, `/bandit-dev:sprint close`): its conclusions into its linked note
- `references/gotchas.md`: once, before a session's first note write

🔗 **Works with:** bandit:project (runs its onboarding rows; its two reference notes) · bandit:minutes · bandit:tasks · bandit:clarify (saves its spec as a note) · bandit:plan (writes planning docs straight onto the project's board) · bandit:audit (its report and stamps notes; runs its notes fix rows) · bandit-dev:sprint (a sprint's records, archived at close)

---

### ✅ bandit:tasks

> [!abstract] Operates the Bandit Brain task board
> `plugin` · [[bandit:tasks/SKILL|open skill]] · home board first, reads and writes across the domain (the `domain:` board folder and its subfolders), nothing outside it except linked cards; Untriaged from the workflow project only (`none` or `pending` → read only, except `load` and `onboard`) · dev commands only with `dev: true`

| Command                                        | ⚙️ Modifiers                        | Does                                                                                                                                                                                                                                                                                                               |        | 📚 Reads             |
|------------------------------------------------|-------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|----------------------|
| `/bandit:tasks`                                | —                                   | Lists the commands and asks which one                                                                                                                                                                                                                                                                              | 👀     | —                    |
| `/bandit:tasks triage` · `/bandit:tasks inbox` | —                                   | Sorts the Inbox board: untriaged → board, parked → column. Counts first; each card with the app's Size, band and Rank, a split proposed for a card banded split                                                                                                                                                                                                                                          | ✋      | `triage.md`          |
| `/bandit:tasks capture`                        | `{text or brain dump}`              | Creates tasks, subtasks, dependencies, repeat rules                                                                                                                                                                                                                                                                | ⚡      | `capture.md`         |
| `/bandit:tasks today`                          | —                                   | Reads Execution: Doing, Next, To Do, each board in the app's rank order (blocked and unsized cards named after). Flags cap breach, overdue, stale Stand By (sprint cards exempt)                                                                                                                                                                                                                                 | 👀     | `execution.md`       |
| `/bandit:tasks doing`                          | `{task}`                            | Moves a task to Doing and dates it today when it has no date (a blocked card can be worked, not completed). Taking a card: it then follows the work, Stand By when it waits, complete when done                                                                                                                                                                                                                                                                  | ⚡      | `execution.md`       |
| `/bandit:tasks done`                           | `{task}`                            | Completes it. First what its comments taught goes into the `Conclusions` section of its linked note, replaced at each close, and a Workflow card keeps a short summary naming the note: one row a card, none when there is nothing to keep (no note: create one or skip; a note in the Inbox: review it first). Skipped on a project with `notes: none`. Recurring → reports the next date | ✋      | `execution.md` · bandit:notes `conclusions.md` |
| `/bandit:tasks bump`                           | `{task…}` `{date}`                  | Changes the due date. Recurring → offers a skip instead                                                                                                                                                                                                                                                            | ⚡      | `execution.md`       |
| `/bandit:tasks week`                           | —                                   | Reads the week, day by day, with each card's Size; workload stays counts. Projections marked                                                                                                                                                                                                                                                                     | 👀     | `week.md`            |
| `/bandit:tasks week`                           | `[board]`                           | Proposes dates for undated tasks, in the app's rank order                                                                                                                                                                                                                                                                                   | ✋      | `week.md`            |
| `/bandit:tasks review`                         | —                                   | Recaps the week from the event log, proposes resize or drop                                                                                                                                                                                                                                                        | 👀 → ✋ | `week.md`            |
| `/bandit:tasks audit`                          | —                                   | Eleven hygiene checks, every finding a numbered fix row with the exact call (unreadable repeat rules rebuilt from their history, marked unchecked; board-shape problems get a concrete change). Archive candidates. Dev boards add card checks V1–V6 (lane/stage tags, plan note linked and reviewed, XL, duplicates, `Spec change needed:` comments, card complete); old-way sprint cards are exempt from V1, V3 and V6; cards in a sprint (a record, or an old `sprint/*` tag) and sprint cards from Stand By rot; `sprint/*` tags from the orphan and off-vocabulary checks | 👀 → ✋ | `audit.md`           |
| `/bandit:tasks email`                          | —                                   | Gmail → proposed tasks. Never writes                                                                                                                                                                                                                                                                               | 👀     | `email.md`           |
| `/bandit:tasks load`                           | `[WBS]`                             | WBS → a board (Workflow unless you say Technical): deliverables become columns, work packages undated tasks, dependencies wired. Resumes a half-done load. Refused on a Technical home board                                                                                                                                               | ✋      | `load.md`            |
| `/bandit:tasks onboard`                        | —                                   | The board step of onboarding, run by bandit:project: resolves the `board:` scope or creates one empty board (Backlog only). New board names follow rulebook S2/S3. `dev: true` → adds the dev board shape rows (tags + six lanes)                                                                              | ✋      | `onboard.md`         |
| `/bandit:tasks spec`                           | `[card]`                            | 🛠️ Dev: writes a complete card from the app's lane template: area column (the module or page; ask if unclear), `lane/*` + `stage/spec` + handler + energy tags, priority, complexity, effort, assignee, dependencies, plus its brief (bandit:notes), linked to the card; the Spec's `Brief:` line names its title. XL splits before anything is created. Merge check first. A screen-changing card gets `stage/spec` only with its approved design page linked as a full web address, and where the handover files live (Design step); with a `design:` line in the Project Context it gets its own design card, linked as its blocker, and waits for that card's approved handover (Design card). Incident: no stage, dated today | ✋      | `dev-workflow.md`    |
| `/bandit:tasks spec reconcile`                 | `{card…}`                           | 🛠️ Dev, on your word only (sprint planning never runs it): brings locked Specs in line with decisions taken since. Applies them with the lock override, no question, reads back, reports old and new, comments each card | ⚡      | `dev-workflow.md`    |
| `/bandit:tasks scope`                          | `{card}`                            | 🛠️ Dev: settles what's open on one card. Writes everything already answered (chat, brief, plan note, comments) into the Spec, brief and plan note, no question; asks only what nobody wrote down, in one decision table | ⚡ → ✋ | `dev-workflow.md`    |
| `/bandit:tasks plan-tech`                      | —                                   | 🛠️ Dev, Claude Code only: drift check, lists `stage/spec` cards, writes the plan note, linked to the card and waiting in the inbox for review, and the card's `Technical plan`                                                                                                                                                                                     | ✋      | `dev-workflow.md`    |
| `/bandit:tasks stage`                          | `{card}` `{spec · planned · ready}` | 🛠️ Dev: the only stage writer. `spec` on a screen-changing card needs its approved design linked (Design step); `planned` needs a plan note linked to the card and reviewed (a sprint's shared plan is the sprint helper's to check); `ready` only on your explicit approval, either surface | ✋      | `dev-workflow.md`    |
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
> Technical boards: **Lane** `lane/incident` `lane/issue` `lane/feature` `lane/maintenance` `lane/content` `lane/tech-debt` · **Stage** `stage/spec` → `stage/planned` → `stage/ready` (kept after completion) · **Sprint** a record on the board (`get_sprints`, `manage_sprints`); an old-way sprint still running keeps its `sprint/{name}` tag until its close

> [!note]- 🛠️ Dev surfaces
> Claude.ai = high-level: `spec`, `scope`, `stage … ready` (on your approval), `pick-ready`. Claude Code (Project Context from the repo `CLAUDE.md`) = the same plus `plan-tech`, every stage and incident `spec`. Cards stay thin: `Spec` + `Technical plan`, up to L; XL splits. Every field filled (`dev.md` → 🧾 Card fields). A written Spec is locked: changes go in a `Spec change needed:` comment. Project-management cards go in the `PM` column.
> **Sprint card** (old-way sprints only; a real sprint has none): PM column (the dev board shape adds it when missing), no lane, stage or Spec; the batch cards are its blockers and carry `sprint/{name}`; its sections and sub-tasks are bandit-dev:sprint's, and only its sprint plan dates the batch. An XL card splits and the new card stays in the sprint.
>
> 📚 `dev.md` = board rules (lanes, stages, card sections and fields, Spec lock, tag merging, old-way sprint card, dev board shape) · `dev-workflow.md` = the dev commands, surfaces, card boundaries, record homes.

> [!note] 🚧 The dependency gate
> Only **completing** waits for blockers: `done` is refused while a blocker is incomplete (a blocker in Stand By is not complete). A blocked card can still move to Next, Doing or Stand By and be worked. Blockers and their dependents complete in one call when the blockers are listed first.

> [!note]- 🔧 The board tools
> Every command works the board through the app's 21 assistant tools: `get_context` (boards, columns, lanes, tags, members, sprints, in one call) · `list_tasks` (a `view`: `inbox` with your inbox groups, `execution`, `week`, `workload`, `sprint`; or filters) · `get_task` · `create_tasks` · `update_tasks` (moves, fields, completing) · `reopen_tasks` · `delete_tasks` · `manage_subtasks` · `manage_recurrence` · `link_tasks` · `manage_boards` · `manage_columns_lanes` · `manage_tags` · `manage_folders` · `set_visibility` · `delete_board_items` · `get_sprints` · `manage_sprints` (sprints are records on a Technical board) · `manage_inbox_groups` (your own groups in an Inbox column) · `add_comment` · `list_events`. The write tools take a list and answer each entry on its own.

📚 **Also reads:** `scope.md` before every read or write (home board, domain, filtering household-wide views) · `board.md` (board profile, sizing, tags and tag view, card descriptions, sub-tasks, safety) · `errors.md` when a call or one of its entries is refused · `gotchas.md` once at the start of a session that writes.

🔗 **Works with:** bandit:project (runs `onboard`, writes `board:` and `dev:`) · bandit:notes (shares Kind and Handler; briefs, plan notes and the lookup of a card's linked notes) · bandit:plan (`load` input; card links on dev projects) · bandit:clarify (its spec becomes a card through `capture` or `spec`) · bandit:audit (runs its board fix rows, including S9's dev board shape) · bandit-dev:sprint (plans and runs sprints over `stage/ready` cards)

---

### 🎙️ bandit:minutes

> [!abstract] Meeting transcript → professional minutes, saved as notes through bandit:notes. It starts from a transcript made where the recording is kept; transcribing a recording in the chat is the fallback. Runs unattended when a transcript arrives
> `plugin` · [[bandit:minutes/SKILL|open skill]] · `/bandit:minutes [transcript]`, or 💬 name or attach the transcript and ask for minutes

| Asks up front | ⚙️ Options                                                       | Default             |
|---------------|------------------------------------------------------------------|---------------------|
| Version       | `Both` · `Full only` · `Short only`                              | Both                |
| Location      | `{Domain} notes` · `In the chat only`                            | Notes               |
| Meeting       | `Supervisors` · `Department` · `Project` (notes only)            | From the transcript |
| Speakers (fallback only) | Separate voices, only if you ask                      | Off                 |
| Model (fallback only)    | `small` · `medium` for poor audio (≈3× slower)        | small               |

📚 **References:** `references/workflow.md` (setup, transcription, verify and save) · `references/scripts.md` (the scripts) · `references/formats.md` (the full and short formats) · `references/notes.md` (saving and filing as notes).
📚 **Scripts:** `scripts/transcribe.py` · `scripts/diarize.py` · `scripts/merge.py`, copied to the working directory before running.
🔗 **Works with:** bandit:notes (its conventions and every note write: two drafts wait for review, then are filed on the domain's workflow board)

---

## 💰 Money

### 💰 bandit:finance

> [!abstract] Works the Bandit Brain Finance module from chat
> `plugin` · [[bandit:finance/SKILL|open skill]] · a `finance: accounts "…"` line in the Project Context limits it to those accounts; no line, or a plain chat, means every account you can see · previews before every bulk write, every delete confirmed, never converts money itself: the one combined figure is the app's net worth, labelled Estimate

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
| `/bandit:finance review`      | `[week · month · YYYY-MM]` | Balances, the forecast (below-zero dates first), spending by category, income against expense, one block per currency; net worth offered, the app's Estimate | 👀     | `review.md`    |
| `/bandit:finance investments` | —                         | Subtypes, contributions and the "Dividend, interest or fee" mark, room left ("Not entered", never zero), tax year, market values with the gain, goals at 65, exchange rates (yours, never proposed), net worth labelled Estimate | 👀 → ✋ | `investments.md` |
| `/bandit:finance audit`       | —                         | Clean-up check: uncategorised, duplicate payees, late or never-matching bills, rules off, budget below zero, not reconciled; fix rows you approve | 👀 → ✋ | `audit.md`     |

> [!note]- 🔧 The Finance tools
> Every command works through the app's 17 Finance tools: `finance_get_context` (accounts, balances, categories, payees, in one call) · `finance_list_transactions` · `finance_get_budget` · `finance_list_schedules` · `finance_get_report` (`forecast`, `reports`, `contributions`, `contribution_room`, `tax_year_contributions`, `goals`, `net_worth`) · `finance_list_rules` · `finance_get_account_history` (with `market_value`) · `finance_manage_accounts` · `finance_manage_transactions` · `finance_manage_budget` · `finance_manage_categories` · `finance_manage_payees` · `finance_manage_schedules` · `finance_import_transactions` · `finance_manage_reconciliation` · `finance_manage_rules` · `finance_delete_items`. Money is whole cents with its currency; some actions stay yours, in the app (who sees an account, deleting accounts and categories, undoing an import, unlocking a reconciled row).

📚 **Also reads:** `scope.md` before every read or write (which accounts) · `money.md` before any amount, date or currency · `errors.md` when a call is refused · `gotchas.md` once at the start of a session that writes.

🔗 **Works with:** bandit:project (writes the `finance:` line) · bandit:tasks (the board; bill reminders arrive there from the app, never from this skill) · bandit:notes (saving a review as a note)

---

## 🧱 Projects & planning

### 🛠️ bandit:project

> [!abstract] The one onboarding command, plus a project's one instructions file and the Project Context block. It works on the surface the chat runs on: a Claude.ai project, or a folder in Claude Code
> `plugin` · [[bandit:project/SKILL|open skill]] · 💬 "onboard this project", "project settings", "audit these instructions"

| Command                            | ⚙️ Modifiers | Does                                                                                                                                                                                                                                  |        | 📚 Reads                                   |
|------------------------------------|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|--------------------------------------------|
| `/bandit:project`                  | —            | No command: picks the mode from the project's state (no instructions → new project, instructions → audit; another project named → says to run it there)                                                                              | —      | `audit.md` → Mode Detection                |
| `/bandit:project onboard`          | —            | New or existing project: interview or audit, then **one proposal** of notes rows (bandit:notes: the hub note), board rows (`/bandit:tasks onboard`) and settings rows, plus a fix row for every finding. In Claude Code the settings rows are the exact changes to `CLAUDE.md` and `.claude/`; on Claude.ai you get the instructions to paste. Only approved rows run | ✋      | `surfaces.md` · `onboard.md` · `interview.md` (new) |
| `/bandit:project audit`            | —            | Says which kind of agent the project is (technical or workflow agent), checks it is ready for Bandit Brain, scores every section of its instructions against the template, flags old Project Context lines, tool names that aren't current, a leftover settings line and a second copy, finds duplicates, and builds the fixed version straight away, all as rows in one proposal. Naming, board and footprint → `/bandit:audit check` (skip for `domain: none`) | 👀 → ✋ | `surfaces.md` · `audit.md`                 |
| `/bandit:project instructions`     | —            | Generates the instructions from the one-page template for the project's type (`workflow`, `product_service`, or `dev` for any `dev: true` project), as one proposal row                                                              | ✋      | `instructions.md`                          |

> [!warning] It proposes; you decide
> Every change to a project's instructions or settings is a row showing the file and the exact change. Nothing is written before your yes. It never writes your own settings (`~/.claude/`, a `settings.local.json`, a permission mode, a model), never removes or loosens a rule or a hook a project has, and never writes outside the project's folder.

> [!note]- 🔀 What `audit` asks first
> Before auditing it asks what changed and what you want: **Full audit** (above), **Targeted update** (you know the change: skips the audit, builds the next version) or **Just the reference notes** (their copies in the app brought up to date).

> [!example]- ⚙️ Answers it records
>
> | Question                   | Options                                                                                                                             |
> |----------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
> | Project type → `type:`     | `product_service` · `workflow` · `claude_marketplace`                                                                               |
> | Dev workflow → `dev: true` | Yes · No. Asked only for `product_service` and `claude_marketplace`; No = no `dev` line                                             |
> | Domain → `domain:`         | A top-level board folder · a new one · none                                                                                         |
> | Task board → `board:`      | existing `project "{name}"` in the domain's folder · a new board (created empty, in the domain's folder) · `none` · `pending`       |
> | Slug and prefix            | The project's own slug · 2–3 letters, or `none`                                                                                     |
> | Notes → `notes: none`      | Yes, in the app (no line; recommended) · No, its records are kept elsewhere (`notes: none`)                                         |
>
> The surface is not asked: it is the one the chat runs on.

> [!tip] One configuration
> A project runs on one surface and has one instructions file: a Claude.ai project's instructions, or `CLAUDE.md` and `.claude/` in its folder. No second copy for another surface is built or kept in step. The reference doc is the note `{slug}-reference` on the project's board; a Claude.ai project's instructions also have a copy there, `{slug}-instructions`.

> [!tip] Kinds of agent (Claude Code)
> **Technical** (`dev: true`, a Technical home board, a repository): the `dev` template, sprints through `bandit-dev`, its own layout. **Workflow agent** (no `dev` line): the working-folder guard (`.claude/hooks/workdir.py`, two hooks, three allow rules) and the layout `work/` `data/` `scratch/` `_closed/` `_backup/`.

📚 **References** (besides each command's file in the table):

- `references/surfaces.md`: first (which surface, where the instructions and settings live, the kind of agent, what a row may write)
- `references/reference-template.md`: before an interview or an audit (the section standard, v2.0: every section, its audit criteria, the token budget)
- `references/project-context.md`: the Project Context block (keys, including the optional `notes: none` line; format; the one copy)
- `references/output.md`: the deliverables and the two reference notes
- `references/workdir.md`: a workflow agent in Claude Code (the guard, onboarding, an S12 row)
- `references/gotchas.md`: once, before onboarding or an audit
- `assets/instructions/`: the one-page templates (`workflow.md` · `product_service.md` · `dev.md`)

🔗 **Works with:** bandit:notes and bandit:tasks (it runs their onboarding steps) · every `bandit` skill (reads its Project Context) · bandit:audit (hands it the rows that change a project's instructions or folder: they are run here, inside that project)

---

### 📐 bandit:audit

> [!abstract] Audits domain and project structure across the boards, each project's Project Context and its working folder, against the structure rulebook. Scored by a script, never by hand. `check` runs inside the project; `audit` and `close` run from Claude Code (the snapshot lives in the folder it runs from)
> `plugin` · [[bandit:audit/SKILL|open skill]] · 💬 "audit the Acme domain", "audit all domains", "check this project in"

| Command               | ⚙️ Modifiers       | Does                                                                                                                                                                                                                    |        | 📚 Reads                          |
|-----------------------|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|-----------------------------------|
| `/bandit:audit`       | —                  | Lists the commands and asks which one                                                                                                                                                                                   | 👀     | —                                 |
| `/bandit:audit check` | —                  | Run inside the project, on its surface: writes its stamp (version, Project Context and, in Claude Code, the working-folder guard and manifest) into the domain's stamps note, scores that project with the script, runs its fix rows. No question | ⚡      | `self-check.md`                   |
| `/bandit:audit audit` | `{domain}` · `all` | From Claude Code. One snapshot of the boards + the stamps + each project's notes → `check_structure.py` → report with numbered fix rows, shown unedited, plus **Extra fix rows** below it for findings the rules don't cover. `all` = every domain, same snapshot. Runs every row in reach, archives the old report, writes the new one (a `log` note) and its snapshot in `.audit/`. No question | ⚡      | `domain-audit.md` · `snapshot.md` |
| `/bandit:audit close` | `{domain}`         | From Claude Code. Replays the report; valid → archives it, snapshot to `.audit/_archive/`                                                                                                                              | ⚡      | `domain-audit.md`                 |

> [!warning] Findings come fixed, through their owners
> Every finding is a fix row, never a bare note; S9 (dev lanes without `dev: true`) is one row with both options; the recommended one runs. It never changes anything with its own calls: every row in reach runs through its owner, no question, in order: notes (bandit:notes) → settings (bandit:project) → board (bandit:tasks). A project changes only itself: a row inside another project comes back as one line saying where to run what.

📚 **Rules:** `structure-rulebook.md` + `structure-rules.yaml` (read-only): 8 rules. S1 domain alignment · S2 one name · S3 one workflow per domain · S4 Project Context (accepts `dev: true`, `notes: none`) · S6 complete footprint · S9 dev board shape · S12 working folder · S13 a sprint card's brief carries the tag `sprint-{name}` (bandit-dev:sprint's SP2 is the same at write time). Retired: S5, S7, S8, S10, S11 (2026-11-22) and S14–S16. **Script:** `scripts/check_structure.py`, snapshot schema 8; an older snapshot is refused and its report is superseded. **Stamps:** the note `{domain}-audit-stamps` on the domain's workflow board, one section per project. **Snapshot:** `.audit/` at the root of the folder Claude Code runs from (`paths.snapshots`), git-ignored.
📚 **Also reads:** `references/fix-rows.md` (building and running fix rows: owners, what is in reach, linked rows, order) · `references/gotchas.md` (once, before a `check` or an `audit`).
🔗 **Works with:** bandit:notes · bandit:tasks · bandit:project (they carry out its fix rows)
🚫 Auditing a skill → `/bandit-maker:skill lint` · board hygiene → `/bandit:tasks audit` · note lint → `/bandit:notes lint`.

---

### 🧭 bandit:plan

> [!abstract] Plans a project in two modes: `project` (idea → project plan → architecture document) and `wbs` (docs or a batch of cards → a numbered, gap-checked work breakdown structure)
> `plugin` · [[bandit:plan/SKILL|open skill]] · 💬 "plan a project", "architecture document", "create a WBS", "break down this project" · saves notes of kind `reference` in the project's place through bandit:notes

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
> | "start a new project" · "plan a project"            | Phase 1 · New    | The `{project}-project-plan` note, every heading `_Pending_` |
> | "continue planning" · "where are we on the project" | Phase 1 · Resume | Picks up at the first `_Pending_` section              |
> | "move to architecture" · "architecture document"    | Phase 2          | The `{project}-architecture` note                      |
> | (planning finished)                                 | Done             | Points you to `/bandit:plan wbs`, which offers the board step |
>
> The phase is read from each note's `status` (`active` / `triaged`) and its `_Pending_` sections; nothing is stored in the project instructions. Planning docs go straight into the project's place, not the inbox, and are saved a section at a time. A note the app refuses as too large (over 200 KB) is split by section, never cut.

> [!example]- 🏗️ `wbs` mode: five phases
>
> | Phase         | Does                                                                                                          |
> |---------------|---------------------------------------------------------------------------------------------------------------|
> | 1 · Ingest    | Reads your docs, or the plan + architecture notes from the project's place                                    |
> | 2 · Analyze   | Gap analysis against a completeness checklist                                                                 |
> | 3 · Resolve   | Asks about the gaps: options + a recommendation                                                               |
> | 4 · Generate  | The WBS as ND-friendly markdown, in the fixed format `/bandit:tasks load` reads                               |
> | 5 · Reconcile | Backports findings into the source doc (the plan note is edited in place), offers to save the `{project}-wbs` note |

⚙️ **Migration mode** (`wbs`): give it an existing WBS (e.g. a Gitea wiki page) → rewritten into this format, gaps listed, no Phase 5 · **Sprint mode** (`wbs`, run by `/bandit-dev:sprint plan`): a WBS over existing cards and their briefs, no Phase 5, no sizes, card links rows for those cards · `dev: true`**:** level glossary in the header, an empty `## 🔗 Card links` section, and it points to `/bandit:tasks spec` per work package, then `/bandit-dev:sprint plan`, instead of `load`. The WBS is saved only as the final note, in the place bandit:notes names; drafts never go to the inbox.
📚 **References:** `references/project.md` (`project` mode) · `references/wbs.md` (`wbs` mode).
🔗 **Works with:** bandit:clarify and bandit:rewrite (before planning) · bandit:project (its Project Context) · bandit:notes (note format, place and every write) · `/bandit:tasks load` (output) · `/bandit:tasks spec` (dev projects, one card per work package) · bandit-dev:sprint (runs sprint mode)

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

⚙️ Simplifies when it's getting too much · offers a deeper pass when it's bigger than it looked · offers a break after 4 or more questions · offers once where the spec goes: a spec that changes skills → a Marketplace card plus brief; dev-project work → `/bandit:tasks spec`; anything else → a note for the domain **and** a card, linked (say *note only* or *card only*; no domain → card only, no board → note only). Cards go through bandit:tasks, notes through bandit:notes.
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

⚙️ Nothing added, nothing dropped: gaps it finds go in an Open questions section at the end, with an offer to run `/bandit:clarify` on them. Code stays as written. Delivers the file (inline for short input); a save as a note goes through bandit:notes.
📚 **References:** `references/rewrite.md` (all four steps).
🚫 A bare "clarify" with nothing to rewrite → bandit:clarify · recordings → bandit:minutes · saving or filing notes → bandit:notes · code, data, slides.

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
🚫 Spreadsheet files → xlsx · charts in HTML artifacts → dataviz · notes → bandit:notes.

---

## 🏃 Delivery (Claude Code)

> [!tip] The `bandit-dev` plugin: the sprint pipeline from plan to close, plus the test data it runs on. Claude Code only, on `dev: true` projects. The stages, surfaces and gates are `docs/pipeline.md`; each project's recipe is its `bandit.yaml` (`docs/bandit-yaml.md`).

### 🏃 bandit-dev:sprint

> [!abstract] Turns a set of existing cards into one planned, approved sprint, then runs, debugs, releases and closes it. The sprint is a real sprint in the app (status, cards in run order); every gate leaves evidence in its ledger, and its papers are notes in the project's notes storage (on the app's Notes tagged `sprint-{name}`; the notes file and the data file in `.sprint/`). No sprint card, no tag; cards with no due date get the sprint date at commit (this week's Sunday when none is given), so the Execution board shows them.
> `plugin` · Claude Code only, from the repo · needs `dev: true`, a `board:` project and `prefix` in the repo `CLAUDE.md` Project Context · 💬 "plan a sprint", "run the waves", "debug the sprint", "close the sprint"

| Command                        | ⚙️ Modifiers                                          | Does                                                                                                                                                                                       |        | 📚 Reads      |
|--------------------------------|-------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|---------------|
| `/bandit-dev:sprint`           | —                                                     | Lists the commands and asks which one                                                                                                                                                      | 👀     | —             |
| `/bandit-dev:sprint plan`      | `[card…]`                                             | The 12-step plan cycle: sticks to the Spec (creative only when you say "creative"), dependencies addressed in the plan, asks only the cards' own open questions or a Spec that cannot be built as written, gaps a convention answers listed for your approval. No list → every open High card not in a sprint, stated and started straight away (open Urgent cards listed as "not selected"). Every card gets its build steps as sub-tasks before its Technical plan: a hook refuses the Technical plan and the commit otherwise. Starts by archiving the papers of any closed or cancelled sprint left behind (SP15). Ends committed: the sprint in the app (cards, run order, expected date, Ready to execute), execution prompt, ledger with one Waves row per wave, one wave note per wave (that wave's part of the plan and ledger, copied word for word), each card's wave and the lands-after links set in the app, and the pre-sprint report: each wave's estimated time in the plan, from the project's past waves, named first in the final message | ✋      | `plan.md` · `pace.md` |
| `/bandit-dev:sprint execute`   | `{sprint}` `[wave N]`                            | One wave in this chat (no number → the first open wave whose cards' blockers are delivered, said out loud). Starts from its wave note and the execution prompt, not the whole plan and ledger; the ledger is read once, before its first ledger write. A search across several files goes to a search agent on Haiku at low effort; the wave reads directly only the files it changes. Refuses a batch card, and a wave whose cards depend on an undelivered card; a paused card in another wave holds back only the cards that depend on it; moves the wave's cards on the Execution board; writes each delivered card's Delivered comment, the one full account of what it delivered (every other paper names the card in one line); rebuilds the sprint's wave report (your open calls, time, checks and tokens measured from the chat logs, lessons for later plans; a one-card wave writes its numbers on its card's ledger row instead of a section); pauses the sprint in the app when the work stops on your answer; never ends while its code review or browser check is still running (a hook holds it), and writes each card's ledger line right after its merge; each card goes through review, one UI check and one full check, in that order (no full check when only docs, notes or comments changed); then stops: next wave, new chat     | ⚡      | `execute.md`  |
| `/bandit-dev:sprint run`       | `{sprint…}` · `--paced [minutes]` (under `/loop`) | Every open wave of each sprint, one new subagent per wave, one at a time, each once its cards' blockers are delivered; the orchestrator checks each wave on the board before the next; stops when no wave is workable (a blocker, or a question only you can answer on a paused card). Refuses a sprint whose plan review isn't done or that an open sprint blocks. `--paced`: one wave per wake-up, 45 minutes apart by default | ⚡      | `run.md`      |
| `/bandit-dev:sprint debug`     | `{sprint}`                                       | After the last wave, in a fresh chat: the sprint's debug card first (it moves to Doing; Claude's Expected lines, your Found lines and the Process lines of every stalled step), your adjustments → one decision table → verified fixes (each fix runs only the tests that cover it; one push at the end, with one full check before it, only when code changed), every line ticked with its outcome. Defects only (against the card or the approved design); anything new becomes a card for a later sprint. With Marketplace cards, the combined test: new helpers from the repo and the new app together on staging                                       | ✋      | `debug.md`    |
| `/bandit-dev:sprint release`   | `{sprint}` + your deploy word                    | Preconditions (every card tested, debug done, your "deploy"/"release"/"ship it" in this message, migration tail recorded, backup confirmed, recipe present, nothing owed to the repository), then the project's `bandit.yaml` release recipe, covering this sprint and every deferred one before it (one `Released:` line names them all); a plugin release for Marketplace cards; the recipe's own steps deploy, watch and confirm the version. A guard runs around every step: a recipe whose notes step comes after the version bump is refused, the project's own release gate runs first, nothing may be committed after the bump's tag, and nothing runs after the deploy push until the CI build is green | ✋      | `release.md`  |
| `/bandit-dev:sprint close`     | `{sprint}`                                       | Releasing is your option: with no app release it writes `Release: deferred` and the next release covers the sprint; a sprint that changed the helpers needs their release first; a card whose last sub-task (`Tested and approved by you`, which no wave, run or debug ever ticks) you ticked is approved, and running close is then the go: no question, no archive proposal; a card with that line open is asked about once, alone. On the app's Notes, writes each card's conclusions into its linked note without asking (descriptions left; a card with no note, two, or a note still in the Inbox is named in the report), completes the approved cards, blockers first, then closes the sprint; archives the sprint's papers and its WBS (each paper set to archived where it is and read back; it does not say closed until the check shows them archived). Makes no commit: it refuses while the trunk is ahead of the released branch | ✋      | `close.md`    |

> [!example]- 📋 The plan cycle: the ledger's 12 Plan steps
>
> | #  | Step                              | Done when                                                                                       |
> |----|-----------------------------------|-------------------------------------------------------------------------------------------------|
> | 1  | Select and freeze the batch       | The sprint created in Planning with the batch as its cards, in no other sprint; the previous open sprint blocks it |
> | 2  | Spec completeness, per card       | Every card read against its brief; gaps as fix rows                                             |
> | 3  | Close the open questions          | One interview answered and recorded                                                             |
> | 4  | Size and classify                 | Every card at most L (XL split), lane and boundaries checked                                    |
> | 5  | Cross-card analysis               | Migrations, shared files, hidden order, docs regeneration written down                          |
> | 6  | Sequence                          | Waves with reasons, split with the WBS (`/bandit:plan wbs`, sprint mode)                        |
> | 7  | Write the one technical plan      | Plan note filed; every card's Technical plan filled; each live check's data from `/bandit-dev:testdata make` |
> | 8  | Risk and rollback                 | Per card and for the sprint, in the plan                                                        |
> | 9  | Definition of ready, per card     | Each Spec reconciled; stage moved on; fix rows for failures                                     |
> | 10 | Approval gate                     | Your explicit approval, quoted in the ledger                                                    |
> | 11 | Independent plan review           | The `plan-reviewer` agent's record with the sprint's papers; majors applied; no blocker open (the only stop) |
> | 12 | Commit the sprint                 | Assignee, the sprint's expected date, Ready to execute, execution prompt, ledger with `Committed:` and one Waves row per wave, one wave note per wave, the debug card assigned to you |

> [!warning] Gates
> **Gate 0** before any command: Claude Code only · Project Context with `dev: true` · a Technical board with Sprints on · repo state (work on the deploy branch is said out loud) · the board server, BanditCloud and a browser tool. **The checker is the proof:** `scripts/check_sprint.py` enforces the sprint rules (SP1–SP3, SP6, SP7, SP9–SP11, SP13–SP15: SP9 and SP10 hold the ledger's Plan steps and Waves) on the project's notes file, `.sprint/{project}-sprint-notes.json`, built fresh through bandit:notes before each run, at step 12, every wave end, `run` and `close`, and runs as the plugin's `Stop` hook in a chat that used the helper (a missing or old notes file is a notice, an error blocks once). `sprint_data.py` and `sprint_targets.py` read the same file. **The recipe** is read through `scripts/recipe.py` from `bandit.yaml`; a missing key refuses by name. Nothing reaches the deploy branch outside `release`, and only `close` completes cards.

📚 **Also reads:** `references/templates.md` (note and card shapes, filenames) · `references/homes.md` (homes, write rules, owners, before a step's first write) · `references/gotchas.md` (once at the start of any command). **Agent:** `plan-reviewer` (read-only, step 11; runs on the top model at high effort, whatever model the chat uses, and the review record names the model that ran). **Hook:** the sprint checker on `Stop`; the description gate refuses a card description the app would show as raw tags (`references/templates.md` → Debug card: a prompt block is never last).
🔗 **Works with:** bandit:tasks (board rules and the `plan-tech` card-write rules) · bandit:notes (the sprint folder, archived at close) · bandit:plan (`wbs` sprint mode) · bandit:project (the Project Context) · bandit-dev:testdata (each live check's data)
🚫 One card's Spec or plan → `/bandit:tasks spec`, `/bandit:tasks plan-tech` · picking ready work outside a sprint → `/bandit:tasks pick-ready`.

---

### 🌱 bandit-dev:testdata

> [!abstract] Made-up data for a dev project's development, test and staging databases, never the user's own
> `plugin` · Claude Code only, from the app repo · needs the `testdata` section of the app's `bandit.yaml` (contract: the sprint skill's `references/bandit-yaml.md`)

| Command                                     | ⚙️ Modifiers                      | Does                                                                                                                       |      | 📚 Reads    |
|---------------------------------------------|-----------------------------------|----------------------------------------------------------------------------------------------------------------------------|------|-------------|
| `/bandit-dev:testdata`                      | —                                 | Lists the commands and asks which one                                                                                      | 👀   | —           |
| `/bandit-dev:testdata map`                  | `[cards or sprint]`               | Reads the schema, the live database's structure, the app's rules and what was built; which tables and rules each card touches | 👀   | `map.md`    |
| `/bandit-dev:testdata fill`                 | `{development, test or staging}`  | A lasting made-up set across the whole app, following its rules, kept until `clean`: a made-up user sees made-up data on every page | ⚡ · staging ✋ | `fill.md`   |
| `/bandit-dev:testdata make`                 | `{cards or sprint}`               | The data each acceptance line needs, in states the rules allow, with the SQL; nothing written                              | 👀   | `make.md`   |
| `/bandit-dev:testdata create`               | `{db}`                            | Writes what `make` prepared and records every id                                                                           | ⚡ · staging ✋ | `create.md` |
| `/bandit-dev:testdata clean`                | `{db}` + a record, `card {label}` or `fill` | Removes exactly the rows a record names, checks none is left; a made-up Account the record created is removed whole by the project's own command (`testdata.owner`) | ⚡ · staging ✋ | `create.md` |

`python3 scripts/dbguard.py records` (in the skill) lists the open run records.

> [!warning] The guard
> Every database call goes through `scripts/dbguard.py`: only development, test and staging; no address or password in `bandit.yaml` (env var names, or `psql` inside the database container); INSERTs only, each recorded; `clean` deletes only recorded ids; staging writes need your yes on every run. Records live in the app's git-ignored `.testdata/`.

📚 **Also reads:** `references/safety.md` once at the start of any command (made-up values, credentials, staging, what the guard enforces).
🔗 **Works with:** bandit-dev:sprint (planning runs `make` per live check; waves run `create` before the check and `clean` after it).

---

## 🔎 Full review prompts

> [!tip] How these run
> Paste one, with the `{…}` placeholder filled in. **Phase 1** runs every audit read-only. **Phase 2** asks every question once: your single answer approves every fix row. **Phase 3** runs everything in reach with no more stops. What's left for you at the end: the rows that belong to another project (run there), and on Claude.ai the paste.

### 📁 One project

Paste into that project's own chat: its Claude.ai project, or Claude Code in its folder.

```
Full setup review of this project: {Project name}. Work in three phases.

PHASE 1 — DISCOVERY (read-only, write nothing)
Run each of these with its own skill and procedure. No shortcuts, and no scoring by hand:
  a. /bandit:project audit, as a full audit ("audit these instructions"). It includes /bandit:audit check and the notes and board rows. Build the updated instructions version, but don't write it yet.
  b. /bandit:notes lint, limited to this project's board.
  c. /bandit:tasks audit.
Collect every fix row from a–c into ONE numbered table: | # | Skill | Action | Target | Recommended option |.

PHASE 2 — ONE QUESTION ROUND
Show the table, then every decision any row needs (either/or choices, deletes, anything a skill would normally ask). Ask everything at once, as numbered questions, each with options and a recommendation. Also mark which rows depend on each other.
My single answer approves everything: "all", a list of row numbers, or "none", plus my answers to the questions. After that, ask me nothing.

PHASE 3 — AUTONOMOUS RUN (no more stops)
- Run exactly the approved rows, through their owner skills, in this order: notes rows (bandit:notes), then settings (bandit:project: the instructions and, in Claude Code, the files in the folder), then board (bandit:tasks).
- My Phase 2 answer is the approval each skill would normally ask for. Don't ask again.
- A row that depends on a declined or failed row is skipped, and the reason is recorded.
- If something new turns up during the run, don't act on it. Add it to the final report as a fix row.
- Never delete anything I didn't approve by name.

FINAL REPORT
One result line per row, then the fix rows for anything new, then my hand-off:
  1. On Claude.ai: the full instructions text to paste into this project. In Claude Code: the files changed, for my own commit.
  2. Then: run /bandit:audit check in this chat.
```

### 🌐 Whole domain

Paste into a Claude Code session (the audit's snapshot lives in the folder it runs from): a repository, or an agent's folder without the working-folder guard.

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
- Write the audit report as a note on the domain's workflow board, and its snapshot to `.audit/`.
- Run exactly the approved rows in reach through their owner skills, in this order: notes rows (bandit:notes), then board (bandit:tasks). A row that changes another project's instructions or folder is not run from here: it goes to the hand-off list.
- My Phase 2 answer is the approval each skill would normally ask for. Don't ask again.
- A row that depends on a declined or failed row is skipped, and the reason is recorded. Half of a linked pair never runs alone.
- If something new turns up during the run, don't act on it. Add it to the final report as a fix row.
- Never delete anything I didn't approve by name.
- Don't run /bandit:audit close. Checks are still pending.

FINAL REPORT
One result line per row, then the fix rows for anything new, then my hand-off list:
  1. For each project with rows of its own: the project, and the line to run there (/bandit:project audit for {the change}).
  2. The projects where I run /bandit:audit check afterwards.
  3. The last step: /bandit:audit close {Domain} in this chat, once 1 and 2 are done.
```

## 🔁 Keeping this page current

- Any marketplace change that adds, removes or changes a command, modifier, trigger phrase or reference file updates this page in the same commit.
- `house_lint.py --names docs/cheat-sheet.md` keeps its bare commands from clashing with skill commands (R15).
- `python3 scripts/check_repo.py` fails when a skill command is missing from this page (rule CS1).
- `python3 scripts/done_check.py` lists what changed since the last release and each place that must change with it, this page included (`docs/dependencies.md`).

## Related

- `README.md` (repo root): the three plugins and how to install them
- `docs/pipeline.md`: the eleven stages from idea to closed release, and the command that owns each
- `docs/dependencies.md`: what changes together
- bandit-maker:skill `references/rulebook.md`: the house standard every skill is audited against