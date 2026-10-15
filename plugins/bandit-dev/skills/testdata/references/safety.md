# 🛡️ Safety: made-up values, credentials, staging

Part of `bandit-dev:testdata`. Read once at the start of any command.

Contents: Made-up values · Reading existing data · Credentials · Databases and staging · What the guard enforces

## Made-up values

The purpose of the skill: test environments with made-up data, none of the user's own.

- **Invented here.** Names, titles, notes, amounts, dates: written in the chat, never selected,
  sampled, shuffled or derived from existing rows.
- **Recognisable.** Usernames start with `td-`; emails end in `@example.test`; phone numbers use the
  `555-01xx` range; owner names say what they are ("Otter Works", "Maple Street Home").
- **Plausible.** Realistic enough to judge a page: mixed lengths, a few accents and emoji, one long
  title per list, amounts with cents.
- **Nothing personal.** No real people, companies, addresses, account numbers or health details,
  even invented-looking ones that match a real person.

## Reading existing data

`map`, the checks and `clean` read the database through `dbguard.py read`, inside a read-only
transaction. Ask for counts, shapes and catalog facts. Never select an existing row's content into
the chat; the guard cuts long output and says so.

## Credentials

- `bandit.yaml` names env vars (`"$DATABASE_URL"`) or runs inside a database container with its own
  login; the guard refuses a command holding an address or password and never prints a command.
- Never run `env`, `printenv`, `echo $VAR` on a database variable, or read a `.env*` file. An unset
  variable is reported by name only.
- Output from the database passes through the guard, which hides addresses and passwords.

## Databases and staging

| Database | Writes |
|---|---|
| `development` | Yes |
| `test` | Yes. The app's own tests may wipe it at any time |
| `staging` | Yes, after the user's yes in this chat, every run; the yes is quoted before `--yes` |
| Any other name | Never. The guard refuses it, and a `bandit.yaml` that lists one |

## What the guard enforces

| Guard | Skill's job |
|---|---|
| Only the three database names; no secret in a command; env vars set | Choose the database the check runs against |
| `create`: INSERTs only, each with `RETURNING 'testdata', …`, one transaction | Write data that follows the rules |
| Every created id recorded; `clean` deletes only those | Clean after every check |
| Staging writes need `--yes` | Ask and quote the yes first |
| `.testdata/` git-ignored before any write | Say so when the app's `.gitignore` lacks it; the app adds it |
| `read` in a read-only transaction, output cut at 200 lines | Ask for counts, not rows |
