# 📈 Investments

**Command:** `/bandit:finance investments`
**Owns:** investment subtypes · contributions · the "Dividend, interest or fee" mark · contribution
room · tax-year contributions · market values · goals · exchange rates · net worth

Which accounts: `references/scope.md`. Amounts, rates and currencies: `references/money.md`. This
file repeats neither.

---

## 🏷️ Subtype

An investment account's subtype: `tfsa` · `rrsp` · `fhsa` · `nonRegistered` · `crypto`.
Set or change it with `finance_manage_accounts { action: "update", accountId, investmentSubtype }`,
`null` to clear it. Only an `investment` account takes one (`INVALID_ARGUMENTS` otherwise). Setting
TFSA, RRSP or FHSA makes the app start a goal for it (its `starter`): say so in the proposal.

`finance_get_context` does not list subtypes: read them from
`finance_get_report { kind: "goals" }` → `accounts` (every investment account the member sees, with
its subtype and goal).

## 💸 Contributions

`finance_get_report { kind: "contributions", accountId? }`: per investment account and year, what
went in and out, the rows behind each and the net to date, each account in its own currency.
Transfers and imported deposits count; typed transactions, opening balances and marked rows never do.

**The mark.** A dividend, interest or a fee is not a contribution. Mark one row at a time, each on
the user's yes: `finance_manage_transactions { action: "update", transactionId, incomeMark: true }`
(`false` takes it off). It changes no amount, so a reconciled row takes it. Never as a bulk edit.

## 🎟️ Contribution room

A room is the **member's own**: nobody else reads it. Three rooms per year: `tfsa`, `rrsp` (the
deduction limit on the Notice of Assessment), `fhsa`.

| Ask | Call |
|---|---|
| Room left this year | `finance_get_report { kind: "contribution_room", year }`: each room's entered amount, what counted against it, the room left (negative once over) |
| Enter or change it | `finance_manage_accounts { action: "set_contribution_room", year, room, amountCents, currency }` |
| Take it away | `clear_contribution_room { year, room }` |

A room with `enteredCents` null reads **"Not entered"**, never zero, and its room left is null too.
Only contributions to accounts in the room's currency count against it.

## 🧾 Tax year

`finance_get_report { kind: "tax_year_contributions", year }`: every RRSP and FHSA contribution of
that calendar year, per account, with a total in the account's own currency and no total across
accounts. The same rows the app's Tax year list downloads for the accountant.

## 📊 Market value

The account's value from the statement or the broker's app. **Never a transaction**: the balance,
the budget and the reports do not change.

| Ask | Call |
|---|---|
| Read it, with the gain | `finance_get_account_history { kind: "market_value", accountId }`: latest value and its date, net contributions, gain or loss, one entry per month (`carried` when a month repeats the last value) |
| Enter it | `finance_manage_accounts { action: "set_market_value", accountId, valueCents, readOn, currency }`: replaces that month's value |
| Remove one month's | `remove_market_value { accountId, month }` |

No value yet reads "Not entered", never zero. The gain is the app's; never work it out.

## 🎯 Goals

Read with `finance_get_report { kind: "goals" }`: each goal's accounts and their latest values,
today's value, accounts without a value (left out, never counted at zero), and `projectedCents`,
the value at 65. The projection is an **Estimate**: label it so; it stays null until the monthly
contribution, the yearly return and the date the owner turns 65 are all entered.

| Ask | Call |
|---|---|
| Make one | `finance_manage_accounts { action: "create_goal", name, currency, accountIds?, monthlyContributionCents?, yearlyReturnBasisPoints?, turns65On? }` |
| Change one | `update_goal { goalId, … }`: only what is sent changes; `null` clears a figure |
| Delete one | `delete_goal { goalId }`, confirmed first. On a goal someone else made, it only takes the member's accounts out of it: say so |

A goal holds accounts of its own currency only, each in one goal at most.

## 💱 Exchange rates

For net worth only. The rate and its date are always the user's (`references/money.md` → Rates are
the user's).

| Ask | Call |
|---|---|
| Enter one | `finance_manage_accounts { action: "set_exchange_rate", fromCurrency, toCurrency, rateOn, rate }`: replaces that pair and date |
| Remove one | `remove_exchange_rate { fromCurrency, toCurrency, rateOn }` |
| See them | `net_worth` → `rates` |

A rate is used for its exact pair only, never inverted, from its date on. Rates are the whole
Account's: say so before entering one.

## 🧮 Net worth

`finance_get_report { kind: "net_worth", currency? }`, one reporting currency (default the
household's). Show the **newest month first**, labelled **Estimate**: its total, each account's
figure with its source (balance or market value), each converted account's rate and date, and the
accounts left out with their reason. Offer the earlier months; never list them all unasked.

A left-out account (`no_rate`, `no_market_value`) is named, never filled in: offer the rate or the
value it needs, from the user.
