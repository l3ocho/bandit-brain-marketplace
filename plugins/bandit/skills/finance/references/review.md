# 📊 Review

**Command:** `/bandit:finance review [week|month]`
**Owns:** the read-only money picture. Writes nothing.

Default: the current month so far. `week` = the last seven days. A named month (`review 2026-09`) =
that month.

---

## 🧱 What it shows, in this order

| Block | Call | Shows |
|---|---|---|
| **Where things stand** | `finance_get_context` | Each scoped account: cleared and working balance |
| **What's coming** | `finance_get_report { kind: "forecast", horizonDays? }` (default 90) | Per account and per currency: `lowestCents`, `lowestDate` and `firstBelowZeroDate` (read them; never list the daily `points`). 🔴 Any `firstBelowZeroDate` comes first, flagged |
| **Where it went** | `finance_get_report { kind: "reports", from, to, currency? }` | Spending by category, biggest first; income against expense |
| **The budget** | `finance_get_budget { month, accountId }` per scoped budget | Left to assign, overspent categories (`references/month.md`) |
| **Loose ends** | Counts only | Uncategorised rows, late bills, accounts not reconciled for a while: each with the command that clears it |

## 🔴 Rules for the numbers

- Every figure is the app's own. No sums, averages or percentages the app didn't return, except a
  difference between two figures of **one** currency the user asked for, shown with both inputs.
- One block per currency. `reports` takes one currency per call: call it once per currency in scope.
- `reports` returns a `note` saying what it leaves out (transfers, opening balances, what isn't posted, other currencies): show it once under the block.
- Reports and the forecast count every account the member can see. With a `finance:` line, say in
  one line that the report also includes accounts outside this project's.
- No judgement about spending. Facts and the next useful command.

## ✍️ Saving it

The review is a chat answer. When the user wants it kept as a note, hand the text to bandit:notes,
which owns where and how notes are written.
