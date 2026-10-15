# 🧩 make: the data each acceptance line needs

Part of `bandit-dev:testdata`. Read before `make`. Needs this chat's `map` for the same cards
(`references/map.md`) and `references/safety.md`. Writes nothing.

Contents: Steps · The data table · In a sprint plan

## Steps

1. Run `map` for the cards if this chat has none for them.
2. For each card, each **acceptance line**: what must exist in the database for that line to be
   tested, in both directions where it applies (the case that works and the case the app refuses,
   the user who sees it and the one who must not).
3. Express it as rows: tables, counts, the field values that matter, the rule each row respects.
4. Make the card's data **self-contained**: its own made-up owner and users, so the check never
   depends on the lasting set or on another card's data, and its `clean` never touches either.
5. Write the SQL the same way as `fill` (`references/fill.md`, step 3), labelled with the card id.
   Keep it in a scratch file outside the repo, one per card, for `create`.
6. A line that needs something no data can give (an outside service, a time of day) is said plainly:
   data is not the blocker there, and what is.

## The data table

Shown in the chat, one table per card:

| Acceptance line | Data it needs | Rows (table: count) | Rules respected |
|---|---|---|---|

Then the sign-in each check uses (which made-up user, which role) and the label `create` will use.

## In a sprint plan

At sprint planning step 7 (`bandit-dev:sprint`, `references/plan.md` → Test data), `make` runs for
each card with a live check, read-only. The plan section of the card carries, per check: the data
it needs in plain words, the label, and the line "created by `/bandit-dev:testdata create` before the
check, removed by `clean` after it". The SQL is not copied into the plan: the wave runs `make` again
on the code as built, then `create`.
