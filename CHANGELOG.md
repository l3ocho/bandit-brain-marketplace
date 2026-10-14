# Changelog

All three plugins (`bandit`, `bandit-dev`, `bandit-maker`) share one version. A release bumps every `plugin.json`, adds an entry here and tags `v{version}` on `main`.

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
