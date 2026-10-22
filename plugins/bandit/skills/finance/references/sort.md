# 🧹 Sort

**Command:** `/bandit:finance sort`
**Owns:** categorising in bulk · payee merges and defaults · the app's category suggestions · rules

Clears the uncategorised pile in batches and turns a repeated fix into a rule, so the same pile
doesn't come back.

---

## 1️⃣ Find the pile

Per scoped account: `finance_list_transactions { accountId, categoryId: "uncategorised", limit? }`.
The read also returns rows that carry no category by design: leave out `isOpeningBalance`, `isSplitParent` and any row with a `transferId`. Show the count per
account, then the rows grouped by payee, biggest group first.

## 2️⃣ Categorise a group

1. Propose a category from the account's own budget, per payee group. The user confirms or changes.
2. `finance_manage_transactions { action: "bulk_edit_preview", transactionIds, field: "category" }`.
   Show what it will change and what it **excludes** (split rows, transfer sides) by name.
3. On yes: `bulk_edit_apply { transactionIds, field: "category", categoryId }`. All or nothing: one
   reconciled row refuses the whole batch and is named. Up to 500 ids per call.

The same two steps work for `payee`, `notes` and `cleared`.

## 3️⃣ Make it stick

When one payee keeps landing in one category, offer, in this order:

| Fix | Call | Best when |
|---|---|---|
| Payee default | `finance_manage_payees { action: "set_default_category", payeeId, categoryId, accountId? }` | The payee is always one category on this budget. A matching rule beats it |
| Rule | `finance_manage_rules` (below) | The bank's text varies, or amount or account matters |

The app also **learns**: it proposes a payee's default from the user's own choices. Answer a
proposal with `confirm_learning` or `decline_learning { payeeId, categoryId }` (a declined pair never
returns). Turning learning on or off is the user's own, in the app.

## 4️⃣ Rules

1. `finance_list_rules` first: change an existing rule rather than add a twin.
2. `create { name, currency? }` → `set_conditions { ruleId, conditions, currency? }` →
   `set_actions { ruleId, ruleActions }`. Each set **replaces all** of its kind: send the full list.
   Conditions: `field` (`importedPayeeText`, `payee`, `amount`, `date`, `account`, `notes`) with
   an `operator` the app accepts for it; amounts in the rule's currency. Actions: `setPayee`,
   `setCategory`, `setNotes`, `setCleared`, `convertToTransfer`.
3. To apply it to rows already there: `preview_run { ruleId, accountId, filters… }`, show it, then
   `apply_run` with the same filters. Reconciled and split rows are left alone.
4. Order matters when two rules disagree: `reorder` with every rule named once.

A rule another member created can be read and run, never edited, renamed, switched, reordered or
deleted (`ASSISTANT_CANNOT`). A rule acts only on accounts its creator can see
(`RULE_CREATOR_CANNOT_SEE_ACCOUNT`) and only in its own currency (`RULE_CURRENCY_MISMATCH`).

## 5️⃣ Duplicate payees

Names that are one shop (`AMZN Mktp`, `Amazon.ca`): pick the clean one as the target.
`merge_preview { sourcePayeeIds, targetPayeeId }` → show the counts → on yes, `merge`. 🔴 Not
reversible: the sources are deleted. A payee another member created can't be merged by an assistant.
A payee nothing uses can be deleted (`finance_delete_items { kind: "payee" }`, confirmed);
`PAYEE_REFERENCED` → merge it instead.
