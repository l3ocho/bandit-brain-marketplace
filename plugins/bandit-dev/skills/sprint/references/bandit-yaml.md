# 📦 `bandit.yaml`: the project recipe

Part of `bandit-dev:sprint`. The contract between the `bandit-dev` skills and a project repo. The skills hold the gates; the project holds the recipe in `bandit.yaml` at its repo root. A missing file or key refuses and names the key. The reader is `scripts/recipe.py`; no skill parses the file by hand. Check a project's file against this list.

Contents: Keys · Sections · Refusals

## 🗝️ Keys

One row per key the skills and scripts read (`recipe.py` `KEYS`; the checker holds the two equal).

| Key | Type | Used by | What it is |
|---|---|---|---|
| `verify` | command | `execute`, `run`, `debug` | The check a wave and a push must pass (a debug fix runs its targeted tests instead, `debug.md`) |
| `branches.trunk` | branch | `execute`, `run`, `debug`, `testdata` | Where waves merge and what a wave pushes |
| `branches.deploy` | branch | `release` | What a release fast-forwards; never touched outside `release` |
| `release` | list of commands | `release` | The ordered release steps, run one by one, stopping on the first failure. `{version}` in a step is replaced by the version picked at release |
| `migrations.dir` | path | `plan` | Where migrations live (step 5, cross-card analysis) |
| `migrations.check` | command | `execute`, `run`, `release` | Prints the current migration tail on its last line |
| `staging.refresh` | command | `execute`, `debug`, `release` | The project's command that puts the branch staging follows on staging (`staging.branch`, else the trunk). `release` only shows it; after a push of the trunk it runs only when staging follows the trunk and `staging.after_push` is `run` (`execute.md` → Pushing `development`, Staging) |
| `staging.commit` | command (optional part) | `execute`, `debug` | Prints the commit staging runs, on its last line; after a push it is compared with the pushed commit. Without it nothing is called ready to test on staging |
| `staging.after_push` | `run` or `show` (optional part) | `execute`, `debug` | Whether a push of the trunk runs `staging.refresh` (`run`) or shows it to the user (`show`). Absent, or any other value, is `show`. The project decides: a freeze or a shared staging is the project's reason to say `show` |
| `staging.branch` | branch (optional part) | `execute`, `debug`, `release` | The branch staging follows, when it is not the trunk (one the release steps move, such as `staging`). Absent, or equal to `branches.trunk`, is the trunk. Another branch: a push of the trunk reaches staging only at release, so the push's staging step runs and shows nothing, and `release` shows `staging.refresh` after its steps |
| `testdata.schema` | list of paths or globs | `testdata` | Where the tables are defined |
| `testdata.logic` | list of paths or globs | `testdata` | Where the project enforces its rules in code |
| `testdata.databases` | map of name → command | `testdata` | One command per test database (`development`, `test`, `staging`, no other name) that runs SQL read from stdin with `psql`. It names env vars, never an address or password; a database with no open port runs `psql` inside its container with the container's own login |
| `testdata.owner.table` | table name (optional part) | `testdata` | The table whose row is a made-up Account: a record holding one has that Account removed whole by `remove` |
| `testdata.owner.dry_run` | map of name → command (optional) | `testdata` | Per test database, the project's dry run of removing an Account; `{id}` is the Account's id |
| `testdata.owner.remove` | map of name → command | `testdata` | Per test database, the project's own command that removes an Account and every row the app made in it, its backup step included; `{id}` is the Account's id. Same guards as `databases`: env var names only |
| `guard.credentials.block` | list of regexes | credential guard hook | Commands no agent runs: credential scripts and raw writes to the login column. A hit is refused before it runs (exit 2) |
| `guard.credentials.allow` | list of regexes (optional) | credential guard hook | The project's dev-only login commands, each matched against a whole part of the command; they still run |
| `stop.paths` | list of git pathspecs | stop gate hook | What counts as implementation: an uncommitted change under one of them stops the chat from ending |
| `stop.close` | text | stop gate hook | The close step the stop gate's message names (the command or step that commits the work) |
| `release_checks.gate` | command (optional) | `release` | The project's own release gate, run before the first release step; non-zero stops the release |
| `release_checks.ci` | command (optional) | `release` | Waits for the deploy branch's CI run and exits non-zero on red; run before any step after the deploy push |
| `release_checks.no_ci` | text (optional) | `release` | Says the release has no CI run and where its build is checked instead (the recipe's own gate steps, such as `verify` and the project's release gate before the push). With it, the deploy push needs no CI run and the guard prints this line. Never together with `ci` |
| `release_checks.version` | command (optional) | `release` | Prints the version production runs; checked against the released version after the last step |
| `release_checks.whats_new` | command (optional) | `release` | Prints the version the app's What's new shows; checked the same way |

For people only, read by no gate: `staging.up`, `staging.down`, `staging.where`.

## 🧩 Sections

**Required:** `verify`, `branches`, `release`. **Optional sections:** `migrations`, `staging`, `testdata`, `guard`, `stop` and `release_checks`. A repo without one leaves the whole section out: `recipe.py tail` prints `none` and the gates skip the tail; `recipe.py opt staging.refresh` prints `none` and neither a push nor `release` gives a staging step. Inside `staging`, `commit`, `after_push` and `branch` may each be left out (`opt` prints `none`). A section that is present must be complete (`migrations` without `check` still refuses), except its optional parts. `testdata.owner` is an optional part: without it, or without a `remove` command for the database, `clean` deletes only the record's rows and says the removal command is missing. Without `testdata`, the skill of that name says the section is missing and stops; the sprint's live checks then build their own data. Without `guard`, the credential guard hook does nothing; inside it only `allow` may be left out. Each `release_checks` command may be left out on its own (`recipe.py opt release_checks.ci` prints `none`): without `ci`, `release` stops after the deploy push until the user confirms the CI run is green, unless `no_ci` says the release has no CI run (then it goes on, printing that line). Without `stop`, the stop gate hook does nothing; once the chat has launched an agent it counts only the files the chat edited itself.

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
| `dbguard.py clean`, the project's Account removal command fails | ``testdata: the project's removal for the made-up Account {id} failed …`` (nothing more removed, the record stays open) | 5 |
| `dbguard.py create` or `clean` on staging without `--yes` | ``testdata: `staging` asks the user's yes on every run …`` | 6 |
| Credential guard, a command part hits `guard.credentials.block` | ``Blocked: this command sets a real login credential (it matches `{pattern}` …)`` | 2 |
| `release_guard.py lint`, a step that writes the release notes after the step that runs the bump | `release guard: step {n} writes the release notes after the bump (step {m}) …` | 4 |
| `release_guard.py before`, a commit after the bump's tag and before the deploy push | `release guard: the trunk moved after {tag} …` (the commits named) | 4 |
| `release_guard.py before`, the CI run red after the deploy push | `release guard: the CI run on {deploy} is not green …` | 5 |
| `release_guard.py before`, the deploy push with neither `ci` nor `no_ci` | `release guard: {deploy} is pushed and the recipe names no CI watch …` (the user confirms) | 6 |
| `release_guard.py`, a recipe naming both `ci` and `no_ci` | ``release guard: bandit.yaml names both `release_checks.ci` and `release_checks.no_ci` …`` | 3 |
| Stop gate, an uncommitted change under `stop.paths` | `Implementation changes are uncommitted: … Close the loop before stopping: {stop.close}.` (the chat does not end) | 2 |
| Stop gate, a `stop` section it cannot read | ``bandit-dev stop gate: bandit.yaml `stop` cannot be read (…); not checked.`` (the chat ends) | 0 |
| Credential guard, a `guard` section it cannot read (broken YAML, bad regex, no `block`, no PyYAML) | `Blocked: the credential guard cannot read bandit.yaml (…)`: every command, until fixed | 2 |
