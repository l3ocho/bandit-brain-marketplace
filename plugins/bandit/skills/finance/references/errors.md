# ⛔ Refusal codes

Read when a Finance call comes back `{ ok: false, code, reason, relatedId?, field? }`. Act on
`code`, show `reason`, and resolve `relatedId` to a name before reporting. Never retry a variant of
the same call to get past a refusal; the one exception is `OVER_ROOM`, the app's own confirm step.
Codes are the app's own Finance refusal set.

## 📦 The answer shape

- Every Finance call is **one** operation. A bulk edit, a rule run, an import commit and a payee
  merge are **all or nothing**: refused → nothing changed.
- `field` names the argument that failed. `INVALID_ARGUMENTS` also names an argument the action
  doesn't take: each `action` or `kind` takes only its own.
- `NOT_FOUND` can't be told apart from an id the member can't see. A read never answers an empty
  list for a hidden account: it answers `NOT_FOUND`.

## 🗂️ Codes

| Code | Means | Do |
|---|---|---|
| `MODULE_DISABLED` | Finance is off for this member | Say so; the admin turns it on in Settings. Stop |
| `NOT_FOUND` · `ACCOUNT_NOT_FOUND` · `CATEGORY_NOT_FOUND` · `PAYEE_NOT_FOUND` · `TRANSACTION_NOT_FOUND` · `SCHEDULE_NOT_FOUND` · `RULE_NOT_FOUND` · `IMPORT_BATCH_NOT_FOUND` · `GOAL_NOT_FOUND` | The id names nothing this member can see: unknown, deleted, malformed, or on a private account | Re-read `finance_get_context` and match by name. Still missing → it may not be shared with them: say so, never search another way |
| `ASSISTANT_CANNOT` | One of the user's own actions: who sees an account, deleting an account, category or group, reversing an import, unlocking a reconciled row, the default currency, learning switches, another member's rule or payee | Tell the user to do it in the app. No workaround |
| `NOT_VISIBLE_TO_MEMBER` · `REQUIRES_ADMIN` · `NOT_AUTHENTICATED` | The member can't see it, or only the admin may | Say who can; stop |
| `INVALID_ARGUMENTS` | A malformed call: missing or wrong-type argument, another action's argument, a bad date | Fix the call from `field` and `reason` |
| `CURRENCY_MISMATCH` | The call's `currency` isn't the target's own; the reason names the right one | Restate the amount in that currency (`references/money.md` → Currencies) |
| `UNKNOWN_CURRENCY` | A code the app doesn't hold | Ask which currency |
| `CATEGORY_CURRENCY_MISMATCH` · `CATEGORY_WRONG_BUDGET` | The category belongs to another budget than the account's | Use a category from this account's own budget |
| `AMOUNT_ZERO` · `AMOUNT_NOT_INTEGER_CENTS` | The amount is 0 or not whole cents | Fix it (`references/money.md`); don't round silently |
| `SPLIT_DOES_NOT_SUM` | The parts don't add up exactly to the transaction | Show the gap; the user fixes a part |
| `SPLIT_CANNOT_NEST` · `SPLIT_PARENT_CANNOT_HOLD_CATEGORY` | A split part can't be split; a split row's categories live in its parts | Edit the parts instead |
| `TRANSACTION_RECONCILED` | The row is locked by a reconciliation | The user unlocks it in the app |
| `TRANSFER_NEEDS_CATEGORY` · `TRANSFER_WRONG_SIDE_CATEGORY` · `TRANSFER_CANNOT_HOLD_CATEGORY` | The category is on the wrong side for this kind of transfer | Fix per `references/log.md` → Transfer |
| `TRANSFER_NEEDS_BOTH_AMOUNTS` | Two currencies, one amount | Ask the user what arrived |
| `TRANSFER_SAME_ACCOUNT` | Both sides are one account | Ask for the other account |
| `ACCOUNT_CLOSED` | The account is closed | Ask before `reopen` |
| `ACCOUNT_BUDGET_NOT_EMPTY` | Its budget still has categories, so it can't go off budget | The user removes them in the app first |
| `ACCOUNT_HAS_TRANSFERS` · `ACCOUNT_LIST_EMPTY` | Account deletion and sharing rules: both are the user's own | Point to the app |
| `INCOME_GROUP_EXISTS` | The budget already has its one income group | Add the category to that group |
| `PAYEE_REFERENCED` | Something still uses the payee | Merge it instead (`references/sort.md`) |
| `ALERT_WITHIN_MATCH_WINDOW` | A bill's alert would fire while a match is still possible | Set `alertAfterDays` above `matchWindowDays` |
| `OCCURRENCE_ALREADY_SETTLED` | That occurrence was already posted, matched or skipped | Show which; nothing to do |
| `IMPORT_BATCH_ALREADY_REVERSED` · `IMPORT_BATCH_NOT_REVERSIBLE` | The import is already undone, or a row of it was since touched | Report the rows the reason names |
| `RULE_CURRENCY_MISMATCH` | The rule's currency isn't the account's | Run it over an account in its currency |
| `RULE_CREATOR_CANNOT_SEE_ACCOUNT` | The rule's creator can't see that account | Report it; the creator decides |
| `OVER_ROOM` | A transfer into a TFSA, RRSP or FHSA is larger than the member's room left for that year; nothing saved. It names the room left | Show the app's line; resend the same call with `overRoomConfirmed: true` only on the user's yes (`references/log.md`) |
| `ROOM_NOT_FOUND` · `RATE_NOT_FOUND` · `MARKET_VALUE_NOT_FOUND` | No room entered for that year, no rate for that pair and date, no value for that month | Say nothing is entered there; nothing to remove |
| `INVALID_ARGUMENTS` on a market value or subtype | The account is not an investment account | Name the account's type; only an investment account takes one (`references/investments.md`) |
| `INTERNAL` | The server failed; the same call fails again | Report it; no retry |
