# 🌱 fill: a lasting made-up set across the whole app

Part of `bandit-dev:testdata`. Read before `fill {db}`. Needs this chat's `map` (`references/map.md`)
and `references/safety.md`.

Contents: Goal · Steps · Shape of the set · Report

## Goal

After a fill, a person signed in as a made-up user sees made-up data on every page of the app, in
every state the rules allow, and none of the user's own. The set stays until `clean {db} fill`.

## Steps

1. **Gate 0** (SKILL.md), then `dbguard.py records {db}`. An open `fill` record on this database →
   say so and ask: keep it, or `clean` it first. Never two fills on one database.
2. **Plan the set** from the map (shape below) and show it: one row per table, the count and the
   states covered. Staging: this is the summary the user says yes to.
3. **Write the SQL** in insert order, parents first: owners, users, then each area's rows. One
   INSERT per statement, each ending `RETURNING 'testdata', '{table}', '{key}', {key}::text`. Keys
   the app generates are left to it; a parent another statement points to gets an id generated in
   the chat (`python3 -c "import uuid; print(uuid.uuid4())"`) or is looked up by its made-up unique
   name in a sub-select.
4. **Create:** `dbguard.py create {db} --kind fill --label {short-name} [--yes] < fill.sql`, the SQL
   in a scratch file outside the repo. A refusal or a rule error rolls everything back: fix, rerun.
5. **Check:** `dbguard.py read {db}` with counts per table for the made-up owners, and one query per
   rule that the set must satisfy (for example "no owner has two admins"). A miss → `clean` the
   record, fix, fill again.
6. **Sign-in:** set the made-up users' sign-in with the app's own tool if `map` found one and it
   runs against this database; otherwise leave it and give the user the command.

## Shape of the set

- **Owners:** two or three made-up owners (accounts, teams, households), so isolation between owners
  shows; each with users in every role the app has.
- **Every area, every page:** each table the app shows gets rows under each owner. Per area cover
  the states the rules allow: empty and full lists, done and open, private and shared, assigned and
  unassigned, overdue, today and future dates, archived, the limits (the longest name, the most
  items a view shows).
- **Volume:** enough to fill a page and show paging where the app pages; not more. A few hundred rows
  for a whole app, not thousands.
- **Dates** relative to today, so overdue stays overdue and "this week" stays this week.
- **Derived rows** the app would write alongside (logs, counters) are written too when pages read
  them; each is recorded like any other row.

## Report

Three lines at most: what was filled (areas, owners, users), how to sign in as a made-up user, and the
record name to remove it (`/bandit-dev:testdata clean {db} fill`).
