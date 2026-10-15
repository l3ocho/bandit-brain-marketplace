# 🗺️ map: the database, the rules, what was built

Part of `bandit-dev:testdata`. Read before `map`, and before the first `fill` or `make` of a chat.
Writes nothing. Its output is the ground every other command stands on.

Contents: Sources · The database · The rules · What was built · The map

## Sources

| What | Where | How |
|---|---|---|
| Table definitions | `recipe.py get testdata.schema` (paths or globs) | Read the files |
| The live structure | The `development` database, else `test` | `dbguard.py read {db}` with catalog queries |
| The rules | `recipe.py get testdata.logic` | Read the code |
| What was built | The cards, the trunk's history | Board `get_task`; `git log`, `git diff` |

`recipe.py` is `${CLAUDE_SKILL_DIR}/../sprint/scripts/recipe.py`; `dbguard.py` is
`${CLAUDE_SKILL_DIR}/scripts/dbguard.py`. Paths are relative to the app repo root.

## The database

1. Read the schema files: tables, columns, types, defaults, enums, links and what a delete does to
   them (cascade, restrict, set null).
2. Confirm against the live database with `read`, catalog only: `information_schema.columns`,
   `table_constraints`, `key_column_usage`, `check_constraints`, `pg_indexes` (partial and unique
   indexes), `pg_trigger` (triggers that write other tables). Constraints kept in migrations rather
   than the schema files show up only here.
3. Note the **owner record**: the table every other row hangs off (an account, workspace, team or
   household). Made-up data gets its own owners, so a person signed in as a made-up user sees only
   made-up data.
4. Row counts per table (`count(*)`), never rows: they tell what the app already holds, not what it
   says.

## The rules

Read the code in `testdata.logic` for every rule the schema does not hold. Look for:

- **Refusals:** the checks that throw or return an error before a write, with their messages
- **Invariants:** one of a kind per owner, contiguous positions, ordered states, totals that must
  match their parts, dates that must follow each other
- **Visibility:** what makes a row visible to one user and hidden from another (roles, membership,
  private flags), so the set exercises both sides
- **Derived rows:** what the app writes alongside a row (an event log, a counter, a child row) that
  the data must also hold for the pages to look right
- **Sign-in:** how a user signs in, and the app's own tool that sets a password, if there is one

Each rule is written as one line with its `file:line`, in plain words.

## What was built

- **One card or a sprint:** `get_task` each card: Spec Acceptance, Scope, Technical plan. For a
  sprint, its batch cards are the blockers of the sprint card.
- **The code:** `git log --oneline {trunk}` for the cards' commits (card ids in messages, merge
  commits of their branches), then `git diff` of those commits: new tables or columns, new rules,
  changed refusals. `{trunk}` is `recipe.py get branches.trunk`.
- Nothing built yet (planning time): the Spec and the Technical plan say what will exist; mark those
  tables and rules "planned" and re-run `map` at execution.

## The map

Shown in the chat, never saved to the repo or the vault:

| Table | Owner path | Columns that matter | Links | Rules (`file:line`) |
|---|---|---|---|---|

Then, per card: the acceptance lines, and for each the tables and rules it touches. End with what
could not be read (a rule in code that is unclear, a table with no schema file) as open points;
nothing is guessed.
