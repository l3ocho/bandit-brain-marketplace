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

Target: core descriptions ≤ 2,400 characters in total.

### §5 · Project recipe: `bandit.yaml`

Skills define the gate; the project provides the recipe in `bandit.yaml` at the app repo root. A missing key refuses and names the key. Contract: `docs/bandit-yaml.md`.

### §7 · What the brief supersedes

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

---

## 🛡️ Build-session guards (brief §9)

| # | Guard | Enforced by |
|---|---|---|
| G1 | The working tree is inert: nothing in `plugins/` or `.work/` loads unless passed with `--plugin-dir` | Claude Code's loading rules |
| G2 | Installed `bandit` and `bandit-dev` are off in this repo (`bandit-maker` stays on: it is the build tool) | `enabledPlugins` in `.claude/settings.json` |
| G3 | The old Claude.ai copies can't be used | A `Skill(anthropic-skills:…)` deny per old skill, plus `skillOverrides: "off"` |
| G4 | The new names can't be called either | A `Skill(bandit:…)` / `Skill(bandit-dev:…)` deny per skill |
| G5 | Nothing is deleted in production | Deny rules on BanditBrain `delete_*` and the vault delete tool (`settings.local.json`) |
| G6 | New skills are covered automatically | `check_repo.py` fails if a skill in `bandit` or `bandit-dev` has no deny rule |
| G7 | Conventions are followed by reading, never invoking | Session rule |
| G8 | Tests run from `.work/test/`, where the shared skill denies don't apply and `settings.local.json` still does | Folder layout |
| G9 | Hub safety: deny `sudo`, `ssh`, `scp`, `tailscale`, `systemctl`, force pushes, `~/.ssh`, `~/.claude/settings.json` | `settings.local.json` |

---

## 📜 Original plan decisions D1–D24

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
| D18 | `mktpl-claude-datasaas` and projman retired, never cited | Kept (checker denylist) |
| D19 | Rules are code, never prose alone | Kept |
| D20 | Step 0 = package with no behaviour change | **Superseded** by brief §7 (rebrand and lighten) |
| D21 | Every marketplace skill may be edited here; outside skills and other projects' notes untouched | Kept |
| D22 | One chat per sprint, one minor release per sprint; deploy only on Leo's word | Kept |
| D23 | Never change a login credential; staging token is never production's | Kept |
| D24 | Low density, brief, no re-asking, one list per gate with a recommendation, findings as fix rows | Kept |
