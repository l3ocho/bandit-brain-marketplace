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
| A market value, a contribution room and a goal's monthly contribution are **zero or more** | Room 7 000 → `700000` |
| A goal's yearly return is in **basis points** | 6% → `600` |
| An exchange rate is a **decimal string**, the one decimal the app takes: one unit of `fromCurrency` in `toCurrency`, at most eight decimals | `'1.3725'` |

Read the user's amount in the account's own writing: `1.234,56` in a Reais account is
`123456`. When a figure could be read two ways (`1,234`), ask.

`AMOUNT_ZERO` and `AMOUNT_NOT_INTEGER_CENTS` mean the amount was 0 or not whole cents: fix it, don't
round it silently.

## 🌎 Currencies

- Every amount the app returns carries its `currency`. Show it with the amount.
- **Every call that carries an amount states `currency`**, equal to the target account's (or
  category's, or rule's) own currency, read from `finance_get_context`. Different →
  `CURRENCY_MISMATCH`, and its reason names the right one.
- **Never convert** (the one home of this rule). The skill never converts, estimates or rounds
  between currencies itself: no rate of its own, no "about", no total across currencies. A summary
  over two currencies is two blocks.
- **The one converted figure is the app's.** `finance_get_report { kind: "net_worth" }` is the only
  figure in one currency across accounts of several. Show it labelled **Estimate**, with each
  converted account's rate and its date, and each month's left-out accounts with their reason
  (`no_rate`, `no_market_value`). Never add to it, work it out again or fill a left-out account.
- **Rates are the user's.** An exchange rate is entered only as the user gives it, with its date:
  never proposed, looked up or inverted by Claude. It feeds net worth only; no write converts.
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
| A market value's `readOn` | The day it was read, today or earlier; its month is the value's month |
| A room's or a tax year's `year` | The calendar year, e.g. `2026` |

"Yesterday", "last Friday" → work out the date from today's date and say it back in the proposal.
A future date is allowed: it counts in the working balance, not the cleared one.

## 🧮 Balances

Each account has two: **cleared** (seen at the bank) and **working** (cleared + uncleared). Say
which one a figure is. Projected bills are in neither, and never in a total.
