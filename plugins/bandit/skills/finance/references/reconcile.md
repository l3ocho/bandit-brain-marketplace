# 🔒 Reconcile

**Command:** `/bandit:finance reconcile`
**Owns:** statements · checking an account against one · locking it

---

## 1️⃣ The statement

Ask for the account, the statement date and its ending balance (signed like the account's balance,
`references/money.md`). For a card, also the minimum payment and due date when the user wants them
kept: `finance_manage_reconciliation { action: "record_statement", accountId, periodEndDate, statementBalanceCents?, minimumPaymentCents?, dueDate?, currency }`.
Earlier statements: `finance_get_account_history { kind: "statements", accountId }`.

## 2️⃣ Check the difference

`finance_get_account_history { kind: "reconciliation", accountId, statementDate, statementBalanceCents, currency? }`
reads the cleared total and the **difference** from the statement. Writes nothing.

| Difference | Next |
|---|---|
| **0** | Offer to complete |
| **Not 0** | Help find it: `finance_list_transactions { accountId, cleared: false, dateTo: statementDate }` lists what isn't cleared yet. The user says which rows are on the statement; mark them with `bulk_edit_preview` → `bulk_edit_apply { field: "cleared", cleared: true }`, then check again |

Never mark a row cleared that the user didn't confirm is on the statement.

## 3️⃣ Complete

`complete { accountId, statementDate, statementBalanceCents, currency, createAdjustment? }` locks
every cleared row up to the statement date. 🔴 A remaining difference is booked as an adjustment
only when the user says yes to `createAdjustment: true` for that amount; otherwise stay at step 2.

After completing, the reconciled rows are locked: editing one later is the user's own, in the app.
Completing closes the app's reconcile reminder task for that account, if there was one.
