# ✍️ Log

**Command:** `/bandit:finance log`
**Owns:** one transaction at a time: create, edit, split, transfer

> **Getting it in beats getting it perfect.** A dated amount on the right account is a success;
> an uncategorised row is legal and `sort` finds it later.

---

## ➕ One spend or income

1. Read the account, amount, date, payee and category from the user's words. Missing account and
   more than one in scope → ask, once. Missing date → today. Missing category → leave it empty.
2. **Payee:** match `finance_get_context → payees` by name, case-insensitive. One match → use it.
   More than one → ask. None → `finance_manage_payees { action: "create", name }` (it answers the
   existing payee when the name is taken).
3. **Category:** match the account's own budget categories by name. Same rule: one → use, several →
   ask, none → leave empty and say so. Never create a category from `log`; that is `setup`.
4. Say it back in one line (date · account · payee · category · amount in the account's writing),
   then write: `finance_manage_transactions { action: "create", accountId, date, amountCents, currency, payeeId?, categoryId?, notes?, cleared? }`.

Several in one message ("coffee 5, lunch 18, bus 3") → one table, one yes, then one `create` each,
reading every result. `create` takes one transaction per call.

## ✂️ Split

`split { transactionId, children: [{ amountCents, categoryId, notes? }], currency }`. Children
replace any earlier split, carry the parent's sign and **sum exactly** to it
(`SPLIT_DOES_NOT_SUM`). One level only (`SPLIT_CANNOT_NEST`); the parent keeps no category of its
own. Show the parts and their total against the parent before writing.

## 🔁 Transfer

`transfer { fromAccountId, toAccountId, date, amountCents, currency, toAmountCents?, toCurrency?, fromCategoryId?, toCategoryId?, notes? }`,
`amountCents` positive, leaving `fromAccountId`. One call writes both linked sides.

| Between | Category |
|---|---|
| Two on-budget accounts | 🔴 Required on the sending side (`TRANSFER_NEEDS_CATEGORY`): each account has its own budget, so the money is spent from the sender's and arrives uncategorised in the other |
| On budget ↔ off budget | 🔴 Required on the on-budget side (`TRANSFER_NEEDS_CATEGORY`), never on the off-budget side (`TRANSFER_WRONG_SIDE_CATEGORY`) |
| Two off-budget accounts | None (`TRANSFER_CANNOT_HOLD_CATEGORY`) |
| Two currencies | Both amounts, asked from the user (`TRANSFER_NEEDS_BOTH_AMOUNTS`) |

The sending side's category counts as spending in that budget's reports. Deleting one side deletes both.

## ✏️ Edit

`update { transactionId, … }`: only the fields sent change; an amount needs `currency`.
Find the row first with `finance_list_transactions { accountId, search?, dateFrom?, dateTo? }`;
more than one candidate → show them and ask. `TRANSACTION_RECONCILED` → the row is locked by a
reconciliation: the user unlocks it in the app (`breakReconciliation` is refused to an assistant).

## 🗑️ Delete

Only on the user's explicit ask, confirmed for that row: `finance_delete_items { kind: "transaction", id }`.
No undo. One side of a transfer deletes both: say so in the confirmation.
