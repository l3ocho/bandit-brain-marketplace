# 📦 `bandit.yaml`: the project recipe

> The contract between the `bandit-dev` skills and an app repo. Skills hold the gates; the project holds the recipe in `bandit.yaml` at its repo root. A missing file or key refuses and names the key.

The reader is `plugins/bandit-dev/skills/sprint/scripts/recipe.py`; no skill parses the file by hand.

## 🗝️ Keys

| Key | Type | Used by | What it is |
|---|---|---|---|
| `verify` | command | `execute`, `run`, `debug` | The check a wave, a fix and a push must pass |
| `branches.trunk` | branch | `execute`, `run`, `debug` | Where waves merge and what a wave pushes |
| `branches.deploy` | branch | `release` | What a release fast-forwards; never touched outside `release` |
| `release` | list of commands | `release` | The ordered release steps, run one by one, stopping on the first failure |
| `migrations.dir` | path | `plan` | Where migrations live (step 5, cross-card analysis) |
| `migrations.check` | command | `execute`, `run`, `release` | Prints the current migration tail on its last line |
| `staging.refresh` | command | `release` | The step Leo runs to put a release on staging; shown, never run by a skill |
| `staging.up` · `staging.down` · `staging.where` | command · command · text | Leo, the runbook | Optional: documented for people, not read by a gate |

`development` and `main` in the sprint references mean `branches.trunk` and `branches.deploy`.

## 🚦 Refusals

| Call | Refuses with | Exit |
|---|---|---|
| Any, no file | `bandit.yaml: no recipe file at {path}` | 3 |
| `get` / `require` a missing or empty key | ``bandit.yaml: missing key `{key}` (used by …)`` | 3 |
| `check-tail {n}` when the tail differs | `bandit.yaml: migration tail is {x}, the plan names {n}: stop the wave and report it` | 4 |
| `tail` when `migrations.check` fails | ``bandit.yaml: `migrations.check` failed …`` | 5 |

## 📝 Example (the Bandit Brain app, checked 2026-10-13)

```yaml
verify: npm run verify
branches: { trunk: development, deploy: main }
release:
  - npm version minor
  - git push origin development --follow-tags
  - git push origin development:main
migrations:
  dir: drizzle
  check: python3 -c 'import json;e=json.load(open("drizzle/meta/_journal.json"))["entries"][-1];print(e["tag"][:4])'
staging:
  up: bb-staging up
  refresh: bb-staging up --refresh
  down: bb-staging down
  where: bandit-port
```

Sources: the app's `package.json` (verify), `docs/branching.md` rules 6, 8 and 9 (branches, migrations, release), `docs/staging-runbook.md` (staging). The app repo writes its own `bandit.yaml` (card "App repo: pipeline recipe and docs"); this file only defines the contract. Test fixture: `tests/fixture-app/bandit.yaml`, and `bandit.missing-key.yaml` for the refusal.
