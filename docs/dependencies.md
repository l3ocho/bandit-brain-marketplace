# 🔗 Dependencies

> What changes together. A change is **done** only when every place its row names is updated too,
> or checked and needs nothing. `python3 scripts/done_check.py` reads this table: it lists every
> file changed since the last release and, for each row it triggers, each place to update, done or
> open. The gate (`scripts/check_repo.py`) enforces the rows marked 🔒 on its own.

## 📋 The map

The first column is what changed (paths, `*` and `**` allowed). The second is what changes with it.
The third is the rule that enforces it, if one does.

| When this changes | Also update | Enforced by |
|---|---|---|
| `plugins/**` | `CHANGELOG.md` | 🔒 CL1 |
| `plugins/*/skills/*/SKILL.md` | `docs/cheat-sheet.md` · `README.md` | 🔒 CS1 (commands) |
| `plugins/*/skills/*/references/*.md` | `docs/cheat-sheet.md` | 🔒 CS1 (commands) |
| `plugins/*/.claude-plugin/plugin.json` | `.claude-plugin/marketplace.json` · `README.md` · `docs/install.md` | 🔒 M1 |
| `.claude-plugin/marketplace.json` | `README.md` · `docs/install.md` (the "Works with Bandit Brain" row for the new version) | 🔒 M1 · AC1 |
| `plugins/bandit/skills/tasks/references/*.md` | `plugins/bandit/skills/tasks/references/errors.md` · `plugins/bandit-dev/skills/sprint/references/*.md` | — |
| `plugins/bandit/skills/tasks/references/board.md` | `plugins/bandit-dev/skills/sprint/scripts/check_sprint.py` · `plugins/bandit-dev/skills/sprint/scripts/subtask_gate.py` · `plugins/bandit-dev/skills/sprint/scripts/sprint_data.py` (the card id patterns, Card IDs) | 🔒 ID1 |
| `plugins/bandit-dev/skills/sprint/references/*.md` | `docs/pipeline.md` · `docs/cheat-sheet.md` · `CLAUDE.md` (the "Done means released" rule, the approval line) · `docs/decisions.md` | 🔒 EX1 (plan step 12 checks the Execution board by date) · AP1 (the approval line) · DK1 (the debug card, its moves and Process lines) |
| `plugins/bandit/skills/notes/references/conventions.md` | `plugins/bandit/skills/notes/references/conventions-vault.md` (the same section numbers; how the vault writes each field) · `plugins/bandit/skills/notes/references/storage-app.md` (Places, Fields) · `plugins/bandit/skills/notes/references/model.md` (the inbox rule) | — |
| `plugins/bandit/skills/notes/references/conventions-vault.md` | `plugins/bandit/skills/notes/references/conventions.md` (the section map) · `plugins/bandit/skills/notes/references/storage-vault.md` · `tests/cases.md` | — |
| `plugins/bandit/skills/notes/references/other-skills.md` | `plugins/bandit/skills/minutes/references/notes.md` · `plugins/bandit/skills/plan/references/project.md` · `plugins/bandit/skills/plan/references/wbs.md` · `plugins/bandit/skills/clarify/references/deliver.md` (who writes what: the kinds, places and draft rules these writers follow) | — |
| `plugins/bandit/skills/notes/references/conclusions.md` | `plugins/bandit/skills/tasks/references/execution.md` (done and Bulk call it) · `plugins/bandit-dev/skills/sprint/references/close.md` (step 1, unattended) · `plugins/bandit/skills/notes/references/other-skills.md` (who writes what; the Note line in the lookup) · `tests/cases.md` | — |
| `plugins/bandit/skills/notes/references/write-safety.md` | `plugins/bandit/skills/notes/references/storage-app.md` · `plugins/bandit/skills/notes/references/storage-vault.md` | — |
| `plugins/bandit/skills/project/references/project-context.md` | `templates/instructions/*.md` · `plugins/bandit/skills/project/assets/instructions/*.md` · `CLAUDE.md` · `plugins/bandit/skills/finance/references/scope.md` | 🔒 AT2 |
| `templates/instructions/*.md` | `plugins/bandit/skills/project/assets/instructions/*.md` | 🔒 L5 |
| `plugins/bandit/skills/project/references/audit.md` | `docs/cheat-sheet.md` | 🔒 AT2 (tool list) |
| `plugins/bandit/skills/project/references/dev-mirror.md` | `.claude/hooks/mirror-check.py` (this repo's own copy, byte for byte; each dev project gets the new copy as a ready change) | 🔒 DM1 |
| `.claude/hooks/mirror-check.py` | `plugins/bandit/skills/project/references/dev-mirror.md` | 🔒 DM1 |
| `plugins/bandit/skills/audit/references/structure-rulebook.md` | `plugins/bandit/skills/audit/references/structure-rules.yaml` · `plugins/bandit/skills/audit/scripts/check_structure.py` | 🔒 A1 |
| `plugins/bandit-dev/skills/sprint/scripts/recipe.py` | `plugins/bandit-dev/skills/sprint/references/bandit-yaml.md` · `docs/bandit-yaml.md` · `bandit.yaml` · `tests/fixture-app/**` | 🔒 Y1 · Y2 |
| `plugins/bandit-dev/skills/sprint/references/bandit-yaml.md` | `plugins/bandit-dev/skills/sprint/scripts/recipe.py` · `docs/bandit-yaml.md` | 🔒 Y2 |
| `docs/bandit-yaml.md` | `plugins/bandit-dev/skills/sprint/references/bandit-yaml.md` · `bandit.yaml` | — |
| `plugins/bandit-dev/hooks/hooks.json` | `README.md` · `docs/decisions.md` | — |
| `plugins/bandit-dev/skills/sprint/scripts/dependency_gate.py` | `docs/decisions.md` · `README.md` | 🔒 DG1 |
| `plugins/bandit-dev/skills/sprint/scripts/subtask_gate.py` | `plugins/bandit-dev/hooks/hooks.json` · `plugins/bandit-dev/skills/sprint/references/plan.md` (steps 7 and 12) · `plugins/bandit/skills/tasks/references/dev-workflow.md` (plan-tech) · `README.md` · `docs/decisions.md` (RS29) | 🔒 SB1 |
| `plugins/bandit-dev/skills/sprint/scripts/description_gate.py` | `plugins/bandit-dev/hooks/hooks.json` · `plugins/bandit/skills/tasks/references/board.md` (Card descriptions) · `plugins/bandit-dev/skills/sprint/references/templates.md` (Handover cards) · `README.md` · `docs/decisions.md` (HK4) | 🔒 DF1 |
| `plugins/bandit-dev/skills/sprint/scripts/code_changed.py` | `plugins/bandit-dev/skills/sprint/references/templates.md` (Gate order) · `plugins/bandit-dev/skills/sprint/references/debug.md` · `plugins/bandit-dev/skills/sprint/references/release.md` · `plugins/bandit-dev/skills/sprint/references/run.md` · `plugins/bandit-dev/skills/sprint/references/execute.md` · `docs/decisions.md` (RS30) | 🔒 FC1 · GO1 |
| `plugins/bandit-dev/skills/sprint/scripts/wave_flow.py` | `tests/fixture-logs/**` · `plugins/bandit-dev/skills/sprint/references/templates.md` (the wave report's Flow and Tokens blocks, including tokens by source, hooks and the estimated cost with its price date) · `docs/decisions.md` (RS14, RS26) | 🔒 WF1 |
| `plugins/bandit-dev/skills/sprint/scripts/sprint_data.py` | `tests/fixture-vault/SprintData/**` · `tests/fixture-expected/sprint-data.csv` · `plugins/bandit-dev/skills/sprint/references/templates.md` (the Sprint data section and the Filenames rows) · `plugins/bandit-dev/skills/sprint/references/homes.md` · `plugins/bandit-dev/skills/sprint/references/execute.md` · `plugins/bandit-dev/skills/sprint/references/close.md` · `docs/decisions.md` (RS27) · `tests/fixture-map/estimate.csv` (the estimate) | 🔒 SD1 · ES1 |
| `plugins/bandit-dev/skills/sprint/scripts/sprint_targets.py` | `tests/fixture-vault/SprintData/**` (the targets note) · `tests/fixture-expected/sprint-targets-*.md` · `plugins/bandit-dev/skills/sprint/scripts/sprint_data.py` (its measures list and their directions) · `plugins/bandit-dev/skills/sprint/references/templates.md` (Sprint targets, the Targets block, Lessons) · `plugins/bandit-dev/skills/sprint/references/execute.md` · `plugins/bandit-dev/skills/sprint/references/close.md` · `docs/decisions.md` (RS28) | 🔒 KP1 |
| `plugins/bandit-dev/skills/sprint/scripts/sprint_map.py` | `tests/fixture-map/**` · `plugins/bandit-dev/skills/sprint/references/templates.md` (the Sprint map's data and the pre-sprint report) · `plugins/bandit-dev/skills/sprint/references/plan.md` (step 12, the final message) · `docs/decisions.md` (RS16) | 🔒 SM1 · SP12 · ES1 |
| `plugins/bandit-dev/skills/sprint/scripts/check_sprint.py` | `tests/fixture-vault/**` · `plugins/bandit-dev/skills/sprint/references/templates.md` (the ledger and wave report shapes) · `docs/decisions.md` | 🔒 SP7 · SP9 · SP11 · SP12 |
| `plugins/bandit-dev/skills/sprint/scripts/release_guard.py` | `plugins/bandit-dev/skills/sprint/references/release.md` · `plugins/bandit-dev/skills/sprint/references/bandit-yaml.md` · `docs/bandit-yaml.md` · `tests/fixture-app/bandit.notes-after-bump.yaml` · `docs/decisions.md` (RS33) | 🔒 RG1 · Y2 |
| `plugins/bandit-dev/skills/sprint/scripts/gate_wait.py` | `plugins/bandit-dev/hooks/hooks.json` · `plugins/bandit-dev/skills/sprint/references/execute.md` (The wave, step 4b) · `tests/fixture-gate/**` · `README.md` · `docs/decisions.md` (HK5) | 🔒 GW1 |
| `plugins/bandit-dev/skills/sprint/scripts/stop_gate.py` | `plugins/bandit-dev/skills/sprint/references/bandit-yaml.md` · `docs/bandit-yaml.md` · `docs/decisions.md` | 🔒 SG1 |
| `plugins/bandit-dev/skills/sprint/scripts/credential_guard.py` | `plugins/bandit-dev/skills/sprint/references/bandit-yaml.md` · `docs/bandit-yaml.md` · `docs/decisions.md` | 🔒 CG1 |
| `scripts/check_repo.py` | `docs/decisions.md` · `docs/dependencies.md` · `CHANGELOG.md` | — |
| `scripts/release.py` | `docs/install.md` · `CONTRIBUTING.md` | — |
| `.claude/settings.json` | `docs/decisions.md` | 🔒 G6 (skill denies) |
| `README.md` | `docs/install.md` (the requirements table) | — |
| `docs/install.md` | `README.md` (the requirements table) | — |

## 🌐 Changes from outside the repo

These start outside, so no file here triggers them. Each has its own check.

| When | Also update | Caught by |
|---|---|---|
| The app adds, removes or renames an assistant tool | Every skill naming it; `CURRENT_TOOLS`, `FINANCE_TOOLS` and `REMOVED_TOOLS` in `scripts/check_repo.py`; the tool list in `plugins/bandit/skills/project/references/audit.md`; `plugins/bandit/skills/tasks/references/errors.md` or `plugins/bandit/skills/finance/references/errors.md` (codes); `README.md` and `docs/install.md` (app version needed); a smoke run on staging; then each project runs `/bandit:project audit` | 🔒 AT1 (app clone on Bandit Port), MT1, BR1 (names renamed for Boards) |
| The app changes a tool's behaviour (a gate, an order, a refusal) | The skill reference that describes it (for the note tools, `plugins/bandit/skills/notes/references/storage-app.md`), checked live on staging; `errors.md` | Staging smoke run |
| The Project Context block changes | Every project's instructions and Claude Code `CLAUDE.md`: each project runs `/bandit:project audit` | The audit's Project Context check |

## ☑️ Checked, nothing to change

A place the done check lists as open, checked and found to need nothing for this release. One line
each: the path as the map writes it, then why. `scripts/release.py --write` empties this list.

- `README.md` — BB-597 changed only the pointers in the notes skill's `SKILL.md` (which reference to read); no command, requirement or plugin row changes. BB-600 adds the app's Notes path to the notes commands; no command is added, removed or renamed, and the README's command examples stay right. BB-591 changes where minutes, plans and specs are written, through the notes skill; no command, requirement or plugin row changes, and the Nextcloud row still holds for vault projects and for minutes saved beside the audio. BB-593 changes where a sprint's papers are written (the sprint skill's description and its references); no command, requirement or plugin row changes, and the Nextcloud row still holds for vault projects. BB-598 adds one row to the notes skill's Read table (`conclusions.md`) and a first step to `/bandit:tasks done`; no command, requirement or plugin row changes. The README's vault wording and the app version the notes skill needs change at the cutover (BB-596).
- `plugins/bandit/skills/tasks/references/errors.md` — BB-594 changed one wording in `scope.md` (`domain:` names the board folder whichever storage holds the notes); no error code, refusal or recovery changes. BB-592 changes how the card workflow finds a card's brief and plan (the linked notes); the note tools' refusals it can meet (`ONE_CARD_ONLY`, `PLAN_FOLLOWS_CARD`) are the notes skill's (`storage-app.md` → Refusals), and no board tool's code changes. BB-598's `done` step meets only codes already in the table (`ASSISTANT_CANNOT`, `SPEC_LOCKED`, `ORIGIN_TASK_READ_ONLY`, `ROLE_CANNOT`); the note tools' codes are the notes skill's (`conclusions.md` → Refusals).
- `plugins/bandit-dev/skills/sprint/references/*.md` — BB-594's `scope.md` wording changes nothing the sprint reads. BB-593 puts a sprint's papers on the app's Notes and rewords the planning step's brief lookup (`plan.md`, `gotchas.md`) to the linked note that BB-592 introduced. BB-598 changes `close.md` itself (step 1 and the report) for the tasks skill's new `done` step.
- `plugins/bandit/skills/finance/references/scope.md` — Finance reads only the `finance:` line; the new `notes: app` line does not change its scope.
- `.claude/hooks/mirror-check.py` — BB-594 added one pointer line to `dev-mirror.md` (settings storage, not notes storage); the script's mechanics are unchanged by design and DM1 is green.

## ✅ Before saying done

1. `python3 scripts/check_repo.py` is green.
2. `python3 scripts/done_check.py` shows nothing open: each place is updated, or listed under **Checked, nothing to change** with why. `scripts/release.py` refuses while anything is open.
3. Behaviour that depends on the app was run on staging.
4. The output of both goes to the user with the report.
