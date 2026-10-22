# 🪙 Money — cents, signs, currencies, dates

Read before any call that carries an amount, a date or a currency. The app refuses a call that
breaks these; the skill gets them right first.

## 💵 Amounts

| Rule | Example |
|---|---|
| **Integer cents**, never a decimal | `12,34` or `12.34` → `1234` |
| **Signed like a transaction**: negative = money out, positive = money in | Spent 40 → `-4000`; salary 3 000 → `300000` |
| A transfer's `amountCents` is **positive**: the amount leaving `fromAccountId` | Moved 500 to savings → `50000` |
| A split's children carry the parent's sign and sum **exactly** to it | Parent `-18000` → `-14000`, `-2500`, `-1500` |
| A bill (schedule) is signed like a transaction | Rent → negative |
| Targets, held money, assigned money and moved money are **positive** amounts | Assign 400 → `40000` |
| An opening balance and a statement balance are **signed like the account's balance**: a card you owe on is negative | Card statement owing 350 → `-35000` |

Read the user's amount in the account's own writing: `1.234,56` in a Reais account is
`123456`. When a figure could be read two ways (`1,234`), ask.

`AMOUNT_ZERO` and `AMOUNT_NOT_INTEGER_CENTS` mean the amount was 0 or not whole cents: fix it, don't
round it silently.

## 🌎 Currencies

- Every amount the app returns carries its `currency`. Show it with the amount.
- **Every call that carries an amount states `currency`**, equal to the target account's (or
  category's, or rule's) own currency, read from `finance_get_context`. Different →
  `CURRENCY_MISMATCH`, and its reason names the right one.
- **Never convert.** No exchange rate, no "about", no total across currencies. A summary over two
  currencies is two blocks.
- A transfer between two currencies needs both amounts: `amountCents` + `currency` for what left,
  `toAmountCents` + `toCurrency` for what arrived. Ask the user for what arrived; never compute it.
- Each on-budget account has **its own budget**. A budget call names its account (`accountId`), or a
  `currency` when the member has one budget in it. `set_held` and auto-assign always need `accountId`.
- A category belongs to one budget. On a transaction, bill or rule it must come from the same
  account's budget (`CATEGORY_WRONG_BUDGET` otherwise).

## 📅 Dates

| Kind | Format |
|---|---|
| A day | `YYYY-MM-DD` |
| A budget month | `YYYY-MM` |
| A bill occurrence | The occurrence's **original** scheduled date, even after it was moved |

"Yesterday", "last Friday" → work out the date from today's date and say it back in the proposal.
A future date is allowed: it counts in the working balance, not the cleared one.

## 🧮 Balances

Each account has two: **cleared** (seen at the bank) and **working** (cleared + uncleared). Say
which one a figure is. Projected bills are in neither, and never in a total.
