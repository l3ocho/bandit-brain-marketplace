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
| `.claude-plugin/marketplace.json` | `README.md` · `docs/install.md` | 🔒 M1 |
| `plugins/bandit/skills/tasks/references/*.md` | `plugins/bandit/skills/tasks/references/errors.md` · `plugins/bandit-dev/skills/sprint/references/*.md` | — |
| `plugins/bandit-dev/skills/sprint/references/*.md` | `docs/pipeline.md` · `docs/cheat-sheet.md` | — |
| `plugins/bandit/skills/project/references/project-context.md` | `templates/instructions/*.md` · `plugins/bandit/skills/project/assets/instructions/*.md` · `CLAUDE.md` · `plugins/bandit/skills/finance/references/scope.md` | 🔒 AT2 |
| `templates/instructions/*.md` | `plugins/bandit/skills/project/assets/instructions/*.md` | 🔒 L5 |
| `plugins/bandit/skills/project/references/audit.md` | `docs/cheat-sheet.md` | 🔒 AT2 (tool list) |
| `plugins/bandit/skills/audit/references/structure-rulebook.md` | `plugins/bandit/skills/audit/references/structure-rules.yaml` · `plugins/bandit/skills/audit/scripts/check_structure.py` | 🔒 A1 |
| `plugins/bandit-dev/skills/sprint/scripts/recipe.py` | `plugins/bandit-dev/skills/sprint/references/bandit-yaml.md` · `docs/bandit-yaml.md` · `bandit.yaml` · `tests/fixture-app/**` | 🔒 Y1 · Y2 |
| `plugins/bandit-dev/skills/sprint/references/bandit-yaml.md` | `plugins/bandit-dev/skills/sprint/scripts/recipe.py` · `docs/bandit-yaml.md` | 🔒 Y2 |
| `docs/bandit-yaml.md` | `plugins/bandit-dev/skills/sprint/references/bandit-yaml.md` · `bandit.yaml` | — |
| `plugins/bandit-dev/hooks/hooks.json` | `README.md` · `docs/decisions.md` | — |
| `plugins/bandit-dev/skills/sprint/scripts/dependency_gate.py` | `docs/decisions.md` · `README.md` | 🔒 DG1 |
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
| The app changes a tool's behaviour (a gate, an order, a refusal) | The skill reference that describes it, checked live on staging; `errors.md` | Staging smoke run |
| The Project Context block changes | Every project's instructions and Claude Code `CLAUDE.md`: each project runs `/bandit:project audit` | The audit's Project Context check |

## ☑️ Checked, nothing to change

A place the done check lists as open, checked and found to need nothing for this release. One line
each: the path as the map writes it, then why. `scripts/release.py --write` empties this list.

- none yet

## ✅ Before saying done

1. `python3 scripts/check_repo.py` is green.
2. `python3 scripts/done_check.py` shows nothing open: each place is updated, or listed under **Checked, nothing to change** with why. `scripts/release.py` refuses while anything is open.
3. Behaviour that depends on the app was run on staging.
4. The output of both goes to the user with the report.
