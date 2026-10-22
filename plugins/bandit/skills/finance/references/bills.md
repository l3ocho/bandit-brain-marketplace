# 🧾 Bills

**Command:** `/bandit:finance bills`
**Owns:** repeating bills and income (schedules) and each of their occurrences

A schedule produces **expected occurrences**. They show in the register and the forecast but count
in no balance until they are posted, auto-posted or matched by an import.

---

## 👀 What's due

`finance_list_schedules { accountId? }`, and per account
`finance_list_transactions { accountId, includePending: true, dateFrom, dateTo }` for the
occurrences still waiting. Show one table: bill, account, next date, expected amount, and
**late** for any occurrence past its date with nothing posted or matched. Missed occurrences are
never merged: three missed rents are three rows.

## ➕ A new bill or income

`finance_manage_schedules { action: "create", accountId, name, startDate, intervalMonths, amountKind, amountCents, currency, … }`.
Signed like a transaction (a bill is negative). Ask only what changes the result:

| Field | Values · default |
|---|---|
| `intervalMonths` | Every N months (1 = monthly, 12 = yearly) |
| `amountKind` | `exact` · `approximate` (+ `toleranceBasisPoints`, 750 = 7.5%) · `range` (+ `minAmountCents`, `maxAmountCents`) |
| `categoryId`, `payeeId` | From the account's own budget |
| `autoPost` | Off by default: the occurrence waits for the real transaction |
| `weekendHandling` | `asScheduled` · `nextBusinessDay` · `previousBusinessDay` |
| `needsHumanAction` | 🔴 On for a bill the user pays by hand: **the app** then creates a reminder task for it, `taskLeadDays` ahead (default 5), with `priority` 1–4 (default 2). This skill never writes the task itself |
| `matchWindowDays` · `alertAfterDays` | Default 5 · 7. The alert must come after the window (`ALERT_WITHIN_MATCH_WINDOW`) |

A variable bill (hydro, phone) is `approximate` or `range`, never a made-up exact figure.

## ✏️ One occurrence, or the whole bill

| Ask | Call | Changes |
|---|---|---|
| Skip this one | `skip { scheduleId, occurrenceDate }` | That occurrence only |
| This one is a different amount or day | `amend { scheduleId, occurrenceDate, date?, amountCents?, currency? }` | That occurrence only |
| It's paid, record it now | `post { scheduleId, occurrenceDate, date?, amountCents?, currency? }` | Creates the real transaction |
| That match was wrong | `unmatch { scheduleId, occurrenceDate }` | The occurrence waits again |
| Change the bill from now on | `update { scheduleId, name?, nextDate?, intervalMonths?, amount?, priority?, currency? }` | Future occurrences. `amount` replaces the whole amount specification |
| Stop the bill | `archive { scheduleId }` | Posted transactions stay |

`occurrenceDate` is always the **original** scheduled date, even after an `amend` moved it.
`OCCURRENCE_ALREADY_SETTLED` → it was already posted, matched or skipped; its `relatedId` is the transaction that settled it: edit that instead, don't retry.

Changing a bill's next date or interval replaces its open reminder tasks; comments or tags on the
old open task are lost. Say so before an `update` that changes either.
