---
name: "testdata"
description: "Fills a dev project's development, test and staging databases with made-up data, and creates and removes the data each card's tests need, from the schema, the app's rules and what was built. Claude Code only. Use for test data, seeding, a sprint's live checks. Not for real data or production."
---

# 🧪 Test data

Reads a project's database, the rules its code enforces and what was built, then writes made-up
data straight into the database: a lasting set that makes every page of the app show made-up
data, and the data each card's acceptance lines need to be tested. The app builds nothing for it.

> **The purpose.** Development, test and staging full of made-up data, none of the user's own.
> Every value is invented here; nothing is copied from existing rows.

## 🧭 Router

`/bandit-dev:testdata <command>`. No command → offer the table and ask which.

| Command | Input | Does | Writes | Reference |
|---|---|---|---|---|
| `map` | Nothing, or card ids, or a sprint card | Reads the schema, the live database's structure, the app's rules and what was built; says which tables and rules each card touches | Nothing | `references/map.md` |
| `fill` | A database: `development`, `test` or `staging` | A complete made-up set across the whole app, following the rules; it stays until `clean` | The database, a run record | `references/fill.md` |
| `make` | Card ids or a sprint card | Works out the made-up data each acceptance line needs, in states the rules allow; shows it with its SQL | Nothing | `references/make.md` |
| `create` | A database, after `make` | Creates that data straight in the database and records every id | The database, a run record | `references/create.md` |
| `clean` | A database and a record, `card {label}`, or `fill` | Removes exactly the rows a record names, then checks none is left | The database | `references/create.md` |

`records` lists the open run records: `python3 ${CLAUDE_SKILL_DIR}/scripts/dbguard.py records`.

| Read | When |
|---|---|
| `references/safety.md` | Once at the start of any command: made-up values, credentials, staging, what the guard enforces |

## 🗺️ Gate 0: before any command

1. **Surface.** Claude Code only, from the app repo root. On Claude.ai say so and stop
2. **The recipe.** `python3 ${CLAUDE_SKILL_DIR}/../sprint/scripts/recipe.py opt testdata.databases`.
   `none` → say the project's `bandit.yaml` has no `testdata` section, show the shape
   (schema, logic, databases) and stop. A missing key refuses by name
3. **The database.** For `fill`, `create` and `clean`:
   `python3 ${CLAUDE_SKILL_DIR}/scripts/dbguard.py check {db}`. A refusal is shown as it is, and the
   command stops: never work around it
4. **Staging.** Any write to `staging` asks the user's yes in this chat first, every run, naming what
   will be written (counts per table) or removed (the record). Quote the yes, then pass `--yes`

## 🔄 How the commands chain

- **On demand.** `map` → `fill {db}`, or `map` → `make {cards}` → `create {db}` → the check →
  `clean {db} card {label}`.
- **In a sprint** (`bandit-dev:sprint`): planning runs `make` for each card with a live check and
  writes the data it needs into the plan; each wave runs `create` before the check and `clean` right
  after it, on the database the check runs against. A card whose data could not be created is a
  failed check, never a skipped one.

## 🔒 Hard rules

1. **Made-up only.** Every value is invented (`references/safety.md`). Existing rows are read as
   counts and shapes, never copied, sampled or shown
2. **One door.** Every database call goes through `scripts/dbguard.py`: `read` for questions, `create`
   for writes, `clean` for removal. Never a database client called directly
3. **The app's rules hold.** Data follows what `map` read: constraints, enums, links, and the rules
   the code enforces. A rule the data cannot meet is reported, not bypassed
4. **Remove only what was created.** `clean` deletes the ids in a run record and nothing else. Rows
   the app made on top of them during a check are reported, never deleted silently
5. **Records stay local.** Run records live in `.testdata/` at the app repo root, git-ignored, never
   committed or copied to the vault

## ⚠️ Gotchas

- `create` refuses UPDATE, DELETE, a `WITH` query or a missing `RETURNING 'testdata', …` → write
  each row as its own INSERT, parents first, and reference a parent by an id generated in the chat
  or by its made-up unique name
- An insert that breaks a rule rolls the whole run back → read the error, fix the data to respect
  the rule, run `create` again; nothing was kept
- The app's own test suite may wipe the test database mid-run → `clean` treats rows already gone as
  clean; run `fill test` again when the set is needed
- `clean` blocked by rows the app added during a check (a comment, a log line on a made-up card) →
  stop, report the table and count, and ask the user; never widen the delete
- Signing in as a made-up user may need the app's own password tool → use the tool `map` found, or
  leave the login unset and tell the user the command; never write a password hash by hand
- First run on a new app: the rules can be misread → show the `map` to the user before the first
  `fill`, and let them check one page before the set is used in a sprint

## 🚫 Never

- Run on a database outside `development`, `test` and `staging`, or on staging without this run's yes
- Copy, sample or derive a value from existing rows, or show an existing row in the chat
- Print, store or echo a database address, password or env file; open `.env*` files
- Change or delete a row no record names; edit the app's code, migrations or `bandit.yaml`
- Commit, push or copy `.testdata/`; leave a card's test data behind after its check
