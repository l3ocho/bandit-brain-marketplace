# ✍️ create and clean: writing and removing, through the guard

Part of `bandit-dev:testdata`. Read before `create` or `clean`. Both go through
`${CLAUDE_SKILL_DIR}/scripts/dbguard.py`, which holds the gates; this file says how to use it.

Contents: create · clean · Records · In a sprint

## create

1. **Gate 0** (SKILL.md) for the database. Staging: show the rows per table and ask; quote the yes.
2. `dbguard.py create {db} --kind card --label {card id} [--yes] < {card}.sql`, the SQL from `make`.
3. The guard runs the INSERTs in one transaction and prints the rows per table and the record name.
   A refusal names what to fix (an UPDATE, a missing `RETURNING`); a rule error from the database
   rolls the whole run back: fix the data, never the rule, and run again.
4. Check what the acceptance line needs is there: `dbguard.py read {db}` with counts on the made-up
   owner. Then the check runs.

## clean

| Call | Removes |
|---|---|
| `clean {db} {record path}` | That record's rows |
| `clean {db} card {label}` | Every open card record with that label on that database |
| `clean {db} fill` | The open fill record on that database |

1. Find the record: `dbguard.py records {db}`. None matches → say so; nothing to remove.
2. Staging: name the record and its row count, ask, quote the yes.
3. `dbguard.py clean {db} {record} [--yes]`. It deletes the record's ids, children first, in one
   transaction, then counts them again; a row left fails the run. Rows already gone are clean. The
   record moves to `.testdata/{db}/cleaned/`.
4. **Blocked** by a row the record does not name (the app added it during the check, and the link
   restricts deletes): the transaction rolled back, nothing was removed. Report the table and the
   count to the user and stop; never widen the delete.

`--dry-run` prints the deletes without running them.

## Records

One JSON file per run in `.testdata/{db}/`: database, kind, label, time, and every created row as
table, key column and id, in creation order. The guard writes them; never edit one by hand. The
folder is git-ignored (the guard refuses writes until it is) and never leaves the machine.

## In a sprint

The wave that runs a card's live check: `make` for the card on the code as built, `create` on the
database the check runs against, the check, then `clean {db} card {label}` before the card leaves
Doing, pass or fail. The ledger line for the check names the label and says "created and removed".
A `create` that cannot be made to pass is a failed check with its reason, never a skipped one.
