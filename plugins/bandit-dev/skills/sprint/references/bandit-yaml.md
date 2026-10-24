# 📦 `bandit.yaml`: the project recipe

Part of `bandit-dev:sprint`. The contract between the `bandit-dev` skills and a project repo. The skills hold the gates; the project holds the recipe in `bandit.yaml` at its repo root. A missing file or key refuses and names the key. The reader is `scripts/recipe.py`; no skill parses the file by hand. Check a project's file against this list.

Contents: Keys · Sections · Refusals

## 🗝️ Keys

One row per key the skills and scripts read (`recipe.py` `KEYS`; the checker holds the two equal).

| Key | Type | Used by | What it is |
|---|---|---|---|
| `verify` | command | `execute`, `run`, `debug` | The check a wave, a fix and a push must pass |
| `branches.trunk` | branch | `execute`, `run`, `debug`, `testdata` | Where waves merge and what a wave pushes |
| `branches.deploy` | branch | `release` | What a release fast-forwards; never touched outside `release` |
| `release` | list of commands | `release` | The ordered release steps, run one by one, stopping on the first failure. `{version}` in a step is replaced by the version picked at release |
| `migrations.dir` | path | `plan` | Where migrations live (step 5, cross-card analysis) |
| `migrations.check` | command | `execute`, `run`, `release` | Prints the current migration tail on its last line |
| `staging.refresh` | command | `release` | The step the user runs to put a release on staging; shown, never run by a skill |
| `testdata.schema` | list of paths or globs | `testdata` | Where the tables are defined |
| `testdata.logic` | list of paths or globs | `testdata` | Where the project enforces its rules in code |
| `testdata.databases` | map of name → command | `testdata` | One command per test database (`development`, `test`, `staging`, no other name) that runs SQL read from stdin with `psql`. It names env vars, never an address or password; a database with no open port runs `psql` inside its container with the container's own login |
| `handover.board` | project name | `plan`, `execute`, `release` | The board both deployment handover cards go on (`templates.md` → Handover cards); `plan` creates them at the sprint commit. A name, resolved live |
| `handover.staging.column` | column name | `plan`, `execute` | The staging handover card's column |
| `handover.staging.runbook` | `path#section` | `execute` | The project's staging deploy steps the staging card's prompt copies; filled by the Final push |
| `handover.production.column` | column name | `plan`, `release` | The production handover card's column |
| `handover.production.runbook` | `path#section` | `release` | The project's deploy steps the production card's prompt copies, read on `branches.deploy`; filled by `release` |
| `guard.credentials.block` | list of regexes | credential guard hook | Commands no agent runs: credential scripts and raw writes to the login column. A hit is refused before it runs (exit 2) |
| `guard.credentials.allow` | list of regexes (optional) | credential guard hook | The project's dev-only login commands, each matched against a whole part of the command; they still run |

For people only, read by no gate: `staging.up`, `staging.down`, `staging.where`.

## 🧩 Sections

**Required:** `verify`, `branches`, `release`. **Optional sections:** `migrations`, `staging`, `testdata`, `handover` and `guard`. A repo without one leaves the whole section out: `recipe.py tail` prints `none` and the gates skip the tail; `recipe.py opt staging.refresh` prints `none` and `release` gives no staging step; without `handover` the plan asks once for it and no handover card is made. A section that is present must be complete (`migrations` without `check` still refuses). Without `testdata`, the skill of that name says the section is missing and stops; the sprint's live checks then build their own data. Without `guard`, the credential guard hook does nothing; inside it only `allow` may be left out.

The `testdata` section is read by the testdata skill's guard, `dbguard.py`, through `recipe.py`. Its records of what it created live in `.testdata/` at the repo root, which the project's `.gitignore` must list; the guard refuses every write until it does.

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
| Credential guard, a command part hits `guard.credentials.block` | ``Blocked: this command sets a real login credential (it matches `{pattern}` …)`` | 2 |
| Credential guard, a `guard` section it cannot read (broken YAML, bad regex, no `block`, no PyYAML) | `Blocked: the credential guard cannot read bandit.yaml (…)`: every command, until fixed | 2 |
