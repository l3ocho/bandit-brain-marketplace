# Changelog

All three plugins (`bandit`, `bandit-dev`, `bandit-maker`) and the marketplace share one version, following [Semantic Versioning](https://semver.org): **major** when a command, mode or skill is removed or renamed or the Project Context format changes, **minor** for a new command, mode, skill or behaviour, **patch** for fixes and wording. Entries group changes as Added, Changed and Fixed, in the spirit of [Keep a Changelog](https://keepachangelog.com). `scripts/release.py` cuts a release: it dates the `Unreleased` entry, bumps every version and tags `vX.Y.Z` on `main`; each tag becomes a [GitHub release](https://github.com/l3ocho/bandit-brain-marketplace/releases).

## Unreleased

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
