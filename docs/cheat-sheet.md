---
type: reference
summary: Every command, mode and trigger of Leo's 12 skills, grouped by skill, with modifiers and the reference files each one reads.
updated: 2026-10-13
---

# 🧭 Skills Cheat Sheet

> Every command, mode and trigger of Leo's 12 skills, grouped by skill, with modifiers and the reference files each one reads.

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
> Kept in the bandit-brain-marketplace repo (`docs/cheat-sheet.md`). Copied on 2026-10-13 from the retired vault folder with every skill and command renamed to the plugin calls (`/bandit:tasks`, `/bandit-dev:sprint` …); detail may lag the v0.1.0 skills, whose routers are the source of truth. Regenerating it from the skills is a later card.

> [!important] Findings come fixed
> Every audit and review (bandit:audit, `/bandit:notes lint` and `onboard`, `/bandit:tasks audit`, bandit:project audits, `/data-tools review`) returns each finding as a numbered **fix row** in the same proposal, fix already built, recommended option first. Answer all, a list or none: one "all" fixes everything. Nothing runs without your yes.

---

## 🗂️ At a glance

|     | Skill                                        | Start it with                 | Use it for                                                                       |
|-----|----------------------------------------------|-------------------------------|----------------------------------------------------------------------------------|
| 🗃️ | [[#🗃️ bandit:notes\|bandit:notes]]         | `/bandit:notes {command}`     | Vault rules, filing the inbox, domain home pages                                 |
| ✅   | [[#✅ bandit:tasks\|bandit:tasks]]           | `/bandit:tasks {command}`     | The BanditBrains task board, plus the dev card workflow on `dev: true` projects  |
| 🎙️ | [[#🎙️ bandit:minutes\|bandit:minutes]]   | 💬 attach audio + "minutes"   | Meeting recording → minutes in the vault                                         |
| 🛠️ | [[#🛠️ bandit:project\|bandit:project]] | 💬 "onboard this project"     | Onboarding (instructions + vault + board, one approval) and project instructions |
| 📐  | [[#📐 bandit:audit\|bandit:audit]]          | `/bandit:audit {command}`     | Domain and project structure: Claude.ai ↔ vault ↔ board                          |
| 🧭  | [[#🧭 bandit:plan\|bandit:plan]]    | 💬 "start a new project"      | Project plan → architecture doc                                                  |
| 🏗️ | [[#🏗️ bandit:plan\|bandit:plan]]       | 💬 "create a WBS"             | Docs → work breakdown structure                                                  |
| 🔍  | [[#🔍 clarify\|clarify]]                    | 💬 "clarify"                  | A thought, no text yet → questions → clear spec                                  |
| ✨   | [[#✨ bandit:rewrite\|bandit:rewrite]]         | 💬 "clean this up"            | Text you already have → readable markdown, no questions                          |
| 💡  | [[#💡 prompt-engineer\|prompt-engineer]]    | 💬 "help me write the prompt" | Prompts for coding work                                                          |
| 🧪  | [[#🧪 bandit-maker:skill\|bandit-maker:skill]]    | 💬 "make a skill for…"        | Build, test and tune skills                                                      |
| 🧰  | [[#🧰 data-tools\|data-tools]]              | `/data-tools {command}`       | Databases, dbt, data audits, profiling, analysis, notebooks                      |

> [!important] New project? Run **bandit:project** ("onboard this project"). It's the one onboarding command: it runs the vault step (bandit:notes) and the board step (bandit:tasks) and shows everything in one proposal.

---

## 📝 Notes & tasks

### 🗃️ bandit:notes

> [!abstract] Owns the MyNotes vault: folders, filenames, frontmatter, status, archiving, home pages
> `plugin` · [[bandit:notes/SKILL|open skill]] · domain comes from the Project Context `domain:`, from bandit:project during onboarding, or the command, or it asks

| Command                  | ⚙️ Modifiers           | Does                                                                                                                                                                                                                       |        |
|--------------------------|------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|
| `/bandit:notes`          | —                      | Lists the commands and asks which one                                                                                                                                                                                      | 👀     |
| `/bandit:notes onboard`  | `[Domain]`             | Audits a domain against the conventions, proposes the migration in stages A→D. New project → use bandit:project                                                                                                          | ✋      |
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

- `references/conventions.md`: before any write into the vault
- `references/commands.md`: the procedure of the command being run, including *Onboarding rows* (run by bandit:project; it adds `Claude/code-{slug}/` for `dev: true` projects and for any other project that runs in Claude Code, and returns domain findings as `domain` fix rows)
- `references/readme-template.md`: for `home` and `init`

🔗 **Works with:** bandit:project (runs its onboarding rows) · bandit:minutes · bandit:tasks · bandit:plan (write planning docs straight into `Projects/{slug}/`, or its `planning/` on a sprint project) · bandit:audit (runs its vault fix rows)

---

### ✅ bandit:tasks

> [!abstract] Operates the BanditBrains task board
> `plugin` · [[bandit:tasks/SKILL|open skill]] · writes only inside the Project Context `board:` (`none` or `pending` → read only, except `load` and `onboard`) · dev commands only with `dev: true`

| Command                                        | ⚙️ Modifiers                        | Does                                                                                                                                                                                                                                                                                                               |        | 📚 Reads             |
|------------------------------------------------|-------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|----------------------|
| `/bandit:tasks`                                | —                                   | Lists the commands and asks which one                                                                                                                                                                                                                                                                              | 👀     | —                    |
| `/bandit:tasks triage` · `/bandit:tasks inbox` | —                                   | Sorts the Inbox board: untriaged → project, parked → column. Counts first                                                                                                                                                                                                                                          | ✋      | `triage.md`          |
| `/bandit:tasks capture`                        | `{text or brain dump}`              | Creates tasks, subtasks, dependencies, repeat rules                                                                                                                                                                                                                                                                | ⚡      | `capture.md`         |
| `/bandit:tasks today`                          | —                                   | Reads Execution: Doing, Next, Assigned. Flags cap breach, overdue, stale Stand By (sprint cards exempt)                                                                                                                                                                                                                                 | 👀     | `execution.md`       |
| `/bandit:tasks doing`                          | `{task}`                            | Moves a task to Doing (dependency gates apply)                                                                                                                                                                                                                                                                     | ⚡      | `execution.md`       |
| `/bandit:tasks done`                           | `{task}`                            | Completes it. Recurring → reports the next date                                                                                                                                                                                                                                                                    | ⚡      | `execution.md`       |
| `/bandit:tasks bump`                           | `{task…}` `{date}`                  | Changes the due date. Recurring → offers a skip instead                                                                                                                                                                                                                                                            | ⚡      | `execution.md`       |
| `/bandit:tasks week`                           | —                                   | Reads the week, day by day. Projections marked                                                                                                                                                                                                                                                                     | 👀     | `week.md`            |
| `/bandit:tasks week`                           | `[project]`                         | Proposes dates for undated tasks                                                                                                                                                                                                                                                                                   | ✋      | `week.md`            |
| `/bandit:tasks review`                         | —                                   | Recaps the week from the event log, proposes resize or drop                                                                                                                                                                                                                                                        | 👀 → ✋ | `week.md`            |
| `/bandit:tasks audit`                          | —                                   | Ten hygiene checks, every finding a numbered fix row with the exact call (unreadable repeat rules rebuilt from their history, marked unchecked; board-shape problems get a concrete change). Archive candidates. Dev boards add card checks V1–V6 (lane/stage tags, plan note filed, XL, duplicates, `Spec change needed:` comments, card complete); sprint cards are exempt from V1, V3 and V6, and from Stand By rot; `sprint/*` tags from the orphan and off-vocabulary checks | 👀 → ✋ | `audit.md`           |
| `/bandit:tasks email`                          | —                                   | Gmail → proposed tasks. Never writes                                                                                                                                                                                                                                                                               | 👀     | `email.md`           |
| `/bandit:tasks load`                           | `[WBS]`                             | WBS → a Deliverable project: deliverables become columns, work packages undated tasks, dependencies wired. Resumes a half-done load. Refused on `dev: true` projects                                                                                                                                               | ✋      | `load.md`            |
| `/bandit:tasks onboard`                        | —                                   | The board step of onboarding, run by bandit:project: resolves the `board:` scope or creates one empty project (Backlog only). New board names follow rulebook S2/S3. `dev: true` → adds the dev board shape rows (tags + six lanes)                                                                              | ✋      | `onboard.md`         |
| `/bandit:tasks spec`                           | `[card]`                            | 🛠️ Dev: writes a complete card from the app's lane template: area column (the module or page; ask if unclear), `lane/*` + `stage/spec` + handler + energy tags, priority, complexity, effort, assignee, dependencies, plus its brief (bandit:notes). XL splits before anything is created. Merge check first. Incident: no stage, dated today | ✋      | `dev-workflow.md`    |
| `/bandit:tasks spec reconcile`                 | `{card…}`                           | 🛠️ Dev: brings locked Specs in line with decisions taken since. Shows old and new Spec for every card, applies your one yes with the lock override, reads back, comments each card | ✋      | `dev-workflow.md`    |
| `/bandit:tasks plan-tech`                      | —                                   | 🛠️ Dev, Claude Code only: drift check, lists `stage/spec` cards, writes the plan note (inbox) and the card's `Technical plan`                                                                                                                                                                                     | ✋      | `dev-workflow.md`    |
| `/bandit:tasks stage`                          | `{card}` `{spec · planned · ready}` | 🛠️ Dev: the only stage writer. `planned` needs the plan note filed (a shared sprint plan counts); `ready` only on your explicit approval, either surface | ✋      | `dev-workflow.md`    |
| `/bandit:tasks pick-ready`                     | —                                   | 🛠️ Dev: `plan` over `stage/ready` cards outside a sprint. Picks and dates work; sprint planning is `bandit-dev:sprint`'s. `sprint` still runs it for one release | ✋      | `dev-workflow.md` · `week.md` |

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
> Dev boards: **Lane** `lane/incident` `lane/issue` `lane/feature` `lane/maintenance` `lane/content` `lane/tech-debt` · **Stage** `stage/spec` → `stage/planned` → `stage/ready` (kept after completion) · **Sprint** `sprint/{name}` (`list_sprints`)

> [!note]- 🛠️ Dev surfaces
> Claude.ai = high-level: `spec`, `stage … ready`, `pick-ready`. Claude Code (Project Context from the repo `CLAUDE.md`) = everything, plus `plan-tech` and all stages. Cards stay thin: `Spec` + `Technical plan`, up to L; XL splits. Every field filled (`dev.md` → 🧾 Card fields). A written Spec is locked: changes go in a `Spec change needed:` comment. Project-management cards go in the `PM` column.
> **Sprint card:** PM column (the dev board shape adds it when missing), no lane, stage or Spec; the batch cards are its blockers and carry `sprint/{name}`; its sections and sub-tasks are bandit-dev:sprint's, and only its sprint plan dates the batch. An XL card splits and the new card stays in the sprint. A blocker in Stand By still blocks Doing (BB-94 not built).
>
> 📚 `dev.md` = board rules (lanes, stages, card sections and fields, Spec lock, tag merging, dev board shape) · `dev-workflow.md` = the dev commands, surfaces, B1–B7, record homes · `errors.md` = every refusal code, read when a call is refused.

🔗 **Works with:** bandit:project (runs `onboard`, writes `board:` and `dev:`) · bandit:notes (shares Kind and Handler; plan notes and the plan-note lookup) · bandit:plan (`load` input; card links on dev projects) · bandit:audit (runs its board fix rows, including S9's dev board shape)

---

### 🎙️ bandit:minutes

> [!abstract] Meeting recording → professional minutes, saved to the vault
> `plugin` · [[bandit:minutes/SKILL|open skill]] · 💬 attach the audio and ask for minutes

| Asks up front | ⚙️ Options                                                       | Default             |
|---------------|------------------------------------------------------------------|---------------------|
| Version       | `Both` · `Full only` · `Short only`                              | Both                |
| Location      | `{Domain} vault` · `Same folder as the audio` · `Another folder` | The vault           |
| Meeting       | `Supervisors` · `Department` · `Project`                         | From the transcript |
| Speakers      | Separate voices, only if you ask                                 | Off                 |
| Model         | `small` · `medium` for poor audio (≈3× slower)                   | small               |

📚 **Scripts:** `scripts/transcribe.py` · `scripts/diarize.py` · `scripts/merge.py`, copied to the working directory before running.
🔗 **Works with:** bandit:notes (its conventions; files to `_inbox/` with `file-to: Meetings/`)

---

## 🧱 Projects & planning

### 🛠️ bandit:project

> [!abstract] The one onboarding command, plus Claude.ai project instructions and the Project Context block
> `plugin` · [[bandit:project/SKILL|open skill]] · 💬 "onboard this project", "project settings", "audit these instructions"

| Mode                   | Starts when                                                                         | ⚙️ Options                                                                                                                                                                                                                                                             |
|------------------------|-------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 🚀 **Onboard**         | New project, or an existing one missing pieces                                      | Interview or audit → one proposal: vault rows (bandit:notes) + board rows (bandit:tasks) + settings files + a fix row for every finding. Only approved rows run                                                                                                        |
| 🆕 **New project**     | The project has no instructions                                                     | Interview in 4 phases → instructions + reference doc, then the onboarding proposal                                                                                                                                                                                     |
| 🔎 **Full audit**      | Instructions exist                                                                  | Scores every section, finds duplicates, builds the fixed version straight away (no "want me to generate?") and adds whatever the vault or board is missing, all as rows in one proposal. Naming, board and footprint → `/bandit:audit check` (skip for `domain: none`) |
| 🎯 **Targeted update** | Instructions exist, you know the change                                             | Skips the audit, writes the next version                                                                                                                                                                                                                               |
| 🔄 **Vault update**    | Another project needs the change (you name it, or bandit:audit runs a settings row) | Only the requested change → next version in that project's vault folder; anything else noticed comes back as an extra fix row. You paste it there, then `/bandit:audit check` (skip for `domain: none`)                                                                |
| ☁️ **Just sync**       | Instructions exist                                                                  | Saves the current version to the vault folder                                                                                                                                                                                                                          |

> [!example]- ⚙️ Answers it records
>
> | Question                   | Options                                                                                                                             |
> |----------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
> | Project type → `type:`     | `product_service` · `workflow` · `claude_marketplace`                                                                               |
> | Dev workflow → `dev: true` | Yes · No. Asked only for `product_service` and `claude_marketplace`; No = no `dev` line                                             |
> | Claude Code surface        | Yes · No. Asked for every project without `dev: true`. Yes → `Claude/code-{slug}/` + the Claude Code twin. No Project Context key   |
> | Task board → `board:`      | existing `project "{name}"` · existing `folder "{name}"` · new project on the board (created empty) · `global` · `none` · `pending` |
> | Output                     | Artifact · + vault folder · vault folder only                                                                                       |
> | Folder backend             | Domain (or custom path → `domain: none`) · project slug · prefix                                                                    |

> [!note] Audits flag and migrate legacy projects: Notes-app storage → vault folder, and old `lifecycle` blocks are dropped.

> [!tip] `dev: true` projects: onboarding adds the dev board shape, the instructions allow `/bandit:tasks spec`, and you get the exact Project Context block to put in the repo's `CLAUDE.md` for Claude Code.

> [!tip] Claude Code surfaces live in `Claude/code-{slug}/`, settings only. Any project without `dev: true` that also runs in Claude Code gets a **twin** `CLAUDE.md` (same core and version; only `## 🖥️ Environment` differs), plus an optional `claude/settings.json` for the agent's permission rules. The twin keeps its type's scope. A `dev: true` repo gets a **dev mirror**: a `Stop` hook has Claude copy `CLAUDE.md` + `.claude/` (stored as `claude/`) into the vault.

📚 **References:**

- `references/reference-template.md`: before any interview or audit (the section standard, v1.4)
- `references/interview.md`: the new-project interview, 4 phases
- `references/vault-storage.md`: before any write to, or audit of, the settings folder
- `references/dev-mirror.md`: onboarding or auditing a `dev: true` project (the Stop hook and mirror script, plus the optional sprint-checker hook)

🔗 **Works with:** bandit:notes and bandit:tasks (it runs their onboarding steps) · bandit:minutes · bandit:plan · bandit:plan (all read its Project Context) · bandit:audit (runs its settings rows)

---

### 📐 bandit:audit

> [!abstract] Audits domain and project structure across Claude.ai, the vault and the board, against the structure rulebook. Scored by a script, never by hand
> `plugin` · [[bandit:audit/SKILL|open skill]] · 💬 "audit the BanditLabs domain", "audit all domains", "is this project in sync with the vault"

| Command               | ⚙️ Modifiers       | Does                                                                                                                                                                                                                    |        | 📚 Reads                          |
|-----------------------|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|-----------------------------------|
| `/bandit:audit`       | —                  | Lists the commands and asks which one                                                                                                                                                                                   | 👀     | —                                 |
| `/bandit:audit check` | —                  | Run inside the project: stamps its running instructions version, scores that project with the script. Its fix rows run with the stamp row on your yes                                                                   | 👀 → ✋ | `self-check.md`                   |
| `/bandit:audit audit` | `{domain}` · `all` | One snapshot of board + vault + stamps → `check_structure.py` → report with numbered fix rows, shown unedited, plus **Extra fix rows** below it for findings the rules don't cover. `all` = every domain, same snapshot | 👀 → ✋ | `domain-audit.md` · `snapshot.md` |
| `/bandit:audit close` | `{domain}`         | Replays the report; valid and fixes done → moves report + snapshot to `_archive/`                                                                                                                                       | ✋      | `domain-audit.md`                 |

> [!warning] Findings come fixed, through their owners
> Every finding is a fix row, never a bare note; S9 (dev lanes without `dev: true`) is one row with both options, recommended first. It never changes anything with its own calls: approved rows run through their owners, in order: vault (bandit:notes) → settings (bandit:project) → board (bandit:tasks). A board rename always comes paired with its `board:` update.

📚 **Rules:** `structure-rulebook.md` + `structure-rules.yaml` (read-only): 16 rules. S9 = dev board shape (`dev: true` boards have the six dev lanes, others have none) · S10 = Claude Code twin of any project without `dev: true` · S11 = dev mirror (`code-{slug}/` has the Stop hook and script) · S12 = Claude Code working folder · S13–S16 = sprint projects' vault content (briefs in their sprint folder, no filename twice in `Projects/` and `_inbox/`, frontmatter parses, root holds only hub + `sprint-*` + `planning/`; bandit-dev:sprint's local checker enforces the same at write time). **Script:** `scripts/check_structure.py`, snapshot schema 5 (lanes + tags + surfaces + working-folder manifests + project files and frontmatter + sprint cards). **Ledger:** `paths.stamps` in the rules. Reports go to `{Domain}/Projects/{workflow-project}/`, never a settings folder.
🔗 **Works with:** bandit:notes · bandit:tasks · bandit:project (they carry out its fix rows)
🚫 Auditing a skill → `/bandit-maker:skill lint` · board hygiene → `/bandit:tasks audit` · note lint → `/bandit:notes lint`.

---

### 🧭 bandit:plan

> [!abstract] Solo project lifecycle: idea → project plan → architecture document
> `plugin` · [[bandit:plan/SKILL|open skill]] · saves to the vault: `MyNotes/{domain}/Projects/{project}/` (`planning/` on a sprint project)

| 💬 Say                                              | Mode             | Output                                                 |
|-----------------------------------------------------|------------------|--------------------------------------------------------|
| "start a new project" · "plan a project"            | Phase 1 · New    | `{project}-project-plan.md`                            |
| "continue planning" · "where are we on the project" | Phase 1 · Resume | Picks up at the first `_Pending_` section              |
| "move to architecture" · "architecture document"    | Phase 2          | `{project}-architecture.md`                            |
| (planning finished)                                 | Done             | Points you to bandit:plan, which offers the board step |

📚 **References:** none. The phase is read from each document's `status` (`active` / `triaged`); nothing is stored in the project instructions.
🔗 **Works with:** bandit:plan · bandit:tasks · bandit:project

---

### 🏗️ bandit:plan

> [!abstract] Project docs → a numbered work breakdown structure
> `plugin` · [[bandit:plan/SKILL|open skill]] · 💬 "create a WBS", "break down this project", "what needs to happen to deliver this?"

| Phase         | Does                                                                                                          |
|---------------|---------------------------------------------------------------------------------------------------------------|
| 1 · Ingest    | Reads your docs, or the plan + architecture from the project's vault folder                                   |
| 2 · Analyze   | Gap analysis against a completeness checklist                                                                 |
| 3 · Resolve   | Asks about the gaps: options + a recommendation                                                               |
| 4 · Generate  | The WBS as ND-friendly markdown, in the fixed format `/bandit:tasks load` reads                               |
| 5 · Reconcile | Backports findings into the source doc (the vault plan is edited in place), offers to save `{project}-wbs.md` |

⚙️ **Migration mode:** give it an existing WBS (e.g. a Gitea wiki page) → rewritten into this format, gaps listed · `dev: true`**:** level glossary in the header, an empty `## 🔗 Card links` section, and it points to `/bandit:tasks spec` per work package, then `/bandit-dev:sprint plan`, instead of `load` · **Sprint mode** (run by bandit-dev:sprint): a WBS over existing cards and their briefs, no Phase 5, no sizes, card links rows for those cards. Saved to the folder bandit:notes names (`planning/` on a sprint project); drafts never go to `_inbox`.
📚 **References:** none.
🔗 **Works with:** bandit:plan (input) · `/bandit:tasks load` (output) · `/bandit:tasks spec` (dev projects, one card per work package)

---

## ✍️ Thinking & writing

> [!tip] Got text yet? No, just a thought → **clarify** asks you questions. Yes → **bandit:rewrite** rewrites it.

### 🔍 clarify

> [!abstract] A thought you can't put into words yet → questions → a clear, actionable spec, with the 4-D method
> `plugin` · [[clarify/SKILL|open skill]] · 💬 "clarify" (that word alone is enough), "help me think through this", "what do I need to decide"

| Phase                  | Does                                                                                 |
|------------------------|--------------------------------------------------------------------------------------|
| Deconstruct · Diagnose | Silent: breaks the request apart, finds what's missing                               |
| Develop                | Asks a few chunked questions, with options                                           |
| Deliver                | A Clarified Specification: summary, scope, requirements, assumptions, open questions |

⚙️ Simplifies when it's getting too much · offers a deeper pass when it's bigger than it looked · checks cheap assumptions with one call before delivering, each marked verified or unverified · offers to save the spec: a spec that changes skills → a Marketplace card plus brief; dev-project work → `/bandit:tasks spec`; anything else → the domain `_inbox` via bandit:notes (not with `domain: none`)
📚 **References:** none. 🔗 Other skills hand off to it with "use the 4-D method".
🚫 Pasted content that needs rewriting → bandit:rewrite.

---

### ✨ bandit:rewrite

> [!abstract] Text you already have (notes, brain dumps, transcripts) → clean, scannable ND-friendly markdown, in one pass, no questions asked
> `plugin` · [[bandit:rewrite/SKILL|open skill]] · 💬 "process this", "clean this up", "make this readable", "deduplicate this"

| Step               | Does                                      |
|--------------------|-------------------------------------------|
| 1 · Ingest & audit | Inventories the content, finds duplicates |
| 2 · Structure      | Designs emoji-anchored sections           |
| 3 · Write          | Rewrites into short, scannable blocks     |
| 4 · Final pass     | Checks nothing was lost                   |

⚙️ Gaps it finds go in an Open questions section at the end, with an offer to run `/bandit:clarify` on them.
📚 **References:** none.
🚫 A bare "clarify" with nothing to rewrite → clarify · recordings → bandit:minutes · filing into the vault → bandit:notes · code, data, slides.

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
🚫 Doing the task itself · vague idea → clarify · project instructions → bandit:project · skills → bandit-maker:skill.

---

## 🛠️ Claude tooling

### 🧪 bandit-maker:skill

> [!abstract] Create, test, benchmark and tune skills
> `plugin` · [[bandit-maker:skill/SKILL|open skill]] · 💬 "make a skill for…", "improve this skill", "run evals"

| 💬 Say                     | Does                                                                                                                 |
|----------------------------|----------------------------------------------------------------------------------------------------------------------|
| "turn this into a skill"   | Captures intent, interviews, writes the SKILL.md                                                                     |
| "test it" · "run evals"    | Runs test prompts with and without the skill, opens the review viewer                                                |
| "benchmark it"             | Repeated runs with variance analysis                                                                                 |
| "which version is better?" | Blind A/B comparison                                                                                                 |
| "fix the triggering"       | Optimizes the description against trigger evals                                                                      |
| "make it house-standard"   | Applies the rulebook: trigger description, Gotchas, Never, emoji H2s. A `house_lint.py` ❌ blocks the package or card |

📚 **References:**

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

## 🔎 Full review prompts

> [!tip] How these run
> Paste one, with the `{…}` placeholder filled in. **Phase 1** runs every audit read-only. **Phase 2** asks every question once: your single answer approves every fix row. **Phase 3** runs everything with no more stops. What's left for you at the end: pasting instructions into Claude.ai, and running `/bandit:audit check` inside those projects.

### 📁 One project

Paste into that project's own chat.

```
Full setup review of this project: {Project name}. Work in three phases.

PHASE 1 — DISCOVERY (read-only, write nothing)
Run each of these with its own skill and procedure. No shortcuts, and no scoring by hand:
  a. bandit:project full audit ("audit these instructions"). It includes /bandit:audit check and the vault and board rows. Build the updated instructions version, but don't write it yet.
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

## Related

- `README.md` (repo root): the three plugins and how to install them
- bandit-maker:skill `references/rulebook.md`: the house standard every skill is audited against