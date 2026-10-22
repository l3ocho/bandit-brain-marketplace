# 🧹 Audit

**Command:** `/bandit:finance audit`
**Owns:** the Finance clean-up check. Read-only until the user approves fix rows.

Runs over the accounts in scope (`references/scope.md`). Every finding comes as a fix row with the
call that fixes it and the command that owns that call; the user approves the rows they want in
one answer, and only those run.

---

## 🔍 The checks

| Check | How it is found | Fix row |
|---|---|---|
| **Uncategorised** | `finance_list_transactions { accountId, categoryId: "uncategorised" }`, opening balances, split rows and transfer sides left out | Run `sort` on them |
| **Duplicate-looking payees** | Payee names that differ only by case, spacing, punctuation or a trailing code | `merge_preview` → `merge` (`references/sort.md`) |
| **Unused payees** | A payee no transaction in scope names, offered for a delete preview only | Delete, confirmed per payee; `PAYEE_REFERENCED` → leave it |
| **Late bills** | Occurrences past their date, nothing posted or matched (`references/bills.md`) | `post`, `skip` or `amend`, the user's pick per row |
| **Bills that never match** | A schedule whose last occurrences were all late or posted by hand | Change its amount kind or window (`update`), or `archive` it |
| **Rules that are off** | `finance_list_rules` with `enabled: false` | Turn on, or leave; another member's rule → "change it in the app" |
| **Budget below zero** | `finance_get_budget` → `assignableCents` negative | Take money back out (`references/month.md`) |
| **Overspent categories** | `availableCents` below 0 this month | `move_between` from a category with money left |
| **Not reconciled for a while** | `finance_get_context` → each account's `lastReconciledDate`: none, or older than the user's usual statement cycle | Run `reconcile` |
| **Targets without money** | A target behind for the month and left to assign above 0 | `auto_assign_preview` |

## 📋 The report

One table: check, what was found (named rows, not just counts), the fix, the command. Then one
question: which rows to run. Rows that hit an action the app keeps for the user (deleting a
category, reversing an import, another member's rule or payee) say "in the app" and have no call.

Never fix anything the user didn't approve in that answer.
