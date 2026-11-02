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

Stages 1–3 are core; stages 4–10 are `bandit-dev`. Dependencies point one way: `bandit-dev` may call core, never the reverse. Each plugin carries its own references (the structure rulebook lives with `audit`).

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
| AT1 | `CURRENT_TOOLS` and `REMOVED_TOOLS` in `check_repo.py` equal the app's tools and removed list, read from the app clone (`BANDIT_APP_REPO`, `BANDIT_APP_REF`, default `origin/development`); skipped where there is no clone |
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

---

## 🏁 Real sprints (sprint 2026-w44-e, wave 7, Leo, 2026-10-30)

| # | Decision |
|---|---|
| RS1 | A sprint is a record in the app (`manage_sprints`, `get_sprints`): it holds the status and the cards in run order. `bandit-dev:sprint` creates it at plan step 1 and moves it: Ready to execute at step 12, Executing at the first wave, Debugging after the last, Closed at close. No sprint card, no sprint tag. Commands name the sprint. (Dates on cards: RS9) |
| RS2 | Planning steps and wave progress live in the sprint's ledger (Plan steps and Waves tables), enforced by `check_sprint.py` SP9 and SP10, which key on the ledger's `Sprint record:` line so the archived old ledgers are not caught. `check_repo.py` rule SP9 tests both on fixtures |
| RS3 | The old way (a sprint card and a `sprint/{name}` tag) keeps running to its close from one reference, `old-way.md`; close brings such a sprint into the app (create, add cards while open, date, Ready, Executing, complete the cards, Closed), then retires its tag and completes its sprint card. The file goes once no old-way sprint is left |
| RS4 | The helpers read real sprints and, until the tags retire, the `sprint/*` tags too. With Sprints off they never report "no sprints": a sprint command stops; an exemption read (`today`, the hygiene audit) says so and uses the tags alone |
| RS5 | The dependency gate (HK3) also covers sprint ends: a blocked card owes its gate sub-task; a blocked sprint, which has no sub-tasks, owes a line in its ledger's Gates section |
| RS6 | Releasing is the user's option (BB-258): a sprint closes with no app release (`Release: deferred`), and one release covers every deferred sprint before it, its `Released:` line naming them all, with one production handover card. A sprint that changed the helpers still needs them released before it closes. The release gates are unchanged |
| RS7 | Planning and execution meet expectations (BB-287, Leo 2026-10-31): the helpers make no rules; each project's settings and docs hold them. Planning reads them first, raises conflicts before card gaps, asks in the user's terms, and lists every gap a convention answers in the plan for approval. Execution applies only the Spec, the plan, that list and the project's rules; anything else pauses that card and asks. Debug holds defects only; new ideas become cards. Checker rule NA1 keeps "decide and continue" out of the sprint helper |
| RS8 | Planning sticks to the Spec (BB-278, Leo 2026-10-30): "planning means plan the execution of the card by analysing dependencies and address them in the plan"; creative only when the user says "creative". Investigators report dependencies and risks, never questions; step 3 asks only the open questions the cards list; a decision row only when a Spec cannot be built as written; planning edits no Spec or brief unless the user asks (no reconcile at step 9); planning stops at step 10, and at step 3 only for a card's open question; the plan reviewer judges against the Spec and the dependencies only. Narrows RS7's conflict questions to that case |
| RS9 | A committed sprint shows on the Execution board (BB-282, Leo 2026-11-02, "Approved. Please set up the card date accordingly."). The board shows an open card only by its own due date, on or before this week's Sunday (app rule), and never reads the sprint's date. So: no date given, the sprint date is this week's Sunday; at commit a card with no due date gets the sprint date, a card with its own keeps it; step 12 checks each card's due date against this week's Sunday, never the columns alone; the final message names every card not on the board yet. Supersedes in part the 2026-10-28 "cards keep their own due dates" for undated cards. Checker rule EX1 keeps the check by date |
