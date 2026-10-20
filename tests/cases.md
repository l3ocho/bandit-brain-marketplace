# 🧪 Test cases: pipeline and inbox behaviour

> One case per behaviour built in sprint marketplace-v1 (BB-133), each written as input → expected refusal or result. Run in W7 from `.work/test/` against staging, and again after any change to these behaviours.

**How:** `auto` cases are code and run in `python3 scripts/check_repo.py` (rule named). `cli` cases run a
plugin in a headless session from `.work/test/`:
`claude -p --plugin-dir ../../plugins/bandit --plugin-dir ../../plugins/bandit-dev "<prompt>"`, against
the `bandit-staging` board only. `read` cases are checked by reading the shipped text.

## 🏃 Sprint (`bandit-dev:sprint`)

| # | Item | Kind | Input | Expected |
|---|---|---|---|---|
| C1 | bandit.yaml contract | auto (Y1) | `recipe.py require …` on `tests/fixture-app/bandit.yaml` | exit 0, every key the sprint skill reads is present |
| C2 | bandit.yaml contract | auto (Y1) | `recipe.py --file bandit.missing-key.yaml check-tail 0002` | exit 3, refusal names ``missing key `migrations.check` `` |
| C3 | P3 migration tail | auto (Y1) | `recipe.py check-tail 0003` on the fixture (tail is 0002) | exit 4, "migration tail is 0002, the plan names 0003: stop the wave" |
| C4 | P3 migration tail | auto (Y1) | `recipe.py check-tail 0002` | exit 0, "matches the plan" |
| C34 | Optional sections | auto (Y1) | `recipe.py --file bandit.no-migrations.yaml tail`, `check-tail none`, `opt staging.refresh` | exit 0; prints `none`; matches |
| C35 | Hook scope | auto (SP8) | `check_sprint.py --hook` on the Bad vault, transcript naming `Projects/home-reno/` vs another project | exit 2 with SP7 vs exit 0 with a `systemMessage` warning |
| C5 | P1 SP7 | auto (SP7) | `check_sprint.py --vault tests/fixture-vault --domain Bad` (committed, no review record) | exit 1, exactly one error, SP7 |
| C6 | P1 SP7 | auto (SP7) | `check_sprint.py … --domain Good` (committed, review record present) | exit 0, "passes SP1-SP7" |
| C7 | P1 review gate | cli | `run` on a staging sprint card whose step 11 sub-task is unticked | refused, names "Independent plan review" (step 11); no wave agent launched |
| C8 | P3 order gate | cli | `run` on a staging sprint card blocked by an open sprint card | refused, names the blocking sprint card; no wave agent launched |
| C9 | P3 order at plan | read | `references/plan.md` step 4 (Sprint order) | the new sprint card is blocked by the previous open sprint card (`link_tasks { blockerTaskId, blockedTaskId }`) |
| C10 | P2 release preconditions | cli | `release` on a staging sprint card with an untested card and no deploy word | refused; names the untested card and the missing deploy word; no recipe step runs |
| C11 | P2 close precondition | read | `references/close.md` precondition 4 | refuses without a `Released:` line unless "close without release" is quoted |
| C12 | P2 debug push | read | `references/debug.md` Rules | pushes follow `execute.md` → Pushing; no "never push" |
| C13 | P7 status line | read | `references/run.md` loop step 2 | a stale sprint card Status line fails the wave |
| C14 | P1 agent | read | `plugins/bandit-dev/agents/plan-reviewer.md` | read-only tools (Read, Glob, Grep); findings table with severity; blockers carry a recommendation |

## 🧪 Test data (`bandit-dev:testdata`, BB-165)

| # | Item | Kind | Input | Expected |
|---|---|---|---|---|
| C36 | Recipe section | auto (TD1) | `recipe.py opt testdata.databases` on the fixture; `opt testdata.logic` on `bandit.no-migrations.yaml`; `dbguard.py check` on `bandit.testdata-missing-key.yaml` | the three databases listed; `none`; exit 3 naming `testdata.logic` |
| C37 | Only test databases | auto (TD1) | `dbguard.py check production`; `check test` on `bandit.testdata-unsafe.yaml` | exit 6, "not a test database"; exit 6, "lists production" |
| C38 | No credentials | auto (TD1) | `check` on `bandit.testdata-secret.yaml`; `check development` with the env var unset; every case with the env var set | exit 6 without printing the command; exit 6 naming the variable only; the value never printed |
| C39 | Create writes only new rows | auto (TD1) | `create` with an UPDATE; with an INSERT lacking `RETURNING 'testdata'`; `read` with a psql meta-command | exit 6 each, nothing run |
| C40 | Staging asks every run | auto (TD1) | `create staging` without `--yes` | exit 6, "asks the user's yes" |
| C41 | Clean removes only the record | auto (TD1) | `create development` (two rows), `clean development card c1 --dry-run`, `clean`, `records` | deletes name exactly the two recorded ids, children first; "none left"; no open record |
| C42 | Real database | cli | `.work/test/testdata/`: a throwaway `postgres:18` container, the fixture schema, one existing row; `create` a made-up team, a rule-breaking insert, `clean` | rows created and recorded; the broken insert keeps nothing; after `clean` only the existing row is left (run 2026-10-15) |
| C43 | Map, fill, make on the app | cli | Bandit Brain with a `testdata` section: `map`, `fill development`, `make` on a sprint's cards, `create`, `clean` | the map lists tables, rules with `file:line` and each card's tables; a made-up user sees made-up data on every page; each acceptance line has its data; `clean` leaves no row |
| C44 | Sprint hook | read | `sprint/references/plan.md` → Test data; `execute.md` → Never | planning runs `make` per live check and names the data; the wave runs `create` before and `clean` after |

## 🗂️ Tasks (`bandit:tasks`)

| # | Item | Kind | Input | Expected |
|---|---|---|---|---|
| C15 | G1 leave the inbox | cli | `triage` on a staging project with one parked card | asks description, priority, effort, complexity, assignee, column, and the **due date last** |
| C16 | G1 exit style | cli | `triage` on a staging **workflow** project and on a **deliverable** project | workflow: daily sweep (every card leaves today); deliverable: the evaluation gate (yes / not yet / no) |
| C17 | P8 dev offer | read | `references/triage.md` → Dev projects | a parked dev item is offered `/bandit:clarify` (fuzzy) or `/bandit:tasks spec` (clear) |
| C18 | P8 Clarified Specification | read | `references/dev-workflow.md` → spec step 1 | a Clarified Specification maps into the Spec; `Source: clarify, {date}` |
| C19 | P8 audit row | read | `references/audit.md` check 2 | untriaged parked cards come back as one fix row per project |
| C20 | G4 structure | cli | `audit` on a staging project with a column named like a member | a fix row: make it a lane for that person (tag, lane, re-file, delete the empty column on confirm) |

## 🧩 Clarify, notes, project

| # | Item | Kind | Input | Expected |
|---|---|---|---|---|
| C21 | P9 hand-off | read | `clarify/references/deliver.md` destination table | dev-project work → `/bandit:tasks spec` with the spec as input |
| C22 | P10 review record | read | `notes/references/conventions.md` §1 Sprint folders | the review record row, `type: log`, dated filename |
| C23 | P11 + C templates | auto (L5) | `templates/instructions/*.md` | three templates, each ≤ one page, with Project Context, stage → command map and modes; shipped byte for byte in `project/assets/instructions/` |
| C24 | P11 dev agent stops at spec | read | `templates/instructions/dev.md` → Role | "It stops at spec"; stages 4–10 are Claude Code |
| C25 | P11 generation | read | `project/references/instructions.md` | instructions are generated from the template for the project's type, through one proposal |

## 🔧 Assistant tools and dependencies (BB-204, BB-205)

| # | Item | Kind | Input | Expected |
|---|---|---|---|---|
| C45 | No removed tool | auto (MT1) | any shipped file naming one of the app's 62 removed tools | gate fails naming file, line and tool |
| C46 | Tool lists = the app's | auto (AT1) | `BANDIT_APP_REF=origin/main python3 scripts/check_repo.py` (the old app) | AT1 fails listing the tools that differ; `origin/development` passes |
| C47 | Copies match | auto (AT2) | a template's names-only line, or the project audit's tool list, edited | AT2 fails naming the file |
| C48 | CHANGELOG line | auto (CL1) | a plugin change since the last tag with no `## Unreleased` line | CL1 fails; a dated entry for an untagged version passes |
| C49 | Commands on the cheat sheet | auto (CS1) | a skill command missing from `docs/cheat-sheet.md` | CS1 fails naming `/plugin:skill word` |
| C50 | Blocked card to Doing | cli | `/bandit:tasks doing` on a staging card whose blocker is open | moved to Doing; the reply says it can be worked, not completed, until the blocker is |
| C51 | Blockers complete first | cli | `/bandit-dev:sprint close` on a staging sprint whose cards are chained | one `update_tasks` call, blockers listed first, every entry applied |
| C52 | Sprint card checklist | read | `references/plan.md` step 3 | one `create_tasks` entry with the 12 steps as `subtasks` in order and `dependencies.blockedBy` |
| C53 | Done check | auto | `python3 scripts/done_check.py` | lists every map row a change since the last tag triggers, each place ✅ or ⚠️ |

## 🗺️ Domain scope (debug D2, 2026-10-14)

Run from `.work/test/` with a Project Context whose `domain:` names a staging board folder with a subfolder, and a second top-level folder outside it.

| # | Item | Kind | Input | Expected |
|---|---|---|---|---|
| C26 | D2 today filter | cli | `today` from a project in domain A, with cards in Doing on a board of domain B | only domain A's cards; the home board first; counts and the five-item cap after the filter |
| C27 | D2 linked card | cli | `today` where a domain A card is blocked by a domain B card | the B card shows as title, board and state, marked `outside the domain`; no other B card |
| C28 | D2 sibling write | cli | from board A1, "add a card to A2" (same domain) | created on A2; the reply names A2; a comment `From {project}: …` on the card |
| C29 | D2 outside write | cli | from board A1, "add a card to B1" (other domain) | refused, names the domain rule; nothing created |
| C30 | D2 Untriaged | cli | `triage` from a non-workflow project, then from the domain's workflow project | first: Stage 1 skipped, no Untriaged count; second: Untriaged shown and filed into domain A only |
| C31 | D2 capture | read | `tasks/references/capture.md` → Placement | no project named, from a non-workflow project → the home board's Inbox (parked) |
| C32 | D2 retired values | read | `tasks/references/scope.md` → `board:` values | `folder "…"` and `global` stop and point to `/bandit:project update` |
| C33 | D2 audit S4 | cli | `check_structure.py` on a snapshot whose project names a board in another top-level folder | S4 ❌ "board `…` is outside the `{domain}` folder", one fix row back to the domain board; the unchanged snapshot scores S4 ✅ (run 2026-10-14 on the 2026-09-29 Summitt snapshot, `.work/test/d2/`) |
