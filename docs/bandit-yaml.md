# 📦 `bandit.yaml`: the project recipe

> The contract between the `bandit-dev` skills and an app repo. Skills hold the gates; the project holds the recipe in `bandit.yaml` at its repo root. A missing file or key refuses and names the key.

The reader is `plugins/bandit-dev/skills/sprint/scripts/recipe.py`; no skill parses the file by hand.

## 🗝️ Keys

| Key | Type | Used by | What it is |
|---|---|---|---|
| `verify` | command | `execute`, `run`, `debug` | The check a wave, a fix and a push must pass |
| `branches.trunk` | branch | `execute`, `run`, `debug` | Where waves merge and what a wave pushes |
| `branches.deploy` | branch | `release` | What a release fast-forwards; never touched outside `release` |
| `release` | list of commands | `release` | The ordered release steps, run one by one, stopping on the first failure. `{version}` in a step is replaced by the version picked at release |
| `migrations.dir` | path | `plan` | Where migrations live (step 5, cross-card analysis) |
| `migrations.check` | command | `execute`, `run`, `release` | Prints the current migration tail on its last line |
| `staging.refresh` | command | `release` | The step the user runs to put a release on staging; shown, never run by a skill |
| `staging.up` · `staging.down` · `staging.where` | command · command · text | People, the runbook | Documented for people, not read by a gate |
| `testdata.schema` | list of paths or globs | `testdata` | Where the tables are defined |
| `testdata.logic` | list of paths or globs | `testdata` | Where the app enforces its rules in code |
| `handover.board` · `handover.column` | project name · column name | `plan`, `release` | Where the deployment handover card goes: `plan` creates it at the sprint commit, `release` fills its prompt (`references/templates.md` → Handover card). Names, resolved live |
| `handover.runbook` | `path#section` | `release` | The app repo's deploy steps the handover prompt copies, read on `branches.deploy` |
| `testdata.databases` | map of name → command | `testdata` | One command per test database (`development`, `test`, `staging`, no other name) that runs SQL read from stdin with `psql`. It names env vars, never an address or password; a database with no open port runs `psql` inside its container with the container's own login |

**Required:** `verify`, `branches`, `release`. **Optional sections:** `migrations`, `staging`, `testdata` and `handover`. A repo without them leaves the whole section out: `recipe.py tail` prints `none` and the gates skip the tail; `recipe.py opt staging.refresh` prints `none` and `release` gives no staging step; without `handover` the plan asks once for it and `release` makes no handover card. A section that is present must be complete (`migrations` without `check` still refuses). Without `testdata`, the skill of that name says the section is missing and stops; the sprint's live checks then build their own data as before.

The `testdata` section is read by the skill's guard, `plugins/bandit-dev/skills/testdata/scripts/dbguard.py`, through `recipe.py`. Its records of what it created live in `.testdata/` at the app repo root, which the app's `.gitignore` must list; the guard refuses every write until it does.

`development` and `main` in the sprint references mean `branches.trunk` and `branches.deploy`.

## 🚦 Refusals

| Call | Refuses with | Exit |
|---|---|---|
| Any, no file | `bandit.yaml: no recipe file at {path}` | 3 |
| `get` / `require` a missing or empty key | ``bandit.yaml: missing key `{key}` (used by …)`` | 3 |
| `check-tail {n}` when the tail differs | `bandit.yaml: migration tail is {x}, the plan names {n}: stop the wave and report it` | 4 |
| `opt` on a key outside the optional sections | ``bandit.yaml: `{key}` is not optional: use get`` | 2 |
| `tail` when `migrations.check` fails | ``bandit.yaml: `migrations.check` failed …`` | 5 |
| `dbguard.py` on a name outside `development`, `test`, `staging`, or a section listing one | ``testdata: `{name}` is not a test database …`` | 6 |
| `dbguard.py` on a command holding an address or password | ``testdata: the `{db}` command holds an address or password …`` (the command is never printed) | 6 |
| `dbguard.py` when an env var the command names is unset | ``testdata: env var `{VAR}` is not set …`` (the name only) | 6 |
| `dbguard.py create` or `clean` on staging without `--yes` | ``testdata: `staging` asks the user's yes on every run …`` | 6 |

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
testdata:
  schema: [src/domains/*/schema.ts]
  logic: [src/domains/*/server/]
  databases:
    development: 'psql "$DATABASE_URL"'
    test: "sh -c 'set -a; . ./.env.test; psql \"$DATABASE_URL\"'"
    staging: "docker exec -i bandit_staging_db sh -c 'psql -U \"$POSTGRES_USER\" -d \"$POSTGRES_DB\"'"
handover:
  board: Bandit CTO
  column: Bandit Labs VPS
  runbook: docs/deployment.md#Deploy now
```

The `handover` lines are a proposal for the app (2026-10-24, from the BC-24 deployment card: board and column as used, deploy steps in the app's `docs/deployment.md` section "Deploy now").

The `testdata` lines are a proposal for the app (checked 2026-10-15: tables in `src/domains/*/schema.ts`, rules in the server actions, staging's database publishes no port, the test suite reads `DATABASE_URL` from the git-ignored `.env.test`). Development reads `DATABASE_URL` from the shell the skill runs in. The app commits its own `bandit.yaml` and adds `.testdata/` to its `.gitignore`.

Sources: the app's `package.json` (verify), `docs/branching.md` rules 6, 8 and 9 (branches, migrations, release), `docs/staging-runbook.md` (staging). The app repo writes its own `bandit.yaml` (card "App repo: pipeline recipe and docs"); this file only defines the contract. Test fixture: `tests/fixture-app/bandit.yaml`, `bandit.missing-key.yaml` for the refusal and `bandit.no-migrations.yaml` for a repo without migrations, staging or testdata, `bandit.testdata-missing-key.yaml`, `bandit.testdata-unsafe.yaml` and `bandit.testdata-secret.yaml` for the guard's refusals; `schema.sql`, `src/rules.py` and `fake_db.py` are a small app and a stand-in database for trying the testdata skill without a server. The marketplace repo's own recipe is `bandit.yaml` at its root.
