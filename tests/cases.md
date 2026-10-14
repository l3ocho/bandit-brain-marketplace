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
| C5 | P1 SP7 | auto (SP7) | `check_sprint.py --vault tests/fixture-vault --domain Bad` (committed, no review record) | exit 1, exactly one error, SP7 |
| C6 | P1 SP7 | auto (SP7) | `check_sprint.py … --domain Good` (committed, review record present) | exit 0, "passes SP1-SP7" |
| C7 | P1 review gate | cli | `run` on a staging sprint card whose step 11 sub-task is unticked | refused, names "Independent plan review" (step 11); no wave agent launched |
| C8 | P3 order gate | cli | `run` on a staging sprint card blocked by an open sprint card | refused, names the blocking sprint card; no wave agent launched |
| C9 | P3 order at plan | read | `references/plan.md` step 1 | the new sprint card is blocked by the previous open sprint card (`add_dependency`) |
| C10 | P2 release preconditions | cli | `release` on a staging sprint card with an untested card and no deploy word | refused; names the untested card and the missing deploy word; no recipe step runs |
| C11 | P2 close precondition | read | `references/close.md` precondition 4 | refuses without a `Released:` line unless "close without release" is quoted |
| C12 | P2 debug push | read | `references/debug.md` Rules | pushes follow `execute.md` → Pushing; no "never push" |
| C13 | P7 status line | read | `references/run.md` loop step 2 | a stale sprint card Status line fails the wave |
| C14 | P1 agent | read | `plugins/bandit-dev/agents/plan-reviewer.md` | read-only tools (Read, Glob, Grep); findings table with severity; blockers carry a recommendation |

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
