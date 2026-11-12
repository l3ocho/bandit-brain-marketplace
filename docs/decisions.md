# 🧭 Decisions

> Every locked decision behind this repo: Leo's direction (R1–R8), the architecture (brief §1–§5, §7), the context-light rules (L1–L7), the build-session guards (G1–G9) and the original plan's D1–D24, each marked kept or superseded.

Sources (BanditCloud vault, `MyNotes/BanditLabs/`): `banditbrain-structure-discussion-points` (R1–R8), `banditbrain-maintenance-marketplace-architecture-2026-10-13` (**the brief**), `banditbrain-maintenance-plugin-marketplace-bootstrap-plan` (D1–D24). Where they disagree: the brief wins, then the sprint plan, then the bootstrap plan.

---

## 🧱 Direction (Leo, 2026-10-13)

| # | Decision |
|---|---|
| R1 | All development is paused until this setup ships. No steps in between |
| R2 | Tune in use: adjustments come while Leo tests the commands, through smaller sprints |
| R3 | The implementation is done after at least 3 full-size sprints have run through it |
| R4 | Then a retroactive process-improvement workflow, so the skills keep adapting to Claude's model and product updates |
| R5 | Claude.ai is the target for every AI feature, for now and for some time |
| R6 | Storage: Nextcloud only for now. The future document module in Bandit Brain owns vault access; tasks and notes are reached through the app's MCP |
| R7 | One storage contract (read, create-if-absent, edit-if-unchanged, move-without-overwrite, list, find, delete), enforced by code; Nextcloud is its first implementation |
| R8 | Rebrand, free of the old names, as light as possible: four owners, three plugins, one skill per area with the verb as argument, rules L1–L7 enforced by the checker, the app's recipe in `bandit.yaml` |

---

## 🏗️ Architecture (the brief)

### §1 · Four owners

| Layer | Owns | Lives in |
|---|---|---|
| Product | Architecture, data model, domain rules, branch model, release and migration recipe | The app repo, its `docs/`, its `.claude/` and `bandit.yaml` |
| Project configuration | Project Context, board shape, vault folder, which command applies at which stage | Claude.ai project instructions and the repo `CLAUDE.md` block, written by `/bandit:project` |
| Behaviour | How Claude works with the tool, the same in every project: capture, triage, spec, sprint, release as stages and gates | This repo's skills |
| Enforcement | Rules that must hold | The app's MCP refusals (both surfaces); `bandit-dev` hooks and repo hooks (Claude Code); `scripts/check_repo.py` (this repo) |

On Claude.ai the agent is the project instructions plus the core skills: hooks and agents don't run there.

### §2 · Three plugins, split by pipeline stage

| Plugin | Contents | Surfaces |
|---|---|---|
| `bandit` | Skills only: no hooks, no agents, no `bin/` | Claude.ai + Claude Code |
| `bandit-dev` | `sprint`, `agents/plan-reviewer.md`, `hooks/hooks.json`; `"dependencies": ["bandit"]` | Claude Code |
| `bandit-maker` | `skill` | Claude Code, Bandit Port |

Stages 1–4 are core (stage 4, design, runs Claude Design); stages 5–11 are `bandit-dev`. Dependencies point one way: `bandit-dev` may call core, never the reverse. Each plugin carries its own references (the structure rulebook lives with `audit`).

### §3 · Names

<!-- denylist:off -->
| Before | Skill | Call | Plugin |
|---|---|---|---|
| bandit-tasks | `tasks` | `/bandit:tasks triage` | bandit |
| bandit-notes | `notes` | `/bandit:notes file` | bandit |
| project-settings | `project` | `/bandit:project onboard` | bandit |
| bandit-audit | `audit` | `/bandit:audit check` | bandit |
| clarify | `clarify` | `/bandit:clarify` | bandit |
| text-rewriter | `rewrite` | `/bandit:rewrite` | bandit |
| project-planner + wbs-generator | `plan` | `/bandit:plan project` · `/bandit:plan wbs` | bandit |
| meeting-minutes | `minutes` | `/bandit:minutes` | bandit |
| bandit-sprint | `sprint` | `/bandit-dev:sprint run` | bandit-dev |
| myskill-creator | `skill` | `/bandit-maker:skill lint` | bandit-maker |
<!-- denylist:on -->

`tasks plan` (week planning) folds into `/bandit:tasks week`. The old names are gone: no aliases, no stubs; the checker fails on any of them.

### §4 · Context-light rules

| # | Rule | Check |
|---|---|---|
| L1 | Description ≤ 300 characters: what the skill does and when to use it; at most one "not for X" clause | `check_repo.py` |
| L2 | `SKILL.md` ≤ 150 lines: a router table (command → `references/{command}.md`) plus hard rules | `check_repo.py` |
| L3 | A rule lives in one place, in the skill that owns it; others name that skill | house lint (judgment) |
| L4 | No project details in skills: no project names, stack tools, IDs or fixed vault paths | `check_repo.py` denylist |
| L5 | Project instructions template ≤ 1 page: Project Context, stage → command map, modes | `check_repo.py` on `templates/` |
| L6 | App repo `CLAUDE.md` ≤ 10 KB | App repo hook (BB-149) |
| L7 | No top-level `bin/` in any plugin | `check_repo.py` |
| L8 | No person in shipped files: skills speak of "the user" (they/them), never the owner's name or he/his/him, because every member of the household runs the same plugins (2026-10-14) | `check_repo.py` |

Target: core descriptions ≤ 2,700 characters in total (2,400 until 2026-10-21, raised for a ninth core skill, `finance`).

### §5 · Project recipe: `bandit.yaml`

Skills define the gate; the project provides the recipe in `bandit.yaml` at the app repo root. A missing key refuses and names the key. Contract: `plugins/bandit-dev/skills/sprint/references/bandit-yaml.md` (shipped with the plugin; checker Y2); the app's proposal: `docs/bandit-yaml.md`.

### §7 · What the brief supersedes

<!-- denylist:off -->
| Old | Now |
|---|---|
| D4 two plugins | Three plugins (§2) |
| D15/D16 wbs-generator and project-planner standalone | Merged into `plan` (project and wbs modes) |
| D20 step 0 = no behaviour change | Step 0 = package, rebrand and lighten; procedures keep their logic |
| BB-147 scope out "renaming" | Renaming is in scope |
| BB-147 acceptance "diff shows only path, ownership, hook changes" | Every skill passes L1–L4 under its new name; no old name anywhere |
| Q1/Q2 owner, visibility | `l3ocho`, public |
| Q3 keep names | Resolved by §3 |
| Plan §1 `claude --add-dir` | `bbm-cc`; the app clone via `additionalDirectories` |
| Skills copied into `~/bb-import` | `.work/import/` inside the repo |
| Manual staging token | `bandit-staging` authenticates through `bb-staging-mcp-headers` |
| Plan §7 layout | Brief §6 (see `CLAUDE.md`) |
| S1 pipeline defined in three places | `docs/pipeline.md` here is canonical |
<!-- denylist:on -->

---

## 🛡️ Build-session guards (brief §9)

| # | Guard | Enforced by |
|---|---|---|
| G1 | The working tree is inert: nothing in `plugins/` or `.work/` loads unless passed with `--plugin-dir` | Claude Code's loading rules |
| G2 | Installed `bandit` and `bandit-dev` are off in this repo (`bandit-maker` stays on: it is the build tool) | `enabledPlugins` in `.claude/settings.json` |
| G3 | The old Claude.ai copies can't be used | A `Skill(anthropic-skills:…)` deny per old skill, plus `skillOverrides: "off"` |
| G4 | The new names can't be called either | A `Skill(bandit:…)` / `Skill(bandit-dev:…)` deny per skill |
| G5 | Nothing is deleted in production without the user's yes | The vault delete tool is denied (`settings.local.json`). The BanditBrain `delete_*` deny was removed on Leo's order on 2026-10-14 (host change log); board deletes (`delete_tasks`, `delete_board_items`) are confirmed per entry by the tasks skill's safety rule |
| G6 | New skills are covered automatically | `check_repo.py` fails if a skill in `bandit` or `bandit-dev` has no deny rule |
| G7 | Conventions are followed by reading, never invoking | Session rule |
| G8 | Tests run from `.work/test/`, where the shared skill denies don't apply and `settings.local.json` still does | Folder layout |
| G9 | Hub safety: deny `sudo`, `ssh`, `scp`, `tailscale`, `systemctl`, force pushes, `~/.ssh`, `~/.claude/settings.json` | `settings.local.json` |

---

## 🧪 Test data (BB-165, Leo, 2026-10-15)

| # | Decision |
|---|---|
| TD1 | A `bandit-dev` skill, `testdata`, reads the database, the app's rules and what was built, and writes made-up data straight into development, test and staging (never production): a lasting set (`fill`) and each card's test data (`make`, `create`, `clean`). Runs in the sprint and on demand. Made-up data only, never the user's own. The app builds nothing; no data files in the app repo; run records in its git-ignored `.testdata/`. Staging asks the user's yes on every run. `bandit.yaml` names one SQL command per database with env var names only; staging runs `psql` inside its container. The guard `dbguard.py` enforces it; `check_repo.py` rule TD1 tests the guard |

## 🔧 Assistant tools (BB-204, Leo, 2026-10-20)

| # | Decision |
|---|---|
| MT1 | The skills call only the app's current assistant tools: `get_context` for boards, tags, members, lanes and sprints; `list_tasks` (with `view` for a whole board); the array writes `create_tasks`, `update_tasks`, `reopen_tasks`, `delete_tasks`, `delete_board_items`; and `manage_*`, `link_tasks`, `set_visibility` for structure. `check_repo.py` rule MT1 fails on any of the 62 names the app removed, in any shipped file |

## 🔗 Done means every dependency (BB-205, Leo, 2026-10-20)

| # | Decision |
|---|---|
| DN1 | `docs/dependencies.md` is the one map of what changes together. A change is done only when every place its rows name is updated or checked; `scripts/done_check.py` lists them, done or open, and its output goes in the report |
| BR1 | No skill uses a name the app renamed for Boards (Projects became Boards, sprint 2026-w44-c): the tool `manage_projects`, the `project*` arguments and answer keys, the `PROJECT` refusal codes, the `project` kind and scope, `get_context → projects`. The app answers them through a bridge for one release only. `check_repo.py` rule BR1 fails on any of them in a shipped file (the CHANGELOG's release history excepted) |
| BP1 | No skill uses the board type the app replaced with the board profile (sprint 2026-w44-d): no `type` on `manage_boards`, no `deliverable` or `hybrid` value, no "board type" or "Deliverable board". `check_repo.py` rule BP1 fails on any of them in a shipped file (the CHANGELOG excepted), with a self-test; the Project Context `type:` and frontmatter `type:` are left alone |
| AT1 | `CURRENT_TOOLS` and `REMOVED_TOOLS` in `check_repo.py` equal the app's tools and removed list, read from the app clone (`BANDIT_APP_REPO`, `BANDIT_APP_REF`, default the app commit `639bdc44`, held there while the new Finance tool `finance_manage_settlements` waits for its own card (Leo, 2026-11-08); skipped where there is no clone |
| TC1 | The Execution column is To Do in every helper (BB-481, the app's rename BB-331, Leo 2026-11-11: "the assistants answer with the new name"). The stored value stays `assigned`; "Assigned to {name}" (the person on a card) and Finance are left alone. `check_repo.py` rule TC1 fails on the old column name in any plugin `.md` outside Finance, and on `execution.md` without its To Do row and the line mapping a person's "To Do" to `assigned` |
| ID1 | Card ids follow their board (BB-482, the app's BB-279, Leo 2026-11-11): a card in a board's Inbox has a temporary id `{prefix}-T{n}`, gets the board's next proper id when filed into a column and a new one on another board, and every id it ever had still finds it. One home: bandit:tasks `board.md` → Card IDs. Ids already written in papers, notes and commits stay as written. Every card id pattern in the sprint scripts reads the temporary form, and the sub-task gate ties an id `get_task` was asked for to the card the answer names. `check_repo.py` rule ID1; L4 catches a temporary id in a skill too |
| AC1 | README and install guide each have a "Works with Bandit Brain" row for the version in `marketplace.json`; a release without one is refused (`check_repo.py` rule AC1, self-tested on a table with and without the row) |
| AT2 | Copies that must match do: the project audit's tool list = `CURRENT_TOOLS`; the Project Context lines in `CLAUDE.md` and the templates = the block in `project-context.md` |
| CL1 | A plugin file changed since the last release tag needs a CHANGELOG entry with a line (`Unreleased`, or the version being released) |
| CS1 | Every skill command (`/plugin:skill word`) is on `docs/cheat-sheet.md` |

## 🗺️ Board scope by domain (debug D2, 2026-10-14)

| # | Decision | By |
|---|---|---|
| DS1 | **Home board first. Read and write across the domain. Nothing outside it.** The domain is the board's top-level folder named like `domain:`, with its subfolders (structure rule S1 already makes the names match); `board:` is the home board. One home: bandit:tasks `references/scope.md` | Leo, 2026-10-14 |
| DS2 | Writing to another board of the domain needs no extra question; the reply names the board and the card gets a `From {project}:` comment (Q1 = A) | Leo |
| DS3 | Untriaged cards are the domain workflow project's only; elsewhere a capture with no project lands parked on the home board (Q2 = A) | Leo |
| DS4 | `board: folder "…"` and `board: global` are retired; audit rule S4 also fails a home board outside its domain folder (Q3 = A) | Leo |
| DS5 | Outside the domain, only a card linked by a dependency to a domain card is shown: title, board and state, read-only | Leo |

## 📜 Original plan decisions D1–D24

The tables marked for the checker (`denylist:off`) are the only place the old skill names may appear: they record what was renamed.

<!-- denylist:off -->
| # | Decision | Status |
|---|---|---|
| D1 | Order BB-147 → BB-133 → BB-111 | Kept (BB-147 and BB-133 share sprint marketplace-v1) |
| D2 | One marketplace repo under the Bandit Brain brand | Kept |
| D3 | Single source of truth; uploaded and local copies removed after install | Kept |
| D4 | Two plugins | **Superseded** by brief §2 (three plugins) |
| D5 | A skill that depends on a marketplace skill lives in the marketplace | Kept |
| D6 | prompt-engineer and data-tools stay outside, untouched | Kept |
| D7 | Every plugin skill usable on Claude.ai; only sprint is Claude Code only | Kept (sprint now in `bandit-dev`) |
| D8 | Surface split: Claude.ai plans, Claude Code develops; Claude.ai's agent is the project instructions | Kept |
| D9 | Developed in Claude Code on Bandit Port | Kept |
| D10 | Claude Code tests write against the staging MCP; Claude.ai tests are read-only on production | Kept |
| D11 | Marketplace cards live in the Marketplace column of the BanditBrain board | Kept |
| D12 | A plugin release is its own version bump (`plugin.json` + CHANGELOG + tag) | Kept |
| D13 | `MyNotes/_skills` retired; sources here, process docs in `Projects/bandit-brain-marketplace/`, mirror in `Claude/code-bandit-brain-marketplace/` | Kept (homes updated by the brief) |
| D14 | Process documents in the vault, working files in the repo | Kept |
| D15 | wbs-generator standalone, two modes | **Superseded**: merged into `plan`; sprint mode kept as `plan wbs` sprint mode |
| D16 | project-planner and `tasks load` stay | **Superseded** in part: planner merged into `plan`; `tasks load` kept |
| D17 | text-rewriter and meeting-minutes in the plugin | Kept (as `rewrite`, `minutes`) |
| D18 | `mktpl-claude-datasaas` and projman retired, never cited; the nine stub skills pointing to them are removed from `~/.claude/skills/` (adr, data, design, doc, labels, project, projman, rfc, sprint) | Kept (checker denylist) |
| D19 | Rules are code, never prose alone | Kept |
| D20 | Step 0 = package with no behaviour change | **Superseded** by brief §7 (rebrand and lighten) |
| D21 | Every marketplace skill may be edited here; outside skills and other projects' notes untouched | Kept |
| D22 | One chat per sprint, one minor release per sprint; deploy only on Leo's word | **Superseded** in part by RS6: releasing is optional per sprint; deploy only on Leo's word is kept |
| D23 | Never change a login credential; staging token is never production's | Kept |
| D24 | Low density, brief, no re-asking, one list per gate with a recommendation, findings as fix rows | Kept |
<!-- denylist:on -->

---

## 🪝 Agent guards (sprint 2026-w43-d, Leo, 2026-10-24)

| # | Decision |
|---|---|
| HK1 | `bandit-dev` ships a credential guard: a PreToolUse hook on Bash that refuses (exit 2) any command part matching `bandit.yaml` `guard.credentials.block`, skips a part an `allow` pattern matches whole, does nothing without a `guard` section and fails closed when the section cannot be read. Script `skills/sprint/scripts/credential_guard.py`; `check_repo.py` rule CG1 tests it |
| HK2 | `bandit-dev` ships a stop gate: a second Stop hook that refuses to end a chat (exit 2) while a change under `bandit.yaml` `stop.paths` is uncommitted, and names `stop.close`. Once the chat has launched an agent it counts only the files the chat edited itself, so a background wave agent sharing the folder never holds the main chat. Off without a `stop` section; a section it cannot read lets the chat end with one line. Script `skills/sprint/scripts/stop_gate.py`; rule SG1 |
| HK3 | `bandit-dev` ships a dependency gate: a PostToolUse hook on any MCP server's `create_tasks` and `link_tasks` that, when a card is made to block another, puts a notice into the session's context naming the blocked card and the gate sub-task it owes. Always on, no `bandit.yaml` key. Silent on a refused write, a created card that lists its own gate and a sprint card; after `link_tasks` the notice says to skip a card that already has its gate, because the answer holds no checklist. Script `skills/sprint/scripts/dependency_gate.py`; rule DG1 |
| HK4 | `bandit-dev` ships a description gate (BB-464, Leo 2026-11-10: "why arent they being written with HTML"; "Yes. All of them. Release it"): a PreToolUse hook on any MCP server's `create_tasks` and `update_tasks` that refuses (exit 2) a card description the app would show as raw tags. The test is the app's own (`rich-text.ts` → `looksLikeHtml`: the whole value opens and closes with `<p>`, `<h1-6>`, `<ul>`, `<ol>` or `<blockquote>`), plus no escaped markup, no `<br>`, and no markdown outside a `<pre>` or `<code>`. A `<pre>` prompt block sits only between two blocks; the handover card's Source paragraph always follows it. Always on, no `bandit.yaml` key; silent on an empty description and other tools. On Claude.ai the read-back in `board.md` stays the guard. Script `skills/sprint/scripts/description_gate.py`; rule DF1 |

---

## 🏁 Real sprints (sprint 2026-w44-e, wave 7, Leo, 2026-10-30)

| # | Decision |
|---|---|
| RS1 | A sprint is a record in the app (`manage_sprints`, `get_sprints`): it holds the status and the cards in run order. `bandit-dev:sprint` creates it at plan step 1 and moves it: Ready to execute at step 12, Executing at the first wave, Debugging after the last, Closed at close. No sprint card, no sprint tag. Commands name the sprint. (Dates on cards: RS9) |
| RS2 | Planning steps and wave progress live in the sprint's ledger (Plan steps and Waves tables), enforced by `check_sprint.py` SP9 and SP10 (SP10 holds a done wave only to the waves it depends on, RS21), which key on the ledger's `Sprint record:` line so the archived old ledgers are not caught. `check_repo.py` rule SP9 tests both on fixtures |
| RS3 | The old way (a sprint card and a `sprint/{name}` tag) keeps running to its close from one reference, `old-way.md`; close brings such a sprint into the app (create, add cards while open, date, Ready, Executing, complete the cards, Closed), then retires its tag and completes its sprint card. The file goes once no old-way sprint is left |
| RS4 | The helpers read real sprints and, until the tags retire, the `sprint/*` tags too. With Sprints off they never report "no sprints": a sprint command stops; an exemption read (`today`, the hygiene audit) says so and uses the tags alone |
| RS5 | The dependency gate (HK3) also covers sprint ends: a blocked card owes its gate sub-task; a blocked sprint, which has no sub-tasks, owes a line in its ledger's Gates section |
| RS6 | Releasing is the user's option (BB-258): a sprint closes with no app release (`Release: deferred`), and one release covers every deferred sprint before it, its `Released:` line naming them all, with one production handover card. A sprint that changed the helpers still needs them released before it closes. The release gates are unchanged |
| RS7 | Planning and execution meet expectations (BB-287, Leo 2026-10-31): the helpers make no rules; each project's settings and docs hold them. Planning reads them first, raises conflicts before card gaps, asks in the user's terms, and lists every gap a convention answers in the plan for approval. Execution applies only the Spec, the plan, that list and the project's rules; anything else pauses that card and asks. Debug holds defects only; new ideas become cards. Checker rule NA1 keeps "decide and continue" out of the sprint helper |
| RS8 | Planning sticks to the Spec (BB-278, Leo 2026-10-30): "planning means plan the execution of the card by analysing dependencies and address them in the plan"; creative only when the user says "creative". Investigators report dependencies and risks, never questions; step 3 asks only the open questions the cards list; a decision row only when a Spec cannot be built as written; planning edits no Spec or brief unless the user asks (no reconcile at step 9); planning stops at step 10, and at step 3 only for a card's open question; the plan reviewer judges against the Spec and the dependencies only. Narrows RS7's conflict questions to that case |
| RS9 | A committed sprint shows on the Execution board (BB-282, Leo 2026-11-02, "Approved. Please set up the card date accordingly."). The board shows an open card only by its own due date, on or before this week's Sunday (app rule), and never reads the sprint's date. So: no date given, the sprint date is this week's Sunday; at commit a card with no due date gets the sprint date, a card with its own keeps it; step 12 checks each card's due date against this week's Sunday, never the columns alone; the final message names every card not on the board yet. Supersedes in part the 2026-10-28 "cards keep their own due dates" for undated cards. Checker rule EX1 keeps the check by date |
| RS10 | Design step for screen changes (BB-239, Leo 2026-10-28): pipeline stage 4, after the Spec is written and before `stage/spec` (corrected 2026-11-02: the Spec comes first, the design gates the stage), for cards that change a screen; the rest skip it. Route: Claude Design inside Claude Code (`/design-sync` once per project from the code, `/design` per card). A design is checked against the project's recorded traps before it is linked; the card carries `Design: {link}` beside `Brief:` and the user's approval as a comment; `/bandit:tasks spec` and `stage` refuse `stage/spec` without both. The old standalone design site's design system copy is not used and closes with the site on 2026-12-14. One home: bandit:tasks `dev-workflow.md` → Design step |
| RS11 | The production handover card is optional (BB-304, Leo 2026-11-03): a `handover` section with `board` and `staging` only is complete; `recipe.py opt handover.production.column` prints `none`; `plan` creates only the staging card and `release` runs the deploy, its watch and its version check through the recipe's own steps, with the results in the Milestone log. A deferred close and a covering release write their note in the Milestone log instead of on a card. The deploy word and the backup confirmation stay. Y1 tests it on `tests/fixture-app/bandit.no-production.yaml` |
| RS12 | Debug fixes run their own tests (BB-299, Leo 2026-11-02): a fix runs the test that fails against the old behaviour, the targeted tests of the files it touched, code review and the UI check on the screens it changed; no full check per fix. One full check (`verify`) runs right before each push of the trunk; red stops the push; several fixes may share a push. Checker rule DB1 |
| RS13 | Design card (BB-316, Leo 2026-11-03, decisions 2026-11-04): with an optional `design: column "{name}"` line in the Project Context (bandit:project owns it; core reads it on both surfaces, nothing in core reads `bandit.yaml`), `spec` on a screen-changing card creates `Design: {title}` in that column in one `create_tasks` with `dependencies.blocks`; the design session's handover, linked and approved on it, completes it; the build card gets `stage/spec` only then. The dependency gate names the design gate line; sprint planning flags an open design card. The sprint checker does not (it cannot see the board). Without the line, RS10 holds as before. The optional line is a minor change, as `finance:` was in 0.7.0. One home: bandit:tasks `dev-workflow.md` → Design card |
| RS14 | Wave report (BB-298, Leo 2026-11-02, trial on sprint cosmetic-1): one cumulative note per sprint, `{project}-sprint-{name}-wave-report.md`, rebuilt by the wave agent at every wave end: per card what was delivered and what came out different, the open calls (a workflow or settings lesson seen twice listed as a proposed change), the Flow trend, the lessons, and per wave a Flow and a Tokens block printed by `wave_flow.py` from the chat logs (steps deduped by message id, per card from `echo CARD-START {card}`, "not measured" for what the logs cannot show). A background code review is briefed with its commit and reads that commit's files. Planning reads earlier sprints' lessons first; close archives the report. Checker SP11 (a done wave needs its section, Flow and Tokens blocks) and WF1 (the script against a hand count). One home: `templates.md` → Wave report |
| RS15 | The wave compares a screen card with its design handover (BB-317, Leo 2026-11-02): for a card with a `Design:` line, the UI check's brief names the handover and makes one comparison in the same launch, after the screen works; the result (matches, or each difference with its handover line) goes in the card's report section, a difference left in is Different in the wave report. The plan's Verification table carries "matches the design handover". The UI-check agent itself lives in the project and is not changed. Checker rule DH1. One home: `templates.md` → Execution prompt |
| RS16 | Sprint map, temporary (BB-318, Leo 2026-11-03: "enforce this model to be updated. Just for now"): every sprint gets `{project}-sprint-{name}-map.html` in its folder, drawn at plan step 12 and redrawn after every wave by `sprint_map.py` from the board and the plan (areas = board columns, waves from the ledger, blocker and lands-after arrows routed by the script, the road from the recipe), in the model of the cosmetic-1 map kept as the app's design reference. Checker SP12 (the page's waves-done marker lists every done wave) and SM1 (no arrow through a card on cosmetic-1's data). SP11 and SP12 apply to sprints committed after 2026-11-04. **End:** when the app's own Sprints view shows the map, a card removes the script, the steps and SP12 |
| RS17 | Shared debug card (BB-319, Leo 2026-11-04): plan step 12 creates `Debug: sprint {name}`, assigned to the user, in the sprint and in no wave (a batch card is a card in a wave); a wave adds an `Expected: {screen} › {part} — {what} ({card})` line for an issue it could not solve, debug reads the card first and turns every point the user raises into a `Found:` line before working it, each line ends ticked with its outcome, and the wave report's Debug section counts them for the lessons. Close refuses an unticked line. Lines are short, plain and name the area of the app. Checker rule DK1. One home: `templates.md` → Debug card |
| RS18 | Faster sprint gates (BB-373, Leo 2026-11-06, measured on sprints cosmetic-2 and brain-drain): per card, code review and every fix first; then one browser check (when UI changed); then one full check, last, after the card's notes and status are committed; then merge. A browser check never starts while code review is still open. After the merge the trunk check counts as done when the project's full check prints "already passed". No gate is removed. The execution prompt carries the order word for word; the run fallback follows it. The dev mirror prunes `.claude/worktrees/` instead of walking it. Checker rules GO1 (gate order) and DM1 (mirror prunes, repo copy = reference). One home: `templates.md` → Gate order |
| RS19 | Helpers create tags (BB-396, Leo 2026-11-08: "I want you to take this rule of not creating tags out. You can create tags by following the credentials and roles that has their own permissions."; "yes. go ahead" to dropping the tasks helper's ask-first): the sprint helper's Never line names columns and boards only; bandit:tasks creates the tag it needs, within the signed-in member's role (a Board tag by anyone who may edit the board's cards, an App tag by the admin, `stage/` and `sprint/` reserved), and reports a refusal as the app's answer with no workaround. One home: bandit:tasks `board.md` → Creating a tag. `check_repo.py` rule TG1 fails if a ban or an ask-first returns |
| RS20 | Build steps are planned, not forgotten (BB-374, Leo 2026-11-06, after sprint adjustments-and-fin was committed with thirteen cards and no build-step sub-tasks): plan step 7 writes each card's build steps as ordered sub-tasks (rule owner: bandit:tasks `dev.md` and `board.md`), step 9 fails a card with none and records `{card id}: {n} steps` per card, and `check_sprint.py` SP13 refuses a sprint committed after 2026-11-08 with no count of at least 1 for a Batch card. Old-way sprints and earlier sprints are untouched. Fixtures StepsGood and StepsBad; `check_repo.py` rule SP13 |
| RS21 | A card waits for its own blockers, not for the wave before it (BB-397, Leo 2026-11-08, "After planning, a sprint knows which card comes next. Why isn't it moving? A different wave shouldn't stop or block it."): `execute.md` refuses a wave only while a card it depends on is not delivered (a `Blocked by` entry in the ledger's Batch table, or a pair on the plan's `Lands after:` line, plan step 5), a later card whose dependencies are delivered goes to Next the moment the last one reaches Stand By, the sprint goes to `debugging` when every wave is done, and the limit of five across Next and Doing counts this sprint's own cards (`list_tasks` with `sprintId`; the day view of `bandit:tasks` stays household-wide). `run.md` runs a wave whose dependencies are delivered even while an earlier wave holds a paused or blocked card, one wave at a time. One wave per chat stays. `check_sprint.py` SP10 follows the same dependencies (fixtures WavesFree and WavesDep, RecordBad updated); `check_repo.py` rule WO1 fails when the strict-order wording comes back |
| RS22 | Every sprint card ends with an approval line (BB-378, Leo 2026-11-08: a sub-task, "You can go with the subtask"; on this repo "I'm good with your plan"): planning step 7 adds a last sub-task `Tested and approved by you`, open, after the build steps and gate lines; step 9 checks it is there and last and does not count it as a build step. No wave, `run` or `debug` ticks it; `close` ticks it for each card the user approved in that chat (quoted in the ledger) and completes no card whose line is open. `templates.md` → Approval line is its one home. Sprints planned before it and old-way sprints close as before; the debug card has none. No tag, no app change. On this repo the release goes out first and the cards stay in Stand By with the line open until Leo has tested and said yes (the repo `CLAUDE.md` "Done means released" rule, edited to match); `check_repo.py` rule AP1 fails when any of this loses its home or a step ticks the line |
| RS23 | The debug card follows the work and collects Process lines (BB-381, Leo 2026-11-07 request, plan approved 2026-11-08 "I'm good with your plan"): `debug` moves the card to Doing when it starts, `release` moves it to Stand By before its first recipe step (on this repo before `release.py --write`), `close` completes it as before; a wave and `run` never move it. A third line shape, `Process: {step} — {what went wrong} ({card or sprint})`, is written at once by the wave, `run`, `debug` or `release` step that meets a build, check, push, gate, board move, release step or run that stalls or fails (one line per stalled step, not per retry), and is ticked once fixed or its lesson is recorded. The wave report's Debug table gains a Process column, Lessons read the lines, and the closing report names them. In Doing the card takes one place of the five (the sprint's own count, RS21). One home: `templates.md` → Debug card; `check_repo.py` rule DK1 fails when any of this loses its home or the old "stays until close" wording returns |
| RS24 | The design page link rides on the card (BB-377, Leo 2026-11-07 request, plan approved 2026-11-08 "I'm good with your plan"): the Claude.ai design page the user approves on is a full `https://` address that the design card carries as `Design page:` beside `Handover:` (where the handover files live) once the handover lands, and the build card's `Design:` line carries the same address; the agent that lands the handover writes both, and the design card is not completed without the page link. Without a design card the build card's Source carries `Design:` (the page) and `Handover:` (the files). The wave's UI check, `run` and `debug` find the handover files through the `Handover:` line (the design card's, reached through `blockedBy`, or the build card's own); sprint planning step 2 raises a fix row for a screen card whose `Design:` line is missing or not a full web address. Cards designed before this change are not touched. One home: bandit:tasks `dev-workflow.md` → Design step and Design card; `check_repo.py` rule DL1 fails when any of this loses its home (RS10 and RS13 still hold) |
| RS25 | A design session that changed the shared look ends by asking for design sync (BB-398, Leo 2026-11-08, split from BB-329 "The design sync didn't run at the end of a big design job.", plan approved "I'm good with your plan"): when a design changed colours, fonts, spacing or shared components, the session's last step asks the user to run `/design-sync` (a Claude Design command the helpers cannot run, so a reminder and a record, not automatic), and the design card (the build card without a design card) carries `Design sync run {date}` or `Design sync not needed: {reason}`; the design card is not completed without one of them. Follows RS10 (design-sync once per project, again on a theme change) and RS24. One home: bandit:tasks `dev-workflow.md` → Design step (closing step) and Design card; `check_repo.py` rule DS1 fails when any of this loses its home |
| RS26 | The wave report shows where the tokens went, with an estimated cost (BB-399, Leo 2026-11-08, split from "Token use per wave in the wave-end report, broken down by skills, plugins, hooks, agents and MCP, with costs and lists", plan approved "I'm good with your plan"): `wave_flow.py`'s Tokens block adds, after the existing lines, tokens by source in three groups (the marketplace's plugins, Bandit Brain's connectors named as Claude Code records them, everything else) with the top five items of each, an unlabelled line, helper agents by type, hooks by time and by characters added (no tokens exist for hooks) and an estimated cost. One step is counted once by its first label (connector, skill, plugin, helper agent), so the groups and the unlabelled line add up to the total. Verified on the real logs first: Claude Code records `attributionSkill`, `attributionPlugin`, `attributionMcpServer` and `attributionMcpTool` on the main chat's steps, helper agents' steps all carry `attributionAgent` (and a plugin or skill when a helper started under one), about half of the main chat's steps carry no label, hooks appear as `hook_success` and `hook_additional_context` attachments and `stop_hook_summary` rows with `durationMs`, and `cost-state` rows are a running session total that cannot be cut to a wave. So the cost is an estimate from a price list in the script (per model id, dated, taken from the Claude API reference) applied to each step's usage; a model with no price is named and left out. The label is read as recorded: on real logs a step's connector tool label can name a different tool from the one the step calls (a step labelled with one board tool called a file-read tool), so the tool items show what Claude Code labelled. Group names are arguments with defaults. Checker WF1 holds the hand count. One home: `templates.md` → Wave report |
| RS27 | The sprint's measures sit in one data file per project, built from the sprint records (BB-400, Leo 2026-11-08, split from "use the sprint documents and reports to build a real database of sprint information, with a clear way to add new measures later", plan approved "I'm good with your plan"): `sprint_data.py` reads a project's sprint folders, live and `_archive`, and prints one CSV row per wave (`sprint`, `where`, `wave`, then one column per measure) from the ledger (Waves, Batch effort, Plan deviations) and the wave report (the wave's Flow and Tokens lines and the Debug table). The measures list is in the script, one `Measure(name, source, reader)` line each, so a new measure is one line and one new column; a project's targets are not in the script but in a note in the project's planning folder (BB-403), so they change without a release. A measure a record does not hold is an empty cell, never an estimate: an older ledger gives the cards and no dates or numbers, a ledger with no wave table is skipped with a note, and a Plan deviations line that names no card leaves that cell empty rather than a count that might be short. A deviation line that names a card counts on that card's wave. Verified first on the real records: the ledger and wave report of this sprint (waves 1 to 6), the previous sprint's ledger and the oldest archived ledger, which has only a Waves and cards table. The helper writes the file to `Projects/{slug}/planning/{project}-sprint-data.csv` through WebDAV; the end of each wave and `close` rebuild it. No database server. Checker SD1 compares the script's output on a fixture domain with a hand-checked file and proves a guessed value, a dropped measure and each missing text fail. Undo: revert the BB-400 merges before the release. |
| RS28 | Sprint measures carry targets, shown in the wave report and at close (BB-403, Leo 2026-11-08, split from "Sprint KPIs": clear targets push the model to meet the standard, plan approved "I'm good with your plan"): a project's targets live in its targets note in the planning folder (one table: measure, target, direction at most or at least, status proposed or approved, approval date, the user's words), keyed by measure name, so they change without a release; only a measure whose line in the measures list names a direction can carry one. **A target is used only once approved**: the row says approved and carries the date and the user's words; a proposed row, or an approved one missing either, is never shown as met or missed. The first targets are proposed from the median of the project's data rows (`sprint_targets.py --propose`) and written as proposed; the user's yes turns a row to approved. The wave report gets a Targets block (measure, value, target, met or missed; "not measured" where the records hold no value) and `close` adds the sprint table to the handover report. A missed target is a Lesson; seen in two waves it is also an Open call proposing a change to CLAUDE.md or a helper, and nothing changes without the user's yes. Choices the plan left open: the script reads the same waves as `sprint_data.py` from the local copy, so the block can be written once the wave's Flow and Tokens are in; the sprint table counts waves met and missed, a sprint is met when no wave missed. Checker KP1 compares the script's four outputs on the fixture domain (including a proposed target and an approved one with no date or words, neither used) with hand-checked files and proves a used proposal, a missing set of words, a flipped direction and each missing text fail. Undo: revert the BB-403 merge before the release. |
| RS29 | The sub-task gate (BB-451, Leo 2026-11-09: "your solution to enforce the llm to create subtasks is not working at all"; "When creating the sprint we should have sub tasks"): a PreToolUse hook (`scripts/subtask_gate.py`) refuses the sprint's move to `ready_to_execute` while a card of that sprint has no build step, and a Technical plan written for a card with no build step. A build step is a sub-task other than a `Gate:` line or the approval line. It reads the chat's record (`get_task`, `get_sprints`, accepted adds, created cards), never a ledger line; an unread card is refused with its `get_task`. Debug, old-way sprint and completed cards are skipped. SP13 stays as the record. Checker rule SB1 |
| RS30 | A full check only on code (BB-452, Leo 2026-11-09: "FULL CHECK FOR COMMENT"): `scripts/code_changed.py` answers needed or not needed for the change since its base (a branch: where it left the trunk; the trunk: `origin/{trunk}`; the release: the last green full check). Docs outside `stop.paths`, and files whose changed lines are all comments or blank, are not code; anything it cannot read is code. The card gates, debug's push check and the release's verify step run the full check only on "needed". RS18's gates stay for code. Checker rule FC1 |
| RS31 | Nothing after the release (BB-450, Leo 2026-11-09: "Why doing reviews after deployment?"): Items to register carries a trigger per item, a wave or debug; SP14 refuses an item for the close, the release or after the sprint in a live plan; release precondition 8 refuses while the sprint owes the repository a change; close precondition 5 refuses while the trunk is ahead of the released deploy branch, and close never commits. Checker rule SP14 |
| RS32 | Closed sprints are archived, checked (BB-437, Leo 2026-11-09): SP15 fails a folder under `Projects/` whose ledger records the close (or named with `--closed`), and a closed or archived sprint's `{project}-sprint-{name}-wbs.md` outside `_archive/`; close step 3 archives the WBS with the folder; close step 4 runs `check_sprint.py --closed {name}` |
