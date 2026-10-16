# Changelog

All three plugins (`bandit`, `bandit-dev`, `bandit-maker`) and the marketplace share one version, following [Semantic Versioning](https://semver.org): **major** when a command, mode or skill is removed or renamed or the Project Context format changes, **minor** for a new command, mode, skill or behaviour, **patch** for fixes and wording. Entries group changes as Added, Changed and Fixed, in the spirit of [Keep a Changelog](https://keepachangelog.com). `scripts/release.py` cuts a release: it dates the `Unreleased` entry, bumps every version and tags `vX.Y.Z` on `main`; each tag becomes a [GitHub release](https://github.com/l3ocho/bandit-brain-marketplace/releases).

## 0.5.1 · 2026-10-16

### Added
- **`/bandit-dev:testdata`:** fills a dev project's development, test and staging databases with made-up data, and creates and removes the data each card's tests need. `map` reads the schema, the live database, the app's rules and what was built; `fill {db}` puts a lasting made-up set across the whole app; `make` works out each acceptance line's data; `create` writes it; `clean` removes exactly what a run created. Every database call goes through a guard that refuses production, a command holding an address or password, and staging writes without the user's yes. New optional `testdata` section in `bandit.yaml`.
- **Sprint:** planning names each live check's data with `testdata make`; waves create it before the check and clean it after.
- **Checker rule TD1:** the guard's refusals and its clean-only-what-was-created, on fixtures.

### Fixed
- **Sprint board between waves:** the next wave's cards go to Next the moment the current wave's last card reaches Stand By, not after the wave-end checks; `run` sets the board before checking anything, whatever the wave reported. The stale rule that the board refuses Doing while a blocker sits in Stand By is gone: the board allows it.

## 0.5.0 · 2026-10-15

### Added
- **`/bandit:tasks scope {card}`:** settles what's still open on one dev card. Everything already answered (the chat, the brief, the plan note, card comments) goes into the Spec, the brief and the plan note with no question; only what nobody wrote down is asked, in one decision table. A limit the brief's Change log shows the user removed never comes back.

### Changed
- **Locked Specs take settled changes without a yes:** the lock override writes in what is already decided and reports old and new afterwards; only an undecided change becomes a question or a `Spec change needed:` comment. `spec reconcile` applies directly.

### Fixed
- **Cheat sheet:** the bandit:audit rows describe 0.4.0's run-everything behaviour.

## 0.4.0 · 2026-10-15

### Changed
- **Audit runs everything in one command:** `check` writes the stamp, scores the project and runs its fix rows; `audit` runs every fix row, archives the old report and writes the new one. No approval is asked; an either/or runs the recommended option and the report names the other. bandit:notes and bandit:project take a row from bandit:audit as the go, without a new proposal. The Claude Code handover runs as written, deletes included, after re-listing each folder.

## 0.3.2 · 2026-10-15

### Fixed
- **Talking to the user, across sprint, debug, spec and clarify:** the user's own words are the baseline and nothing they did not ask for is built; the repo, cards, briefs and ledger are read before any question, and only what they cannot answer is asked; decisions and debug adjustments go in the one plain decision table, never numbered rows or invented codes (Q1, A2); reports are three lines at most, no counts of what was created. In debug, the ledger and the board win over a memory note. Checker rule **T1** fails any return of numbered rows in these skills.

## 0.3.1 · 2026-10-14

### Changed
- **Sprint planning puts every decision in one table:** `Issue | Recommendation | Different from what you requested? | If yes, how?`, plain words, no row numbers. The user's original request is the baseline; nothing they did not ask for is added, and "applied defaults" are gone. "What is missing" is answered with that list only. Spec text is copied from the card, never retyped (`bandit-dev:sprint` plan.md, gotchas.md).

## 0.3.0 · 2026-10-14

### Added
- **Optional `migrations` and `staging` in `bandit.yaml`:** a repo without them leaves the section out; `recipe.py tail` prints `none`, the new `recipe.py opt` prints an optional key or `none`, and plan, execute and release skip those steps. Release steps may hold `{version}`. The marketplace repo has its own `bandit.yaml` (BB-162).

### Fixed
- **Sprint Stop hook scope:** the hook blocks only on errors in a project the session worked in; problems elsewhere in the domain show as a warning instead of stopping every sprint (checker rule **SP8**, BB-162).
- **Update instructions:** README and the install guide give the update path that works (desktop app, Chat tab, Manage marketplaces, Check for updates) and name Anthropic's open issues (#86818, #93825); the wrong "Re-sync" and `/plugin marketplace update` steps are gone.
- **CI on release tags:** the gate re-fetches the tags after checkout, so a tag-triggered run sees the annotated tag and V2 passes (actions/checkout turns the pushed tag into a lightweight one).

## 0.2.0 · 2026-10-14

### Added
- **README as the front door:** the Bandit Brain logo, badges, highlights, install and requirements, a pipeline diagram and an index of every doc. `docs/install.md` is now a standing guide (install, update, first project, migration, release).
- **Versioning as code:** `scripts/release.py` (dry run, `--write`, `--push`); the marketplace carries `metadata.version`; checker rule **V2** requires an annotated tag for every released version; a GitHub Action publishes each tag as a release with its CHANGELOG section.
- **CI:** a GitHub Action runs the repo gate on every push and pull request.
- **Community files:** `CONTRIBUTING.md`, `SECURITY.md`, issue and pull request templates.

### Changed
- **Every member, not one owner:** the skills speak of "the user" (they/them), never the owner's name; the assignee is the signed-in member. Checker rule **L8** keeps a person's name and he/his/him out of every plugin file. `workdir.py`'s message changed, so existing Claude Code twins score their copy as outdated until `/bandit:project` re-hands it.
- **Releasing a sprint's Marketplace cards** picks the version by Semantic Versioning instead of "next minor", through `scripts/release.py`.


## 0.1.1 · 2026-10-14 · debug of sprint marketplace-v1

- **Board scope by domain (D2):** home board first, read and write across the domain's board folder and its subfolders, nothing outside it except cards linked to the domain. Today, Week, Inbox and audit filter to the domain; Untriaged is the workflow project's; `board: folder` and `board: global` retired; audit S4 fails a home board outside its domain folder (`tasks/references/scope.md`, `docs/decisions.md` DS1–DS5).

## 0.1.0 · first version: rebrand, lighten, pipeline behaviour

Sprint marketplace-v1 (cards BB-147, BB-133), 2026-10-13. Pre-approval release candidate: tag on Leo's deploy word (`docs/install.md`).

- **Marketplace `bandit-brain`**, three plugins: `bandit` (tasks, notes, project, audit, clarify, rewrite, plan, minutes), `bandit-dev` (sprint, the `plan-reviewer` agent, the sprint Stop hook; depends on `bandit`), `bandit-maker` (skill).
- **Rebrand:** one skill per area, the verb as argument (`/bandit:tasks triage`); the project planner and WBS generator merge into `plan` (project and wbs modes); week planning folds into `tasks week`. No old name remains (checker D1).
- **Lighten:** every description ≤ 300 characters (core 7,693 → 2,280), every `SKILL.md` ≤ 150 lines as a router plus hard rules, no project details in skills.
- **Pipeline:** independent plan review (step 11, SP7), `release` command and the close precondition, sprint order gate, migration-tail stop, status line at every stage, the `bandit.yaml` contract (`docs/bandit-yaml.md`).
- **Inbox:** leaving the inbox answers every field with the due date last; the exit style follows the project type; clarify hands dev work to `spec`; the audit spots a column that should be a lane.
- **Project instructions** come from one-page templates per project type (`templates/instructions/`).
- **The old vault skills folder is retired** (archived under `BanditLabs/_archive/skills/`): the rulebooks ship with `audit` and `skill`, the cheat sheet is `docs/cheat-sheet.md`.
